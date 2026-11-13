import io
import pytest
import pdfplumber
import pandas as pd
from backend.app.services.ingestion import load_dataset_file
from backend.app.services.cleaning import CleaningService
from backend.app.services.semantic_service import SemanticService
from backend.app.services.dashboard_generator import DashboardGenerator
from backend.app.services.export_service import ExportService

def test_cricket_dataset_autonomous_dashboard():
    """Verify cricket dataset generation: domain is sports, KPIs and charts strictly from data, no wins/losses."""
    df = pd.read_csv("sample_data/cricket_dataset.csv")
    assert len(df) == 516
    assert list(df.columns) == ["index", "runs", "opponent", "ground", "date", "match", "Match_No", "total"]

    sem = SemanticService.build_semantic_layer(df)
    assert sem["domain"] == "sports"

    spec = DashboardGenerator.generate_auto_dashboard(df, sem, dataset_name="Cricket Matches")
    assert spec["domain"] == "sports"
    assert spec["theme"]["primary"] == "emerald"

    # 4 KPI cards
    kpis = spec["kpi_cards"]
    assert len(kpis) == 4
    
    kpi_map = {k["title"]: k for k in kpis}
    assert "Total Matches" in kpi_map
    assert kpi_map["Total Matches"]["value"] == 516
    assert len(kpi_map["Total Matches"]["sparkline"]) == 10

    assert "Total Runs" in kpi_map
    assert kpi_map["Total Runs"]["value"] == 23709 or kpi_map["Total Runs"]["value"] == 25232

    assert "Highest Match Runs" in kpi_map
    assert kpi_map["Highest Match Runs"]["value"] == 254

    assert "Top Opponent" in kpi_map
    assert kpi_map["Top Opponent"]["value"] == "Australia"

    # Strict Data Grounding: Verify charts use ONLY dataset columns
    all_spec_text = str(spec).lower()
    assert "wins" not in all_spec_text
    assert "losses" not in all_spec_text
    assert "wicket" not in all_spec_text

    # Top Entities Leaderboard
    assert spec["top_entities_table"] is not None
    assert spec["top_entities_table"]["dimension"] == "opponent"
    assert len(spec["top_entities_table"]["rows"]) > 0
    assert spec["top_entities_table"]["rows"][0]["entity"] == "Australia"

def test_sales_dataset_adaptation():
    """Verify second dataset: domain changes to sales, theme changes to indigo, metrics change to revenue/sales."""
    raw_df, _ = load_dataset_file("sample_data/messy_sales_data.xlsx", "xlsx")
    clean_df, _ = CleaningService.auto_clean_safe_defaults(raw_df)
    sem = SemanticService.build_semantic_layer(clean_df)
    
    assert sem["domain"] == "sales"

    spec = DashboardGenerator.generate_auto_dashboard(clean_df, sem, dataset_name="Retail Sales Report")
    assert spec["domain"] == "sales"
    assert spec["theme"]["primary"] == "indigo"
    assert "indigo" in spec["theme"]["gradient"]

    # Verify KPI wording adapted
    kpi_titles = [k["title"] for k in spec["kpi_cards"]]
    assert any("Transaction" in t or "Sales" in t for t in kpi_titles)

def test_pdf_export_matches_onscreen_numbers():
    """Verify that exported PDF numbers equal the on-screen dashboard numbers."""
    df = pd.read_csv("sample_data/cricket_dataset.csv")
    sem = SemanticService.build_semantic_layer(df)
    spec = DashboardGenerator.generate_auto_dashboard(df, sem, dataset_name="Cricket Dataset")
    
    # Export PDF via headless Playwright
    pdf_bytes = ExportService.export_pdf(spec, user_name="Lead Analyst")
    assert len(pdf_bytes) > 10000

    # Extract text from PDF
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        extracted_text = "\n".join([page.extract_text() for page in pdf.pages])

    # Assert exact dashboard values appear in the PDF
    assert "516" in extracted_text
    assert "23,709" in extracted_text or "25,232" in extracted_text
    assert "254" in extracted_text
    assert "Australia" in extracted_text
    assert "Sports" in extracted_text
    assert "Lead Analyst" in extracted_text
    assert "wins" not in extracted_text.lower()
    assert "losses" not in extracted_text.lower()

def test_all_export_formats_generated_validly():
    """Verify PNG, PPTX, Excel, and CSV export outputs."""
    df = pd.read_csv("sample_data/cricket_dataset.csv")
    sem = SemanticService.build_semantic_layer(df)
    spec = DashboardGenerator.generate_auto_dashboard(df, sem, dataset_name="Cricket Dataset")

    png = ExportService.export_png(spec)
    assert len(png) > 10000
    assert png.startswith(b"\x89PNG")

    pptx = ExportService.export_pptx(spec, df)
    assert len(pptx) > 10000

    excel = ExportService.export_excel(df, spec)
    assert len(excel) > 5000

    csv_data = ExportService.export_csv(df)
    assert "opponent" in csv_data
    assert "runs" in csv_data

def test_cricket_automl_feature_importance_and_what_if():
    """
    Verify Bug 1 Fix:
    1. Feature importance is computed from best non-baseline model and is non-empty.
    2. What-if fields are populated in feature_metadata.
    3. Index and monotonic cumulative columns (like 'total') are excluded.
    4. Time-ordered engineered features (rolling means, seq_num) are generated.
    """
    from backend.app.ml.automl import AutoMLTrainer
    df = pd.read_csv("sample_data/cricket_dataset.csv")
    res = AutoMLTrainer.train_and_evaluate(df, "runs", "pytest_cricket_eval")

    # Feature importance must not be empty
    assert len(res["feature_importance"]) > 0, "Feature importance must be non-empty"
    features_present = [f["feature"] for f in res["feature_importance"]]
    
    # Exclude identifier and cumulative columns
    assert "index" not in features_present, "Row index must be excluded"
    assert "total" not in features_present, "Monotonic cumulative total must be excluded"

    # What-if form metadata fields must exist
    assert len(res["feature_metadata"]) > 0, "What-if form fields must exist"
    meta_names = [m["name"] for m in res["feature_metadata"]]
    assert any("opponent" in m for m in meta_names), "Opponent features must be present"
    assert any("rolling_mean" in m for m in meta_names), "Shifted rolling features must be present"

    # Verify each what-if field has proper control attributes
    for field in res["feature_metadata"][:5]:
        assert "name" in field
        assert "min" in field
        assert "max" in field
        assert "default" in field
        assert field["min"] <= field["max"]

    # When no model beats baseline, confidence is flagged as low
    if res["best_algorithm"] == "Baseline" or res["no_model_beats_baseline"]:
        assert res["confidence"] == "low"
        assert any("predicts" in w.lower() for w in res["warnings"])
