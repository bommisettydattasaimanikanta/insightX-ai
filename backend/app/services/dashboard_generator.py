import json
from typing import Dict, Any, List, Optional
import pandas as pd
from backend.app.services.semantic_service import SemanticService

class DashboardGenerator:
    """Generates declarative JSON dashboard specs that bind directly to the Semantic Layer."""

    @staticmethod
    def generate_auto_dashboard(df: pd.DataFrame, semantic_layer: Dict[str, Any], title: str = "Overview Executive Dashboard") -> Dict[str, Any]:
        metrics = semantic_layer.get("metrics", [])
        dimensions = semantic_layer.get("dimensions", [])
        time_grains = semantic_layer.get("time_grains", [])
        domain = semantic_layer.get("domain", "general")
        
        # 1. Generate KPI Summary Cards (3-4 top metrics)
        kpi_cards = []
        for i, m in enumerate(metrics[:4]):
            col = m["name"]
            agg = m.get("aggregation", "SUM")
            series = df[col].dropna()
            
            val = float(series.sum() if agg == "SUM" else series.mean())
            delta = None
            if len(series) > 1:
                # Compare second half vs first half for delta
                mid = len(series) // 2
                first_half = series.iloc[:mid].mean()
                second_half = series.iloc[mid:].mean()
                if first_half != 0:
                    delta = round(((second_half - first_half) / abs(first_half)) * 100, 1)
                    
            kpi_cards.append({
                "id": f"kpi_{col}",
                "title": m["label"],
                "value": round(val, 2),
                "format": m.get("format", "number"),
                "delta_pct": delta,
                "formula_sql": f"SELECT {m['expression']} AS `{m['name']}` FROM data",
                "tag": "Computed",
                "grid": {"x": i * 3, "y": 0, "w": 3, "h": 2}
            })
            
        # 2. Charts (8-12 charts based on semantic roles)
        charts = []
        grid_y = 2
        chart_id = 1
        
        primary_time = time_grains[0]["column"] if time_grains else None
        primary_metric = metrics[0]["name"] if metrics else None
        secondary_metric = metrics[1]["name"] if len(metrics) > 1 else None
        primary_dim = dimensions[0]["column"] if dimensions else None
        secondary_dim = dimensions[1]["column"] if len(dimensions) > 1 else None

        # Chart 1: Time Series Trend Line (if time column exists)
        if primary_time and primary_metric:
            try:
                temp = df[[primary_time, primary_metric]].dropna().copy()
                temp[primary_time] = pd.to_datetime(temp[primary_time], errors="coerce")
                trend_data = temp.dropna().groupby(pd.Grouper(key=primary_time, freq="M"))[primary_metric].sum().reset_index()
                if len(trend_data) > 1:
                    trend_data[primary_time] = trend_data[primary_time].dt.strftime("%Y-%m")
                    charts.append({
                        "id": f"chart_{chart_id}",
                        "title": f"{primary_metric.replace('_', ' ').title()} Over Time",
                        "chart_type": "line",
                        "x_axis": primary_time,
                        "y_axis": primary_metric,
                        "data": trend_data.to_dict(orient="records"),
                        "sql_query": f"SELECT strftime('%Y-%m', `{primary_time}`) AS `{primary_time}`, SUM(`{primary_metric}`) AS `{primary_metric}` FROM data GROUP BY 1 ORDER BY 1",
                        "tag": "Computed",
                        "grid": {"x": 0, "y": grid_y, "w": 8, "h": 4}
                    })
                    chart_id += 1
            except Exception:
                pass

        # Chart 2: Category Breakdown Donut / Pie
        if primary_dim and primary_metric:
            cat_data = df.groupby(primary_dim)[primary_metric].sum().reset_index().sort_values(by=primary_metric, ascending=False).head(6)
            charts.append({
                "id": f"chart_{chart_id}",
                "title": f"{primary_metric.replace('_', ' ').title()} Share by {primary_dim.replace('_', ' ').title()}",
                "chart_type": "donut",
                "x_axis": primary_dim,
                "y_axis": primary_metric,
                "data": cat_data.to_dict(orient="records"),
                "sql_query": f"SELECT `{primary_dim}`, SUM(`{primary_metric}`) AS `{primary_metric}` FROM data GROUP BY `{primary_dim}` ORDER BY 2 DESC LIMIT 6",
                "tag": "Computed",
                "grid": {"x": 8, "y": grid_y, "w": 4, "h": 4}
            })
            chart_id += 1
            grid_y += 4

        # Chart 3: Horizontal Bar Ranking
        if secondary_dim and primary_metric:
            rank_data = df.groupby(secondary_dim)[primary_metric].sum().reset_index().sort_values(by=primary_metric, ascending=False).head(8)
            charts.append({
                "id": f"chart_{chart_id}",
                "title": f"Top {secondary_dim.replace('_', ' ').title()} Performance",
                "chart_type": "bar",
                "x_axis": secondary_dim,
                "y_axis": primary_metric,
                "data": rank_data.to_dict(orient="records"),
                "sql_query": f"SELECT `{secondary_dim}`, SUM(`{primary_metric}`) AS `{primary_metric}` FROM data GROUP BY `{secondary_dim}` ORDER BY 2 DESC LIMIT 8",
                "tag": "Computed",
                "grid": {"x": 0, "y": grid_y, "w": 6, "h": 4}
            })
            chart_id += 1

        # Chart 4: Correlation / Two-Metric Scatter Plot
        if primary_metric and secondary_metric:
            scatter_sample = df[[primary_metric, secondary_metric]].dropna().head(200)
            charts.append({
                "id": f"chart_{chart_id}",
                "title": f"{primary_metric.replace('_', ' ').title()} vs {secondary_metric.replace('_', ' ').title()}",
                "chart_type": "scatter",
                "x_axis": primary_metric,
                "y_axis": secondary_metric,
                "data": scatter_sample.to_dict(orient="records"),
                "sql_query": f"SELECT `{primary_metric}`, `{secondary_metric}` FROM data LIMIT 200",
                "tag": "Computed",
                "grid": {"x": 6, "y": grid_y, "w": 6, "h": 4}
            })
            chart_id += 1
            grid_y += 4

        # Chart 5: Additional Dimensions Bar Chart
        if len(dimensions) > 2 and primary_metric:
            extra_dim = dimensions[2]["column"]
            extra_data = df.groupby(extra_dim)[primary_metric].mean().reset_index().sort_values(by=primary_metric, ascending=False).head(8)
            charts.append({
                "id": f"chart_{chart_id}",
                "title": f"Average {primary_metric.replace('_', ' ').title()} by {extra_dim.replace('_', ' ').title()}",
                "chart_type": "bar",
                "x_axis": extra_dim,
                "y_axis": primary_metric,
                "data": extra_data.to_dict(orient="records"),
                "sql_query": f"SELECT `{extra_dim}`, AVG(`{primary_metric}`) AS `{primary_metric}` FROM data GROUP BY `{extra_dim}` ORDER BY 2 DESC LIMIT 8",
                "tag": "Computed",
                "grid": {"x": 0, "y": grid_y, "w": 6, "h": 4}
            })
            chart_id += 1

        # Chart 6: Heatmap / Cross-tabulation if 2 dimensions exist
        if primary_dim and secondary_dim and primary_metric:
            pivot = df.pivot_table(index=primary_dim, columns=secondary_dim, values=primary_metric, aggfunc="sum").fillna(0)
            # Limit to top 5x5
            top_rows = df.groupby(primary_dim)[primary_metric].sum().nlargest(5).index
            top_cols = df.groupby(secondary_dim)[primary_metric].sum().nlargest(5).index
            sub_pivot = pivot.loc[pivot.index.isin(top_rows), pivot.columns.isin(top_cols)]
            
            heatmap_cells = []
            for r in sub_pivot.index:
                for c in sub_pivot.columns:
                    heatmap_cells.append({"row": str(r), "col": str(c), "value": round(float(sub_pivot.loc[r, c]), 2)})
                    
            charts.append({
                "id": f"chart_{chart_id}",
                "title": f"{primary_metric.replace('_', ' ').title()} Matrix: {primary_dim.title()} vs {secondary_dim.title()}",
                "chart_type": "heatmap",
                "data": heatmap_cells,
                "sql_query": f"SELECT `{primary_dim}`, `{secondary_dim}`, SUM(`{primary_metric}`) AS value FROM data GROUP BY 1, 2",
                "tag": "Computed",
                "grid": {"x": 6, "y": grid_y, "w": 6, "h": 4}
            })
            chart_id += 1

        # Global Filters
        filter_dimensions = [d["column"] for d in dimensions[:3]]
        
        return {
            "title": title,
            "domain": domain,
            "kpi_cards": kpi_cards,
            "charts": charts,
            "filters": {
                "dimensions": filter_dimensions,
                "date_range_column": primary_time
            },
            "theme": "indigo",
            "grid_columns": 12
        }
