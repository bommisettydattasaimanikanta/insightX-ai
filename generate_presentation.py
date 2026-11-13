import os
import win32com.client
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_clean_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Executive Clean Dark Palette
    BG_COLOR = RGBColor(11, 19, 43)        # #0B132B (Deep Navy)
    CARD_BG = RGBColor(22, 33, 62)         # #16213E (Card background)
    CARD_BORDER = RGBColor(46, 62, 102)    # #2E3E66 (Card border)
    ACCENT_CYAN = RGBColor(0, 210, 255)    # #00D2FF (Primary highlight)
    ACCENT_BLUE = RGBColor(79, 140, 255)   # #4F8CFF (Secondary highlight)
    ACCENT_GREEN = RGBColor(34, 197, 94)   # #22C55E (Success green)
    TEXT_WHITE = RGBColor(255, 255, 255)
    TEXT_LIGHT = RGBColor(226, 232, 240)   # #E2E8F0 (Readable text)
    TEXT_MUTED = RGBColor(148, 163, 184)   # #94A3B8 (Subtitle text)

    logo_path = os.path.abspath("extracted_media/image1.png")

    def set_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.color.rgb = BG_COLOR
        return bg

    def add_clean_header(slide, title_text, subtitle_text):
        t_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.65), Inches(11.333), Inches(0.65))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(28)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE

        s_box = slide.shapes.add_textbox(Inches(1.0), Inches(1.3), Inches(11.333), Inches(0.45))
        tf_s = s_box.text_frame
        tf_s.word_wrap = True
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle_text
        p_s.font.size = Pt(14)
        p_s.font.color.rgb = TEXT_MUTED

        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.8), Inches(11.333), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = CARD_BORDER
        line.line.color.rgb = CARD_BORDER

    def add_grid_card(slide, left, top, width, height, side_heading, points, accent_color=ACCENT_CYAN):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.2)

        strip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(0.08), height)
        strip.fill.solid()
        strip.fill.fore_color.rgb = accent_color
        strip.line.color.rgb = accent_color

        tx_box = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.18), width - Inches(0.45), height - Inches(0.3))
        tf = tx_box.text_frame
        tf.word_wrap = True

        p_head = tf.paragraphs[0]
        p_head.text = side_heading
        p_head.font.size = Pt(17)
        p_head.font.bold = True
        p_head.font.color.rgb = accent_color
        p_head.space_after = Pt(8)

        for pt in points:
            p = tf.add_paragraph()
            p.text = "• " + pt
            p.font.size = Pt(13)
            p.font.color.rgb = TEXT_LIGHT
            p.space_after = Pt(4)

        return card

    # ==========================================
    # SLIDE 1: InsightX AI (Title Slide)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_background(s1)

    if os.path.exists(logo_path):
        s1.shapes.add_picture(logo_path, Inches(1.0), Inches(0.7), height=Inches(0.95))

    t1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(11.3), Inches(1.1))
    p1 = t1.text_frame.paragraphs[0]
    p1.text = "InsightX AI"
    p1.font.size = Pt(46)
    p1.font.bold = True
    p1.font.color.rgb = ACCENT_CYAN

    sub1 = s1.shapes.add_textbox(Inches(1.0), Inches(2.95), Inches(11.3), Inches(0.6))
    psub1 = sub1.text_frame.paragraphs[0]
    psub1.text = "Autonomous AI Data Analyst & Decision Platform"
    psub1.font.size = Pt(22)
    psub1.font.color.rgb = TEXT_LIGHT

    add_grid_card(
        s1,
        left=Inches(1.0), top=Inches(3.9), width=Inches(5.4), height=Inches(2.8),
        side_heading="Student Information",
        points=[
            "Name: B. Datta Sai Manikanta",
            "Registration No: 72311633",
            "Branch: B.Tech CSE (AI & DS)",
            "College: CT University, Ludhiana (Punjab)"
        ],
        accent_color=ACCENT_CYAN
    )

    add_grid_card(
        s1,
        left=Inches(6.9), top=Inches(3.9), width=Inches(5.4), height=Inches(2.8),
        side_heading="Project & Internship Details",
        points=[
            "Training Partner: DataValley Pvt. Ltd. (APSCHE)",
            "Supervisor: Mr. Shaik Arshad / Shaik Nazeerb",
            "Project Type: Capstone Industrial Training",
            "Code: github.com/bommisettydattasaimanikanta/insightX-ai"
        ],
        accent_color=ACCENT_BLUE
    )

    s1.notes_slide.notes_text_frame.text = (
        "Good morning respected professors. My name is B. Datta Sai Manikanta, Registration Number 72311633, "
        "from CT University. Today I will present my project, InsightX AI – an autonomous AI data analyst "
        "platform that turns raw data into interactive dashboards in under 60 seconds."
    )

    # ==========================================
    # SLIDE 2: Problem Statement
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_background(s2)
    add_clean_header(s2, "Problem Statement", "Why traditional data analysis is slow and painful for businesses today.")

    add_grid_card(
        s2,
        left=Inches(1.0), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="1. Messy Data Everywhere",
        points=[
            "Most raw Excel files have missing values, wrong dates, and duplicate rows.",
            "Files must be cleaned before anyone can make charts or reports."
        ],
        accent_color=ACCENT_CYAN
    )

    add_grid_card(
        s2,
        left=Inches(6.9), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="2. Manual Cleaning is Too Slow",
        points=[
            "Data analysts waste 80% of their working hours just cleaning spreadsheets.",
            "Important business decisions get delayed by several days or weeks."
        ],
        accent_color=ACCENT_BLUE
    )

    add_grid_card(
        s2,
        left=Inches(1.0), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="3. Normal AI Gives Wrong Numbers",
        points=[
            "General chatbots like ChatGPT make up fake numbers and calculations.",
            "In business and finance, wrong numbers can lead to huge financial losses."
        ],
        accent_color=ACCENT_CYAN
    )

    add_grid_card(
        s2,
        left=Inches(6.9), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="4. Coding is Hard for Managers",
        points=[
            "Business managers cannot write complex SQL queries or Python code.",
            "They always depend on technical data teams for even small reports."
        ],
        accent_color=ACCENT_BLUE
    )

    s2.notes_slide.notes_text_frame.text = (
        "Every company faces four big problems: First, raw data is very messy. Second, data analysts waste 80% of their "
        "time just cleaning files manually. Third, generic AI tools like ChatGPT hallucinate and make up wrong numbers. "
        "Fourth, managers cannot write SQL or Python code. InsightX AI solves all these problems."
    )

    # ==========================================
    # SLIDE 3: Platform Overview
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_background(s3)
    add_clean_header(s3, "Platform Overview", "What InsightX AI does and how it helps anyone analyze data instantly.")

    add_grid_card(
        s3,
        left=Inches(1.0), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="1. What is InsightX AI?",
        points=[
            "An autonomous platform that does the complete job of a data analyst.",
            "Turns raw data into clean charts and predictions in under 60 seconds."
        ],
        accent_color=ACCENT_CYAN
    )

    add_grid_card(
        s3,
        left=Inches(6.9), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="2. Simple Drag & Drop",
        points=[
            "Just upload any Excel or CSV file without writing a single line of code.",
            "The platform automatically reads columns, cleans errors, and builds charts."
        ],
        accent_color=ACCENT_BLUE
    )

    add_grid_card(
        s3,
        left=Inches(1.0), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="3. Accurate Numbers (No Guessing)",
        points=[
            "Our core rule: 'Code Computes, AI Explains'.",
            "Real SQL code calculates all totals and averages; the AI never guesses math."
        ],
        accent_color=ACCENT_GREEN
    )

    add_grid_card(
        s3,
        left=Inches(6.9), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="4. Clear English Explanations",
        points=[
            "The AI explains every chart and trend in simple, understandable English.",
            "Managers get clear recommendations on how to improve business results."
        ],
        accent_color=ACCENT_CYAN
    )

    s3.notes_slide.notes_text_frame.text = (
        "InsightX AI is an autonomous data analyst platform. You simply drag and drop any Excel or CSV file. "
        "Within 60 seconds, it cleans the data, runs real SQL calculations, and builds an interactive dashboard. "
        "Our golden rule is 'Code Computes, AI Explains' – so numbers are 100% accurate, and the AI explains them in plain English."
    )

    # ==========================================
    # SLIDE 4: System Architecture
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_background(s4)
    add_clean_header(s4, "System Architecture", "How the system is built across Frontend, Backend, and Storage.")

    add_grid_card(
        s4,
        left=Inches(1.0), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="1. User Interface (Frontend)",
        points=[
            "Built with React 18, TypeScript, and Tailwind CSS for a modern dark look.",
            "Uses Apache ECharts for smooth, interactive charts with click and zoom."
        ],
        accent_color=ACCENT_CYAN
    )

    add_grid_card(
        s4,
        left=Inches(6.9), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="2. Processing Engine (Backend)",
        points=[
            "Built with Python 3.11 and FastAPI for high-speed API connections.",
            "Uses DuckDB database to execute analytical SQL queries in milliseconds."
        ],
        accent_color=ACCENT_BLUE
    )

    add_grid_card(
        s4,
        left=Inches(1.0), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="3. Safe Data Storage (Data Lake)",
        points=[
            "Stores files in fast, compressed Parquet format.",
            "Original files are never deleted or modified; full undo and restore is supported."
        ],
        accent_color=ACCENT_GREEN
    )

    add_grid_card(
        s4,
        left=Inches(6.9), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="4. Built-in Security Firewall",
        points=[
            "Checks every SQL query before running it on the database.",
            "Blocks harmful commands like DROP, DELETE, or UPDATE to protect your data."
        ],
        accent_color=ACCENT_CYAN
    )

    s4.notes_slide.notes_text_frame.text = (
        "Our architecture has three main parts: A React 18 frontend with Apache ECharts for interactive visualizations; "
        "a Python FastAPI backend with DuckDB that calculates queries in just a few milliseconds; and a safe Parquet data lake "
        "where original files are never overwritten. A security parser automatically blocks any dangerous SQL commands."
    )

    # ==========================================
    # SLIDE 5: Key Features
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_background(s5)
    add_clean_header(s5, "Key Features", "Four powerful capabilities that make data analysis fast and effortless.")

    add_grid_card(
        s5,
        left=Inches(1.0), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="1. Automatic Data Cleaning",
        points=[
            "Gives a 0 to 100 Data Quality Health Score instantly upon upload.",
            "Automatically fixes date formats, removes duplicates, and fills missing values."
        ],
        accent_color=ACCENT_CYAN
    )

    add_grid_card(
        s5,
        left=Inches(6.9), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="2. Ask Questions in Plain English",
        points=[
            "Type questions like 'What are top 5 products by revenue?' to get instant answers.",
            "Converts your English question into safe SQL and creates charts automatically."
        ],
        accent_color=ACCENT_BLUE
    )

    add_grid_card(
        s5,
        left=Inches(1.0), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="3. 1-Click Machine Learning",
        points=[
            "Trains prediction models (Random Forest & XGBoost) with a single button click.",
            "Shows which factors (like price or discount) most strongly drive sales."
        ],
        accent_color=ACCENT_GREEN
    )

    add_grid_card(
        s5,
        left=Inches(6.9), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="4. What-If Business Simulator",
        points=[
            "Move sliders to test scenarios like 'What if we increase discount by 5%?'.",
            "Instantly forecasts the impact on sales and profit before making real changes."
        ],
        accent_color=ACCENT_CYAN
    )

    s5.notes_slide.notes_text_frame.text = (
        "Here are the four key features: First, automatic data cleaning with a 0 to 100 quality score. "
        "Second, natural language chat where you can ask questions in plain English. Third, one-click machine learning "
        "to forecast future trends. Fourth, an interactive what-if simulator to test business decisions before applying them."
    )

    # ==========================================
    # SLIDE 6: Technologies Used
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_background(s6)
    add_clean_header(s6, "Technologies Used", "Simple, modern, and reliable tools chosen for speed and accuracy.")

    add_grid_card(
        s6,
        left=Inches(1.0), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="1. Frontend Technologies",
        points=[
            "React 18 & Vite: For creating a fast, responsive user interface.",
            "TypeScript: Ensures code has no errors and runs smoothly.",
            "Apache ECharts: Renders beautiful interactive business charts."
        ],
        accent_color=ACCENT_CYAN
    )

    add_grid_card(
        s6,
        left=Inches(6.9), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="2. Backend & Data Engine",
        points=[
            "Python 3.11 & FastAPI: Handles backend requests quickly.",
            "DuckDB: Ultra-fast in-memory database built for big data analytics.",
            "SQLite: Saves user accounts, workspaces, and history."
        ],
        accent_color=ACCENT_BLUE
    )

    add_grid_card(
        s6,
        left=Inches(1.0), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="3. Machine Learning & AI",
        points=[
            "Scikit-Learn & XGBoost: Trains fast, accurate prediction models.",
            "Google Gemini AI: Writes simple summaries and business insights.",
            "sqlglot: Validates SQL to block hacking or unwanted modifications."
        ],
        accent_color=ACCENT_GREEN
    )

    add_grid_card(
        s6,
        left=Inches(6.9), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="4. Export & Reports",
        points=[
            "ReportLab: Downloads a 1-page executive summary PDF with 1 click.",
            "Jupyter Notebook: Exports complete Python code for data scientists.",
            "Pytest: Automated test suite ensuring everything works reliably."
        ],
        accent_color=ACCENT_CYAN
    )

    s6.notes_slide.notes_text_frame.text = (
        "We used proven technologies: React and Apache ECharts on the frontend for smooth charts; "
        "Python FastAPI and DuckDB on the backend for ultra-fast calculations; Scikit-learn and XGBoost for predictions; "
        "and Google Gemini to explain the insights in simple English."
    )

    # ==========================================
    # SLIDE 7: Results & Performance
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_background(s7)
    add_clean_header(s7, "Results & Performance", "Real test results proving high speed, accuracy, and security.")

    add_grid_card(
        s7,
        left=Inches(1.0), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="1. 100% Accuracy on SQL Benchmark",
        points=[
            "Tested with 30 realistic business questions (sales, rankings, date ranges).",
            "All 30 out of 30 queries passed perfectly with 100% correct answers."
        ],
        accent_color=ACCENT_GREEN
    )

    add_grid_card(
        s7,
        left=Inches(6.9), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="2. Blazing Fast Speed (8.2 ms)",
        points=[
            "Average query execution time is only 8.2 milliseconds using DuckDB.",
            "Dashboards load instantly even when analyzing large datasets."
        ],
        accent_color=ACCENT_CYAN
    )

    add_grid_card(
        s7,
        left=Inches(1.0), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="3. Sub-2 Second Machine Learning",
        points=[
            "Trains complete predictive models in under 2 seconds on 10,000+ rows.",
            "Instantly ranks which factors most heavily impact business outcomes."
        ],
        accent_color=ACCENT_BLUE
    )

    add_grid_card(
        s7,
        left=Inches(6.9), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="4. 100% Secure Against Attacks",
        points=[
            "All SQL injection attack attempts were detected and blocked by the parser.",
            "Original data remained 100% safe and intact with zero accidental deletes."
        ],
        accent_color=ACCENT_GREEN
    )

    s7.notes_slide.notes_text_frame.text = (
        "We tested the platform rigorously: Our SQL query engine achieved 100% accuracy on all 30 benchmark questions. "
        "Thanks to DuckDB, queries take just 8 milliseconds. Machine learning models train in under 2 seconds, "
        "and 100% of malicious SQL injections were blocked safely."
    )

    # ==========================================
    # SLIDE 8: Future Scope
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_background(s8)
    add_clean_header(s8, "Future Scope", "Upcoming improvements and the positive impact on business teams.")

    add_grid_card(
        s8,
        left=Inches(1.0), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="1. Live Streaming Data",
        points=[
            "Connect live data feeds (like IoT sensors or stock markets) using Apache Kafka.",
            "Dashboards will update continuously in real time without refreshing."
        ],
        accent_color=ACCENT_CYAN
    )

    add_grid_card(
        s8,
        left=Inches(6.9), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="2. Cloud Warehouse Connectors",
        points=[
            "Connect directly to cloud data warehouses like Snowflake and Google BigQuery.",
            "Enables enterprises to analyze petabytes of company data effortlessly."
        ],
        accent_color=ACCENT_BLUE
    )

    add_grid_card(
        s8,
        left=Inches(1.0), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="3. Voice-Activated Queries",
        points=[
            "Ask questions using voice on mobile devices (e.g. 'Show me today's sales').",
            "Makes it easy for busy managers to check metrics while traveling."
        ],
        accent_color=ACCENT_GREEN
    )

    add_grid_card(
        s8,
        left=Inches(6.9), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="4. Big Time & Cost Savings",
        points=[
            "Saves 80% of data cleaning time and cuts reliance on expensive software.",
            "Helps non-technical teams make smarter decisions based on real data."
        ],
        accent_color=ACCENT_CYAN
    )

    s8.notes_slide.notes_text_frame.text = (
        "In the future, we plan to connect live streaming data with Apache Kafka, add cloud connections like Snowflake "
        "and BigQuery, and introduce voice search. InsightX AI cuts 80% of data preparation time and helps anyone "
        "make data-backed business decisions."
    )

    # ==========================================
    # SLIDE 9: Project Conclusion (Dedicated Slide)
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_background(s9)
    add_clean_header(s9, "Project Conclusion", "Summary of key project achievements, business value, and reliability.")

    add_grid_card(
        s9,
        left=Inches(1.0), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="1. Fast & Fully Autonomous",
        points=[
            "Turns raw, messy files into interactive dashboards and ML models in < 60 seconds.",
            "Eliminates the need for manual spreadsheet cleaning and complex SQL writing."
        ],
        accent_color=ACCENT_CYAN
    )

    add_grid_card(
        s9,
        left=Inches(6.9), top=Inches(2.2), width=Inches(5.4), height=Inches(2.1),
        side_heading="2. Zero AI Hallucinations",
        points=[
            "Our core principle 'Code Computes, AI Explains' guarantees 100% accurate math.",
            "All metrics are calculated by deterministic SQL queries, never guessed by AI."
        ],
        accent_color=ACCENT_GREEN
    )

    add_grid_card(
        s9,
        left=Inches(1.0), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="3. Enterprise-Ready Security",
        points=[
            "Keeps original raw data safe with immutable, versioned Parquet lake storage.",
            "Built-in AST firewall successfully blocks all harmful SQL queries and injection attacks."
        ],
        accent_color=ACCENT_BLUE
    )

    add_grid_card(
        s9,
        left=Inches(6.9), top=Inches(4.6), width=Inches(5.4), height=Inches(2.1),
        side_heading="4. Real Business Value",
        points=[
            "Reduces data preparation and reporting time by 80% across business teams.",
            "Empowers non-technical managers to make fast, reliable, data-backed decisions."
        ],
        accent_color=ACCENT_CYAN
    )

    s9.notes_slide.notes_text_frame.text = (
        "In conclusion, InsightX AI proves that data analytics can be autonomous, lightning-fast, and 100% mathematically honest. "
        "By enforcing 'Code Computes, AI Explains', we eliminate AI hallucinations. The platform saves 80% of data preparation time "
        "and enables non-technical managers to make smart decisions with confidence."
    )

    # ==========================================
    # SLIDE 10: Thank You! (Dedicated Clean Slide)
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_background(s10)

    # University Logo centered on Slide 10
    if os.path.exists(logo_path):
        s10.shapes.add_picture(logo_path, Inches(4.9), Inches(1.2), height=Inches(1.2))

    # Center Thank You Title
    t10 = s10.shapes.add_textbox(Inches(1.0), Inches(2.7), Inches(11.333), Inches(1.1))
    tf10 = t10.text_frame
    p10 = tf10.paragraphs[0]
    p10.text = "Thank You!"
    p10.font.size = Pt(50)
    p10.font.bold = True
    p10.font.color.rgb = ACCENT_CYAN
    p10.alignment = PP_ALIGN.CENTER

    # Subtitle
    sub10 = s10.shapes.add_textbox(Inches(1.0), Inches(3.85), Inches(11.333), Inches(0.6))
    tf_sub10 = sub10.text_frame
    psub10 = tf_sub10.paragraphs[0]
    psub10.text = "Questions & Discussion"
    psub10.font.size = Pt(24)
    psub10.font.color.rgb = TEXT_LIGHT
    psub10.alignment = PP_ALIGN.CENTER

    # Clean Center Project Ribbon / Box
    ribbon = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.6), Inches(4.8), Inches(8.133), Inches(1.6))
    ribbon.fill.solid()
    ribbon.fill.fore_color.rgb = CARD_BG
    ribbon.line.color.rgb = CARD_BORDER
    ribbon.line.width = Pt(1.2)

    strip10 = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.6), Inches(4.8), Inches(8.133), Inches(0.06))
    strip10.fill.solid()
    strip10.fill.fore_color.rgb = ACCENT_CYAN
    strip10.line.color.rgb = ACCENT_CYAN

    tx_ribbon = s10.shapes.add_textbox(Inches(2.8), Inches(5.0), Inches(7.733), Inches(1.2))
    tf_rib = tx_ribbon.text_frame
    tf_rib.word_wrap = True

    p_r1 = tf_rib.paragraphs[0]
    p_r1.text = "InsightX AI: Autonomous AI Data Analyst & Decision Platform"
    p_r1.font.size = Pt(15)
    p_r1.font.bold = True
    p_r1.font.color.rgb = TEXT_WHITE
    p_r1.alignment = PP_ALIGN.CENTER
    p_r1.space_after = Pt(6)

    p_r2 = tf_rib.add_paragraph()
    p_r2.text = "Official GitHub Repository: https://github.com/bommisettydattasaimanikanta/insightX-ai"
    p_r2.font.size = Pt(13)
    p_r2.font.color.rgb = ACCENT_CYAN
    p_r2.alignment = PP_ALIGN.CENTER

    s10.notes_slide.notes_text_frame.text = (
        "Thank you very much for your valuable time and attention. I am now open to your questions, "
        "feedback, and discussion."
    )

    output_pptx = os.path.abspath("InsightX_AI_Project_Presentation.pptx")
    prs.save(output_pptx)
    print(f"Presentation saved to: {output_pptx}")
    return output_pptx

def convert_pptx_to_pdf(pptx_path):
    pdf_path = pptx_path.replace(".pptx", ".pdf")
    try:
        ppt_app = win32com.client.Dispatch("PowerPoint.Application")
        pres = ppt_app.Presentations.Open(pptx_path, WithWindow=False)
        pres.SaveAs(pdf_path, 32) # 32 = ppSaveAsPDF
        pres.Close()
        ppt_app.Quit()
        print(f"PDF successfully exported to: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"Error converting PPTX to PDF: {e}")
        return None

if __name__ == "__main__":
    pptx_file = build_clean_presentation()
    convert_pptx_to_pdf(pptx_file)
