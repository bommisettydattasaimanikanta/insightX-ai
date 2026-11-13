import io
import os
from typing import Dict, Any, List, Optional
import pandas as pd
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

class ExportService:
    """Server-side rendering and export service for InsightX AI Dashboards."""

    @staticmethod
    def build_dashboard_html(spec: Dict[str, Any], user_name: str = "Lead Analyst") -> str:
        domain = spec.get("domain", "other").capitalize()
        dataset_name = spec.get("dataset_name", "Dataset")
        analyzed_at = spec.get("analyzed_at", "Recently")
        kpis = spec.get("kpi_cards", [])
        charts = spec.get("charts", [])
        top_table = spec.get("top_entities_table")
        insights = spec.get("insights", [])

        # Build KPI Cards HTML
        kpi_html = ""
        for k in kpis[:4]:
            delta_badge = ""
            if k.get("delta_pct") is not None:
                d = k["delta_pct"]
                color = "#10b981" if d >= 0 else "#f43f5e"
                symbol = "↑" if d >= 0 else "↓"
                delta_badge = f'<span style="font-size:11px;font-weight:600;color:{color};margin-left:8px;">{symbol} {abs(d)}%</span>'
            
            subtext_html = ""
            if k.get("subtext"):
                subtext_html = f'<div style="font-size:11px;color:#94a3b8;margin-top:4px;">{k["subtext"]}</div>'

            kpi_html += f"""
            <div style="background:rgba(16, 23, 53, 0.85);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:20px;flex:1;min-width:200px;box-shadow:0 8px 24px rgba(0,0,0,0.3);">
                <div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;display:flex;align-items:center;justify-content:space-between;">
                    <span>{k.get('title', 'Metric')}</span>
                    <span style="background:rgba(255,255,255,0.05);color:#38bdf8;padding:2px 8px;border-radius:6px;font-size:9px;font-family:monospace;">{k.get('tag', 'Computed')}</span>
                </div>
                <div style="font-size:28px;font-weight:700;color:#ffffff;margin-top:10px;display:flex;align-items:baseline;">
                    <span>{k.get('formatted_value', str(k.get('value', '0')))}</span>
                    {delta_badge}
                </div>
                {subtext_html}
                <div style="font-size:9px;color:#64748b;margin-top:8px;font-family:monospace;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                    {k.get('formula_sql', '')}
                </div>
            </div>
            """

        # Build Top N Table HTML
        table_html = ""
        if top_table and top_table.get("rows"):
            rows_html = ""
            for r in top_table["rows"][:8]:
                rows_html += f"""
                <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                    <td style="padding:10px 14px;color:#f8fafc;font-weight:600;">{r.get('entity')}</td>
                    <td style="padding:10px 14px;text-align:right;color:#cbd5e1;">{r.get('count')}</td>
                    <td style="padding:10px 14px;text-align:right;color:#38bdf8;font-weight:600;">{r.get('total'):,}</td>
                    <td style="padding:10px 14px;text-align:right;color:#cbd5e1;">{r.get('average')}</td>
                    <td style="padding:10px 14px;text-align:right;color:#10b981;font-weight:600;">{r.get('highest')}</td>
                </tr>
                """
            table_html = f"""
            <div style="background:rgba(16, 23, 53, 0.85);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:20px;margin-top:20px;">
                <div style="font-size:16px;font-weight:700;color:#ffffff;margin-bottom:12px;">{top_table.get('title', 'Leaderboard')}</div>
                <table style="width:100%;border-collapse:collapse;font-size:12px;">
                    <thead>
                        <tr style="border-bottom:1px solid rgba(255,255,255,0.1);color:#94a3b8;text-align:left;">
                            <th style="padding:8px 14px;">{top_table.get('dimension_label', 'Entity')}</th>
                            <th style="padding:8px 14px;text-align:right;">{top_table.get('count_label', 'Count')}</th>
                            <th style="padding:8px 14px;text-align:right;">Total {top_table.get('metric_label', '')}</th>
                            <th style="padding:8px 14px;text-align:right;">Avg</th>
                            <th style="padding:8px 14px;text-align:right;">High</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            """

        # Build AI Insights HTML
        insights_html = ""
        for ins in insights[:3]:
            tag_color = "#38bdf8"
            tag = ins.get("tag", "Computed")
            if "Statistical" in tag:
                tag_color = "#a855f7"
            elif "ML" in tag:
                tag_color = "#f59e0b"
            elif "AI" in tag:
                tag_color = "#10b981"

            insights_html += f"""
            <div style="background:rgba(16, 23, 53, 0.7);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:14px;margin-bottom:10px;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                    <span style="font-size:12px;font-weight:700;color:#ffffff;">{ins.get('title', 'Insight')}</span>
                    <span style="font-size:9px;color:{tag_color};background:rgba(255,255,255,0.04);border:1px solid {tag_color}40;padding:2px 8px;border-radius:6px;font-weight:600;">{tag}</span>
                </div>
                <div style="font-size:11px;color:#cbd5e1;line-height:1.4;">{ins.get('description', '')}</div>
                <div style="font-size:9px;color:#64748b;margin-top:6px;font-family:monospace;">{ins.get('formula_or_sql', '')}</div>
            </div>
            """

        # Full HTML Document with Print / PDF styles
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{spec.get('title', 'InsightX AI Dashboard')}</title>
    <style>
        @page {{
            size: A4 landscape;
            margin: 12mm;
        }}
        body {{
            background: #070b19;
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 16px;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}
    </style>
</head>
<body>
    <!-- Brand Header -->
    <div style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:16px;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg, #10b981, #06b6d4);display:flex;align-items:center;justify-content:center;font-weight:800;color:#ffffff;font-size:18px;">
                ⚡
            </div>
            <div>
                <div style="font-size:18px;font-weight:800;letter-spacing:-0.02em;color:#ffffff;">InsightX AI <span style="font-size:12px;font-weight:500;color:#38bdf8;margin-left:6px;">Autonomous Dashboard</span></div>
                <div style="font-size:11px;color:#94a3b8;">Welcome back, {user_name} • Domain: <strong style="color:#10b981;">{domain}</strong> • Analyzed {analyzed_at}</div>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:14px;font-weight:700;color:#ffffff;">{dataset_name}</div>
            <div style="font-size:10px;color:#64748b;font-family:monospace;">Verified Deterministic Calculation Spec</div>
        </div>
    </div>

    <!-- 4 KPI Cards -->
    <div style="display:flex;gap:14px;margin-bottom:16px;">
        {kpi_html}
    </div>

    <!-- Main Content Grid -->
    <div style="display:flex;gap:16px;align-items:flex-start;">
        <!-- Left: Top N Leaderboard Table -->
        <div style="flex:2;">
            {table_html}
        </div>

        <!-- Right: AI Insights Card -->
        <div style="flex:1;background:rgba(16, 23, 53, 0.85);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:20px;margin-top:20px;">
            <div style="font-size:16px;font-weight:700;color:#ffffff;margin-bottom:12px;display:flex;align-items:center;justify-content:space-between;">
                <span>AI Insights & Synthesis</span>
                <span style="font-size:10px;color:#10b981;font-weight:600;">Top 3 Verified</span>
            </div>
            {insights_html}
        </div>
    </div>

    <!-- Footer Note -->
    <div style="margin-top:24px;border-top:1px solid rgba(255,255,255,0.06);padding-top:10px;font-size:10px;color:#64748b;display:flex;justify-content:space-between;">
        <span>Generated by InsightX AI Autonomous Platform • Code computes, AI explains.</span>
        <span>Every number is grounded by SQL / mathematical formula.</span>
    </div>
</body>
</html>
"""

    @classmethod
    def export_pdf(cls, spec: Dict[str, Any], user_name: str = "Lead Analyst") -> bytes:
        html_content = cls.build_dashboard_html(spec, user_name)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1400, "height": 900})
            page.set_content(html_content, wait_until="load")
            pdf_bytes = page.pdf(
                format="A4",
                landscape=True,
                print_background=True,
                margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
            )
            browser.close()
        return pdf_bytes

    @classmethod
    def export_png(cls, spec: Dict[str, Any], user_name: str = "Lead Analyst") -> bytes:
        html_content = cls.build_dashboard_html(spec, user_name)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1400, "height": 900})
            page.set_content(html_content, wait_until="load")
            png_bytes = page.screenshot(full_page=True)
            browser.close()
        return png_bytes

    @classmethod
    def export_pptx(cls, spec: Dict[str, Any], df: pd.DataFrame, user_name: str = "Lead Analyst") -> bytes:
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        blank_layout = prs.slide_layouts[6]

        # Slide 1: Title Slide
        s1 = prs.slides.add_slide(blank_layout)
        # Background
        bg1 = s1.shapes.add_shape(1, 0, 0, Inches(13.333), Inches(7.5))
        bg1.fill.solid()
        bg1.fill.fore_color.rgb = RGBColor(7, 11, 25)
        bg1.line.color.rgb = RGBColor(7, 11, 25)

        tb1 = s1.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.3), Inches(2.5))
        tf1 = tb1.text_frame
        p1 = tf1.paragraphs[0]
        p1.text = "InsightX AI Autonomous Executive Dashboard"
        p1.font.bold = True
        p1.font.size = Pt(36)
        p1.font.color.rgb = RGBColor(255, 255, 255)

        p2 = tf1.add_paragraph()
        p2.text = f"Dataset: {spec.get('dataset_name', 'Dataset')} | Domain: {spec.get('domain', 'general').capitalize()}"
        p2.font.size = Pt(20)
        p2.font.color.rgb = RGBColor(56, 189, 248)

        p3 = tf1.add_paragraph()
        p3.text = f"Prepared for {user_name} • Analyzed {spec.get('analyzed_at', 'Recently')}"
        p3.font.size = Pt(14)
        p3.font.color.rgb = RGBColor(148, 163, 184)

        # Slide 2: KPI Metrics Slide
        s2 = prs.slides.add_slide(blank_layout)
        bg2 = s2.shapes.add_shape(1, 0, 0, Inches(13.333), Inches(7.5))
        bg2.fill.solid()
        bg2.fill.fore_color.rgb = RGBColor(7, 11, 25)
        bg2.line.color.rgb = RGBColor(7, 11, 25)

        tb2 = s2.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(1.0))
        tf2 = tb2.text_frame
        p_hdr = tf2.paragraphs[0]
        p_hdr.text = "Key Performance Indicators (Grounded)"
        p_hdr.font.bold = True
        p_hdr.font.size = Pt(28)
        p_hdr.font.color.rgb = RGBColor(255, 255, 255)

        kpis = spec.get("kpi_cards", [])
        for i, k in enumerate(kpis[:4]):
            left = Inches(1.0 + i * 2.85)
            card = s2.shapes.add_shape(1, left, Inches(2.2), Inches(2.7), Inches(3.5))
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(16, 23, 53)
            card.line.color.rgb = RGBColor(56, 189, 248)

            ctb = s2.shapes.add_textbox(left + Inches(0.15), Inches(2.4), Inches(2.4), Inches(3.0))
            ctf = ctb.text_frame
            cp1 = ctf.paragraphs[0]
            cp1.text = k.get("title", "Metric")
            cp1.font.bold = True
            cp1.font.size = Pt(14)
            cp1.font.color.rgb = RGBColor(148, 163, 184)

            cp2 = ctf.add_paragraph()
            cp2.text = k.get("formatted_value", str(k.get("value", "0")))
            cp2.font.bold = True
            cp2.font.size = Pt(26)
            cp2.font.color.rgb = RGBColor(255, 255, 255)

            if k.get("subtext"):
                cp3 = ctf.add_paragraph()
                cp3.text = str(k["subtext"])
                cp3.font.size = Pt(11)
                cp3.font.color.rgb = RGBColor(16, 185, 129)

        # Slide 3: Dimension Breakdown Table
        top_table = spec.get("top_entities_table")
        if top_table and top_table.get("rows"):
            s3 = prs.slides.add_slide(blank_layout)
            bg3 = s3.shapes.add_shape(1, 0, 0, Inches(13.333), Inches(7.5))
            bg3.fill.solid()
            bg3.fill.fore_color.rgb = RGBColor(7, 11, 25)
            bg3.line.color.rgb = RGBColor(7, 11, 25)

            tb3 = s3.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(1.0))
            tf3 = tb3.text_frame
            p_t3 = tf3.paragraphs[0]
            p_t3.text = top_table.get("title", "Performance Leaderboard")
            p_t3.font.bold = True
            p_t3.font.size = Pt(28)
            p_t3.font.color.rgb = RGBColor(255, 255, 255)

            rows = top_table.get("rows", [])[:8]
            t_shape = s3.shapes.add_table(len(rows) + 1, 5, Inches(1.0), Inches(2.0), Inches(11.333), Inches(4.5))
            tbl = t_shape.table

            headers = [top_table.get("dimension_label", "Entity"), top_table.get("count_label", "Count"), f"Total {top_table.get('metric_label','')}", "Average", "High Score"]
            for col_idx, h in enumerate(headers):
                cell = tbl.cell(0, col_idx)
                cell.text = h
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
                for p in cell.text_frame.paragraphs:
                    p.font.bold = True
                    p.font.color.rgb = RGBColor(255, 255, 255)

            for r_idx, r in enumerate(rows):
                vals = [str(r.get("entity")), str(r.get("count")), f"{r.get('total'):,}", str(r.get("average")), str(r.get("highest"))]
                for col_idx, val in enumerate(vals):
                    cell = tbl.cell(r_idx + 1, col_idx)
                    cell.text = val
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(16, 23, 53)
                    for p in cell.text_frame.paragraphs:
                        p.font.size = Pt(12)
                        p.font.color.rgb = RGBColor(241, 245, 249)

        # Slide 4: Ranked AI Insights
        insights = spec.get("insights", [])
        if insights:
            s4 = prs.slides.add_slide(blank_layout)
            bg4 = s4.shapes.add_shape(1, 0, 0, Inches(13.333), Inches(7.5))
            bg4.fill.solid()
            bg4.fill.fore_color.rgb = RGBColor(7, 11, 25)
            bg4.line.color.rgb = RGBColor(7, 11, 25)

            tb4 = s4.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(1.0))
            tf4 = tb4.text_frame
            p_t4 = tf4.paragraphs[0]
            p_t4.text = "Ranked AI Insights & Findings"
            p_t4.font.bold = True
            p_t4.font.size = Pt(28)
            p_t4.font.color.rgb = RGBColor(255, 255, 255)

            for i, ins in enumerate(insights[:3]):
                top_pos = Inches(2.0 + i * 1.6)
                icard = s4.shapes.add_shape(1, Inches(1.0), top_pos, Inches(11.333), Inches(1.3))
                icard.fill.solid()
                icard.fill.fore_color.rgb = RGBColor(16, 23, 53)
                icard.line.color.rgb = RGBColor(56, 189, 248)

                itb = s4.shapes.add_textbox(Inches(1.2), top_pos + Inches(0.1), Inches(10.9), Inches(1.1))
                itf = itb.text_frame
                ip1 = itf.paragraphs[0]
                ip1.text = f"{ins.get('title', 'Insight')}  [{ins.get('tag', 'Computed')}]"
                ip1.font.bold = True
                ip1.font.size = Pt(15)
                ip1.font.color.rgb = RGBColor(56, 189, 248)

                ip2 = itf.add_paragraph()
                ip2.text = ins.get("description", "")
                ip2.font.size = Pt(12)
                ip2.font.color.rgb = RGBColor(226, 232, 240)

        stream = io.BytesIO()
        prs.save(stream)
        return stream.getvalue()

    @classmethod
    def export_excel(cls, df: pd.DataFrame, spec: Dict[str, Any]) -> bytes:
        stream = io.BytesIO()
        with pd.ExcelWriter(stream, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Cleaned Data", index=False)
            
            # KPI Sheet
            kpis = spec.get("kpi_cards", [])
            kpi_rows = []
            for k in kpis:
                kpi_rows.append({
                    "Metric": k.get("title"),
                    "Value": k.get("formatted_value", str(k.get("value"))),
                    "Type": k.get("tag"),
                    "Formula SQL": k.get("formula_sql")
                })
            pd.DataFrame(kpi_rows).to_excel(writer, sheet_name="KPI Summary", index=False)

            # Top entities sheet if exists
            top_table = spec.get("top_entities_table")
            if top_table and top_table.get("rows"):
                pd.DataFrame(top_table["rows"]).to_excel(writer, sheet_name="Top Entities", index=False)

        return stream.getvalue()

    @classmethod
    def export_csv(cls, df: pd.DataFrame) -> str:
        return df.to_csv(index=False)
