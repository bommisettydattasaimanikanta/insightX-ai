import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA

class TimeSeriesForecaster:
    """Forecasting engine with backtesting, naive baseline, MAPE/sMAPE, and confidence intervals."""

    @staticmethod
    def forecast(
        df: pd.DataFrame, 
        time_col: str, 
        metric_col: str, 
        horizon: int = 30, 
        freq: str = "D"
    ) -> Dict[str, Any]:
        temp = df[[time_col, metric_col]].dropna().copy()
        temp[time_col] = pd.to_datetime(temp[time_col], errors="coerce")
        temp = temp.dropna().sort_values(by=time_col)
        
        # Resample to regular frequency
        series = temp.groupby(pd.Grouper(key=time_col, freq=freq))[metric_col].sum()
        series = series.ffill().fillna(0)
        
        if len(series) < 10:
            raise ValueError("Time series requires at least 10 historical data points to generate forecast.")
            
        # Backtesting split (last 20% of data as validation)
        split_idx = max(5, int(len(series) * 0.8))
        train_series = series.iloc[:split_idx]
        test_series = series.iloc[split_idx:]
        
        # 1. Naive Baseline (Last known value)
        naive_forecast = [train_series.iloc[-1]] * len(test_series)
        naive_mape = float(np.mean(np.abs((test_series.values - naive_forecast) / np.maximum(np.abs(test_series.values), 1e-5))) * 100)
        
        # 2. Exponential Smoothing or ARIMA Model
        try:
            model = ExponentialSmoothing(train_series, trend="add", seasonal=None, initialization_method="estimated").fit()
            model_test_preds = model.forecast(len(test_series))
        except Exception:
            # Fallback to simple moving average drift
            slope = (train_series.iloc[-1] - train_series.iloc[0]) / len(train_series)
            model_test_preds = train_series.iloc[-1] + slope * np.arange(1, len(test_series) + 1)
            
        # Evaluation Metrics
        y_true = test_series.values
        y_pred = np.array(model_test_preds)
        mape = float(np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-5))) * 100)
        smape = float(np.mean(2 * np.abs(y_pred - y_true) / np.maximum(np.abs(y_true) + np.abs(y_pred), 1e-5)) * 100)
        mae = float(np.mean(np.abs(y_true - y_pred)))
        
        # Full Series Fit for Out-of-Sample Horizon Forecast
        try:
            full_model = ExponentialSmoothing(series, trend="add", seasonal=None, initialization_method="estimated").fit()
            base_forecast = full_model.forecast(horizon)
        except Exception:
            slope = (series.iloc[-1] - series.iloc[0]) / len(series)
            base_forecast = series.iloc[-1] + slope * np.arange(1, horizon + 1)
            
        # Compute standard error of residuals for confidence bounds & scenarios
        residuals = series.iloc[1:].values - series.iloc[:-1].values
        std_err = float(np.std(residuals)) if len(residuals) > 0 else 1.0
        
        last_date = series.index[-1]
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq=freq)
        
        forecast_points = []
        for i, (dt, val) in enumerate(zip(future_dates, base_forecast)):
            margin_80 = 1.28 * std_err * np.sqrt(i + 1)
            margin_95 = 1.96 * std_err * np.sqrt(i + 1)
            
            base_val = max(0.0, float(val))
            best_val = base_val + margin_80
            worst_val = max(0.0, base_val - margin_80)
            
            forecast_points.append({
                "date": dt.strftime("%Y-%m-%d"),
                "base_case": round(base_val, 2),
                "best_case": round(best_val, 2),
                "worst_case": round(worst_val, 2),
                "lower_95": round(max(0.0, base_val - margin_95), 2),
                "upper_95": round(base_val + margin_95, 2),
            })
            
        historical_points = [
            {"date": dt.strftime("%Y-%m-%d"), "actual": round(float(v), 2)}
            for dt, v in series.tail(60).items()
        ]
        
        return {
            "time_column": time_col,
            "metric_column": metric_col,
            "horizon": horizon,
            "tag": "ML prediction",
            "backtest": {
                "model_mape_pct": round(mape, 2),
                "model_smape_pct": round(smape, 2),
                "naive_baseline_mape_pct": round(naive_mape, 2),
                "mae": round(mae, 2),
                "outperforms_baseline": mape < naive_mape,
            },
            "historical": historical_points,
            "forecast": forecast_points,
        }
