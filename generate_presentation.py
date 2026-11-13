import os
import win32com.client
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Executive Color Palette
    BG_DARK = RGBColor(11, 19, 43)        # #0B132B
    CARD_BG = RGBColor(26, 38, 70)        # #1A2646
    CARD_BORDER = RGBColor(56, 80, 130)   # #385082
    CARD_BG_ALT = RGBColor(18, 28, 54)    # #121C36
    ACCENT_CYAN = RGBColor(0, 210, 255)   # #00D2FF
    ACCENT_BLUE = RGBColor(59, 130, 246)  # #3B82F6
    ACCENT_GREEN = RGBColor(16, 185, 129) # #10B981
    ACCENT_AMBER = RGBColor(245, 158, 11) # #F59E0B
    TEXT_WHITE = RGBColor(255, 255, 255)
    TEXT_LIGHT = RGBColor(226, 232, 240)  # #E2E8F0
    TEXT_MUTED = RGBColor(148, 163, 184)  # #94A3B8

    logo_path = os.path.abspath("extracted_media/image1.png")
    dash_img = os.path.abspath("fresh_screenshots/01_dashboard.png")
    pred_img = os.path.abspath("fresh_screenshots/04_predictions.png")

    def set_slide_bg(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.color.rgb = color
        return bg

    def add_header(slide, tag_text, title_text, subtitle_text):
        # Header Tag Pill
        tag_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(3.4), Inches(0.35))
        tag_box.fill.solid()
        tag_box.fill.fore_color.rgb = CARD_BG
        tag_box.line.color.rgb = ACCENT_CYAN
        tag_box.line.width = Pt(1)
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_top = Inches(0.04)
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ACCENT_CYAN
        p_tag.alignment = PP_ALIGN.CENTER

        # Slide Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.6))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE

        # Slide Subtitle
        s_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.4))
        tf_s = s_box.text_frame
        tf_s.word_wrap = True
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle_text
        p_s.font.size = Pt(13)
        p_s.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, title, points, accent_color=ACCENT_CYAN, title_size=16, body_size=12):
        # Card container
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.2)

        # Top accent bar
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent_color
        bar.line.color.rgb = accent_color

        # Card Text Frame
        tx_box = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.18), width - Inches(0.5), height - Inches(0.3))
        tf = tx_box.text_frame
        tf.word_wrap = True

        p_title = tf.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(title_size)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE
        p_title.space_after = Pt(10)

        for pt in points:
            p = tf.add_paragraph()
            p.text = "• " + pt
            p.font.size = Pt(body_size)
            p.font.color.rgb = TEXT_LIGHT
            p.space_after = Pt(6)

        return card

    # ==========================================
    # SLIDE 1: Front / Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1, BG_DARK)

    # University Logo
    if os.path.exists(logo_path):
        s1.shapes.add_picture(logo_path, Inches(0.8), Inches(0.6), height=Inches(0.9))

    # Project Pill
    pill1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.5), Inches(0.4))
    pill1.fill.solid()
    pill1.fill.fore_color.rgb = CARD_BG
    pill1.line.color.rgb = ACCENT_CYAN
    p_pill = pill1.text_frame.paragraphs[0]
    p_pill.text = "INDUSTRIAL TRAINING CAPSTONE PROJECT PRESENTATION"
    p_pill.font.size = Pt(11)
    p_pill.font.bold = True
    p_pill.font.color.rgb = ACCENT_CYAN
    p_pill.alignment = PP_ALIGN.CENTER

    # Project Title
    t_box1 = s1.shapes.add_textbox(Inches(0.8), Inches(2.35), Inches(11.7), Inches(1.1))
    p1 = t_box1.text_frame.paragraphs[0]
    p1.text = "InsightX AI"
    p1.font.size = Pt(46)
    p1.font.bold = True
    p1.font.color.rgb = ACCENT_CYAN

    # Subtitle
    sub_box1 = s1.shapes.add_textbox(Inches(0.8), Inches(3.45), Inches(11.7), Inches(0.6))
    p_sub1 = sub_box1.text_frame.paragraphs[0]
    p_sub1.text = "Autonomous AI Data Analyst & Predictive Decision Intelligence Platform"
    p_sub1.font.size = Pt(20)
    p_sub1.font.color.rgb = TEXT_LIGHT

    # Two Bottom Information Cards
    # Left: Student Details
    add_card(
        s1,
        left=Inches(0.8), top=Inches(4.3), width=Inches(5.7), height=Inches(2.6),
        title="Student Details",
        points=[
            "Presented By: B. Datta Sai Manikanta",
            "University Roll No / Reg No: 72311633",
            "Program: B.Tech Computer Science and Engineering (AI & DS)",
            "Institution: CT University, Ludhiana (Punjab), India"
        ],
        accent_color=ACCENT_CYAN,
        title_size=17,
        body_size=13
    )

    # Right: Industry Training Details
    add_card(
        s1,
        left=Inches(6.8), top=Inches(4.3), width=Inches(5.7), height=Inches(2.6),
        title="Training & Supervisor Details",
        points=[
            "Training Organization: DataValley Pvt. Ltd. (collab with APSCHE)",
            "Internship Supervisor: Mr. Shaik Arshad / Shaik Nazeerb",
            "Core Technologies: FastAPI, React 18, DuckDB, scikit-learn, XGBoost",
            "GitHub: github.com/bommisettydattasaimanikanta/insightX-ai"
        ],
        accent_color=ACCENT_BLUE,
        title_size=17,
        body_size=13
    )

    s1.notes_slide.notes_text_frame.text = (
        "Good morning respected evaluators. My name is B. Datta Sai Manikanta, Registration Number 72311633, "
        "from CT University. Today, I am presenting InsightX AI, an autonomous AI data analyst and decision "
        "intelligence platform developed during my industrial training at DataValley Pvt. Ltd."
    )

    # ==========================================
    # SLIDE 2: Problem Statement & Motivation
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2, BG_DARK)
    add_header(s2, "SLIDE 02 | PROBLEM STATEMENT", "The Analytics Bottleneck & AI Hallucination Risk",
               "Traditional Business Intelligence is too slow, and generic LLMs hallucinate inaccurate numbers.")

    add_card(
        s2,
        left=Inches(0.8), top=Inches(1.95), width=Inches(3.7), height=Inches(4.9),
        title="1. Messy Raw Data",
        points=[
            "Spreadsheets contain missing values, mixed date formats, and duplicates.",
            "Analysts waste 80% of their work hours just cleaning and formatting data.",
            "Manual data preparation delays time-critical business decisions by days."
        ],
        accent_color=ACCENT_AMBER,
        title_size=16, body_size=12
    )

    add_card(
        s2,
        left=Inches(4.8), top=Inches(1.95), width=Inches(3.7), height=Inches(4.9),
        title="2. The Hallucination Risk",
        points=[
            "General-purpose LLMs (like ChatGPT) cannot perform deterministic arithmetic.",
            "Chatbots invent plausible but fake sales figures, percentages, and totals.",
            "In enterprise finance or healthcare, hallucinated data causes severe loss."
        ],
        accent_color=ACCENT_CYAN,
        title_size=16, body_size=12
    )

    add_card(
        s2,
        left=Inches(8.8), top=Inches(1.95), width=Inches(3.7), height=Inches(4.9),
        title="3. High Technical Barrier",
        points=[
            "Business managers cannot write complex SQL queries or Python scripts.",
            "Constant dependency on busy data engineering teams causes delays.",
            "Companies need a self-service tool that delivers trusted answers in seconds."
        ],
        accent_color=ACCENT_BLUE,
        title_size=16, body_size=12
    )

    s2.notes_slide.notes_text_frame.text = (
        "There are three major industry challenges: First, 80% of analyst time is wasted cleaning messy files. "
        "Second, if you feed raw data to generic AI chatbots, they hallucinate fake numbers because LLMs are not calculators. "
        "Third, business managers cannot write SQL or Python. InsightX AI directly addresses all three pain points."
    )

    # ==========================================
    # SLIDE 3: Introduction to InsightX AI
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3, BG_DARK)
    add_header(s3, "SLIDE 03 | PLATFORM OVERVIEW", "Introducing InsightX AI: The Autonomous Analyst",
               "End-to-end data intelligence from raw upload to interactive dashboards and predictions in under 60 seconds.")

    add_card(
        s3,
        left=Inches(0.8), top=Inches(1.95), width=Inches(5.7), height=Inches(2.35),
        title="What is InsightX AI?",
        points=[
            "An autonomous platform automating data cleaning, analytics, and modeling.",
            "Ingests CSV, Excel, Parquet, or connects directly to live SQL databases.",
            "Zero coding required: business users get executive answers immediately."
        ],
        accent_color=ACCENT_CYAN,
        title_size=15, body_size=12
    )

    add_card(
        s3,
        left=Inches(0.8), top=Inches(4.45), width=Inches(5.7), height=Inches(2.4),
        title="Guiding Principle: Code Computes, AI Explains",
        points=[
            "The AI never calculates numbers; all math is executed by DuckDB SQL & SciPy.",
            "The LLM only interprets verified numbers and generates strategic advice.",
            "Transparent provenance badges: [Computed], [ML prediction], [Statistical test]."
        ],
        accent_color=ACCENT_GREEN,
        title_size=15, body_size=12
    )

    # Embed Dashboard Preview Screenshot on right
    if os.path.exists(dash_img):
        # Card frame for picture
        img_card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.95), Inches(5.7), Inches(4.9))
        img_card.fill.solid()
        img_card.fill.fore_color.rgb = CARD_BG
        img_card.line.color.rgb = CARD_BORDER
        img_card.line.width = Pt(1.2)
        s3.shapes.add_picture(dash_img, Inches(6.9), Inches(2.2), width=Inches(5.5))
        # Label below image
        lbl = s3.shapes.add_textbox(Inches(6.9), Inches(6.3), Inches(5.5), Inches(0.4))
        p_lbl = lbl.text_frame.paragraphs[0]
        p_lbl.text = "InsightX AI Live Interactive Executive Dashboard"
        p_lbl.font.size = Pt(11)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = ACCENT_CYAN
        p_lbl.alignment = PP_ALIGN.CENTER

    s3.notes_slide.notes_text_frame.text = (
        "InsightX AI is an autonomous AI analyst. You upload any messy dataset, and within 60 seconds it produces "
        "clean data, an interactive dashboard, and machine learning models. Our core rule is 'Code Computes, AI Explains' – "
        "every number is verified by deterministic SQL code, while the LLM generates plain-English insights."
    )

    # ==========================================
    # SLIDE 4: System Architecture & Workflow
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4, BG_DARK)
    add_header(s4, "SLIDE 04 | SYSTEM ARCHITECTURE", "High-Performance 3-Tier Architecture & Workflow",
               "Built with modern web frameworks, columnar query engines, and immutable Parquet storage.")

    add_card(
        s4,
        left=Inches(0.8), top=Inches(1.95), width=Inches(3.7), height=Inches(4.9),
        title="1. Frontend UI Layer",
        points=[
            "React 18 & Vite: Ultra-responsive, smooth user experience.",
            "TypeScript: Strict type safety preventing runtime crashes.",
            "Apache ECharts: Declarative charts, heatmaps, and trendlines.",
            "Tailwind CSS: High-contrast executive dark mode."
        ],
        accent_color=ACCENT_CYAN,
        title_size=16, body_size=12
    )

    add_card(
        s4,
        left=Inches(4.8), top=Inches(1.95), width=Inches(3.7), height=Inches(4.9),
        title="2. Backend & Compute",
        points=[
            "FastAPI (Python 3.11): High-speed asynchronous REST endpoints.",
            "DuckDB In-Memory: Columnar OLAP engine executing queries in 8.2ms.",
            "sqlglot AST Gate: Blocks dangerous SQL injections and mutations.",
            "Scikit-learn & XGBoost: Real-time predictive modeling."
        ],
        accent_color=ACCENT_BLUE,
        title_size=16, body_size=12
    )

    add_card(
        s4,
        left=Inches(8.8), top=Inches(1.95), width=Inches(3.7), height=Inches(4.9),
        title="3. Storage & Lake Layer",
        points=[
            "Immutable Parquet Lake: Raw uploads are never overwritten.",
            "Versioned Transformation: Full diff, undo, and restore capability.",
            "SQLite Metadata: Manages user auth, workspaces, and audit trails.",
            "Single Semantic Registry: Unifies metrics across the platform."
        ],
        accent_color=ACCENT_GREEN,
        title_size=16, body_size=12
    )

    s4.notes_slide.notes_text_frame.text = (
        "Our architecture has three layers: First, a React 18 and Apache ECharts frontend. "
        "Second, a FastAPI backend with DuckDB that runs SQL queries in just 8 milliseconds, protected by a sqlglot security gate. "
        "Third, an immutable Parquet data lake where raw data is never destroyed, allowing complete version control and rollback."
    )

    # ==========================================
    # SLIDE 5: Core Features & Capabilities
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5, BG_DARK)
    add_header(s5, "SLIDE 05 | CORE CAPABILITIES", "Four Intelligent Pillars of InsightX AI",
               "Automating the complete analytics lifecycle from data hygiene to predictive decision support.")

    add_card(
        s5,
        left=Inches(0.8), top=Inches(1.95), width=Inches(5.7), height=Inches(2.35),
        title="1. Automated Data Cleaning Studio",
        points=[
            "Calculates a real-time Data Quality Health Score (0 to 100%).",
            "Auto-fixes mixed date formats, strips symbols, and handles null values.",
            "Autopilot mode for 1-click speed or Review mode with row-impact previews."
        ],
        accent_color=ACCENT_AMBER,
        title_size=15, body_size=12
    )

    add_card(
        s5,
        left=Inches(6.8), top=Inches(1.95), width=Inches(5.7), height=Inches(2.35),
        title="2. Grounded Semantic Layer",
        points=[
            "Automatically identifies business dimensions, metrics, and KPI definitions.",
            "Single source of truth: ensures dashboards, chat, and reports match 100%.",
            "Eliminates departmental disputes over how metrics (like profit) are defined."
        ],
        accent_color=ACCENT_CYAN,
        title_size=15, body_size=12
    )

    add_card(
        s5,
        left=Inches(0.8), top=Inches(4.45), width=Inches(5.7), height=Inches(2.4),
        title="3. Safe Text-to-SQL Assistant",
        points=[
            "Type plain English questions (e.g., 'What are top 5 regions by profit?').",
            "AST Parser guarantees read-only access: DROP, DELETE, and UPDATE are blocked.",
            "Every metric card contains a 'Show how' link showing the exact SQL formula."
        ],
        accent_color=ACCENT_BLUE,
        title_size=15, body_size=12
    )

    add_card(
        s5,
        left=Inches(6.8), top=Inches(4.45), width=Inches(5.7), height=Inches(2.4),
        title="4. Automated ML & Scenario Simulator",
        points=[
            "1-Click AutoML: Automatically selects best model (Random Forest, XGBoost).",
            "Feature Importance Ranking: Discovers primary drivers of business outcomes.",
            "What-If Simulator: Interactively adjust variables to forecast future revenue."
        ],
        accent_color=ACCENT_GREEN,
        title_size=15, body_size=12
    )

    s5.notes_slide.notes_text_frame.text = (
        "Here are the four pillars: 1) Auto Cleaning with a 0 to 100 quality score. 2) A Unified Semantic Layer "
        "ensuring all metrics stay consistent. 3) Safe Text-to-SQL that lets users ask questions in natural language "
        "without SQL injection risks. 4) Automated ML and What-If simulation for future forecasting."
    )

    # ==========================================
    # SLIDE 6: Key Technologies Used
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6, BG_DARK)
    add_header(s6, "SLIDE 06 | TECHNOLOGY STACK", "Modern, Production-Ready Technology Stack",
               "Engineered with industry-standard, robust technologies across the full stack.")

    add_card(
        s6,
        left=Inches(0.8), top=Inches(1.95), width=Inches(3.7), height=Inches(4.9),
        title="Frontend Engineering",
        points=[
            "React 18: Modern component state management & virtual DOM.",
            "TypeScript: Static typing for zero runtime interface errors.",
            "Vite: Ultra-fast hot module replacement & bundling.",
            "Apache ECharts: Interactive charts with zoom and tooltips.",
            "Tailwind CSS: Responsive, clean layout and dark theme.",
            "Lucide Icons: Modern minimalist icon system."
        ],
        accent_color=ACCENT_CYAN,
        title_size=16, body_size=12
    )

    add_card(
        s6,
        left=Inches(4.8), top=Inches(1.95), width=Inches(3.7), height=Inches(4.9),
        title="Backend & Analytics",
        points=[
            "Python 3.11: High performance asynchronous core runtime.",
            "FastAPI: Modern async REST API framework with docs.",
            "DuckDB: Columnar in-memory analytical SQL engine.",
            "sqlglot: Secure AST parser for SQL validation.",
            "PyArrow & Pandas: Fast, memory-efficient data processing.",
            "SQLAlchemy & SQLite: Persistent metadata and audit logging."
        ],
        accent_color=ACCENT_BLUE,
        title_size=16, body_size=12
    )

    add_card(
        s6,
        left=Inches(8.8), top=Inches(1.95), width=Inches(3.7), height=Inches(4.9),
        title="AI, ML & Quality",
        points=[
            "Scikit-learn: Classification, regression, and preprocessing.",
            "XGBoost: Gradient boosting for high-accuracy predictions.",
            "Statsmodels: Time-series forecasting and trendlines.",
            "Swappable LLMs: Google Gemini, OpenAI, Claude adapters.",
            "ReportLab: Native automated PDF executive summary exporter.",
            "Pytest & Playwright: Comprehensive test automation."
        ],
        accent_color=ACCENT_GREEN,
        title_size=16, body_size=12
    )

    s6.notes_slide.notes_text_frame.text = (
        "We chose industry-standard tools: React 18, TypeScript, and Apache ECharts on the frontend; "
        "FastAPI and DuckDB on the backend for blazing fast columnar queries; and Scikit-learn, XGBoost, and "
        "swappable LLM adapters for machine learning and natural language explanations."
    )

    # ==========================================
    # SLIDE 7: Experimental Results & Benchmarks
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7, BG_DARK)
    add_header(s7, "SLIDE 07 | VALIDATION & BENCHMARKS", "Rigorous Performance Benchmarks & Results",
               "Tested on 30 complex analytical queries and real-world messy enterprise datasets.")

    # 3 Stat Cards on Left
    add_card(
        s7,
        left=Inches(0.8), top=Inches(1.95), width=Inches(3.6), height=Inches(1.5),
        title="100.0% Pass Rate",
        points=["Text-to-SQL Benchmark (30 of 30 queries passed perfectly)."],
        accent_color=ACCENT_GREEN,
        title_size=18, body_size=11
    )

    add_card(
        s7,
        left=Inches(0.8), top=Inches(3.65), width=Inches(3.6), height=Inches(1.5),
        title="8.2 ms Latency",
        points=["Average SQL query execution time using DuckDB in-memory engine."],
        accent_color=ACCENT_CYAN,
        title_size=18, body_size=11
    )

    add_card(
        s7,
        left=Inches(0.8), top=Inches(5.35), width=Inches(3.6), height=Inches(1.5),
        title="< 2.0s AutoML",
        points=["Rapid model training and feature ranking on 10,000+ data rows."],
        accent_color=ACCENT_BLUE,
        title_size=18, body_size=11
    )

    # Detailed Summary Card on Right
    add_card(
        s7,
        left=Inches(4.7), top=Inches(1.95), width=Inches(7.8), height=Inches(4.9),
        title="Key Benchmark Achievements & Security Gates",
        points=[
            "Text-to-SQL Benchmark: 30 analytical test cases covering aggregations, multi-column groupings, time-series windows, and top-K rankings all passed successfully.",
            "Security Verification: 100% of injected SQL attack payloads (DROP TABLE, INSERT, OR 1=1) were trapped and blocked by the AST firewall.",
            "End-to-End Pipeline Efficiency: From raw upload to schema cleaning, semantic mapping, and interactive dashboard synthesis in under 60 seconds.",
            "Non-Destructive Storage: Successfully verified 100% data integrity with immutable Parquet lake versioning, diff calculation, and instant rollback.",
            "High User Satisfaction: Simple, honest labels ([Computed], [ML prediction]) ensure business users trust the numbers without fear of AI hallucination."
        ],
        accent_color=ACCENT_CYAN,
        title_size=16, body_size=12
    )

    s7.notes_slide.notes_text_frame.text = (
        "We tested InsightX AI thoroughly: Our Safe Text-to-SQL engine achieved a 100% pass rate across 30 analytical "
        "queries with an average latency of only 8.2 milliseconds. AutoML models train in under 2 seconds. Furthermore, "
        "our security gate successfully blocked 100% of SQL injection attempts."
    )

    # ==========================================
    # SLIDE 8: Future Enhancements & Business Impact
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8, BG_DARK)
    add_header(s8, "SLIDE 08 | FUTURE SCOPE & IMPACT", "Future Roadmap & Industry Value Proposition",
               "Expanding connectivity and democratizing data intelligence for modern enterprises.")

    add_card(
        s8,
        left=Inches(0.8), top=Inches(1.95), width=Inches(5.7), height=Inches(4.9),
        title="Future Engineering Roadmap",
        points=[
            "Real-Time Stream Processing: Integrating Apache Kafka for live IoT, logistics, and stock market telemetry.",
            "Cloud Warehouse Connectors: Direct connectors for Snowflake, Google BigQuery, AWS Redshift, and Databricks.",
            "Voice-Activated Analytics: Speech-to-SQL conversational interface for executives on mobile devices.",
            "Collaborative Workspaces: Multi-user shared dashboards with live commenting and role-based access control.",
            "Advanced Deep Learning: Adding LSTM and Transformer-based models for complex multivariate forecasting."
        ],
        accent_color=ACCENT_CYAN,
        title_size=16, body_size=12
    )

    add_card(
        s8,
        left=Inches(6.8), top=Inches(1.95), width=Inches(5.7), height=Inches(4.9),
        title="Business & Industry Impact",
        points=[
            "80% Time Reduction: Eliminates days spent manually cleaning spreadsheets and writing repetitive SQL queries.",
            "Democratic Data Access: Enables non-technical managers and domain experts to explore data independently.",
            "100% Verified Truth: Eliminates hallucination risks by relying strictly on deterministic SQL mathematics.",
            "Cost Efficiency: Replaces expensive, rigid proprietary BI software with a modern, flexible AI-driven platform.",
            "Faster Decision Making: Delivers actionable recommendations within minutes instead of waiting on data teams."
        ],
        accent_color=ACCENT_GREEN,
        title_size=16, body_size=12
    )

    s8.notes_slide.notes_text_frame.text = (
        "In the future, we plan to connect with real-time Kafka streams and cloud data warehouses like Snowflake. "
        "The business impact is huge: it cuts manual data preparation time by 80%, democratizes data access for non-programmers, "
        "and completely eliminates AI hallucinations in business reporting."
    )

    # ==========================================
    # SLIDE 9: Conclusion & Thank You Slide
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9, BG_DARK)

    # University Logo
    if os.path.exists(logo_path):
        s9.shapes.add_picture(logo_path, Inches(0.8), Inches(0.6), height=Inches(0.9))

    # Center Thank You Title
    t_box9 = s9.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(1.0))
    p9 = t_box9.text_frame.paragraphs[0]
    p9.text = "Thank You!"
    p9.font.size = Pt(46)
    p9.font.bold = True
    p9.font.color.rgb = ACCENT_CYAN

    # Subtitle
    sub_box9 = s9.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(11.7), Inches(0.5))
    p_sub9 = sub_box9.text_frame.paragraphs[0]
    p_sub9.text = "Questions & Discussion"
    p_sub9.font.size = Pt(22)
    p_sub9.font.color.rgb = TEXT_LIGHT

    # Two Cards on Slide 9
    add_card(
        s9,
        left=Inches(0.8), top=Inches(3.7), width=Inches(5.7), height=Inches(3.2),
        title="Project Summary & Conclusion",
        points=[
            "InsightX AI successfully bridges the gap between raw data and executive decision-making.",
            "Proven principle: 'Code Computes, AI Explains' guarantees accurate mathematical truth.",
            "Delivers automated data cleaning, safe natural language querying, and predictive modeling in < 60s.",
            "Democratizes advanced data science for non-technical business leaders."
        ],
        accent_color=ACCENT_CYAN,
        title_size=16, body_size=12
    )

    add_card(
        s9,
        left=Inches(6.8), top=Inches(3.7), width=Inches(5.7), height=Inches(3.2),
        title="Author & Academic Credentials",
        points=[
            "Author: B. Datta Sai Manikanta",
            "University Roll No / Reg No: 72311633",
            "Program: B.Tech Computer Science and Engineering (AI & DS)",
            "Institution: CT University, Ludhiana (Punjab), India",
            "Training Partner: DataValley Pvt. Ltd. (In collab with APSCHE)",
            "GitHub: github.com/bommisettydattasaimanikanta/insightX-ai"
        ],
        accent_color=ACCENT_BLUE,
        title_size=16, body_size=12
    )

    s9.notes_slide.notes_text_frame.text = (
        "In conclusion, InsightX AI demonstrates that artificial intelligence can be fast, autonomous, and 100% honest. "
        "Thank you very much for your time and guidance. I welcome your questions and feedback."
    )

    output_pptx = os.path.abspath("InsightX_AI_Project_Presentation.pptx")
    prs.save(output_pptx)
    print(f"PowerPoint Presentation saved to: {output_pptx}")
    return output_pptx

def convert_pptx_to_pdf(pptx_path):
    pdf_path = pptx_path.replace(".pptx", ".pdf")
    try:
        ppt_app = win32com.client.Dispatch("PowerPoint.Application")
        pres = ppt_app.Presentations.Open(pptx_path, WithWindow=False)
        pres.SaveAs(pdf_path, 32) # 32 = ppSaveAsPDF
        pres.Close()
        ppt_app.Quit()
        print(f"PDF Presentation successfully exported to: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"Error converting PPTX to PDF: {e}")
        return None

if __name__ == "__main__":
    pptx_file = create_presentation()
    convert_pptx_to_pdf(pptx_file)
