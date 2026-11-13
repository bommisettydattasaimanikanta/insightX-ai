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

    @staticmethod
    def auto_clean_safe_defaults(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Applies only low-risk safe fixes automatically without user approval:
        - Trim whitespace in text columns
        - Fix and cast data types (numeric, dates)
        - Clean currencies ($ € £ ₹), percentages (%), and Indian numbering (lakhs, crores)
        - Parse mixed date formats into datetime
        - Remove blank rows and blank columns
        - Detect and remove subtotal/grand total summary rows
        - Standardize text casing
        - Remove exact duplicate rows
        
        High-risk operations (outlier dropping, high-volume imputation, category merging)
        are flagged as 'suggestions' for review rather than auto-applied.
        """
        from backend.app.services.ingestion import clean_indian_or_currency_number, detect_subtotal_rows
        
        score_before = calculate_data_quality_score(df)
        df_clean = df.copy()
        applied_steps = []
        suggestions = []
        
        # 1. Remove completely blank rows & columns
        blank_rows = int(df_clean.isna().all(axis=1).sum())
        if blank_rows > 0:
            df_clean = df_clean.dropna(how="all").reset_index(drop=True)
            applied_steps.append({
                "type": "remove_blank_rows",
                "title": "Remove Empty Rows",
                "description": f"Removed {blank_rows} completely empty rows.",
                "rows_affected": blank_rows
            })
            
        blank_cols = [c for c in df_clean.columns if df_clean[c].isna().all()]
        if blank_cols:
            df_clean = df_clean.drop(columns=blank_cols)
            applied_steps.append({
                "type": "remove_blank_cols",
                "title": "Remove Empty Columns",
                "description": f"Removed {len(blank_cols)} completely empty columns ({', '.join(blank_cols)}).",
                "rows_affected": len(blank_cols)
            })

        # 2. Detect & remove subtotal / summary rows
        try:
            subtotals = detect_subtotal_rows(df_clean)
            if subtotals:
                df_clean = df_clean.drop(index=subtotals).reset_index(drop=True)
                applied_steps.append({
                    "type": "remove_subtotals",
                    "title": "Remove Summary / Subtotal Rows",
                    "description": f"Detected and removed {len(subtotals)} subtotal/total rows that would skew aggregations.",
                    "rows_affected": len(subtotals)
                })
        except Exception:
            pass

        # 3. Trim whitespace & standardize text casing
        for col in df_clean.columns:
            if df_clean[col].dtype == object:
                sample_series = df_clean[col].dropna().astype(str)
                # Whitespace trimming
                has_spaces = sample_series.str.contains(r"^\s+|\s+$", regex=True).sum()
                if has_spaces > 0:
                    df_clean[col] = df_clean[col].apply(lambda x: str(x).strip() if pd.notna(x) else x)
                    applied_steps.append({
                        "type": "trim_whitespace",
                        "title": f"Trim Whitespace in '{col}'",
                        "description": f"Trimmed leading/trailing whitespace across {has_spaces} entries in '{col}'.",
                        "rows_affected": int(has_spaces)
                    })
                
                # Standardize casing for low-cardinality text (1 < unique <= 30)
                n_uniq = df_clean[col].nunique()
                if 1 < n_uniq <= 30 and not any(k in str(col).lower() for k in ["id", "url", "email", "code", "guid"]):
                    df_clean[col] = df_clean[col].apply(lambda x: str(x).strip().title() if pd.notna(x) else x)
                    applied_steps.append({
                        "type": "standardize_casing",
                        "title": f"Standardize Casing in '{col}'",
                        "description": f"Standardized inconsistent casing to Title Case in category column '{col}'.",
                        "rows_affected": len(df_clean)
                    })

        # 4. Clean currencies, percentages, and Indian number formats into numeric
        for col in df_clean.columns:
            if df_clean[col].dtype == object:
                sample_non_null = df_clean[col].dropna()
                if len(sample_non_null) > 0:
                    cleaned_sample = sample_non_null.apply(clean_indian_or_currency_number)
                    numeric_count = pd.to_numeric(cleaned_sample, errors="coerce").notna().sum()
                    if numeric_count / len(sample_non_null) >= 0.7:  # 70%+ numeric after currency/number clean
                        df_clean[col] = df_clean[col].apply(clean_indian_or_currency_number)
                        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
                        applied_steps.append({
                            "type": "parse_currency_numbers",
                            "title": f"Format Numbers & Currency in '{col}'",
                            "description": f"Converted currency symbols, %, and Indian number formats in '{col}' to clean numeric values.",
                            "rows_affected": int(numeric_count)
                        })

        # 5. Parse mixed dates
        for col in df_clean.columns:
            name_lower = str(col).lower()
            if df_clean[col].dtype == object and ("date" in name_lower or "time" in name_lower or "day" in name_lower or "period" in name_lower):
                try:
                    parsed_dates = pd.to_datetime(df_clean[col], errors="coerce", format="mixed")
                    if parsed_dates.notna().mean() >= 0.5:
                        valid_count = int(parsed_dates.notna().sum())
                        df_clean[col] = parsed_dates
                        applied_steps.append({
                            "type": "parse_dates",
                            "title": f"Parse Dates in '{col}'",
                            "description": f"Standardized mixed date strings in '{col}' to ISO timestamps ({valid_count} dates converted).",
                            "rows_affected": valid_count
                        })
                except Exception:
                    pass

        # 6. Remove exact duplicate rows
        dup_count = int(df_clean.duplicated().sum())
        if dup_count > 0:
            df_clean = df_clean.drop_duplicates().reset_index(drop=True)
            applied_steps.append({
                "type": "remove_duplicates",
                "title": "Deduplicate Rows",
                "description": f"Removed {dup_count} exact duplicate rows.",
                "rows_affected": dup_count
            })

        # 7. Collect high-risk actions as suggestions for review (NOT auto-applied)
        # Check outliers
        for col in df_clean.columns:
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                vals = df_clean[col].dropna()
                if len(vals) > 10:
                    q25 = vals.quantile(0.25)
                    q75 = vals.quantile(0.75)
                    iqr = q75 - q25
                    if iqr > 0:
                        lower_bound = q25 - 1.5 * iqr
                        upper_bound = q75 + 1.5 * iqr
                        outlier_count = int(((vals < lower_bound) | (vals > upper_bound)).sum())
                        if outlier_count > 0:
                            suggestions.append({
                                "type": "outlier_review",
                                "column": col,
                                "count": outlier_count,
                                "title": f"Review {outlier_count} Outliers in '{col}'",
                                "description": f"Found {outlier_count} values outside 1.5x IQR [{round(lower_bound, 2)}, {round(upper_bound, 2)}]. Kept in data to preserve natural variance."
                            })

        # Check high missingness (> 10%)
        for col in df_clean.columns:
            miss_count = int(df_clean[col].isna().sum())
            if miss_count > 0:
                pct = round((miss_count / max(1, len(df_clean))) * 100, 1)
                if pct >= 10.0:
                    suggestions.append({
                        "type": "missing_review",
                        "column": col,
                        "missing_pct": pct,
                        "title": f"Missing Values in '{col}' ({pct}%)",
                        "description": f"Column has {miss_count} missing values ({pct}%). Kept as NULL rather than guessing values."
                    })

        score_after = calculate_data_quality_score(df_clean)

        return df_clean, {
            "score_before": score_before,
            "score_after": score_after,
            "improvement": round(score_after["overall"] - score_before["overall"], 1),
            "applied_steps": applied_steps,
            "suggestions": suggestions,
            "issues_fixed_count": len(applied_steps),
            "initial_rows": len(df),
            "final_rows": len(df_clean),
            "initial_cols": len(df.columns),
            "final_cols": len(df_clean.columns)
        }
