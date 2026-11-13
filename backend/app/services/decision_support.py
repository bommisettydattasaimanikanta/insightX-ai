import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from backend.app.config import settings

class DecisionSupportService:
    """Provides What-If simulations, sensitivity tornado analysis, and Goal Seek optimization."""

    @staticmethod
    def simulate_what_if(
        model_path: str, 
        base_features: Dict[str, float], 
        feature_tweaks: Dict[str, float]
    ) -> Dict[str, Any]:
        """Runs trained model against modified inputs to calculate predicted delta."""
        if not os.path.exists(model_path):
            raise FileNotFoundError("Trained ML model artifact not found.")
            
        bundle = joblib.load(model_path)
        # Always use the best non-baseline model for feature sensitivity & what-if
        model = bundle.get("non_baseline_model") or bundle["model"]
        features = bundle["features"]
        
        # Build baseline input vector
        base_vec = [base_features.get(f, 0.0) for f in features]
        # Build tweaked input vector
        tweaked_vec = [feature_tweaks.get(f, base_features.get(f, 0.0)) for f in features]
        
        base_pred = float(model.predict([base_vec])[0])
        tweaked_pred = float(model.predict([tweaked_vec])[0])
        
        diff = tweaked_pred - base_pred
        pct_change = (diff / max(abs(base_pred), 1e-5)) * 100.0
        
        return {
            "baseline_prediction": round(base_pred, 2),
            "simulated_prediction": round(tweaked_pred, 2),
            "absolute_delta": round(diff, 2),
            "percentage_delta": round(pct_change, 2),
            "tag": "ML prediction",
            "message": f"Simulated changes result in a {pct_change:+.1f}% shift in predicted outcome."
        }

    @staticmethod
    def sensitivity_tornado(model_path: str, base_features: Dict[str, float]) -> List[Dict[str, Any]]:
        """Calculates sensitivity tornado: variations in each feature by +/- 15%."""
        if not os.path.exists(model_path):
            return []
            
        bundle = joblib.load(model_path)
        # Always use the best non-baseline model for feature sensitivity & what-if
        model = bundle.get("non_baseline_model") or bundle["model"]
        features = bundle["features"]
        
        base_vec = [base_features.get(f, 0.0) for f in features]
        base_pred = float(model.predict([base_vec])[0])
        
        tornado = []
        for i, feat in enumerate(features[:8]):
            orig_val = base_features.get(feat, 1.0)
            val_down = orig_val * 0.85
            val_up = orig_val * 1.15
            
            vec_down = list(base_vec)
            vec_down[i] = val_down
            pred_down = float(model.predict([vec_down])[0])
            
            vec_up = list(base_vec)
            vec_up[i] = val_up
            pred_up = float(model.predict([vec_up])[0])
            
            swing = abs(pred_up - pred_down)
            tornado.append({
                "feature": feat,
                "base_val": round(orig_val, 2),
                "low_val": round(val_down, 2),
                "high_val": round(val_up, 2),
                "pred_low": round(pred_down, 2),
                "pred_high": round(pred_up, 2),
                "swing": round(swing, 2),
                "tag": "ML prediction"
            })
            
        tornado.sort(key=lambda x: x["swing"], reverse=True)
        return tornado

    @staticmethod
    def goal_seek(
        model_path: str, 
        base_features: Dict[str, float], 
        target_feature: str, 
        desired_output: float,
        bounds: Tuple[float, float] = (0.0, 100000.0)
    ) -> Dict[str, Any]:
        """Binary search solver to find what value of target_feature achieves desired_output."""
        if not os.path.exists(model_path):
            raise FileNotFoundError("Model not found")
            
        bundle = joblib.load(model_path)
        # Always use the best non-baseline model for feature sensitivity & what-if
        model = bundle.get("non_baseline_model") or bundle["model"]
        features = bundle["features"]
        if target_feature not in features:
            raise ValueError(f"Feature '{target_feature}' not used by model.")
            
        f_idx = features.index(target_feature)
        low, high = bounds
        base_vec = [base_features.get(f, 0.0) for f in features]
        
        # Test 50 iterations of bisection
        for _ in range(50):
            mid = (low + high) / 2.0
            vec = list(base_vec)
            vec[f_idx] = mid
            pred = float(model.predict([vec])[0])
            
            if abs(pred - desired_output) < 0.01:
                break
                
            # Assume monotonic local slope
            vec_high = list(base_vec)
            vec_high[f_idx] = high
            pred_high = float(model.predict([vec_high])[0])
            
            if pred_high > pred: # increasing
                if pred < desired_output:
                    low = mid
                else:
                    high = mid
            else: # decreasing
                if pred < desired_output:
                    high = mid
                else:
                    low = mid
                    
        return {
            "target_feature": target_feature,
            "required_value": round(mid, 2),
            "desired_output": desired_output,
            "achieved_prediction": round(pred, 2),
            "tag": "ML prediction"
        }
