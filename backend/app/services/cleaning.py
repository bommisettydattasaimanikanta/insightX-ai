import re
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sklearn.ensemble import IsolationForest
from backend.app.services.profiling import calculate_data_quality_score

class CleaningService:
    """Generates and executes reversible cleaning steps with impact analysis."""

    @staticmethod
    def generate_cleaning_plan(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Inspects the dataframe and proposes a list of actionable cleaning cards
        with impact preview ('affects X rows / Y%').
        """
        plan = []
        total_rows = max(1, len(df))
        step_idx = 1
        
        # 1. Duplicates check
        dup_count = int(df.duplicated().sum())
        if dup_count > 0:
            pct = round(dup_count / total_rows * 100, 2)
            plan.append({
                "step_index": step_idx,
                "step_type": "remove_duplicates",
                "title": "Remove Exact Duplicate Rows",
                "column": None,
                "description": f"Identified {dup_count} duplicate rows ({pct}%).",
                "impact_rows": dup_count,
                "impact_pct": pct,
                "config": {"keep": "first"},
                "status": "pending",
                "category": "Duplicates"
            })
            step_idx += 1
            
        # 2. Missing values per column
        for col in df.columns:
            missing_count = int(df[col].isna().sum())
            if missing_count > 0:
                pct = round(missing_count / total_rows * 100, 2)
                # Recommend imputation based on dtype
                if pd.api.types.is_numeric_dtype(df[col]):
                    strategy = "median" if abs(df[col].skew()) > 1.0 else "mean"
                    desc = f"Column '{col}' has {missing_count} missing values ({pct}%). Propose imputing with {strategy}."
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    strategy = "forward_fill"
                    desc = f"Datetime column '{col}' has {missing_count} missing entries ({pct}%). Propose forward fill."
                else:
                    strategy = "mode"
                    desc = f"Categorical column '{col}' has {missing_count} missing entries ({pct}%). Propose imputing with most frequent value."
                    
                plan.append({
                    "step_index": step_idx,
                    "step_type": "impute_missing",
                    "title": f"Impute Missing Values in '{col}'",
                    "column": col,
                    "description": desc,
                    "impact_rows": missing_count,
                    "impact_pct": pct,
                    "config": {"strategy": strategy},
                    "status": "pending",
                    "category": "Missing Values"
                })
                step_idx += 1

        # 3. Outlier detection in numeric columns (IQR method)
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                vals = df[col].dropna()
                if len(vals) > 10:
                    q25 = vals.quantile(0.25)
                    q75 = vals.quantile(0.75)
                    iqr = q75 - q25
                    if iqr > 0:
                        lower_bound = q25 - 1.5 * iqr
                        upper_bound = q75 + 1.5 * iqr
                        outliers = ((vals < lower_bound) | (vals > upper_bound)).sum()
                        if outliers > 0 and (outliers / total_rows) <= 0.15:  # up to 15%
                            pct = round(outliers / total_rows * 100, 2)
                            plan.append({
                                "step_index": step_idx,
                                "step_type": "clip_outliers",
                                "title": f"Cap Outliers in '{col}' (IQR 1.5x)",
                                "column": col,
                                "description": f"Found {outliers} outlier values ({pct}%) outside [{round(lower_bound, 2)}, {round(upper_bound, 2)}]. Propose clipping to boundaries.",
                                "impact_rows": int(outliers),
                                "impact_pct": pct,
                                "config": {"method": "iqr", "lower": float(lower_bound), "upper": float(upper_bound)},
                                "status": "pending",
                                "category": "Outliers"
                            })
                            step_idx += 1

        # 4. Text standardization (trim whitespace, casing consistency)
        for col in df.columns:
            if df[col].dtype == object:
                sample = df[col].dropna().astype(str)
                has_trailing = sample.str.contains(r"^\s+|\s+$", regex=True).any()
                if has_trailing:
                    trailing_count = int(sample.str.contains(r"^\s+|\s+$", regex=True).sum())
                    pct = round(trailing_count / total_rows * 100, 2)
                    plan.append({
                        "step_index": step_idx,
                        "step_type": "trim_whitespace",
                        "title": f"Trim Whitespace in '{col}'",
                        "column": col,
                        "description": f"Detected leading or trailing whitespaces affecting {trailing_count} values ({pct}%).",
                        "impact_rows": trailing_count,
                        "impact_pct": pct,
                        "config": {"method": "strip"},
                        "status": "pending",
                        "category": "Text Cleaning"
                    })
                    step_idx += 1

        return plan

    @staticmethod
    def apply_cleaning_step(df: pd.DataFrame, step: Dict[str, Any]) -> Tuple[pd.DataFrame, int]:
        """Applies a single cleaning transformation and returns (modified_df, affected_rows)."""
        df_out = df.copy()
        step_type = step.get("step_type")
        col = step.get("column")
        config = step.get("config", {})
        affected_rows = 0

        if step_type == "remove_duplicates":
            before_len = len(df_out)
            df_out = df_out.drop_duplicates(keep=config.get("keep", "first")).reset_index(drop=True)
            affected_rows = before_len - len(df_out)

        elif step_type == "impute_missing" and col in df_out.columns:
            strategy = config.get("strategy", "mean")
            missing_mask = df_out[col].isna()
            affected_rows = int(missing_mask.sum())
            if affected_rows > 0:
                if strategy == "mean" and pd.api.types.is_numeric_dtype(df_out[col]):
                    df_out[col] = df_out[col].fillna(df_out[col].mean())
                elif strategy == "median" and pd.api.types.is_numeric_dtype(df_out[col]):
                    df_out[col] = df_out[col].fillna(df_out[col].median())
                elif strategy == "mode":
                    mode_val = df_out[col].mode()
                    val = mode_val.iloc[0] if not mode_val.empty else "Unknown"
                    df_out[col] = df_out[col].fillna(val)
                elif strategy == "forward_fill":
                    df_out[col] = df_out[col].ffill().bfill()
                elif strategy == "constant":
                    df_out[col] = df_out[col].fillna(config.get("fill_value", 0))

        elif step_type == "clip_outliers" and col in df_out.columns:
            lower = config.get("lower")
            upper = config.get("upper")
            if lower is not None and upper is not None:
                mask = (df_out[col] < lower) | (df_out[col] > upper)
                affected_rows = int(mask.sum())
                df_out[col] = df_out[col].clip(lower=lower, upper=upper)

        elif step_type == "trim_whitespace" and col in df_out.columns:
            affected_rows = int(df_out[col].dropna().astype(str).str.contains(r"^\s+|\s+$", regex=True).sum())
            df_out[col] = df_out[col].apply(lambda x: str(x).strip() if pd.notna(x) else x)

        elif step_type == "change_casing" and col in df_out.columns:
            casing = config.get("casing", "title")
            if casing == "title":
                df_out[col] = df_out[col].apply(lambda x: str(x).title() if pd.notna(x) else x)
            elif casing == "lower":
                df_out[col] = df_out[col].apply(lambda x: str(x).lower() if pd.notna(x) else x)
            elif casing == "upper":
                df_out[col] = df_out[col].apply(lambda x: str(x).upper() if pd.notna(x) else x)
            affected_rows = len(df_out)

        return df_out, affected_rows

    @staticmethod
    def execute_cleaning_plan(df: pd.DataFrame, approved_steps: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Executes a list of approved cleaning steps, recording before/after Quality Score."""
        score_before = calculate_data_quality_score(df)
        df_current = df.copy()
        
        applied_results = []
        for step in approved_steps:
            df_current, rows_affected = CleaningService.apply_cleaning_step(df_current, step)
            step_record = dict(step)
            step_record["rows_affected"] = rows_affected
            step_record["status"] = "applied"
            applied_results.append(step_record)
            
        score_after = calculate_data_quality_score(df_current)
        
        return df_current, {
            "score_before": score_before,
            "score_after": score_after,
            "improvement": round(score_after["overall"] - score_before["overall"], 1),
            "applied_steps": applied_results,
            "final_rows": len(df_current),
            "final_cols": len(df_current.columns)
        }
