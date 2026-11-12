# InsightForge AI (v2) - Architecture Specification

## 1. Executive Summary & Tenets
**InsightForge AI** is an enterprise-grade autonomous data analyst platform designed to ingest raw, messy datasets or live relational databases and produce clean data, declarative dashboards, statistical tests, and machine learning forecasts in under 60 seconds.

### Fundamental Non-Negotiable Tenets:
1. **Code computes, AI explains**: The LLM is strictly prohibited from generating numbers. Every number on every chart, card, and insight originates from deterministic SQL (DuckDB), SciPy, or scikit-learn models, equipped with reproducible "Show how" links.
2. **Honest labels**: Transparent badges accompany every datum:
   - `[Computed]` (SQL/mathematical aggregation)
   - `[Statistical test]` (ANOVA, FDR-corrected p-values, Pearson/Spearman)
   - `[ML prediction]` (XGBoost, Holt-Winters, Optuna, Scikit-learn)
   - `[AI-generated]` (Qualitative explanations and recommendations)
3. **Non-destructive Parquet lake**: Raw uploads are never mutated. All operations generate immutable versioned Parquet files with full undo/redo and restore capabilities.
4. **Autopilot vs. Review modes**: Autopilot executes end-to-end cleaning and dashboarding instantly; Review mode presents step-by-step impact previews for human-in-the-loop authorization.

---

## 2. System Architecture Diagram

```mermaid
flowchart TD
    subgraph UI_Layer ["Frontend Client (React + TypeScript + Vite + Tailwind + ECharts)"]
        Dashboard["Declarative Dashboard (ECharts Grid)"]
        CleanStudio["Cleaning Studio (Quality Score 0-100)"]
        SemanticUI["Semantic Layer Manager"]
        ChatAgentUI["Safe Text-to-SQL Agent Chat"]
        Simulator["What-If & Sensitivity Tornado Simulator"]
    end

    subgraph API_Layer ["API Gateway (FastAPI + Pydantic + SSE)"]
        IngestRouter["/api/datasets/upload"]
        CleanRouter["/api/clean/apply"]
        SemanticRouter["/api/semantic"]
        StatsRouter["/api/stats"]
        MLRouter["/api/ml/train & forecast"]
        ChatRouter["/api/chat/query"]
        JobsRouter["/api/jobs/stream"]
    end

    subgraph Core_Engines ["Core Analytical Engines"]
        DuckEngine["DuckDB In-Memory Engine"]
        SqlglotGate["Safe AST Validator (sqlglot)"]
        Profiler["Statistical Profiler & PII Detector"]
        AutoML["AutoML (Optuna, XGBoost, Scikit-learn)"]
        Forecaster["Holt-Winters & ARIMA Forecaster"]
        Scorer["Insight Scorer (Effect x Significance x Coverage)"]
    end

    subgraph Storage_Layer ["Data Lake & Persistent Storage"]
        ParquetLake[("Versioned Parquet Lake (data/parquet/)")]
        MetaDB[("SQLite Metadata (data/insightforge_meta.db)")]
        ModelsStore[("Saved Joblib Models (data/saved_models/)")]
    end

    UI_Layer <--> API_Layer
    API_Layer --> Core_Engines
    Core_Engines --> Storage_Layer
```

---

## 3. Data Processing Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Ingestion as Ingestion Service
    participant Profiler as Statistical Profiler
    participant Semantic as Semantic Layer
    participant Cleaner as Cleaning Studio
    participant DuckDB as DuckDB / Parquet
    participant Dashboard as Dashboard Engine

    User->>Ingestion: Upload Messy File (.xlsx / .csv / .sqlite)
    Ingestion->>Ingestion: Unmerge cells, clean currency, strip subtotals
    Ingestion->>DuckDB: Save Version 1 Parquet
    Ingestion->>Profiler: Run statistical profiling & PII detection
    Profiler->>Semantic: Classify domain, metric & dimension roles
    Semantic->>Semantic: Auto-generate Metric formulas (e.g. Revenue = SUM(sales))
    User->>Cleaner: Approve recommended cleaning plan
    Cleaner->>DuckDB: Apply steps & commit Version 2 Parquet
    Cleaner->>Dashboard: Build declarative JSON dashboard spec
    Dashboard->>User: Interactive Dashboard rendered in <60 seconds
```

---

## 4. Security Architecture

1. **sqlglot AST Query Validation**:
   - Only `SELECT` and `UNION` statements are permitted.
   - Access is restricted to virtual memory tables (`data`, `dataset`).
   - System/disk-access functions (`read_parquet`, `copy`, `install`) are completely banned.
   - Automatic query limit enforcement (max 10,000 rows) prevents denial-of-service.
2. **Read-Only Database Enforcement**:
   - Connection validation blocks `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, and `CREATE`.
3. **Privacy Mode & PII Masking**:
   - Automatic regex detection for emails, phones, SSNs, and credit cards.
   - Dynamic hashing masks PII before any data reaches external LLM adapters.
4. **Sandboxed Code Execution**:
   - Zero network connectivity inside analytical sandbox.
   - 10-second hard execution timeout and 512 MB memory boundary.
