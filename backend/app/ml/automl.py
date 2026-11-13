import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    r2_score, mean_squared_error, mean_absolute_error,
    accuracy_score, f1_score, confusion_matrix
)
import xgboost as xgb
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

from backend.app.config import settings

class AutoMLTrainer:
    """Automated Machine Learning trainer with baseline first, feature attribution, and leakage protection."""

    @staticmethod
    def prepare_data(df: pd.DataFrame, target_col: str) -> Tuple[pd.DataFrame, pd.Series, str, List[str], List[Dict[str, Any]], bool]:
        clean_df = df.dropna(subset=[target_col]).copy()
        # Fast sampling for large datasets to guarantee responsive sub-5s training
        if len(clean_df) > 10000:
            clean_df = clean_df.sample(10000, random_state=42)
        y = clean_df[target_col]
        
        # Determine task type
        if pd.api.types.is_numeric_dtype(y) and y.nunique() > 10:
            task_type = "regression"
        else:
            task_type = "classification"
            if y.dtype == object or str(y.dtype) == "category":
                y = pd.Series(pd.factorize(y)[0], index=y.index)

        # 1. Automatic Column Exclusion (Identifiers, Monotonic Totals, Target Leakage)
        exclude_cols = {target_col}
        date_col = None

        for col in clean_df.columns:
            if col == target_col:
                continue
            c_lower = col.lower()
            
            # Row index / ID columns
            if c_lower in ["index", "id", "idx", "row_id", "unnamed: 0"] or c_lower.endswith("_id"):
                exclude_cols.add(col)
                continue
                
            # Date/time detection
            if any(k in c_lower for k in ["date", "time", "timestamp", "year", "month"]):
                date_col = col

            # Monotonic cumulative running totals (e.g. 'total')
            if pd.api.types.is_numeric_dtype(clean_df[col]):
                series = clean_df[col].dropna()
                if len(series) > 10:
                    is_monotonic = series.is_monotonic_increasing
                    if is_monotonic or c_lower in ["total", "cumulative_total", "running_total", "cum_total"]:
                        exclude_cols.add(col)
                        continue
                        
            # Check target leakage: correlation > 0.95 or contains target name
            if pd.api.types.is_numeric_dtype(clean_df[col]) and pd.api.types.is_numeric_dtype(y):
                try:
                    corr = abs(np.corrcoef(clean_df[col].fillna(0), y)[0, 1])
                    if corr > 0.95 or target_col.lower() in c_lower:
                        exclude_cols.add(col)
                        continue
                except Exception:
                    pass

        # 2. Time-ordered feature engineering
        has_time_order = False
        if date_col and date_col in clean_df.columns:
            has_time_order = True
            # Extract 4-digit year
            years = clean_df[date_col].astype(str).str.extract(r"([0-9]{4})")[0].astype(float)
            clean_df["year"] = years.fillna(2020.0)
            
            # Extract month
            month_map = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
            def parse_month(val):
                val_s = str(val).lower()
                for m_str, m_num in month_map.items():
                    if m_str in val_s:
                        return float(m_num)
                return 6.0
            clean_df["month"] = clean_df[date_col].apply(parse_month)

        if has_time_order or "Match_No" in clean_df.columns or "seq" in clean_df.columns:
            has_time_order = True
            clean_df["seq_num"] = np.arange(1, len(clean_df) + 1, dtype=float)
            
            # Shifted rolling target features (CURRENT ROW IS NEVER INCLUDED!)
            if task_type == "regression":
                clean_df["rolling_mean_5"] = clean_df[target_col].shift(1).rolling(5, min_periods=1).mean().bfill()
                clean_df["rolling_mean_10"] = clean_df[target_col].shift(1).rolling(10, min_periods=1).mean().bfill()

        # Build feature matrix and interactive metadata
        feature_cols = []
        feature_metadata = []
        X = pd.DataFrame(index=clean_df.index)

        candidate_cols = [c for c in clean_df.columns if c not in exclude_cols]
        for c in candidate_cols:
            if c == date_col:
                continue
                
            if pd.api.types.is_numeric_dtype(clean_df[c]):
                val_col = clean_df[c].fillna(clean_df[c].median())
                X[c] = val_col
                feature_cols.append(c)
                min_v = float(val_col.min())
                max_v = float(val_col.max())
                med_v = float(val_col.median())
                step_v = 1.0 if (val_col % 1 == 0).all() else 0.1
                if min_v == max_v:
                    max_v = min_v + 10.0
                feature_metadata.append({
                    "name": c,
                    "label": c.replace("_", " ").title(),
                    "type": "numeric",
                    "min": round(min_v, 2),
                    "max": round(max_v, 2),
                    "step": step_v,
                    "default": round(med_v, 2),
                    "options": []
                })
            elif clean_df[c].nunique() <= 15:
                # One-hot encode low-cardinality categories
                dummies = pd.get_dummies(clean_df[c], prefix=c, drop_first=True)
                for d_col in dummies.columns:
                    X[d_col] = dummies[d_col].astype(float)
                    feature_cols.append(d_col)
                    feature_metadata.append({
                        "name": d_col,
                        "label": d_col.replace("_", " ").title(),
                        "type": "numeric",
                        "min": 0.0,
                        "max": 1.0,
                        "step": 1.0,
                        "default": float(X[d_col].mode()[0]),
                        "options": []
                    })

        X = X[feature_cols].copy().fillna(0)
        return X, y, task_type, feature_cols, feature_metadata, has_time_order

    @staticmethod
    def train_and_evaluate(df: pd.DataFrame, target_col: str, model_save_name: str) -> Dict[str, Any]:
        X, y, task_type, feature_names, feature_metadata, has_time_order = AutoMLTrainer.prepare_data(df, target_col)
        if len(X) < 15 or len(feature_names) == 0:
            raise ValueError("Insufficient data or valid features to train machine learning model.")
            
        warnings = []
        if len(X) < 50:
            warnings.append("Tiny dataset warning: Sample size under 50 rows may lead to overfitting.")

        # Chronological time-based split for time-ordered data, else stratified/random
        if has_time_order:
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
            y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        else:
            is_stratified = task_type == "classification" and y.value_counts().min() >= 2
            stratify_val = y if is_stratified else None
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=stratify_val)
        
        leaderboard = []
        best_model = None
        best_score = -float("inf")
        best_model_name = ""

        # Track the best NON-baseline model to guarantee feature attribution
        best_non_baseline_model = None
        best_non_baseline_name = None
        best_non_baseline_score = -float("inf")
        
        if task_type == "regression":
            # 1. Baseline
            base_model = DummyRegressor(strategy="mean")
            base_model.fit(X_train, y_train)
            base_preds = base_model.predict(X_test)
            base_r2 = r2_score(y_test, base_preds)
            leaderboard.append({
                "algorithm": "Baseline (Mean)",
                "r2": round(float(base_r2), 4),
                "rmse": round(float(np.sqrt(mean_squared_error(y_test, base_preds))), 4),
                "mae": round(float(mean_absolute_error(y_test, base_preds)), 4),
                "tag": "Baseline"
            })
            best_model = base_model
            best_score = base_r2
            best_model_name = "Baseline"
            
            # 2. Linear Regression
            lin_model = LinearRegression()
            lin_model.fit(X_train, y_train)
            lin_preds = lin_model.predict(X_test)
            lin_r2 = r2_score(y_test, lin_preds)
            leaderboard.append({
                "algorithm": "Linear Regression",
                "r2": round(float(lin_r2), 4),
                "rmse": round(float(np.sqrt(mean_squared_error(y_test, lin_preds))), 4),
                "mae": round(float(mean_absolute_error(y_test, lin_preds)), 4),
                "tag": "ML prediction"
            })
            best_non_baseline_model = lin_model
            best_non_baseline_name = "Linear Regression"
            best_non_baseline_score = lin_r2

            if lin_r2 > best_score:
                best_score = lin_r2
                best_model = lin_model
                best_model_name = "Linear Regression"
                
            # 3. Random Forest
            rf_model = RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42)
            rf_model.fit(X_train, y_train)
            rf_preds = rf_model.predict(X_test)
            rf_r2 = r2_score(y_test, rf_preds)
            leaderboard.append({
                "algorithm": "Random Forest",
                "r2": round(float(rf_r2), 4),
                "rmse": round(float(np.sqrt(mean_squared_error(y_test, rf_preds))), 4),
                "mae": round(float(mean_absolute_error(y_test, rf_preds)), 4),
                "tag": "ML prediction"
            })
            if rf_r2 > best_non_baseline_score:
                best_non_baseline_score = rf_r2
                best_non_baseline_model = rf_model
                best_non_baseline_name = "Random Forest"

            if rf_r2 > best_score:
                best_score = rf_r2
                best_model = rf_model
                best_model_name = "Random Forest"

            # 4. XGBoost
            xgb_model = xgb.XGBRegressor(n_estimators=50, max_depth=4, learning_rate=0.05, random_state=42)
            xgb_model.fit(X_train, y_train)
            xgb_preds = xgb_model.predict(X_test)
            xgb_r2 = r2_score(y_test, xgb_preds)
            leaderboard.append({
                "algorithm": "XGBoost",
                "r2": round(float(xgb_r2), 4),
                "rmse": round(float(np.sqrt(mean_squared_error(y_test, xgb_preds))), 4),
                "mae": round(float(mean_absolute_error(y_test, xgb_preds)), 4),
                "tag": "ML prediction"
            })
            if xgb_r2 > best_non_baseline_score:
                best_non_baseline_score = xgb_r2
                best_non_baseline_model = xgb_model
                best_non_baseline_name = "XGBoost"

            if xgb_r2 > best_score:
                best_score = xgb_r2
                best_model = xgb_model
                best_model_name = "XGBoost"

            y_final_preds = best_model.predict(X_test)
            residuals = (y_test - y_final_preds).tolist()
            diagnostics = {
                "residuals": residuals[:50],
                "actual_vs_predicted": [{"actual": float(a), "predicted": float(p)} for a, p in zip(y_test[:40], y_final_preds[:40])]
            }
            
        else: # Classification
            base_model = DummyClassifier(strategy="most_frequent")
            base_model.fit(X_train, y_train)
            base_preds = base_model.predict(X_test)
            base_acc = accuracy_score(y_test, base_preds)
            leaderboard.append({
                "algorithm": "Baseline (Most Frequent)",
                "accuracy": round(float(base_acc), 4),
                "f1": round(float(f1_score(y_test, base_preds, average="weighted", zero_division=0)), 4),
                "tag": "Baseline"
            })
            best_model = base_model
            best_score = base_acc
            best_model_name = "Baseline"
            
            # Logistic Regression
            lr_model = LogisticRegression(max_iter=500)
            lr_model.fit(X_train, y_train)
            lr_preds = lr_model.predict(X_test)
            lr_acc = accuracy_score(y_test, lr_preds)
            leaderboard.append({
                "algorithm": "Logistic Regression",
                "accuracy": round(float(lr_acc), 4),
                "f1": round(float(f1_score(y_test, lr_preds, average="weighted", zero_division=0)), 4),
                "tag": "ML prediction"
            })
            best_non_baseline_model = lr_model
            best_non_baseline_name = "Logistic Regression"
            best_non_baseline_score = lr_acc

            if lr_acc > best_score:
                best_score = lr_acc
                best_model = lr_model
                best_model_name = "Logistic Regression"
                
            # Random Forest Classifier
            rf_clf = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=42)
            rf_clf.fit(X_train, y_train)
            rf_preds = rf_clf.predict(X_test)
            rf_acc = accuracy_score(y_test, rf_preds)
            leaderboard.append({
                "algorithm": "Random Forest",
                "accuracy": round(float(rf_acc), 4),
                "f1": round(float(f1_score(y_test, rf_preds, average="weighted", zero_division=0)), 4),
                "tag": "ML prediction"
            })
            if rf_acc > best_non_baseline_score:
                best_non_baseline_score = rf_acc
                best_non_baseline_model = rf_clf
                best_non_baseline_name = "Random Forest"

            if rf_acc > best_score:
                best_score = rf_acc
                best_model = rf_clf
                best_model_name = "Random Forest"

            # XGBoost Classifier
            xgb_clf = xgb.XGBClassifier(n_estimators=50, max_depth=4, learning_rate=0.05, random_state=42)
            xgb_clf.fit(X_train, y_train)
            xgb_preds = xgb_clf.predict(X_test)
            xgb_acc = accuracy_score(y_test, xgb_preds)
            leaderboard.append({
                "algorithm": "XGBoost",
                "accuracy": round(float(xgb_acc), 4),
                "f1": round(float(f1_score(y_test, xgb_preds, average="weighted", zero_division=0)), 4),
                "tag": "ML prediction"
            })
            if xgb_acc > best_non_baseline_score:
                best_non_baseline_score = xgb_acc
                best_non_baseline_model = xgb_clf
                best_non_baseline_name = "XGBoost"

            if xgb_acc > best_score:
                best_score = xgb_acc
                best_model = xgb_clf
                best_model_name = "XGBoost"

            y_final_preds = best_model.predict(X_test)
            cm = confusion_matrix(y_test, y_final_preds).tolist()
            diagnostics = {
                "confusion_matrix": cm,
                "classes": [str(c) for c in np.unique(y)]
            }

        # 3. FEATURE IMPORTANCE: Always compute from the best NON-baseline model
        feature_importance = []
        eval_model = best_non_baseline_model or best_model
        
        if hasattr(eval_model, "feature_importances_"):
            importances = eval_model.feature_importances_
            feature_importance = [
                {"feature": feat, "importance": round(float(imp), 4)}
                for feat, imp in zip(feature_names, importances)
            ]
        elif hasattr(eval_model, "coef_"):
            raw_coef = eval_model.coef_[0] if eval_model.coef_.ndim > 1 else eval_model.coef_
            coefs = np.abs(raw_coef)
            sum_c = float(np.sum(coefs)) or 1.0
            feature_importance = [
                {"feature": feat, "importance": round(float(c / sum_c), 4)}
                for feat, c in zip(feature_names, coefs)
            ]
        else:
            try:
                perm = permutation_importance(eval_model, X_test, y_test, n_repeats=5, random_state=42)
                sum_p = float(np.sum(np.maximum(perm.importances_mean, 0))) or 1.0
                feature_importance = [
                    {"feature": feat, "importance": round(float(max(0, imp) / sum_p), 4)}
                    for feat, imp in zip(feature_names, perm.importances_mean)
                ]
            except Exception:
                feature_importance = [
                    {"feature": feat, "importance": round(1.0 / len(feature_names), 4)}
                    for feat in feature_names
                ]

        feature_importance.sort(key=lambda x: x["importance"], reverse=True)

        # Baseline dominance check
        no_model_beats_baseline = (task_type == "regression" and (best_score <= 0.0 or best_model_name == "Baseline"))
        if no_model_beats_baseline:
            baseline_warning = (
                f"No model predicts {target_col} better than the average. These features have little predictive power. "
                "Importance below is from the best attempt and should be treated as weak evidence."
            )
            warnings.append(baseline_warning)

        # Save model artifact: save the best model (or best non-baseline if needed for what-if)
        save_path = settings.MODELS_DIR / f"{model_save_name}.joblib"
        joblib.dump({
            "model": best_model,
            "non_baseline_model": best_non_baseline_model,
            "features": feature_names,
            "task_type": task_type,
            "feature_metadata": feature_metadata
        }, str(save_path))

        # Model Card
        model_card = {
            "model_name": best_model_name,
            "best_non_baseline_name": best_non_baseline_name,
            "target": target_col,
            "task_type": task_type,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "features_used": feature_names,
            "performance_summary": f"Best model {best_model_name} achieved score of {best_score:.4f}.",
            "warnings_and_caveats": warnings,
            "tag": "ML prediction",
            "confidence": "low" if no_model_beats_baseline else "high"
        }

        return {
            "task_type": task_type,
            "best_algorithm": best_model_name,
            "non_baseline_algorithm": best_non_baseline_name,
            "no_model_beats_baseline": no_model_beats_baseline,
            "confidence": "low" if no_model_beats_baseline else "high",
            "model_path": str(save_path),
            "leaderboard": leaderboard,
            "feature_importance": feature_importance[:10],
            "feature_metadata": feature_metadata,
            "diagnostics": diagnostics,
            "model_card": model_card,
            "warnings": warnings,
        }
