import re
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from scipy import stats

PII_PATTERNS = {
    "email": re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"),
    "phone": re.compile(r"^(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$"),
    "ssn": re.compile(r"^\d{3}-\d{2}-\d{4}$"),
    "credit_card": re.compile(r"^(?:\d{4}[-\s]?){3}\d{4}$"),
    "aadhaar_id": re.compile(r"^\d{4}\s\d{4}\s\d{4}$"),
}

def detect_column_pii(series: pd.Series) -> Optional[str]:
    """Inspects non-null string samples to detect PII."""
    sample = series.dropna().astype(str).str.strip().head(50)
    if len(sample) == 0:
        return None
        
    for pii_type, pattern in PII_PATTERNS.items():
        matches = sum(1 for val in sample if pattern.match(val))
        if matches / len(sample) >= 0.4:
            return pii_type
    return None

def calculate_data_quality_score(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes Data Quality Score (0-100) across 4 pillars:
    - Completeness (40%)
    - Uniqueness (20%)
    - Validity (20%)
    - Consistency (20%)
    """
    total_cells = df.shape[0] * df.shape[1]
    if total_cells == 0:
        return {"overall": 100.0, "completeness": 100.0, "uniqueness": 100.0, "validity": 100.0, "consistency": 100.0}
        
    # 1. Completeness
    missing_cells = df.isna().sum().sum()
    completeness = max(0.0, 100.0 - (missing_cells / total_cells * 100.0))
    
    # 2. Uniqueness
    duplicate_rows = df.duplicated().sum()
    uniqueness = max(0.0, 100.0 - (duplicate_rows / max(1, len(df)) * 100.0))
    
    # 3. Validity (valid types, absence of infinite values)
    valid_cols = 0
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            inf_count = np.isinf(df[col].dropna()).sum()
            valid_cols += 1.0 - (inf_count / max(1, len(df)))
        else:
            valid_cols += 1.0
    validity = (valid_cols / max(1, len(df.columns))) * 100.0
    
    # 4. Consistency (consistent types and capitalization in text)
    consistency_scores = []
    for col in df.columns:
        if df[col].dtype == object:
            str_series = df[col].dropna().astype(str)
            if len(str_series) > 0:
                is_title = str_series.str.istitle().mean()
                is_lower = str_series.str.islower().mean()
                is_upper = str_series.str.isupper().mean()
                dominant_casing = max(is_title, is_lower, is_upper)
                consistency_scores.append(dominant_casing * 100.0)
            else:
                consistency_scores.append(100.0)
        else:
            consistency_scores.append(100.0)
    consistency = float(np.mean(consistency_scores)) if consistency_scores else 100.0
    
    overall = (0.40 * completeness) + (0.20 * uniqueness) + (0.20 * validity) + (0.20 * consistency)
    return {
        "overall": round(overall, 1),
        "completeness": round(completeness, 1),
        "uniqueness": round(uniqueness, 1),
        "validity": round(validity, 1),
        "consistency": round(consistency, 1),
    }

def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Profiles entire dataset: summary stats, column distributions, 
    missing values, cardinality, PII detection, quality score.
    """
    row_count, col_count = df.shape
    duplicate_rows = int(df.duplicated().sum())
    
    columns_profile = []
    
    for col in df.columns:
        series = df[col]
        missing_count = int(series.isna().sum())
        missing_pct = round((missing_count / max(1, row_count)) * 100.0, 2)
        unique_count = int(series.nunique(dropna=True))
        unique_pct = round((unique_count / max(1, row_count)) * 100.0, 2)
        
        col_type = "string"
        stats_dict: Dict[str, Any] = {}
        top_values: List[Dict[str, Any]] = []
        pii_detected = None
        
        if pd.api.types.is_numeric_dtype(series):
            col_type = "numeric"
            valid_vals = series.dropna()
            if len(valid_vals) > 0:
                stats_dict = {
                    "min": float(valid_vals.min()),
                    "max": float(valid_vals.max()),
                    "mean": round(float(valid_vals.mean()), 2),
                    "std": round(float(valid_vals.std()), 2) if len(valid_vals) > 1 else 0.0,
                    "median": round(float(valid_vals.median()), 2),
                    "p25": round(float(valid_vals.quantile(0.25)), 2),
                    "p75": round(float(valid_vals.quantile(0.75)), 2),
                    "skew": round(float(stats.skew(valid_vals)), 2) if len(valid_vals) > 2 else 0.0,
                    "kurtosis": round(float(stats.kurtosis(valid_vals)), 2) if len(valid_vals) > 3 else 0.0,
                }
        elif pd.api.types.is_datetime64_any_dtype(series):
            col_type = "datetime"
            valid_dates = series.dropna()
            if len(valid_dates) > 0:
                stats_dict = {
                    "min_date": str(valid_dates.min()),
                    "max_date": str(valid_dates.max()),
                }
        elif pd.api.types.is_bool_dtype(series):
            col_type = "boolean"
            counts = series.value_counts(dropna=True)
            top_values = [{"value": str(k), "count": int(v), "pct": round(v/max(1, row_count)*100, 1)} for k, v in counts.items()]
        else:
            col_type = "categorical" if unique_pct < 20.0 else "text"
            pii_detected = detect_column_pii(series)
            counts = series.value_counts(dropna=True).head(10)
            top_values = [{"value": str(k), "count": int(v), "pct": round(v/max(1, row_count)*100, 1)} for k, v in counts.items()]
            
        columns_profile.append({
            "name": str(col),
            "type": col_type,
            "missing_count": missing_count,
            "missing_pct": missing_pct,
            "unique_count": unique_count,
            "unique_pct": unique_pct,
            "is_constant": unique_count <= 1,
            "is_unique_id": unique_count == row_count and row_count > 1,
            "pii_type": pii_detected,
            "stats": stats_dict,
            "top_values": top_values,
        })
        
    quality_score = calculate_data_quality_score(df)
    
    return {
        "row_count": row_count,
        "col_count": col_count,
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": round(duplicate_rows / max(1, row_count) * 100, 2),
        "quality_score": quality_score,
        "columns": columns_profile,
    }
