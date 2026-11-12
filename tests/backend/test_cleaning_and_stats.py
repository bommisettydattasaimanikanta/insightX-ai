import pytest
import pandas as pd
import numpy as np
from backend.app.services.cleaning import CleaningService
from backend.app.services.profiling import calculate_data_quality_score, profile_dataset
from backend.app.services.statistics import StatisticsService

def test_data_quality_and_cleaning_pipeline():
    # Construct a test dataset with duplicates, missing values, outliers, and untrimmed text
    data = {
        "Name": [" Alice ", "Bob", "Charlie", "Bob", None, "David", "Eva  "],
        "Age": [25, np.nan, 35, 25, 40, 250, 28], # 250 is an outlier
        "Income": [50000, 60000, 75000, 50000, 80000, 95000, 55000],
        "Department": ["Sales", "Engineering", "Marketing", "Sales", "Sales", "Engineering", "Marketing"]
    }
    df = pd.DataFrame(data)
    
    # 1. Profile before cleaning
    initial_score = calculate_data_quality_score(df)
    assert initial_score["overall"] < 100.0
    
    # 2. Generate plan
    plan = CleaningService.generate_cleaning_plan(df)
    assert len(plan) >= 2 # should detect duplicates and missing values
    
    # 3. Execute approved plan
    cleaned_df, report = CleaningService.execute_cleaning_plan(df, plan)
    
    # Check that quality improved
    assert report["score_after"]["overall"] >= report["score_before"]["overall"]
    assert len(cleaned_df) <= len(df) # duplicate removed

def test_statistics_correlations_and_trends():
    np.random.seed(42)
    x = np.linspace(10, 100, 50)
    y = 2.5 * x + np.random.normal(0, 5, 50) # strong positive correlation
    z = np.random.normal(50, 10, 50)
    
    df = pd.DataFrame({"VarX": x, "VarY": y, "VarZ": z})
    corr_results = StatisticsService.compute_correlations(df)
    
    top_pair = corr_results["top_pairs"][0]
    assert top_pair["col1"] in ["VarX", "VarY"]
    assert top_pair["col2"] in ["VarX", "VarY"]
    assert top_pair["pearson_r"] > 0.9
    assert top_pair["p_value"] < 0.001
    assert "significant" in top_pair["significance"]

def test_hypothesis_testing_anova():
    # 3 distinct groups
    group_a = np.random.normal(100, 5, 30)
    group_b = np.random.normal(150, 5, 30)
    group_c = np.random.normal(200, 5, 30)
    
    df = pd.DataFrame({
        "Category": ["A"] * 30 + ["B"] * 30 + ["C"] * 30,
        "Score": np.concatenate([group_a, group_b, group_c])
    })
    
    results = StatisticsService.run_hypothesis_tests(df)
    assert len(results) > 0
    test_res = results[0]
    assert test_res["is_significant"] is True
    assert test_res["p_value_fdr"] < 0.05
    assert test_res["effect_size_label"] == "large"
