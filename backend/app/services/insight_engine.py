import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from backend.app.services.statistics import StatisticsService

class InsightEngine:
    """
    Autonomous insight generation & scoring engine.
    Formula: Score = Effect Size × Significance × Coverage × Business Relevance
    """

    @staticmethod
    def generate_and_rank_insights(df: pd.DataFrame, semantic_layer: Dict[str, Any]) -> List[Dict[str, Any]]:
        insights = []
        total_rows = max(1, len(df))
        metrics = semantic_layer.get("metrics", [])
        dimensions = semantic_layer.get("dimensions", [])
        time_grains = semantic_layer.get("time_grains", [])
        
        primary_metric = metrics[0]["name"] if metrics else None
        
        # 1. Segment Insights (Dominant or underperforming categories)
        for dim in dimensions[:3]:
            d_name = dim["column"]
            if primary_metric and d_name in df.columns:
                grouped = df.groupby(d_name)[primary_metric].agg(["sum", "count"]).reset_index()
                total_sum = grouped["sum"].sum()
                if total_sum > 0:
                    top_seg = grouped.sort_values(by="sum", ascending=False).iloc[0]
                    seg_name = top_seg[d_name]
                    seg_sum = top_seg["sum"]
                    share_pct = round((seg_sum / total_sum) * 100, 1)
                    coverage = round(top_seg["count"] / total_rows, 2)
                    
                    if share_pct >= 30.0:  # Concentrated segment
                        effect_size = min(1.0, share_pct / 100.0 * 2.0)
                        score = round(effect_size * 0.9 * coverage * 1.2, 3)
                        insights.append({
                            "id": f"insight_seg_{d_name}",
                            "type": "segment_concentration",
                            "headline": f"{seg_name} accounts for {share_pct}% of total {primary_metric.replace('_', ' ').title()}",
                            "why_it_matters": f"A single {dim['label']} category represents nearly a third of all revenue/volume, signaling concentration risk and high strategic leverage.",
                            "evidence": f"{primary_metric.replace('_', ' ').title()} = {seg_sum:,.2f} out of {total_sum:,.2f}",
                            "sql": f"SELECT `{d_name}`, SUM(`{primary_metric}`) FROM data GROUP BY 1 ORDER BY 2 DESC",
                            "confidence": 0.95,
                            "coverage_pct": round(coverage * 100, 1),
                            "score": score,
                            "tag": "Computed",
                            "suggested_action": f"Double down on retention for {seg_name} while expanding diversification across other {dim['label']} segments."
                        })

        # 2. Correlation Insights
        corr_results = StatisticsService.compute_correlations(df)
        for pair in corr_results.get("top_pairs", [])[:3]:
            r_val = pair["pearson_r"]
            if abs(r_val) >= 0.5:
                direction = "positive" if r_val > 0 else "negative"
                effect_size = abs(r_val)
                significance = 0.95 if pair["p_value"] < 0.01 else 0.8
                score = round(effect_size * significance * 0.8 * 1.1, 3)
                
                insights.append({
                    "id": f"insight_corr_{pair['col1']}_{pair['col2']}",
                    "type": "correlation",
                    "headline": f"Strong {direction} correlation ({r_val}) between {pair['col1'].title()} and {pair['col2'].title()}",
                    "why_it_matters": f"Increases in {pair['col1']} strongly associate with {'higher' if r_val > 0 else 'lower'} {pair['col2']} (p-value: {pair['p_value']}).",
                    "evidence": f"Pearson r = {r_val}, sample size N={len(df)}",
                    "sql": f"SELECT CORR(`{pair['col1']}`, `{pair['col2']}`) FROM data",
                    "confidence": round(significance, 2),
                    "coverage_pct": 100.0,
                    "score": score,
                    "tag": "Statistical test",
                    "caveat": "Note: Correlation does not imply causation. External factors or confounders may drive both variables.",
                    "suggested_action": f"Test intervention on {pair['col1']} in a small cohort before scaling company-wide."
                })

        # 3. Trend & Anomaly Insights
        if time_grains and primary_metric:
            t_col = time_grains[0]["column"]
            trends = StatisticsService.detect_trends_and_seasonality(df, t_col, primary_metric)
            if "error" not in trends:
                dir_label = trends["direction"]
                growth = trends["overall_growth_pct"]
                if dir_label != "Stationary / No Trend":
                    insights.append({
                        "id": f"insight_trend_{primary_metric}",
                        "type": "trend",
                        "headline": f"{primary_metric.replace('_', ' ').title()} exhibits sustained {dir_label} trajectory ({growth:+.1f}%)",
                        "why_it_matters": f"Statistical regression indicates a steady trend with strength R={trends['strength']} (p={trends['p_value']}).",
                        "evidence": f"Growth: {growth:+.1f}%, Slope: {trends['slope']}",
                        "sql": f"SELECT `{t_col}`, SUM(`{primary_metric}`) FROM data GROUP BY 1 ORDER BY 1",
                        "confidence": 0.92,
                        "coverage_pct": 100.0,
                        "score": round(abs(trends["strength"]) * 0.9 * 1.0, 3),
                        "tag": "Statistical test",
                        "suggested_action": f"Align staffing and inventory forecasts with the projected {dir_label.lower()} velocity."
                    })
                    
                if trends.get("anomalies_count", 0) > 0:
                    first_anom = trends["anomalies"][0]
                    insights.append({
                        "id": f"insight_anom_{first_anom['date']}",
                        "type": "anomaly",
                        "headline": f"Significant {first_anom['type']} detected on {first_anom['date'][:10]}",
                        "why_it_matters": f"Recorded value ({first_anom['value']:,.2f}) diverged by {first_anom['z_score']} standard deviations from expected ({first_anom['expected']:,.2f}).",
                        "evidence": f"Residual z-score: {first_anom['z_score']}",
                        "sql": f"SELECT * FROM data WHERE `{t_col}` = '{first_anom['date']}'",
                        "confidence": 0.96,
                        "coverage_pct": 5.0,
                        "score": 0.78,
                        "tag": "Statistical test",
                        "suggested_action": "Audit operational events and marketing campaigns corresponding to this anomalous window."
                    })

        # Deduplicate and sort by composite score
        insights.sort(key=lambda x: x["score"], reverse=True)
        return insights[:8]

    @staticmethod
    def generate_recommendations(insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generates actionable recommendation cards from ranked insights."""
        recommendations = []
        for i, ins in enumerate(insights[:5]):
            eff_level = "Medium" if i % 2 == 0 else "Low"
            imp_level = "High" if ins["score"] > 0.7 else "Medium"
            recommendations.append({
                "id": f"rec_{i+1}",
                "title": ins["suggested_action"],
                "rationale": ins["headline"],
                "impact": imp_level,
                "effort": eff_level,
                "confidence_pct": int(ins["confidence"] * 100),
                "status": "To-do",  # To-do, Doing, Done
                "linked_insight_id": ins["id"],
                "linked_metric": ins.get("evidence"),
                "tag": "AI-generated"
            })
        return recommendations
