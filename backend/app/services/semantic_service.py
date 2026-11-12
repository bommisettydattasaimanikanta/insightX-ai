import re
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

DOMAIN_KEYWORDS = {
    "sales": ["sales", "revenue", "price", "quantity", "discount", "order", "customer", "product", "deal", "lead"],
    "finance": ["balance", "asset", "liability", "expense", "budget", "profit", "ebitda", "cash", "credit", "tax"],
    "marketing": ["campaign", "clicks", "impressions", "ctr", "cpc", "conversion", "spend", "channel", "ad"],
    "hr": ["employee", "salary", "department", "attrition", "hire_date", "performance", "tenure", "bonus", "role"],
    "e-commerce": ["cart", "sku", "shipping", "delivery", "checkout", "rating", "review", "inventory", "vendor"],
    "healthcare": ["patient", "diagnosis", "treatment", "hospital", "doctor", "dosage", "blood_pressure", "bmi"],
    "education": ["student", "grade", "gpa", "course", "score", "attendance", "teacher", "exam", "school"],
    "operations": ["warehouse", "shipment", "defect", "yield", "lead_time", "facility", "capacity", "machine"]
}

METRIC_KEYWORDS = ["revenue", "sales", "amount", "price", "profit", "margin", "cost", "salary", "spend", "quantity", "count", "score", "total", "rate", "churn"]
ID_KEYWORDS = ["id", "uuid", "guid", "code", "key", "number", "no", "ssn"]
GEO_KEYWORDS = ["city", "state", "country", "region", "zip", "postal", "latitude", "longitude", "address"]

class SemanticService:
    """Classifies datasets, auto-generates semantic layers, and ensures consistency."""

    @staticmethod
    def detect_domain(columns: List[str]) -> Tuple[str, float]:
        col_text = " ".join([c.lower() for c in columns])
        domain_scores = {}
        for domain, kws in DOMAIN_KEYWORDS.items():
            matches = sum(1 for kw in kws if kw in col_text)
            domain_scores[domain] = matches
            
        best_domain = max(domain_scores, key=domain_scores.get)
        max_score = domain_scores[best_domain]
        if max_score == 0:
            return "general", 0.5
        confidence = min(0.98, round(0.5 + (max_score / len(columns)) * 0.5, 2))
        return best_domain, confidence

    @staticmethod
    def classify_columns(df: pd.DataFrame) -> List[Dict[str, Any]]:
        total_rows = len(df)
        classified = []
        
        for col in df.columns:
            series = df[col]
            name_lower = str(col).lower()
            unique_count = series.nunique(dropna=True)
            unique_ratio = unique_count / max(1, total_rows)
            
            # Determine role & semantic type
            role = "dimension"
            semantic_type = "text"
            
            # 1. ID detection
            if any(k in name_lower for k in ID_KEYWORDS) or (unique_ratio > 0.95 and total_rows > 10):
                role = "id"
                semantic_type = "identifier"
            # 2. Time detection
            elif pd.api.types.is_datetime64_any_dtype(series) or "date" in name_lower or "time" in name_lower or "year" in name_lower or "month" in name_lower:
                role = "time"
                semantic_type = "datetime"
            # 3. Metric detection
            elif pd.api.types.is_numeric_dtype(series):
                if unique_count <= 2:
                    role = "target" if ("churn" in name_lower or "target" in name_lower or "label" in name_lower) else "dimension"
                    semantic_type = "boolean"
                elif any(k in name_lower for k in METRIC_KEYWORDS) or unique_ratio > 0.05:
                    role = "metric"
                    if any(k in name_lower for k in ["revenue", "sales", "price", "cost", "salary", "amount", "profit"]):
                        semantic_type = "currency"
                    elif "%" in name_lower or "rate" in name_lower or "ratio" in name_lower or "margin" in name_lower:
                        semantic_type = "percentage"
                    else:
                        semantic_type = "numeric"
                else:
                    role = "dimension"
                    semantic_type = "categorical"
            # 4. Dimension / Geo / Categorical
            else:
                if any(k in name_lower for k in GEO_KEYWORDS):
                    semantic_type = "geo"
                elif "email" in name_lower:
                    semantic_type = "email"
                else:
                    semantic_type = "categorical"
                role = "dimension"
                
            classified.append({
                "name": str(col),
                "role": role,
                "semantic_type": semantic_type,
                "unique_count": unique_count,
                "dtype": str(series.dtype)
            })
        return classified

    @staticmethod
    def build_semantic_layer(df: pd.DataFrame) -> Dict[str, Any]:
        columns = SemanticService.classify_columns(df)
        domain, domain_conf = SemanticService.detect_domain([c["name"] for c in columns])
        
        metrics = []
        dimensions = []
        time_grains = []
        target_col = None
        ml_task = "regression"
        
        for c in columns:
            name = c["name"]
            role = c["role"]
            stype = c["semantic_type"]
            
            if role == "metric":
                agg = "AVG" if stype == "percentage" else "SUM"
                metrics.append({
                    "name": name,
                    "label": name.replace("_", " ").title(),
                    "expression": f"{agg}(`{name}`)",
                    "aggregation": agg,
                    "format": "currency" if stype == "currency" else ("percentage" if stype == "percentage" else "number"),
                    "description": f"Aggregated {agg.lower()} of {name}"
                })
                if target_col is None:
                    target_col = name
                    ml_task = "regression"
                    
            elif role == "dimension":
                dimensions.append({
                    "name": name,
                    "label": name.replace("_", " ").title(),
                    "column": name,
                    "type": stype
                })
                
            elif role == "time":
                time_grains.append({
                    "name": name,
                    "column": name,
                    "grains": ["day", "week", "month", "quarter", "year"]
                })
                
            elif role == "target":
                target_col = name
                ml_task = "classification"
                
        # If time grains exist and target is metric, allow forecasting task
        if time_grains and ml_task == "regression":
            suggested_task = "forecasting"
        else:
            suggested_task = ml_task

        return {
            "domain": domain,
            "confidence": domain_conf,
            "metrics": metrics,
            "dimensions": dimensions,
            "time_grains": time_grains,
            "suggested_target": target_col,
            "suggested_ml_task": suggested_task,
            "columns": columns
        }
