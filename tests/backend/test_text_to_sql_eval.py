import os
import pytest
import pandas as pd
import duckdb
from backend.app.agents.text_to_sql import SafeTextToSQLAgent
from backend.app.services.ingestion import save_to_parquet
from backend.app.services.semantic_service import SemanticService

# 30 Comprehensive Text-to-SQL Evaluation Benchmark Questions
EVAL_QUESTIONS = [
    # Basic Aggregations
    {"q": "What is the total sales amount?", "expected_type": "number", "metric": "Sales Amount"},
    {"q": "What is the average sales amount?", "expected_type": "number", "metric": "Sales Amount"},
    {"q": "What is the total quantity sold?", "expected_type": "number", "metric": "Quantity"},
    {"q": "What is the average quantity per order?", "expected_type": "number", "metric": "Quantity"},
    {"q": "How many total transactions or orders are there?", "expected_type": "number", "metric": "count"},
    {"q": "What is the highest sales amount recorded?", "expected_type": "number", "metric": "Sales Amount"},
    {"q": "What is the lowest sales amount recorded?", "expected_type": "number", "metric": "Sales Amount"},
    {"q": "What is the average discount rate?", "expected_type": "number", "metric": "Discount Rate"},
    
    # Categorical Groupings & Breakdowns
    {"q": "Show sales amount by region", "expected_type": "grouped", "dim": "Region"},
    {"q": "What is the total sales amount by category?", "expected_type": "grouped", "dim": "Category"},
    {"q": "Break down quantity sold by region", "expected_type": "grouped", "dim": "Region"},
    {"q": "What is the average sales amount per category?", "expected_type": "grouped", "dim": "Category"},
    {"q": "What is the total quantity by category?", "expected_type": "grouped", "dim": "Category"},
    {"q": "List sales amount for each customer name", "expected_type": "grouped", "dim": "Customer Name"},
    
    # Top-K & Rankings
    {"q": "What are the top 3 regions by sales amount?", "expected_type": "grouped", "dim": "Region", "limit": 3},
    {"q": "What are the top 5 categories by sales amount?", "expected_type": "grouped", "dim": "Category", "limit": 5},
    {"q": "Show top 5 customer names by sales amount", "expected_type": "grouped", "dim": "Customer Name", "limit": 5},
    {"q": "What is the top region by sales amount?", "expected_type": "grouped", "dim": "Region", "limit": 1},
    {"q": "Which category has the highest sales amount?", "expected_type": "grouped", "dim": "Category", "limit": 1},
    {"q": "Which region has the lowest sales amount?", "expected_type": "grouped", "dim": "Region", "order": "asc"},
    
    # Time-Series & Trends
    {"q": "What is the sales amount over time?", "expected_type": "grouped", "dim": "Order Date"},
    {"q": "Show trend of sales amount by order date", "expected_type": "grouped", "dim": "Order Date"},
    {"q": "What is total quantity by order date?", "expected_type": "grouped", "dim": "Order Date"},
    
    # Multi-metric / Multi-condition queries
    {"q": "Show sales amount and quantity by region", "expected_type": "grouped", "dim": "Region"},
    {"q": "What is the count of orders by region?", "expected_type": "grouped", "dim": "Region"},
    {"q": "Show the average discount rate by category", "expected_type": "grouped", "dim": "Category"},
    {"q": "What is the maximum quantity sold by category?", "expected_type": "grouped", "dim": "Category"},
    {"q": "Show all customer records", "expected_type": "table"},
    {"q": "Show top 10 raw transactions", "expected_type": "table", "limit": 10},
    {"q": "What is the total sales amount for Electronics?", "expected_type": "number", "metric": "Sales Amount"}
]

@pytest.fixture(scope="module")
def prepared_dataset():
    from backend.app.services.ingestion import load_dataset_file
    df, _ = load_dataset_file("sample_data/messy_sales_data.xlsx", "xlsx")
    parquet_path = save_to_parquet(df, "eval_dataset_test", 1)
    sem_dict = SemanticService.build_semantic_layer(df)
    return parquet_path, sem_dict, df

def test_text_to_sql_30_question_eval_benchmark(prepared_dataset):
    parquet_path, sem_dict, df = prepared_dataset
    
    passed_count = 0
    total_count = len(EVAL_QUESTIONS)
    results_summary = []
    
    for idx, item in enumerate(EVAL_QUESTIONS, 1):
        question = item["q"]
        res = SafeTextToSQLAgent.query(
            question=question,
            parquet_path=parquet_path,
            semantic_layer=sem_dict
        )
        
        # Verify success criteria: can_answer is True, data returned, sql generated
        has_sql = bool(res.get("sql"))
        has_data = len(res.get("data", [])) > 0
        can_answer = res.get("can_answer", False)
        is_safe = "SELECT" in res.get("sql", "").upper()
        
        passed = has_sql and has_data and can_answer and is_safe
        if passed:
            passed_count += 1
            
        results_summary.append({
            "id": idx,
            "question": question,
            "passed": passed,
            "sql": res.get("sql"),
            "data_count": len(res.get("data", []))
        })
        
    pass_rate = (passed_count / total_count) * 100.0
    print(f"\nText-to-SQL Benchmark Evaluation Result: {passed_count}/{total_count} ({pass_rate:.1f}%)")
    assert pass_rate >= 90.0, f"Benchmark target is >= 90%, achieved {pass_rate:.1f}%"

def test_cricket_five_core_text_to_sql_questions():
    """
    Verify Bug 2 Fix on cricket CSV:
    1. 'total runs' -> 23,709 with SQL visible
    2. 'average runs per match' -> 45.95 with SQL visible
    3. 'which opponent has the highest average' -> Afghanistan (58.50) with SQL visible
    4. 'runs by year' -> 15 yearly breakdown points with SQL visible
    5. 'highest score' -> 254 with SQL visible
    """
    df = pd.read_csv("sample_data/cricket_dataset.csv")
    parquet_path = "data/parquet/pytest_cricket_eval.parquet"
    df.to_parquet(parquet_path)
    sem_dict = SemanticService.build_semantic_layer(df)

    # 1. Total runs
    res1 = SafeTextToSQLAgent.query("total runs", parquet_path, sem_dict)
    assert res1["can_answer"] is True
    assert "SELECT" in res1["sql"].upper()
    assert res1["data"][0]["result"] == 23709
    assert "23,709" in res1["answer"]

    # 2. Average runs per match
    res2 = SafeTextToSQLAgent.query("average runs per match", parquet_path, sem_dict)
    assert res2["can_answer"] is True
    assert "SELECT" in res2["sql"].upper()
    assert res2["data"][0]["avg_val"] == 45.95
    assert "45.95" in res2["answer"]

    # 3. Which opponent has the highest average
    res3 = SafeTextToSQLAgent.query("which opponent has the highest average", parquet_path, sem_dict)
    assert res3["can_answer"] is True
    assert "SELECT" in res3["sql"].upper()
    assert res3["data"][0]["opponent"] == "Afghanistan"
    assert res3["data"][0]["avg_val"] == 58.5
    assert "Afghanistan" in res3["answer"]

    # 4. Runs by year
    res4 = SafeTextToSQLAgent.query("runs by year", parquet_path, sem_dict)
    assert res4["can_answer"] is True
    assert "SELECT" in res4["sql"].upper()
    assert len(res4["data"]) >= 10
    assert any(r.get("year") == "2008" and r.get("total_runs") == 159 for r in res4["data"])
    assert res4["chart"] is not None

    # 5. Highest score
    res5 = SafeTextToSQLAgent.query("highest score", parquet_path, sem_dict)
    assert res5["can_answer"] is True
    assert "SELECT" in res5["sql"].upper()
    assert res5["data"][0]["highest_score"] == 254
    assert "254" in res5["answer"]

