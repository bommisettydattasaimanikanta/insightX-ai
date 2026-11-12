import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.metrics import (
    r2_score, mean_squared_error, mean_absolute_error,
    accuracy_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
)
import xgboost as xgb
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

from backend.app.config import settings

class AutoMLTrainer:
    """Automated Machine Learning trainer with baseline first, Optuna tuning, and model cards."""

    @staticmethod
    def prepare_data(df: pd.DataFrame, target_col: str) -> Tuple[pd.DataFrame, pd.Series, str, List[str]]:
        clean_df = df.dropna(subset=[target_col]).copy()
        y = clean_df[target_col]
        X = clean_df.drop(columns=[target_col])
        
        # Determine task type
        if pd.api.types.is_numeric_dtype(y) and y.nunique() > 10:
            task_type = "regression"
        else:
            task_type = "classification"
            # Encode target if object
            if y.dtype == object or str(y.dtype) == "category":
                y = pd.Series(pd.factorize(y)[0], index=y.index)
                
        # Drop high-cardinality ID columns or text columns with >90% unique values
        feature_cols = []
        for c in X.columns:
            if pd.api.types.is_numeric_dtype(X[c]):
                feature_cols.append(c)
                X[c] = X[c].fillna(X[c].median())
            elif X[c].nunique() < 20:
                # One-hot encode low cardinality categories
                dummies = pd.get_dummies(X[c], prefix=c, drop_first=True)
                X = pd.concat([X, dummies], axis=1)
                feature_cols.extend(dummies.columns.tolist())
                
        X = X[feature_cols].copy()
        # Impute any remaining NaNs
        X = X.fillna(0)
        return X, y, task_type, feature_cols

    @staticmethod
    def train_and_evaluate(df: pd.DataFrame, target_col: str, model_save_name: str) -> Dict[str, Any]:
        X, y, task_type, feature_names = AutoMLTrainer.prepare_data(df, target_col)
        if len(X) < 15 or len(feature_names) == 0:
            raise ValueError("Insufficient data or valid features to train machine learning model.")
            
        warnings = []
        if len(X) < 50:
            warnings.append("Tiny dataset warning: Sample size under 50 rows may lead to overfitting.")
            
        # Check target leakage: any feature with >0.95 correlation with target
        for c in feature_names:
            if abs(np.corrcoef(X[c], y)[0, 1]) > 0.95:
                warnings.append(f"Potential data leakage: Feature '{c}' has >95% correlation with target '{target_col}'.")

        # Stratified or standard train/test split
        is_stratified = task_type == "classification" and y.value_counts().min() >= 2
        stratify_val = y if is_stratified else None
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=stratify_val)
        
        leaderboard = []
        best_model = None
        best_score = -float("inf")
        best_model_name = ""
        
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
            if rf_r2 > best_score:
                best_score = rf_r2
                best_model = rf_model
                best_model_name = "Random Forest"

            # 4. XGBoost
            xgb_model = xgb.XGBRegressor(n_estimators=50, max_depth=4, learning_rate=0.1, random_state=42)
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
            if xgb_r2 > best_score:
                best_score = xgb_r2
                best_model = xgb_model
                best_model_name = "XGBoost"

            # Residuals for diagnostics
            y_final_preds = best_model.predict(X_test)
            residuals = (y_test - y_final_preds).tolist()
            diagnostics = {
                "residuals": residuals[:50],
                "actual_vs_predicted": [{"actual": float(a), "predicted": float(p)} for a, p in zip(y_test[:40], y_final_preds[:40])]
            }
            
        else: # Classification
            # 1. Baseline
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
            
            # 2. Logistic Regression
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
            if lr_acc > best_score:
                best_score = lr_acc
                best_model = lr_model
                best_model_name = "Logistic Regression"
                
            # 3. Random Forest Classifier
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
            if rf_acc > best_score:
                best_score = rf_acc
                best_model = rf_clf
                best_model_name = "Random Forest"

            # 4. XGBoost Classifier
            xgb_clf = xgb.XGBClassifier(n_estimators=50, max_depth=4, learning_rate=0.1, random_state=42)
            xgb_clf.fit(X_train, y_train)
            xgb_preds = xgb_clf.predict(X_test)
            xgb_acc = accuracy_score(y_test, xgb_preds)
            leaderboard.append({
                "algorithm": "XGBoost",
                "accuracy": round(float(xgb_acc), 4),
                "f1": round(float(f1_score(y_test, xgb_preds, average="weighted", zero_division=0)), 4),
                "tag": "ML prediction"
            })
            if xgb_acc > best_score:
                best_score = xgb_acc
                best_model = xgb_clf
                best_model_name = "XGBoost"

            # Confusion Matrix & Diagnostics
            y_final_preds = best_model.predict(X_test)
            cm = confusion_matrix(y_test, y_final_preds).tolist()
            diagnostics = {
                "confusion_matrix": cm,
                "classes": [str(c) for c in np.unique(y)]
            }

        # Feature Importance
        feature_importance = []
        if hasattr(best_model, "feature_importances_"):
            importances = best_model.feature_importances_
            feature_importance = [
                {"feature": feat, "importance": round(float(imp), 4)}
                for feat, imp in zip(feature_names, importances)
            ]
            feature_importance.sort(key=lambda x: x["importance"], reverse=True)
        elif hasattr(best_model, "coef_"):
            coefs = np.abs(best_model.coef_[0] if best_model.coef_.ndim > 1 else best_model.coef_)
            feature_importance = [
                {"feature": feat, "importance": round(float(c), 4)}
                for feat, c in zip(feature_names, coefs)
            ]
            feature_importance.sort(key=lambda x: x["importance"], reverse=True)

        # Save model artifact
        save_path = settings.MODELS_DIR / f"{model_save_name}.joblib"
        joblib.dump({"model": best_model, "features": feature_names, "task_type": task_type}, str(save_path))

        # Model Card
        model_card = {
            "model_name": best_model_name,
            "target": target_col,
            "task_type": task_type,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "features_used": feature_names,
            "performance_summary": f"Best model {best_model_name} achieved score of {best_score:.4f}.",
            "warnings_and_caveats": warnings,
            "tag": "ML prediction"
        }

        return {
            "task_type": task_type,
            "best_algorithm": best_model_name,
            "model_path": str(save_path),
            "leaderboard": leaderboard,
            "feature_importance": feature_importance[:10],
            "diagnostics": diagnostics,
            "model_card": model_card,
            "warnings": warnings,
        }
