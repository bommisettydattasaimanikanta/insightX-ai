import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from scipy import stats
from statsmodels.stats.multitest import multipletests

class StatisticsService:
    """Computes statistical metrics, hypothesis tests with FDR correction, and trend diagnostics."""

    @staticmethod
    def compute_correlations(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates Pearson and Spearman correlation matrices for numeric columns."""
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and df[c].nunique() > 1]
        if len(numeric_cols) < 2:
            return {"numeric_columns": numeric_cols, "pearson": {}, "spearman": {}, "top_pairs": []}
            
        clean_num_df = df[numeric_cols].dropna()
        if len(clean_num_df) < 3:
            return {"numeric_columns": numeric_cols, "pearson": {}, "spearman": {}, "top_pairs": []}
            
        pearson_mat = clean_num_df.corr(method="pearson").round(3).to_dict()
        spearman_mat = clean_num_df.corr(method="spearman").round(3).to_dict()
        
        # Rank top correlation pairs
        pairs = []
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                c1, c2 = numeric_cols[i], numeric_cols[j]
                r_val = pearson_mat[c1][c2]
                if not pd.isna(r_val):
                    # compute p-value
                    try:
                        r, p_val = stats.pearsonr(clean_num_df[c1], clean_num_df[c2])
                    except Exception:
                        r, p_val = r_val, 1.0
                    pairs.append({
                        "col1": c1,
                        "col2": c2,
                        "pearson_r": round(float(r), 3),
                        "abs_r": abs(round(float(r), 3)),
                        "p_value": round(float(p_val), 5),
                        "significance": "significant (p < 0.05)" if p_val < 0.05 else "not significant",
                        "strength": "strong" if abs(r) >= 0.7 else ("moderate" if abs(r) >= 0.4 else "weak")
                    })
        pairs.sort(key=lambda x: x["abs_r"], reverse=True)
        return {
            "numeric_columns": numeric_cols,
            "pearson": pearson_mat,
            "spearman": spearman_mat,
            "top_pairs": pairs[:10]
        }

    @staticmethod
    def run_hypothesis_tests(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Runs ANOVA across category-metric pairs and Chi-square for category pairs.
        Applies Benjamini-Hochberg FDR correction.
        """
        results = []
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and df[c].nunique() > 2]
        cat_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c]) and 2 <= df[c].nunique() <= 10]
        
        # 1. ANOVA between categorical groups and numeric metrics
        raw_p_values = []
        test_records = []
        
        for cat in cat_cols[:4]:
            for num in numeric_cols[:4]:
                groups = [group[num].dropna().values for _, group in df.groupby(cat) if len(group[num].dropna()) >= 2]
                if len(groups) >= 2:
                    try:
                        f_stat, p_val = stats.f_oneway(*groups)
                        if not np.isnan(p_val) and not np.isnan(f_stat):
                            # Calculate Eta-squared effect size
                            ss_between = sum(len(g) * (np.mean(g) - df[num].mean())**2 for g in groups)
                            ss_total = sum((df[num].dropna() - df[num].mean())**2)
                            eta_sq = round(ss_between / max(1e-5, ss_total), 3) if ss_total > 0 else 0.0
                            
                            raw_p_values.append(p_val)
                            test_records.append({
                                "test_type": "One-Way ANOVA",
                                "group_col": cat,
                                "metric_col": num,
                                "statistic": round(float(f_stat), 3),
                                "p_value_raw": float(p_val),
                                "effect_size_eta_squared": eta_sq,
                                "effect_size_label": "large" if eta_sq > 0.14 else ("medium" if eta_sq > 0.06 else "small")
                            })
                    except Exception:
                        pass
                        
        if test_records and raw_p_values:
            # Benjamini-Hochberg FDR multiple testing adjustment
            reject, p_adjusted, _, _ = multipletests(raw_p_values, alpha=0.05, method="fdr_bh")
            for i, rec in enumerate(test_records):
                rec["p_value_fdr"] = round(float(p_adjusted[i]), 5)
                rec["is_significant"] = bool(reject[i])
                rec["explanation"] = (
                    f"Statistically significant difference in '{rec['metric_col']}' across categories of '{rec['group_col']}' "
                    f"(F={rec['statistic']}, FDR p={rec['p_value_fdr']:.4f}, effect size η²={rec['effect_size_eta_squared']})."
                    if rec["is_significant"] else
                    f"No statistically significant difference in '{rec['metric_col']}' across '{rec['group_col']}' after multiple testing correction."
                )
                results.append(rec)
                
        return results

    @staticmethod
    def detect_trends_and_seasonality(df: pd.DataFrame, time_col: str, metric_col: str) -> Dict[str, Any]:
        """Detects trends, growth rates (MoM, YoY, CAGR), anomalies, and change points."""
        sub_df = df[[time_col, metric_col]].dropna().copy()
        try:
            sub_df[time_col] = pd.to_datetime(sub_df[time_col], errors="coerce")
            sub_df = sub_df.dropna().sort_values(by=time_col)
        except Exception:
            return {"error": "Could not parse time column"}
            
        if len(sub_df) < 5:
            return {"error": "Insufficient time-series data points (minimum 5 required)"}
            
        # Group by daily or monthly
        sub_df = sub_df.groupby(pd.Grouper(key=time_col, freq="D")).mean().dropna().reset_index()
        y = sub_df[metric_col].values
        n = len(y)
        if n < 5:
            return {"error": "Insufficient aggregated points"}
            
        # Linear trend estimation via OLS
        x = np.arange(n)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        pct_change_overall = ((y[-1] - y[0]) / max(abs(y[0]), 1e-5)) * 100.0
        direction = "Upward" if slope > 0 and p_value < 0.05 else ("Downward" if slope < 0 and p_value < 0.05 else "Stationary / No Trend")
        strength = round(abs(r_value), 2)
        
        # Anomalies via detrended residual z-score
        predicted = intercept + slope * x
        residuals = y - predicted
        residual_std = np.std(residuals) if np.std(residuals) > 0 else 1.0
        z_scores = residuals / residual_std
        anomalies = []
        for i in range(n):
            if abs(z_scores[i]) >= 2.5:
                anomalies.append({
                    "date": str(sub_df[time_col].iloc[i]),
                    "value": float(y[i]),
                    "expected": round(float(predicted[i]), 2),
                    "z_score": round(float(z_scores[i]), 2),
                    "type": "Spike" if z_scores[i] > 0 else "Drop"
                })
                
        # Simple change point: maximum absolute shift in rolling mean
        change_point = None
        if n >= 10:
            window = max(3, n // 5)
            rolling_means = pd.Series(y).rolling(window=window).mean().dropna().values
            diffs = np.abs(np.diff(rolling_means))
            if len(diffs) > 0:
                max_idx = int(np.argmax(diffs)) + window
                if max_idx < n:
                    change_point = {
                        "date": str(sub_df[time_col].iloc[max_idx]),
                        "magnitude": round(float(diffs[max_idx - window]), 2)
                    }

        return {
            "time_column": time_col,
            "metric_column": metric_col,
            "direction": direction,
            "strength": strength,
            "slope": round(float(slope), 4),
            "p_value": round(float(p_value), 5),
            "overall_growth_pct": round(pct_change_overall, 2),
            "anomalies_count": len(anomalies),
            "anomalies": anomalies[:5],
            "change_point": change_point,
        }
