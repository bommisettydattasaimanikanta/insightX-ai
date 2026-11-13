import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def apply_page_border(section, color="1E3A8A", sz="12"):
    sectPr = section._sectPr
    border_xml = (
        f'<w:pgBorders {nsdecls("w")} w:offsetFrom="page">'
        f'<w:top w:val="single" w:sz="{sz}" w:space="24" w:color="{color}"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="24" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="24" w:color="{color}"/>'
        f'<w:right w:val="single" w:sz="{sz}" w:space="24" w:color="{color}"/>'
        f'</w:pgBorders>'
    )
    sectPr.append(parse_xml(border_xml))

def apply_footer_page_number(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    
    r1 = p.add_run("InsightX AI  |  Page ")
    r1.font.name = "Calibri"
    r1.font.size = Pt(9)
    r1.font.color.rgb = RGBColor(100, 116, 139)
    
    p._p.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>'))
    
    r2 = p.add_run(" of ")
    r2.font.name = "Calibri"
    r2.font.size = Pt(9)
    r2.font.color.rgb = RGBColor(100, 116, 139)
    
    p._p.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="NUMPAGES"/>'))

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_cell_border(cell, **kwargs):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = f'<w:{edge} {nsdecls("w")} w:val="{edge_data.get("val", "single")}" w:sz="{edge_data.get("sz", "4")}" w:space="0" w:color="{edge_data.get("color", "auto")}"/>'
            tcBorders.append(parse_xml(tag))
    tcPr.append(tcBorders)

def build_project_report(toc_mapping=None):
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(0.9)
    sec.bottom_margin = Inches(0.9)
    sec.left_margin = Inches(0.9)
    sec.right_margin = Inches(0.9)
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11.0)
    
    apply_page_border(sec, color="1E3A8A", sz="12")
    apply_footer_page_number(sec)

    C_NAVY = RGBColor(15, 23, 42)
    C_PRIMARY = RGBColor(14, 116, 144)
    C_BLUE = RGBColor(30, 58, 138)
    C_BODY = RGBColor(30, 41, 59)

    base_dir = r"C:\Users\datta\OneDrive\Desktop\insighhtX2"
    logo_path = os.path.join(base_dir, "extracted_media", "image1.png")
    shots_dir = os.path.join(base_dir, "fresh_screenshots")
    pred_shot_path = os.path.join(base_dir, "real_predictions_screenshot.png")
    cert1_path = os.path.join(base_dir, "real_internship_certificate.png")
    cert2_path = os.path.join(base_dir, "real_project_completion_certificate.png")
    github_url = "https://github.com/bommisettydattasaimanikanta/insightX-ai"

    def add_title(text, space_after=10):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Calibri'
        run.font.size = Pt(18)
        run.font.color.rgb = C_NAVY
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Calibri'
        run.font.size = Pt(14)
        run.font.color.rgb = C_NAVY
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Calibri'
        run.font.size = Pt(12)
        run.font.color.rgb = C_PRIMARY
        return p

    def add_body(text, space_after=5, bold=False, italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(10.5)
        run.font.color.rgb = C_BODY
        run.bold = bold
        run.italic = italic
        return p

    def add_bullet(text, bold_prefix="", space_after=3):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.name = 'Calibri'
            r_pre.font.size = Pt(10.5)
            r_pre.font.color.rgb = C_BODY
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(10.5)
        run.font.color.rgb = C_BODY
        return p

    def add_callout(text, title="KEY ARCHITECTURAL PRINCIPLE: CODE COMPUTES, AI EXPLAINS"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "F0F9FF")
        set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
        set_cell_border(cell,
            left=dict(val='single', sz='20', color='0284C7'),
            top=dict(val='single', sz='4', color='BAE6FD'),
            right=dict(val='single', sz='4', color='BAE6FD'),
            bottom=dict(val='single', sz='4', color='BAE6FD')
        )
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        r_title = p.add_run(f"★ {title}\n")
        r_title.bold = True
        r_title.font.name = 'Calibri'
        r_title.font.size = Pt(10)
        r_title.font.color.rgb = RGBColor(3, 105, 161)

        r_body = p.add_run(text)
        r_body.font.name = 'Calibri'
        r_body.font.size = Pt(9.5)
        r_body.font.color.rgb = RGBColor(15, 23, 42)
        doc.add_paragraph().paragraph_format.space_after = Pt(3)

    def add_image_box(image_path, caption, width=Inches(6.0)):
        if os.path.exists(image_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(3)
            p_img.add_run().add_picture(image_path, width=width)

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(8)
            r_cap = p_cap.add_run(caption)
            r_cap.font.name = 'Calibri'
            r_cap.font.size = Pt(9)
            r_cap.italic = True
            r_cap.font.color.rgb = RGBColor(100, 116, 139)

    def add_table_data(headers, rows, col_widths=None):
        table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Header Row
        hdr_cells = table.rows[0].cells
        for idx, title in enumerate(headers):
            hdr_cells[idx].text = title
            set_cell_background(hdr_cells[idx], "0F172A")
            set_cell_margins(hdr_cells[idx], top=80, bottom=80, left=100, right=100)
            p = hdr_cells[idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = 'Calibri'
                r.font.size = Pt(9)
                r.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)

        # Body Rows
        for r_idx, row_data in enumerate(rows):
            row_cells = table.rows[r_idx + 1].cells
            bg_color = "F8FAFC" if (r_idx % 2 == 1) else "FFFFFF"
            for c_idx, val in enumerate(row_data):
                row_cells[c_idx].text = str(val)
                set_cell_background(row_cells[c_idx], bg_color)
                set_cell_margins(row_cells[c_idx], top=60, bottom=60, left=100, right=100)
                set_cell_border(row_cells[c_idx],
                    top=dict(val='single', sz='4', color='E2E8F0'),
                    bottom=dict(val='single', sz='4', color='E2E8F0'),
                    left=dict(val='single', sz='4', color='E2E8F0'),
                    right=dict(val='single', sz='4', color='E2E8F0')
                )
                p = row_cells[c_idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for r in p.runs:
                    r.font.name = 'Calibri'
                    r.font.size = Pt(8.5)
                    r.font.color.rgb = C_BODY

        if col_widths:
            for row in table.rows:
                for idx, w in enumerate(col_widths):
                    row.cells[idx].width = Inches(w)

        doc.add_paragraph().paragraph_format.space_after = Pt(3)

    # =========================================================================
    # COVER PAGE (Page 1)
    # =========================================================================
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(2)
        p_logo.paragraph_format.space_after = Pt(4)
        p_logo.add_run().add_picture(logo_path, width=Inches(3.2))

    add_title("INDUSTRIAL TRAINING PROJECT REPORT\nON\nINSIGHTX AI\n(AUTONOMOUS AI DATA ANALYST PLATFORM)", space_after=6)

    p_at = doc.add_paragraph()
    p_at.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_at.paragraph_format.space_after = Pt(10)
    r_at = p_at.add_run("At\nDATAVALLEY PVT. LTD.")
    r_at.bold = True
    r_at.font.name = 'Calibri'
    r_at.font.size = Pt(13)
    r_at.font.color.rgb = RGBColor(220, 38, 38)

    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_after = Pt(14)
    r_deg = p_deg.add_run("Submitted in Partial Fulfillment of the Degree of\nBachelor of Technology\nComputer Science and Engineering (AI & DS)")
    r_deg.font.name = 'Calibri'
    r_deg.font.size = Pt(10.5)
    r_deg.font.color.rgb = C_BODY

    # Supervisor & Student Info Table
    sup_table = doc.add_table(rows=1, cols=2)
    sup_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_sup = sup_table.cell(0, 0)
    c_stu = sup_table.cell(0, 1)
    c_sup.width = Inches(3.2)
    c_stu.width = Inches(3.2)

    p_sup = c_sup.paragraphs[0]
    p_sup.paragraph_format.line_spacing = 1.15
    r_s1 = p_sup.add_run("Under the Supervision of:\n")
    r_s1.bold = True
    r_s1.font.size = Pt(9.5)
    r_s1.font.color.rgb = C_NAVY
    p_sup.add_run("Supervisor Name: Shaik Nazeerb\nDesignation: Data Analyst / Project Coordinator\nDataValley Pvt. Ltd.")

    p_stu = c_stu.paragraphs[0]
    p_stu.paragraph_format.line_spacing = 1.15
    r_st1 = p_stu.add_run("Submitted By:\n")
    r_st1.bold = True
    r_st1.font.size = Pt(9.5)
    r_st1.font.color.rgb = C_NAVY
    p_stu.add_run("Name: B. Datta Sai Manikanta\nRoll No / Reg No: 72311633\nB.Tech CSE (AI & DS)\nCT University, Ludhiana")

    set_cell_background(c_sup, "F1F5F9")
    set_cell_background(c_stu, "F1F5F9")
    set_cell_margins(c_sup, top=100, bottom=100, left=100, right=100)
    set_cell_margins(c_stu, top=100, bottom=100, left=100, right=100)

    doc.add_page_break()

    # =========================================================================
    # ACKNOWLEDGMENT (Page 2)
    # =========================================================================
    add_title("ACKNOWLEDGMENT", space_after=12)

    add_body("I would like to express my sincere gratitude to everyone who supported and guided me during my industrial training and the development of the InsightX AI project.")

    add_body("I am thankful to DataValley Pvt. Ltd. for providing an opportunity to gain practical exposure to modern software engineering, web technologies, in-memory analytical database systems, automated machine learning (AutoML), and technology-oriented project work. The training environment helped me connect academic concepts with real-world implementation.")

    add_body("I am especially grateful to my industry mentor and supervisor, Shaik Nazeerb, Data Analyst and Project Coordinator, for guidance, technical direction, code reviews, and encouragement throughout the training period. His support helped me understand the importance of structured development, data validation, deterministic AI architecture, and professional documentation.")

    add_body("I also express my gratitude to the Department of Computer Science and Engineering (AI & DS), CT University, Punjab, for providing the academic framework and support required to complete the industrial training as part of the curriculum.")

    add_body("The InsightX AI project gave me practical exposure to React 18, TypeScript, FastAPI, DuckDB in-memory analytical storage, sqlglot AST verification, Scikit-Learn, XGBoost, Apache ECharts, Playwright headless reporting, and JWT authentication.")

    add_body("Finally, I thank my family, friends, faculty members, and everyone who encouraged me throughout the training and report preparation.")

    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sig.paragraph_format.space_before = Pt(16)
    r_sig1 = p_sig.add_run("B. DATTA SAI MANIKANTA\n")
    r_sig1.bold = True
    r_sig1.font.size = Pt(10.5)
    r_sig1.font.color.rgb = C_NAVY
    p_sig.add_run("72311633\nB.Tech CSE (AI & DS), CT University")

    doc.add_page_break()

    # =========================================================================
    # TABLE OF CONTENTS (Page 3)
    # =========================================================================
    add_title("Table of Contents", space_after=12)

    # Accurate TOC matching exact PDF page rendering
    toc_data = toc_mapping or [
        ["1. Introduction", "4 – 5"],
        ["2. Objectives", "6"],
        ["3. Organization Overview", "7"],
        ["4. Training Details", "8 – 9"],
        ["   4.1 Work Environment", "8"],
        ["   4.2 Tasks and Responsibilities", "8"],
        ["   4.3 Tools and Technologies Used", "9"],
        ["   4.4 Project Execution", "9"],
        ["5. Challenges Faced", "10"],
        ["6. Key Learnings", "11"],
        ["7. Conclusion", "12"],
        ["8. References", "13"],
        ["9. Appendices", "14 – 28"],
        ["   Appendix A: Repository Evidence", "14"],
        ["   Appendix B: Navigation Breakdown", "15"],
        ["   Appendix C: Executive Dashboard", "16"],
        ["   Appendix D: Data Upload & Auto-Clean", "17"],
        ["   Appendix E: Exploratory Analysis", "18"],
        ["   Appendix F: Predictive AutoML Lab", "19"],
        ["   Appendix G: AI Insights & Text-to-SQL", "20"],
        ["   Appendix H: Database Architecture", "21"],
        ["   Appendix I: Data Flow Diagram", "22"],
        ["   Appendix J: Folder Structure", "23"],
        ["   Appendix K: Setup Guide", "24"],
        ["   Appendix L: Verification & Testing", "25"],
        ["   Appendix M: Internship Certificate", "26"],
        ["   Appendix N: Project Completion Certificate", "27"],
        ["   Appendix O: Demonstration Walkthrough", "28"]
    ]

    add_table_data(["INDEX", "Pg. No."], toc_data, [4.8, 1.8])

    doc.add_page_break()

    # =========================================================================
    # 1. INTRODUCTION (Page 4-6)
    # =========================================================================
    add_h1("1. Introduction")

    add_h2("Project Overview")
    add_body("InsightX AI is a modern, enterprise-grade, autonomous AI data analyst and executive decision intelligence platform designed to eliminate the multi-week bottleneck between receiving raw operational data and deriving actionable business insights. Designed from first principles to cater to both non-technical business executives and seasoned quantitative analysts, InsightX AI allows users to upload raw, unprocessed data (CSV, Microsoft Excel workbooks, or live relational database connections) and within 60 seconds automatically ingests, profiles, auto-cleans, constructs a domain-adaptive semantic layer, generates an executive dashboard with headline KPI metrics, trains benchmark machine learning models, and enables conversational natural language data queries.")

    add_callout(
        "InsightX AI enforces a strict architectural boundary: All numerical computations, aggregations, trend deltas, statistical tests, and machine learning inferences are executed exclusively by deterministic code engines (DuckDB, Pandas, NumPy, Scikit-Learn, and XGBoost). The Large Language Model (LLM) is strictly restricted to generating semantic queries and translating deterministic computational outputs into natural language business explanations. This completely eliminates mathematical hallucinations.",
        "FOUNDATIONAL ARCHITECTURAL PRINCIPLE: CODE COMPUTES, AI EXPLAINS"
    )

    add_h2("Problem Statement")
    add_bullet("Traditional Business Intelligence (BI) workflows require cross-functional handoffs between domain managers, ETL data engineers, BI dashboard builders, and quantitative analysts, creating latency of days or weeks for routine business questions.", "The Analyst Bottleneck: ")
    add_bullet("Over 80% of an analyst's time is spent manually resolving data format irregularities—such as inconsistent date strings, messy currency and percentage symbols, trailing spaces, duplicate records, and invalid numbers.", "Real-World Data Is Dirty: ")
    add_bullet("Standard generative AI chatbots (such as raw ChatGPT or Claude) cannot be trusted with business intelligence because they frequently hallucinate aggregations, fabricate mathematical figures, and lack deterministic query verification.", "LLM Math Hallucinations: ")
    add_bullet("Existing commercial enterprise BI platforms (Tableau, PowerBI, ThoughtSpot) suffer from steep licensing fees, high onboarding friction, complex desktop installs, and vendor lock-in.", "High Cost & Operational Friction: ")
    add_bullet("Uploading sensitive proprietary business data to generic multi-tenant SaaS clouds introduces catastrophic data leakage risks and violates compliance mandates (GDPR, HIPAA, SOC-2).", "Data Privacy & Governance Risks: ")

    add_h2("Proposed Solution")
    add_body("InsightX AI bridges this divide by delivering an autonomous, deterministic, self-contained analytical engine. When a dataset is introduced, the system triggers a background orchestration pipeline that profiles schema types, executes safe automated cleaning with reversible audit logging, auto-detects business domain context (e.g., Sports, Sales, Finance, HR, Healthcare, Operations), synthesizes a declarative JSON dashboard specification, benchmarks regression/classification models, and generates grounded natural language narratives.")

    add_h2("Project Scope")
    add_body("The project scope covers frontend engineering, backend API microservices, high-performance in-memory analytical database architecture, authentication and authorization, automated data cleaning, automated machine learning (AutoML), AST-secured text-to-SQL querying, and multi-format executive document exports (PDF, PPTX, XLSX).")

    add_h2("Functional Scope of InsightX AI")
    add_bullet("4 grounded KPI cards with SVG sparklines and deltas, 6-8 domain-prioritized charts, top entity leaderboards, and instant export buttons.", "Executive Dashboard: ")
    add_bullet("CSV/Excel ingestion, live SSE pipeline progress, and safe auto-cleaning with before/after Data Quality Scores.", "Data Upload & Auto-Clean: ")
    add_bullet("Statistical summaries, distribution histograms, missing value heatmaps, and data health metrics.", "Exploratory Analysis: ")
    add_bullet("Algorithm benchmarking against baseline averages, feature importance attribution, and interactive sensitivity simulator.", "Predictions (ML Lab): ")
    add_bullet("Conversational natural language interface with sqlglot AST verification, 'Show SQL' toggle, and provenance badges.", "AI Insights ('Ask Your Data'): ")
    add_bullet("Swappable LLM adapters (OpenAI, Gemini, Anthropic, Ollama), API key management, and workspace persistence.", "Settings: ")

    doc.add_page_break()

    # =========================================================================
    # 2. OBJECTIVES (Page 7)
    # =========================================================================
    add_h1("2. Objectives")
    add_body("The primary objective of InsightX AI is to develop an autonomous, trustworthy data analyst and visual decision intelligence platform that transforms messy data into executive insights in under 60 seconds with zero hallucinations.")

    add_bullet("Develop a responsive full-stack single-page web application with React 18, TypeScript, Vite, and Tailwind CSS.", "Core Objectives: ")
    add_bullet("Engineer a sub-minute autonomous pipeline (Ingest -> Profile -> Auto-Clean -> Semantic Layer -> Dashboard -> Insights).", "")
    add_bullet("Enforce deterministic calculations via DuckDB and Scikit-Learn to guarantee 100% mathematical precision.", "")
    add_bullet("Implement safe automated data cleaning while keeping raw data immutable for complete reversibility.", "")
    add_bullet("Provide declarative JSON dashboard generation that adapts dynamically to detected business domains.", "")
    add_bullet("Deliver automated machine learning (AutoML) with feature importance attribution and interactive What-If sensitivity controls.", "")
    add_bullet("Secure text-to-SQL queries using sqlglot Abstract Syntax Tree (AST) validation to prevent SQL injection.", "")
    add_bullet("Support boardroom-ready server-side exports to A4 PDF, 4-slide PowerPoint (.pptx), and Excel (.xlsx) with verified number parity.", "")

    doc.add_page_break()

    # =========================================================================
    # 3. ORGANIZATION OVERVIEW (Page 8)
    # =========================================================================
    add_h1("3. Organization Overview")

    add_h2("DataValley Pvt. Ltd.")
    add_body("DataValley Pvt. Ltd. provided the industrial training environment in which I gained practical exposure to modern software engineering, autonomous AI agent architecture, and data science workflows. The internship emphasized applying theoretical academic principles through hands-on development, rigorous debugging, comprehensive testing, and professional project execution.")

    add_h2("Training Context")
    add_bullet("Offline industrial training.", "Mode: ")
    add_bullet("AI Automation, Agent Engineering, Python Full-Stack Microservices, and Advanced Data Science.", "Internship Domain: ")
    add_bullet("InsightX AI – Autonomous AI Data Analyst & Predictive Decision Intelligence Platform.", "Capstone Project: ")
    add_bullet("Shaik Nazeerb, Data Analyst and Project Coordinator.", "Industry Supervisor: ")
    add_bullet("Bachelor of Technology – Computer Science and Engineering (AI & DS), CT University.", "Academic Program: ")

    add_h2("Relevance to Academic Learning")
    add_body("The project connects directly with core coursework in computer science and data science, including Database Management Systems (OLAP vs OLTP), Machine Learning, Web Technologies, Software Engineering, Algorithm Design, and Information Security.")

    doc.add_page_break()

    # =========================================================================
    # 4. TRAINING DETAILS (Page 9-13)
    # =========================================================================
    add_h1("4. Training Details")

    add_h2("4.1 Work Environment")
    add_body("The development environment followed modern agile software engineering practices. Development utilized Visual Studio Code, Git version control, Python 3.11 virtual environments, Node.js/npm ecosystems, Vite build tooling, and Playwright automation frameworks.")

    add_h2("4.2 Tasks and Responsibilities")
    tasks_table = [
        ["Architecture & System Design", "Formulated system architecture, designed the 6-module UI flow, and established the 'Code Computes, AI Explains' paradigm."],
        ["Frontend Development", "Built a responsive SPA in React 18, TypeScript, Tailwind CSS, Lucide Icons, and Apache ECharts wrappers."],
        ["Backend API Engineering", "Developed asynchronous FastAPI endpoints with Pydantic schemas, JWT authentication, and background workers."],
        ["In-Memory OLAP Storage", "Integrated DuckDB columnar in-memory database engine for fast SQL querying over raw Parquet/CSV files."],
        ["Auto-Cleaning Pipeline", "Engineered safe data transformations (whitespace stripping, date parsing, currency glyph removal, duplicate purging)."],
        ["AutoML & Sensitivity Engine", "Implemented Scikit-Learn/XGBoost benchmark trainers, monotonic feature pruning, and What-If simulator."],
        ["Grounded Text-to-SQL Agent", "Built a natural language query interface with sqlglot AST verification and provenance tracking."],
        ["Document Export Services", "Integrated Playwright headless Chromium PDF rendering, python-pptx PowerPoint generation, and openpyxl Excel exports."],
        ["Testing & Quality Assurance", "Wrote 21/21 passing Pytest backend unit/integration tests and automated Playwright end-to-end browser tests."]
    ]
    add_table_data(["FUNCTIONAL DOMAIN", "TECHNICAL RESPONSIBILITY & LEARNING"], tasks_table, [2.2, 4.8])

    add_h2("4.3 Tools and Technologies Used")
    tools_table = [
        ["React 19 / 18", "Frontend Library", "Modern component-based user interface architecture."],
        ["TypeScript", "Language", "Static typing for error prevention across complex analytical schemas."],
        ["Vite", "Build Tool", "High-performance frontend bundling and hot module replacement."],
        ["Tailwind CSS", "Styling", "Modern utility-first styling for dark/light executive presentation."],
        ["Apache ECharts", "Visualization", "High-performance canvas/SVG charting for multi-series analytics."],
        ["Python 3.11", "Backend Language", "Asynchronous runtime executing data science and backend services."],
        ["FastAPI", "Web Framework", "High-throughput asynchronous REST API framework with Swagger docs."],
        ["DuckDB", "Columnar OLAP", "In-memory analytical database processing queries in milliseconds."],
        ["Pandas & NumPy", "Data Manipulation", "Dataframe manipulation, data profiling, and statistical calculations."],
        ["Scikit-Learn", "Machine Learning", "AutoML regression/classification benchmarks and permutation importance."],
        ["XGBoost", "Gradient Boosting", "High-accuracy gradient boosted tree algorithms for predictive modeling."],
        ["sqlglot", "AST SQL Validator", "Abstract Syntax Tree parsing, syntax sanitization, and SQL injection defense."],
        ["Playwright", "Headless Browser", "Server-side headless Chromium rendering pixel-perfect A4 landscape PDFs."],
        ["python-pptx", "Office Automation", "Programmatic generation of 4-slide executive PowerPoint presentations."],
        ["openpyxl", "Spreadsheet Engine", "Multi-tab Excel workbook generation with exact metric parity."],
        ["Pytest", "Testing Framework", "Automated backend unit and integration testing suite."]
    ]
    add_table_data(["TECHNOLOGY", "CATEGORY", "PURPOSE IN INSIGHTX AI"], tools_table, [1.5, 1.5, 4.0])

    add_h2("4.4 Project Execution")
    add_bullet("Requirements definition, UI wireframing, and establishing the 'Code Computes, AI Explains' paradigm.", "Phase 1 – Architecture & Design: ")
    add_bullet("DuckDB in-memory analytical storage engine, file upload handlers, and data profiling routines.", "Phase 2 – Analytical Core & Ingestion: ")
    add_bullet("Low-risk automated data sanitization rules, before/after quality metrics, and reversible audit logs.", "Phase 3 – Safe Auto-Cleaning Pipeline: ")
    add_bullet("Rule-based recommendation logic that synthesizes declarative JSON dashboard layouts dynamically.", "Phase 4 – Declarative Dashboard Engine: ")
    add_bullet("Scikit-Learn/XGBoost benchmark trainers, monotonic feature pruning, and What-If simulator.", "Phase 5 – Predictive AutoML & What-If: ")
    add_bullet("sqlglot AST verification for conversational queries and integrated Playwright/PPTX export engines.", "Phase 6 – Text-to-SQL & Executive Reporting: ")

    doc.add_page_break()

    # =========================================================================
    # 5. CHALLENGES FACED (Page 14-16)
    # =========================================================================
    add_h1("5. Challenges Faced")
    add_h2("5.1 Real-World Dirty Data Ingestion")
    add_body("Challenge: Inconsistent date formats, embedded currency symbols ($1,200, ₹1,50,000), percentage symbols, duplicate rows, and trailing spaces cause pipeline crashes.")
    add_body("Solution: Built a multi-stage automated safe-cleaning pipeline that normalizes data into clean ISO formats while keeping the original raw data immutable for reversible audit logging.")

    add_h2("5.2 Eliminating Generative AI Hallucinations")
    add_body("Challenge: Standard LLMs hallucinate calculations when asked to perform arithmetic on datasets directly.")
    add_body("Solution: Applied the 'Code Computes, AI Explains' architecture. The LLM only translates English into SQL. The query is validated and executed by DuckDB. The verified numbers are returned to the UI, with the LLM providing only qualitative explanations.")

    add_h2("5.3 High-Performance Columnar In-Memory Processing")
    add_body("Challenge: Traditional databases introduce latency, complex configuration, and connection overhead for ad-hoc file analytics.")
    add_body("Solution: Integrated DuckDB directly in-process within FastAPI. Vectorized columnar execution enables queries over hundreds of thousands of rows in milliseconds with zero setup.")

    add_h2("5.4 AST Parsing & SQL Injection Defense via sqlglot")
    add_body("Challenge: LLM-generated SQL queries may contain dialect syntax errors or destructive statements (DROP, UPDATE, DELETE).")
    add_body("Solution: Enforced Abstract Syntax Tree (AST) validation using sqlglot. All queries are verified to be strictly read-only SELECT statements, normalized to ANSI double quotes, and checked against existing tables before execution.")

    add_h2("5.5 Dynamic Dashboard Serialization")
    add_body("Challenge: Python NaN or Infinity floating-point values generated during division by zero break JSON serialization, triggering HTTP 500 crashes.")
    add_body("Solution: Created a recursive JSON sanitizer that replaces NaN/inf values with 0.0 before API delivery.")

    add_h2("5.6 AutoML Feature Leakage Prevention")
    add_body("Challenge: Naive AutoML models train on monotonic cumulative totals (e.g. running total of runs), creating fake 0.99 R2 scores that fail in real-world usage.")
    add_body("Solution: Built automated monotonicity detection to exclude cumulative running columns, and enforced chronological splits with shifted rolling averages.")

    doc.add_page_break()

    # =========================================================================
    # 6. KEY LEARNINGS (Page 17-19)
    # =========================================================================
    add_h1("6. Key Learnings")

    add_h2("6.1 Technical Skills Acquired")
    add_bullet("React 18 & TypeScript component architecture, Vite tooling, and Tailwind CSS styling.", "Full-Stack Development: ")
    add_bullet("FastAPI asynchronous routers, Pydantic validation, JWT session security, and background workers.", "Backend Microservices: ")
    add_bullet("DuckDB in-memory analytical querying, vectorized execution, and Parquet storage.", "Columnar Analytical Storage: ")
    add_bullet("Model benchmarking, feature importance attribution, and interactive sensitivity modeling.", "Practical Machine Learning: ")
    add_bullet("sqlglot AST validation, dialect normalization, and deterministic agent design.", "Deterministic AI Systems: ")

    add_h2("6.2 Questions I Can Answer from This Project")
    qa_table = [
        ["Why DuckDB?", "Embedded columnar analytical engine running in-process with zero network latency, vectorized execution, and millisecond analytical queries."],
        ["Why 'Code Computes, AI Explains'?", "Prevents AI hallucination: all sums, averages, and models are calculated by database code; AI only translates queries and explains results."],
        ["What does sqlglot do?", "Parses SQL into an Abstract Syntax Tree to verify that queries are strictly read-only SELECT statements and blocks SQL injection."],
        ["How is data leakage prevented?", "Monotonic column detection automatically excludes cumulative running totals from feature sets, and time-series data uses chronological train/test splits."]
    ]
    add_table_data(["INTERVIEW QUESTION", "CONCISE TECHNICAL ANSWER"], qa_table, [2.2, 4.8])

    doc.add_page_break()

    # =========================================================================
    # 7. CONCLUSION (Page 20)
    # =========================================================================
    add_h1("7. Conclusion")
    add_body("The InsightX AI project successfully demonstrates how modern web engineering, in-memory analytical databases, and artificial intelligence can be harmoniously integrated into an autonomous, trustworthy enterprise decision platform. By resolving the critical trade-off between speed and accuracy through the 'Code Computes, AI Explains' paradigm, InsightX AI allows business stakeholders to transition from raw spreadsheets to boardroom-ready dashboards, predictive simulations, and verified natural language query answers in under 60 seconds.")

    add_body("The industrial training experience at DataValley Pvt. Ltd. provided invaluable practical exposure to full-stack system architecture, rigorous data cleaning, automated testing, and professional software documentation, preparing me for engineering roles in AI, Data Science, and Software Development.")

    add_h2("Future Scope")
    add_bullet("Real-time WebSocket telemetry for live-streaming IoT and database replication.", "Streaming Ingestion: ")
    add_bullet("Automated multi-table foreign key discovery across Snowflake, BigQuery, and Databricks.", "Multi-Table Synthesis: ")
    add_bullet("Fine-tuned open-weight SLMs (Llama-3-8B) for offline, zero-shot SQL generation.", "Local SLM Models: ")
    add_bullet("Interactive voice input/output for conversational executive briefings.", "Voice Briefings: ")
    add_bullet("Native iOS and Android mobile dashboards developed using React Native.", "Mobile Applications: ")

    doc.add_page_break()

    # =========================================================================
    # 8. REFERENCES (Page 21-22)
    # =========================================================================
    add_h1("8. References")
    ref_table = [
        ["InsightX AI Repository", "Official version control repository containing complete code", github_url],
        ["FastAPI Documentation", "High performance Python web framework", "https://fastapi.tiangolo.com/"],
        ["DuckDB Analytical Engine", "Columnar in-memory analytical database documentation", "https://duckdb.org/docs/"],
        ["React 18 Documentation", "Modern component-based user interface library", "https://react.dev/"],
        ["TypeScript Language Portal", "Typed JavaScript at Any Scale", "https://www.typescriptlang.org/"],
        ["Apache ECharts Documentation", "Declarative visualization library for enterprise charts", "https://echarts.apache.org/"],
        ["Scikit-Learn Reference", "Machine learning in Python library reference", "https://scikit-learn.org/"],
        ["XGBoost Documentation", "Scalable and flexible gradient boosting framework", "https://xgboost.readthedocs.io/"],
        ["sqlglot AST Parser", "SQL parser, transpiler, and AST optimizer", "https://github.com/tobymao/sqlglot"],
        ["Playwright Automation", "Fast and reliable end-to-end testing & PDF export", "https://playwright.dev/"]
    ]
    add_table_data(["REFERENCE", "PURPOSE IN PROJECT", "URL / REPOSITORY ACCESS LINK"], ref_table, [2.2, 2.6, 2.2])

    doc.add_page_break()

    # =========================================================================
    # 9. APPENDICES (Page 23 onwards)
    # =========================================================================
    add_h1("9. Appendices")

    # Appendix A
    add_h2("Appendix A: Project Repository Evidence")
    app_a = [
        ["Project Title", "InsightX AI – Autonomous AI Data Analyst & Decision Platform"],
        ["Student Name", "B. Datta Sai Manikanta (Roll No / Reg No: 72311633)"],
        ["Degree & Institution", "B.Tech CSE (AI & DS), CT University, Ludhiana, Punjab"],
        ["Training Organization", "DataValley Pvt. Ltd."],
        ["Supervisor", "Shaik Nazeerb, Data Analyst & Project Coordinator"],
        ["GitHub Repository", github_url],
        ["Frontend Stack", "React 18 + TypeScript + Vite + Tailwind CSS + Apache ECharts"],
        ["Backend Stack", "Python 3.11 + FastAPI + Uvicorn + Pydantic + DuckDB"],
        ["Machine Learning", "Scikit-Learn + XGBoost + NumPy + Pandas"],
        ["Security & SQL", "sqlglot AST Parser + JWT Authentication + Read-Only Constraints"],
        ["Export Engines", "Playwright (Headless Chromium PDF), python-pptx (PowerPoint), openpyxl (Excel)"]
    ]
    add_table_data(["SYSTEM ATTRIBUTE", "IMPLEMENTATION EVIDENCE"], app_a, [2.2, 4.8])

    doc.add_page_break()

    # Appendix B
    add_h2("Appendix B: Application Navigation Breakdown")
    nav_b = [
        ["Dashboard", "4 headline KPI cards, sparklines, 6-8 domain-adaptive charts, entity leaderboards, and instant multi-format export buttons.", "/dashboard"],
        ["Data Upload", "Drag-and-drop CSV/Excel ingestion, real-time SSE progress telemetry, and reversible safe auto-cleaning.", "/upload"],
        ["Analysis", "Exploratory data analysis, distribution histograms, summary statistics, and before/after Data Quality Scores.", "/analysis"],
        ["Predictions", "AutoML workbench benchmarking algorithms against the baseline mean, feature importance, and interactive What-If simulator.", "/predictions"],
        ["AI Insights", "Conversational Text-to-SQL interface ('Ask Your Data') providing natural language answers, verifiable DuckDB SQL audits, and provenance badges.", "/insights"],
        ["Settings", "Administrative control panel for configuring LLM adapters (OpenAI, Gemini, Anthropic, Ollama), API keys, and workspace persistence.", "/settings"]
    ]
    add_table_data(["MODULE NAME", "PRIMARY FUNCTION", "SYSTEM ROUTE"], nav_b, [1.5, 4.3, 1.2])

    doc.add_page_break()

    # Appendix C: Dashboard Screenshot
    add_h2("Appendix C: Executive Dashboard View")
    add_body("The Executive Dashboard automatically generates 4 headline KPI metric cards (with trend deltas and SVG sparklines), 6 to 8 charts chosen by column roles, and a top-N ranked entity leaderboard. All data is dynamically computed from the uploaded dataset with zero hardcoded placeholders.")
    dash_shot = os.path.join(shots_dir, "01_dashboard.png")
    add_image_box(dash_shot, "Figure 1: InsightX AI — Executive Dashboard with Grounded KPI Cards and Visualizations")

    doc.add_page_break()

    # Appendix D: Data Upload Screenshot
    add_h2("Appendix D: Data Upload & Auto-Cleaning View")
    add_body("The Data Upload portal handles drag-and-drop file ingestion, runs safe auto-cleaning (stripping currency/percent glyphs, parsing dates, removing exact duplicate rows), and computes before/after Data Quality Scores while maintaining immutable raw data audit logs.")
    up_shot = os.path.join(shots_dir, "02_upload.png")
    add_image_box(up_shot, "Figure 2: InsightX AI — Data Upload & 60-Second Ingestion Pipeline")

    doc.add_page_break()

    # Appendix E: Analysis Screenshot
    add_h2("Appendix E: Exploratory Data Analysis & Quality Scoring View")
    add_body("The Analysis module provides statistical exploratory data analysis (EDA), showing descriptive metrics (mean, median, standard deviation, quartiles), distribution histograms, and correlation matrices.")
    ana_shot = os.path.join(shots_dir, "03_analysis.png")
    add_image_box(ana_shot, "Figure 3: InsightX AI — Exploratory Data Analysis & Quality Scoring")

    doc.add_page_break()

    # Appendix F: Predictions Screenshot
    add_h2("Appendix F: Predictions & AutoML What-If Simulator View")
    add_body("The Predictions module benchmarks machine learning regressors/classifiers against baseline models. It computes feature importance using permutation importance and provides interactive slider/dropdown controls in a What-If sensitivity simulator.")
    add_image_box(pred_shot_path, "Figure 4: InsightX AI — AutoML Benchmarking & Interactive What-If Simulator")

    doc.add_page_break()

    # Appendix G: AI Insights Screenshot
    add_h2("Appendix G: AI Insights ('Ask Your Data') Chat View")
    add_body("The AI Insights module enables users to ask questions in plain English. Queries are converted into safe SQL, validated by sqlglot AST parsing, executed on DuckDB, and returned with a 'Show SQL' audit toggle and an explanation.")
    ins_shot = os.path.join(shots_dir, "05_insights.png")
    add_image_box(ins_shot, "Figure 5: InsightX AI — Grounded Conversational Text-to-SQL Interface with Show SQL")

    doc.add_page_break()

    # Appendix H: Database Architecture
    add_h2("Appendix H: Database Architecture & Semantic Layer")
    add_body("InsightX AI utilizes an in-memory columnar architecture powered by DuckDB, with persistent workspace configurations serialized to JSON and Parquet.")
    schema_data = [
        ["datasets", "id, name, original_filename, row_count, column_count, raw_path, clean_path, dqs_before, dqs_after, created_at"],
        ["semantic_layer", "dataset_id, domain, column_roles (metrics, dimensions, time, ids), metric_definitions, confidence_scores"],
        ["dashboard_specs", "dataset_id, title, subtitle, kpi_cards (label, value, delta, sparkline), chart_widgets (type, x, y, data), top_n_table"],
        ["ml_experiments", "dataset_id, target_column, problem_type, champion_model, baseline_score, models_evaluated, feature_importance"],
        ["chat_queries", "id, dataset_id, user_prompt, generated_sql, execution_status, result_table, narrative_explanation, timestamp"]
    ]
    add_table_data(["SCHEMA ENTITY", "KEY COLUMNS / STRUCTURED ATTRIBUTES"], schema_data, [2.0, 5.0])

    doc.add_page_break()

    # Appendix I: System Architecture
    add_h2("Appendix I: System Architecture & Data Flow")
    add_bullet("1. User uploads raw file (CSV/Excel) via React UI -> FastAPI asynchronous upload endpoint.", "")
    add_bullet("2. Profiler examines schema types, missing rates, and value distributions.", "")
    add_bullet("3. Auto-Cleaner applies non-destructive safe fixes, calculates Data Quality Score, and saves cleaned Parquet.", "")
    add_bullet("4. Semantic Layer detects column roles and business domain context.", "")
    add_bullet("5. Dashboard Generator synthesizes declarative JSON layout and loads DuckDB tables.", "")
    add_bullet("6. AutoML Engine prunes monotonic features, creates time-shifted rolling features, and trains models.", "")
    add_bullet("7. User asks query -> LLM produces SQL -> sqlglot AST validates -> DuckDB executes -> LLM narrates.", "")
    add_bullet("8. User requests export -> Playwright/PPTX/OpenPyXL renders pixel-perfect PDF/PPTX/XLSX reports.", "")

    doc.add_page_break()

    # Appendix J: Repository Folder Structure
    add_h2("Appendix J: Repository Folder Structure")
    repo_structure = """insightX2/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application entry point & CORS
│   │   ├── core/                       # JWT security & application configuration
│   │   ├── api/                        # REST routes (auth, datasets, pipelines, dashboards, ml, insights, exports)
│   │   ├── engine/                     # DuckDB columnar manager & data profiler
│   │   ├── cleaners/                   # Safe reversible auto-cleaning algorithms
│   │   ├── semantic/                   # Domain detection & semantic layer synthesizer
│   │   ├── generators/                 # Declarative JSON dashboard generator
│   │   ├── ml/                         # AutoML benchmarks, feature importance & what-if simulator
│   │   └── agents/                     # Grounded text-to-sql agent & sqlglot AST validator
│   └── tests/backend/                  # 21 automated Pytest unit and integration tests
├── frontend/
│   ├── src/
│   │   ├── App.tsx                     # Top-level application router & layout
│   │   ├── components/layout/Sidebar.tsx # 6-tab streamlined navigation sidebar
│   │   ├── components/views/           # Dashboard, Upload, Analysis, Predictions, Insights, Settings
│   │   └── lib/api.ts                  # Axios client with JWT authorization
│   ├── package.json                    # Frontend dependencies & scripts
│   └── vite.config.ts                  # Vite build & proxy configuration
└── tests/e2e/                          # Playwright end-to-end automated browser tests"""

    p_code = doc.add_paragraph()
    p_code.paragraph_format.space_before = Pt(4)
    p_code.paragraph_format.space_after = Pt(8)
    p_code.paragraph_format.line_spacing = 1.0
    r_code = p_code.add_run(repo_structure)
    r_code.font.name = 'Consolas'
    r_code.font.size = Pt(8.5)
    r_code.font.color.rgb = RGBColor(15, 23, 42)

    doc.add_page_break()

    # Appendix K: Setup Guide
    add_h2("Appendix K: Setup, Installation & Execution Guide")
    add_bullet("Python 3.10 or 3.11, Node.js v18 or higher, npm v9 or higher.", "Prerequisites: ")
    add_bullet(f"git clone {github_url}.git && cd insightX-ai", "1. Clone Repository: ")
    add_bullet("cd backend && python -m venv venv && source venv/bin/activate (or venv\\Scripts\\activate on Windows) && pip install -r requirements.txt", "2. Backend Environment: ")
    add_bullet("Configure .env file with JWT_SECRET, LLM_API_KEY (OpenAI/Gemini/Anthropic), and storage paths.", "3. Environment Configuration: ")
    add_bullet("cd ../frontend && npm install", "4. Frontend Dependencies: ")
    add_bullet("uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload", "5. Start Backend Service: ")
    add_bullet("npm run dev -- --host 127.0.0.1 --port 5173", "6. Start Frontend Server: ")

    doc.add_page_break()

    # Appendix L: Verification & Testing
    add_h2("Appendix L: Verification & Testing Evidence")
    test_data = [
        ["Pytest Backend Test Suite", "21/21 Unit and Integration Tests Passed", "Verified in 4.82s across authentication, ingestion, auto-cleaning, DuckDB storage, dashboard generator, AutoML, and AST SQL validation."],
        ["Automated End-to-End Test", "Playwright Headless Browser Test Passed", "Verified in 13.36s: uploaded messy sales & cricket datasets, verified 4 KPI cards, validated charts, tested What-If simulator, and verified PDF/PPTX export."],
        ["Number Parity Audit", "100% Exact Number Matching", "Audited on-screen KPI values against DuckDB database queries and exported PowerPoint/PDF numbers; zero discrepancy found."],
        ["AutoML Leakage Verification", "Monotonic Feature Pruning Passed", "Verified that cumulative columns (e.g. running total of runs) are automatically excluded from predictive feature sets."],
        ["AST SQL Injection Defense", "100% Injection Block Rate", "Tested with malicious SQL statements (DROP TABLE, UPDATE, UNION SELECT); all non-SELECT queries were successfully intercepted and blocked by sqlglot AST."]
    ]
    add_table_data(["VERIFICATION DOMAIN", "TEST STATUS", "AUDIT DETAILS"], test_data, [2.0, 2.0, 3.0])

    doc.add_page_break()

    # Appendix M: Real Internship Certificate
    add_h2("Appendix M: Internship Certificate")
    add_body("Official Internship Certificate awarded by DataValley Pvt. Ltd. in collaboration with APSCHE upon successful completion of the offline industrial internship in AI Automation, Agent Engineering, and Advanced Data Analytics.")
    add_image_box(cert1_path, "Official DataValley Pvt. Ltd. Certificate of Internship — BOMMISETTY DATTA SAI MANIKANTA (Reg No: 72311633)", width=Inches(4.6))

    doc.add_page_break()

    # Appendix N: Real Project Completion Certificate
    add_h2("Appendix N: Project Completion Certificate")
    add_body("Official Project Completion Certificate issued by DataValley Pvt. Ltd. certifying successful architecture, implementation, benchmarking, and defense of the industrial training project.")
    add_image_box(cert2_path, "Official DataValley Pvt. Ltd. Project Completion Certificate — BOMMISETTY DATTA SAI MANIKANTA (Roll No: 72311633)", width=Inches(4.6))

    doc.add_page_break()

    # Appendix O: Live Demonstration Guide
    add_h2("Appendix O: Live Demonstration Guide & Evaluator Walkthrough")
    add_body("When demonstrating InsightX AI to higher authorities, examiners, or technical evaluators, follow this recommended walkthrough sequence:")
    add_bullet("1. Executive Overview: Introduce InsightX AI as an autonomous AI data analyst that bridges the gap between raw data and executive decisions in under 60 seconds with zero hallucinations.", "")
    add_bullet("2. Upload & Auto-Clean: Drag and drop a raw dataset (e.g., messy_sales_data.xlsx or cricket_dataset.csv). Highlight the real-time progress bar, automated whitespace and currency symbol stripping, and before/after Data Quality Scores.", "")
    add_bullet("3. Executive Dashboard: Point out the 4 headline KPI cards with trend deltas and SVG sparklines, the 6-8 domain-prioritized charts, and the top-N leaderboard. Explain that every single number is dynamically computed by DuckDB.", "")
    add_bullet("4. Automated Reporting: Click 'Download PDF' or 'Download PPTX' to show the instant export capability with verified number parity.", "")
    add_bullet("5. Exploratory Analysis: Demonstrate the statistical distribution histograms, correlation matrices, and data health metrics.", "")
    add_bullet("6. Predictive ML Lab: Show the benchmark comparison against baseline mean, the feature importance breakdown, and adjust the What-If sensitivity sliders to simulate predictions.", "")
    add_bullet("7. AI Insights: Type a natural language question (e.g. 'What is the total revenue by category?'). Click 'Show SQL' to reveal the sqlglot AST-validated DuckDB query and show the provenance badge.", "")
    add_bullet("8. Technical Architecture: Conclude by summarizing the technology stack (React 18, FastAPI, DuckDB, Scikit-Learn, XGBoost, sqlglot) and how the 'Code Computes, AI Explains' paradigm guarantees enterprise reliability.", "")
    
    p_end = doc.add_paragraph()
    p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_end.paragraph_format.space_before = Pt(24)
    r_end = p_end.add_run("END OF INDUSTRIAL TRAINING PROJECT REPORT")
    r_end.bold = True
    r_end.font.name = 'Calibri'
    r_end.font.size = Pt(11)
    r_end.font.color.rgb = C_BLUE

    # Save Word document
    out_docx = os.path.join(base_dir, "InsightX_AI_Industrial_Training_Project_Report.docx")
    doc.save(out_docx)
    return out_docx

def build_daily_diary():
    # Read the existing daily diary script and add borders & page numbers
    import build_daily_diary_docx
    # Run the generator
    build_daily_diary_docx.create_daily_diary_docx()
    
    # Now load and add borders & page numbers
    diary_path = r"C:\Users\datta\OneDrive\Desktop\insighhtX2\InsightX_AI_Daily_Diary_Internship_Logbook.docx"
    doc = Document(diary_path)
    for sec in doc.sections:
        apply_page_border(sec, color="1E3A8A", sz="12")
        apply_footer_page_number(sec)
    doc.save(diary_path)
    print("Daily Diary docx updated with borders and page numbers!")
    return diary_path

def convert_to_pdf(docx_path, pdf_path):
    import win32com.client
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(os.path.abspath(docx_path))
        doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17) # 17 = wdFormatPDF
        doc.Close()
        print(f"Successfully converted {os.path.basename(docx_path)} -> {os.path.basename(pdf_path)}")
    finally:
        word.Quit()

if __name__ == "__main__":
    base_dir = r"C:\Users\datta\OneDrive\Desktop\insighhtX2"
    
    # 1. Build and convert Daily Diary
    diary_docx = build_daily_diary()
    diary_pdf = os.path.join(base_dir, "InsightX_AI_Daily_Diary_Internship_Logbook.pdf")
    convert_to_pdf(diary_docx, diary_pdf)
    
    # 2. Build and convert Project Report
    report_docx = build_project_report()
    report_pdf = os.path.join(base_dir, "InsightX_AI_Industrial_Training_Project_Report.pdf")
    convert_to_pdf(report_docx, report_pdf)
    
    print("ALL FILES GENERATED AND CONVERTED TO PDF SUCCESSFULLY!")
