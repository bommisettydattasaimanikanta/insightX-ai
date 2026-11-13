import os
import win32com.client
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_three_point_presentation():
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

    def add_column_card(slide, left, top, width, height, side_heading, points, accent_color=ACCENT_CYAN):
        # Card box
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

        # Text Frame
        tx_box = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.25), width - Inches(0.5), height - Inches(0.4))
        tf = tx_box.text_frame
        tf.word_wrap = True

        # Side Heading
        p_head = tf.paragraphs[0]
        p_head.text = side_heading
        p_head.font.size = Pt(18)
        p_head.font.bold = True
        p_head.font.color.rgb = accent_color
        p_head.space_after = Pt(14)

        # Content lines
        for pt in points:
            p = tf.add_paragraph()
            p.text = "• " + pt
            p.font.size = Pt(14)
            p.font.color.rgb = TEXT_LIGHT
            p.space_after = Pt(10)

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

    # Two Clean Bottom Cards
    add_column_card(
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

    add_column_card(
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
    # SLIDE 2: Problem Statement (3 Points)
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_background(s2)
    add_clean_header(s2, "Problem Statement", "Why traditional data analysis is slow and painful for businesses today.")

    add_column_card(
        s2,
        left=Inches(1.0), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="1. Messy Raw Data",
        points=[
            "Most raw Excel files have missing values, wrong dates, and duplicate rows.",
            "Files must be cleaned before anyone can make charts or reports."
        ],
        accent_color=ACCENT_CYAN
    )

    add_column_card(
        s2,
        left=Inches(4.9), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="2. Slow Manual Work",
        points=[
            "Data analysts waste 80% of their working hours just cleaning spreadsheets.",
            "Important business decisions get delayed by several days or weeks."
        ],
        accent_color=ACCENT_BLUE
    )

    add_column_card(
        s2,
        left=Inches(8.8), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="3. Fake AI Numbers",
        points=[
            "General chatbots like ChatGPT make up fake numbers and calculations.",
            "Managers cannot trust normal AI chatbots for real financial figures."
        ],
        accent_color=ACCENT_GREEN
    )

    s2.notes_slide.notes_text_frame.text = (
        "There are three major industry problems: First, raw data is very messy. Second, data analysts waste 80% of "
        "their time cleaning files manually. Third, generic AI tools like ChatGPT hallucinate fake numbers."
    )

    # ==========================================
    # SLIDE 3: Platform Overview (3 Points)
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_background(s3)
    add_clean_header(s3, "Platform Overview", "What InsightX AI does and how it helps anyone analyze data instantly.")

    add_column_card(
        s3,
        left=Inches(1.0), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="1. Autonomous Analyst",
        points=[
            "Acts as a virtual data analyst that works completely automatically.",
            "Turns raw data into interactive dashboards in under 60 seconds."
        ],
        accent_color=ACCENT_CYAN
    )

    add_column_card(
        s3,
        left=Inches(4.9), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="2. Simple Drag & Drop",
        points=[
            "Just upload any Excel or CSV file without writing code or SQL.",
            "The system automatically fixes formats and builds business charts."
        ],
        accent_color=ACCENT_BLUE
    )

    add_column_card(
        s3,
        left=Inches(8.8), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="3. 100% Accurate Math",
        points=[
            "Core principle: 'Code Computes, AI Explains'.",
            "Real SQL code calculates all totals; AI never guesses arithmetic."
        ],
        accent_color=ACCENT_GREEN
    )

    s3.notes_slide.notes_text_frame.text = (
        "InsightX AI is an autonomous data analyst platform. You drag and drop any dataset, and within 60 seconds "
        "it produces verified charts. Our golden rule is 'Code Computes, AI Explains' – guaranteeing 100% accurate numbers."
    )

    # ==========================================
    # SLIDE 4: System Architecture (3 Points)
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_background(s4)
    add_clean_header(s4, "System Architecture", "How the system is built across Frontend, Backend, and Storage.")

    add_column_card(
        s4,
        left=Inches(1.0), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="1. User Interface",
        points=[
            "Built with React 18, TypeScript, and Tailwind CSS for speed.",
            "Uses Apache ECharts for smooth, clickable, and zoomable charts."
        ],
        accent_color=ACCENT_CYAN
    )

    add_column_card(
        s4,
        left=Inches(4.9), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="2. Backend & DuckDB",
        points=[
            "Built with Python 3.11 and FastAPI for high-speed API connections.",
            "DuckDB database executes analytical SQL queries in milliseconds."
        ],
        accent_color=ACCENT_BLUE
    )

    add_column_card(
        s4,
        left=Inches(8.8), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="3. Safe Data Lake",
        points=[
            "Stores files in fast, compressed, immutable Parquet format.",
            "Built-in security firewall blocks harmful commands like DROP or DELETE."
        ],
        accent_color=ACCENT_GREEN
    )

    s4.notes_slide.notes_text_frame.text = (
        "Our architecture has three layers: A React 18 frontend with Apache ECharts; a Python FastAPI backend "
        "with DuckDB for sub-10ms queries; and a safe Parquet data lake with a security firewall."
    )

    # ==========================================
    # SLIDE 5: Key Features (3 Points)
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_background(s5)
    add_clean_header(s5, "Key Features", "Three powerful capabilities that make data analysis fast and effortless.")

    add_column_card(
        s5,
        left=Inches(1.0), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="1. Auto Data Cleaning",
        points=[
            "Provides a 0 to 100 Data Quality Health Score instantly upon upload.",
            "Automatically fixes dates, removes duplicate rows, and handles nulls."
        ],
        accent_color=ACCENT_CYAN
    )

    add_column_card(
        s5,
        left=Inches(4.9), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="2. Plain English Chat",
        points=[
            "Ask questions like 'What are top 5 products by revenue?' to get charts.",
            "Converts your English question into safe SQL without SQL injection risk."
        ],
        accent_color=ACCENT_BLUE
    )

    add_column_card(
        s5,
        left=Inches(8.8), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="3. 1-Click ML Predictor",
        points=[
            "Trains prediction models (Random Forest & XGBoost) with 1 click.",
            "Includes a What-If slider to test business scenarios before deciding."
        ],
        accent_color=ACCENT_GREEN
    )

    s5.notes_slide.notes_text_frame.text = (
        "The three key features are: Automatic data cleaning with a 0 to 100 score; natural language querying in plain English; "
        "and one-click machine learning with a What-If business simulator."
    )

    # ==========================================
    # SLIDE 6: Technologies Used (3 Points)
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_background(s6)
    add_clean_header(s6, "Technologies Used", "Simple, modern, and reliable tools chosen for speed and accuracy.")

    add_column_card(
        s6,
        left=Inches(1.0), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="1. Frontend Stack",
        points=[
            "React 18 & Vite: For creating a fast, responsive user interface.",
            "TypeScript: Ensures code has no errors and runs smoothly.",
            "Apache ECharts: Renders beautiful interactive business charts."
        ],
        accent_color=ACCENT_CYAN
    )

    add_column_card(
        s6,
        left=Inches(4.9), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="2. Backend & Data",
        points=[
            "Python 3.11 & FastAPI: Handles backend requests quickly.",
            "DuckDB: Ultra-fast in-memory database built for big data analytics.",
            "SQLite: Saves user accounts, workspaces, and history safely."
        ],
        accent_color=ACCENT_BLUE
    )

    add_column_card(
        s6,
        left=Inches(8.8), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="3. AI & Machine Learning",
        points=[
            "Scikit-Learn & XGBoost: Trains fast, accurate prediction models.",
            "Google Gemini AI: Writes simple summaries and explanations.",
            "sqlglot: Validates SQL to block hacking or unwanted modifications."
        ],
        accent_color=ACCENT_GREEN
    )

    s6.notes_slide.notes_text_frame.text = (
        "We used React and Apache ECharts on the frontend; Python FastAPI and DuckDB on the backend; "
        "and Scikit-learn, XGBoost, and Google Gemini for predictive modeling and natural language explanations."
    )

    # ==========================================
    # SLIDE 7: Results & Performance (3 Points)
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_background(s7)
    add_clean_header(s7, "Results & Performance", "Real test results proving high speed, accuracy, and security.")

    add_column_card(
        s7,
        left=Inches(1.0), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="1. 100% SQL Accuracy",
        points=[
            "Tested with 30 realistic business questions (sales, rankings, date ranges).",
            "All 30 out of 30 queries passed perfectly with 100% correct answers."
        ],
        accent_color=ACCENT_GREEN
    )

    add_column_card(
        s7,
        left=Inches(4.9), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="2. 8.2 ms Query Latency",
        points=[
            "Average query execution time is only 8.2 milliseconds using DuckDB.",
            "Dashboards load instantly even when analyzing large datasets."
        ],
        accent_color=ACCENT_CYAN
    )

    add_column_card(
        s7,
        left=Inches(8.8), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="3. < 2.0s Model Training",
        points=[
            "Trains complete predictive models in under 2 seconds on 10,000+ rows.",
            "100% of malicious SQL injection attack attempts were safely blocked."
        ],
        accent_color=ACCENT_BLUE
    )

    s7.notes_slide.notes_text_frame.text = (
        "Our test results are: 100% accuracy on our 30-question benchmark; an average query latency of only "
        "8.2 milliseconds; and sub-2 second machine learning model training."
    )

    # ==========================================
    # SLIDE 8: Future Scope (3 Points)
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_background(s8)
    add_clean_header(s8, "Future Scope", "Upcoming improvements and the positive impact on business teams.")

    add_column_card(
        s8,
        left=Inches(1.0), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="1. Live Streaming Data",
        points=[
            "Connect live data feeds (like IoT sensors or stock markets) using Apache Kafka.",
            "Dashboards will update continuously in real time without refreshing."
        ],
        accent_color=ACCENT_CYAN
    )

    add_column_card(
        s8,
        left=Inches(4.9), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="2. Cloud Connections",
        points=[
            "Connect directly to cloud data warehouses like Snowflake and Google BigQuery.",
            "Enables enterprises to analyze massive company datasets effortlessly."
        ],
        accent_color=ACCENT_BLUE
    )

    add_column_card(
        s8,
        left=Inches(8.8), top=Inches(2.2), width=Inches(3.5), height=Inches(4.5),
        side_heading="3. Voice Commands",
        points=[
            "Ask questions using voice on mobile devices (e.g. 'Show me today's sales').",
            "Cuts 80% of data cleaning time and helps non-programmers make smart decisions."
        ],
        accent_color=ACCENT_GREEN
    )

    s8.notes_slide.notes_text_frame.text = (
        "In the future, we plan to support live data streaming with Kafka, cloud warehouse connections with Snowflake, "
        "and voice querying for mobile devices."
    )

    # ==========================================
    # SLIDE 9: Project Conclusion (SINGLE POINT!)
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_background(s9)
    add_clean_header(s9, "Project Conclusion", "Final takeaway and business impact of InsightX AI.")

    # Single prominent center card
    c9 = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(2.4), Inches(9.733), Inches(4.0))
    c9.fill.solid()
    c9.fill.fore_color.rgb = CARD_BG
    c9.line.color.rgb = CARD_BORDER
    c9.line.width = Pt(1.5)

    bar9 = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.8), Inches(2.4), Inches(9.733), Inches(0.1))
    bar9.fill.solid()
    bar9.fill.fore_color.rgb = ACCENT_CYAN
    bar9.line.color.rgb = ACCENT_CYAN

    tx9 = s9.shapes.add_textbox(Inches(2.2), Inches(2.8), Inches(8.933), Inches(3.2))
    tf9 = tx9.text_frame
    tf9.word_wrap = True

    p_head9 = tf9.paragraphs[0]
    p_head9.text = "Fast, Autonomous & 100% Mathematically Honest Data Intelligence"
    p_head9.font.size = Pt(22)
    p_head9.font.bold = True
    p_head9.font.color.rgb = ACCENT_CYAN
    p_head9.space_after = Pt(20)

    p_body9 = tf9.add_paragraph()
    p_body9.text = (
        "• InsightX AI proves that artificial intelligence can analyze business data with zero hallucinations "
        "by strictly enforcing 'Code Computes, AI Explains' — turning messy raw files into verified interactive "
        "dashboards and predictive machine learning models in under 60 seconds without writing code, cutting 80% "
        "of manual reporting time for business leaders."
    )
    p_body9.font.size = Pt(17)
    p_body9.font.color.rgb = TEXT_LIGHT

    s9.notes_slide.notes_text_frame.text = (
        "In conclusion, InsightX AI proves that business intelligence can be fast and completely free of AI hallucinations "
        "by strictly enforcing 'Code Computes, AI Explains'. It turns messy files into dashboards in under 60 seconds, "
        "saving 80% of data preparation time."
    )

    # ==========================================
    # SLIDE 10: Thank You! (Dedicated Clean Slide)
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_background(s10)

    if os.path.exists(logo_path):
        s10.shapes.add_picture(logo_path, Inches(4.9), Inches(1.2), height=Inches(1.2))

    t10 = s10.shapes.add_textbox(Inches(1.0), Inches(2.7), Inches(11.333), Inches(1.1))
    tf10 = t10.text_frame
    p10 = tf10.paragraphs[0]
    p10.text = "Thank You!"
    p10.font.size = Pt(50)
    p10.font.bold = True
    p10.font.color.rgb = ACCENT_CYAN
    p10.alignment = PP_ALIGN.CENTER

    sub10 = s10.shapes.add_textbox(Inches(1.0), Inches(3.85), Inches(11.333), Inches(0.6))
    tf_sub10 = sub10.text_frame
    psub10 = tf_sub10.paragraphs[0]
    psub10.text = "Questions & Discussion"
    psub10.font.size = Pt(24)
    psub10.font.color.rgb = TEXT_LIGHT
    psub10.alignment = PP_ALIGN.CENTER

    ribbon = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.6), Inches(4.8), Inches(8.133), Inches(1.6))
    ribbon.fill.solid()
    ribbon.fill.fore_color.rgb = CARD_BG
    ribbon.line.color.rgb = CARD_BORDER
    ribbon.line.width = Pt(1.2)

    strip10 = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.6), Inches(4.8), Inches(8.133), Inches(0.06))
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
    pptx_file = build_three_point_presentation()
    convert_pptx_to_pdf(pptx_file)
