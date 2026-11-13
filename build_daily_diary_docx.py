import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_daily_diary_docx():
    doc = Document()

    # Margins (0.8 inch for clean logbook layout)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    C_NAVY = RGBColor(15, 23, 42)
    C_BLUE = RGBColor(30, 58, 138)
    C_RED = RGBColor(220, 38, 38)
    C_BODY = RGBColor(30, 41, 59)
    C_MUTED = RGBColor(71, 85, 105)

    base_dir = r"C:\Users\datta\OneDrive\Desktop\insighhtX2"
    logo_path = os.path.join(base_dir, "extracted_media", "image1.png")

    # Header with Logo
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(0)
        p_logo.paragraph_format.space_after = Pt(4)
        p_logo.add_run().add_picture(logo_path, width=Inches(3.2))

    p_h1 = doc.add_paragraph()
    p_h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_h1.paragraph_format.space_before = Pt(2)
    p_h1.paragraph_format.space_after = Pt(2)
    r_h1 = p_h1.add_run("CT UNIVERSITY, LUDHIANA (PUNJAB)\nSCHOOL OF ENGINEERING & TECHNOLOGY\nDEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\n(ARTIFICIAL INTELLIGENCE & DATA SCIENCE)")
    r_h1.bold = True
    r_h1.font.name = 'Calibri'
    r_h1.font.size = Pt(12)
    r_h1.font.color.rgb = C_BLUE

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(2)
    r_t = p_title.add_run("DAILY DIARY / INTERNSHIP TRAINING LOG BOOK\nOFFLINE SHORT-TERM INDUSTRIAL TRAINING ON AI AUTOMATION & AGENT ENGINEERING\n(18 JUNE 2026 – 14 AUGUST 2026)")
    r_t.bold = True
    r_t.font.name = 'Calibri'
    r_t.font.size = Pt(13)
    r_t.font.color.rgb = C_NAVY

    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_before = Pt(4)
    p_proj.paragraph_format.space_after = Pt(12)
    r_cp = p_proj.add_run("CAPSTONE PROJECT:\nInsightX AI: Autonomous AI Data Analyst & Predictive Decision Intelligence Platform")
    r_cp.bold = True
    r_cp.font.name = 'Calibri'
    r_cp.font.size = Pt(12)
    r_cp.font.color.rgb = C_RED

    # Student & Supervisor Table
    info_table = doc.add_table(rows=1, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_stu = info_table.cell(0, 0)
    c_sup = info_table.cell(0, 1)
    c_stu.width = Inches(3.4)
    c_sup.width = Inches(3.4)

    p_s = c_stu.paragraphs[0]
    p_s.paragraph_format.line_spacing = 1.15
    r_s_head = p_s.add_run("SUBMITTED BY:\n")
    r_s_head.bold = True
    r_s_head.font.size = Pt(10)
    r_s_head.font.color.rgb = C_BLUE
    p_s.add_run("Name: B. Datta Sai Manikanta\nUniversity Roll No / Reg No: 72311633\nB.Tech CSE (AI & DS)\nCT University, Ludhiana")

    p_u = c_sup.paragraphs[0]
    p_u.paragraph_format.line_spacing = 1.15
    r_u_head = p_u.add_run("SUPERVISED BY:\n")
    r_u_head.bold = True
    r_u_head.font.size = Pt(10)
    r_u_head.font.color.rgb = C_BLUE
    p_u.add_run("Mr. Shaik Arshad / Shaik Nazeerb\nProject Coordinator & Data Analyst\nDataValley India Pvt. Ltd.\n(In Collaboration with APSCHE)")

    set_cell_background(c_stu, "F1F5F9")
    set_cell_background(c_sup, "F1F5F9")
    set_cell_margins(c_stu, top=100, bottom=100, left=120, right=120)
    set_cell_margins(c_sup, top=100, bottom=100, left=120, right=120)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    def add_day_entry(date_str, obj, summary, skills, challenges, solutions, conclusion):
        # Date Header
        p_date = doc.add_paragraph()
        p_date.paragraph_format.space_before = Pt(12)
        p_date.paragraph_format.space_after = Pt(4)
        p_date.paragraph_format.keep_with_next = True
        r_d = p_date.add_run(date_str)
        r_d.bold = True
        r_d.font.name = 'Calibri'
        r_d.font.size = Pt(11.5)
        r_d.font.color.rgb = C_BLUE

        fields = [
            ("1. Objectives of the Day: ", obj),
            ("2. Summary of Work Done / Tasks Performed: ", summary),
            ("3. Skills/Concepts Learned: ", skills),
            ("4. Challenges Faced: ", challenges),
            ("5. Solutions/Support Received: ", solutions),
            ("6. Conclusion/Reflection: ", conclusion),
        ]

        for label, text in fields:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            r_lbl = p.add_run(label)
            r_lbl.bold = True
            r_lbl.font.name = 'Calibri'
            r_lbl.font.size = Pt(10)
            r_lbl.font.color.rgb = C_NAVY

            r_txt = p.add_run(text)
            r_txt.font.name = 'Calibri'
            r_txt.font.size = Pt(10)
            r_txt.font.color.rgb = C_BODY

    # Entries: 18 June to 31 July (AI & Agent Training)
    entries = [
        ("18 June 2026",
         "To understand the internship schedule, the Datavalley training structure, and the basics of AI Automation and Agentic AI.",
         "Attended the orientation at Datavalley, learned about the internship program and its modules, and studied what AI Automation and Agentic AI mean, with real-world uses such as business process automation and customer support.",
         "The difference between AI models, AI agents, and agentic AI systems, and an overview of Large Language Models (LLMs) and Generative AI.",
         "Telling apart a simple AI model from an autonomous agent that plans and uses tools.",
         "Followed the trainer's explanations and compared each concept with everyday applications.",
         "Gained a clear starting point for the internship and understood the topics to be covered in the coming weeks."),

        ("19 June 2026",
         "To learn the fundamentals of Prompt Engineering for working with LLMs such as ChatGPT, Claude, and Gemini.",
         "Practised writing prompts with clear instructions, context, and constraints, and compared the quality of responses for different prompt styles.",
         "Clear instruction design, context management, and the effect of prompt wording on output quality.",
         "Vague prompts produced inconsistent answers.",
         "Added context, the expected format, and examples to the prompts and re-ran them to compare the outputs.",
         "Understood that the quality of the prompt directly decides the quality of the AI output."),

        ("22 June 2026",
         "To apply advanced prompting techniques for more reliable AI outputs.",
         "Worked with role-based prompting (researcher, analyst, support assistant), step-by-step instructions, and few-shot examples, and tested how each changed the responses.",
         "Role-based prompting, structured prompting, and improving prompts through iteration.",
         "Keeping long prompts focused without losing important instructions.",
         "Broke long prompts into labelled parts and refined them over several attempts.",
         "Improved my ability to get consistent, well-structured results from AI models."),

        ("23 June 2026",
         "To understand the Natural Language Processing (NLP) concepts used in AI systems.",
         "Studied tokenization, text understanding, and intent recognition, and reviewed how NLP supports chatbots and document analysis.",
         "Basics of NLP, tokens, and how text is prepared for AI processing.",
         "Understanding how a model interprets context and meaning rather than just individual words.",
         "Worked through short text examples with the trainer to see how text is processed step by step.",
         "Built a base for the upcoming work on structured outputs and retrieval."),

        ("24 June 2026",
         "To learn how AI models return structured outputs and call external tools.",
         "Practised getting responses in JSON format and studied function calling, where a model triggers a tool or API instead of only writing text.",
         "JSON structure, structured outputs for system integration, and the basics of function calling.",
         "Small formatting mistakes made some JSON outputs unusable.",
         "Specified the exact JSON fields in the prompt and validated each output.",
         "Understood how structured outputs let AI connect with other applications."),

        ("25 June 2026",
         "To apply the earlier concepts by building the mini project, an AI Resume Analyzer.",
         "Built an AI-powered tool that reads a resume, assesses skills, experience, and qualifications, and returns structured JSON feedback with improvement suggestions.",
         "Combining prompt engineering, structured outputs, and LLMs in one working solution.",
         "Getting the analysis in a consistent format for different resumes.",
         "Refined the prompt and the JSON structure after testing with several sample resumes.",
         "Completed the first mini project and gained confidence in building AI-based tools."),

        ("29 June 2026",
         "To understand workflow automation and get started with N8N.",
         "Studied what workflow automation is, explored the N8N interface and its nodes, and built a simple workflow connecting two applications.",
         "Workflow automation concepts, nodes, and visual workflow building in N8N.",
         "Understanding how data passes from one node to the next.",
         "Inspected the output of each node and followed the trainer's demo workflow.",
         "Became comfortable with the N8N workspace and the idea of no-code automation."),

        ("30 June 2026",
         "To learn event-driven automation using triggers and actions.",
         "Created workflows started by events such as a new email or a form submission, and explored Zapier as another no-code automation platform.",
         "Triggers, actions, event-driven workflows, and a comparison of N8N and Zapier.",
         "Choosing the right trigger for each task.",
         "Tested each trigger with sample events and checked the workflow results.",
         "Understood how events start automated processes."),

        ("1 July 2026",
         "To connect applications using APIs and webhooks.",
         "Studied how APIs let AI systems communicate with external services, set up a webhook to start a workflow, and sent test requests.",
         "APIs, webhooks, HTTP requests and responses, and the basics of API authentication.",
         "Handling errors when a request failed or returned unexpected data.",
         "Checked the request details and response codes and corrected the configuration.",
         "Learned how real-time integrations link AI workflows to other tools."),

        ("2 July 2026",
         "To build an AI-powered Gmail auto-reply workflow.",
         "Created a workflow that detects a new email, sends its content to an LLM, and drafts a suitable reply automatically.",
         "Integrating Gmail, an LLM, and automation nodes in one workflow.",
         "Getting replies with the right tone and content.",
         "Improved the prompt given to the LLM and tested with different sample emails.",
         "Completed a working email auto-reply automation."),

        ("3 July 2026",
         "To extend the auto-reply workflow into a full AI Email Automation Bot.",
         "Added email categorization, conditional routing, and reply generation, then tested and optimized the workflow.",
         "Conditional logic in workflows, email classification, and workflow testing and optimization.",
         "Routing different types of email to the correct path.",
         "Added decision nodes and retested with sample emails of each type.",
         "Finished the email automation project and learned how AI reduces manual communication work."),

        ("6 July 2026",
         "To understand multi-agent systems and the CrewAI framework.",
         "Studied why several specialised agents work better than one for complex tasks, and explored the basic structure of a CrewAI project.",
         "Multi-agent architecture and the basics of CrewAI.",
         "Understanding how agents share the work.",
         "Went through the trainer's example crew step by step.",
         "Understood the idea behind collaborative AI agents."),

        ("7 July 2026",
         "To define agents with clear roles, goals, and tools.",
         "Created agents such as Researcher, Planner, and Writer, gave each a goal, and attached tools such as web search.",
         "Agent roles, goals, backstory, and tool usage.",
         "Writing role and goal descriptions specific enough to give good results.",
         "Rewrote the role descriptions and compared how the agents behaved.",
         "Learned how well-defined roles improve agent performance."),

        ("8 July 2026",
         "To understand agent memory, collaboration, and the difference between AI models and AI agents.",
         "Enabled memory for agents, assigned tasks between them, and compared a plain LLM response with an agent that plans and uses tools.",
         "Agent memory, task delegation, agent communication, and models versus agents.",
         "Keeping context consistent between agents.",
         "Reviewed the task outputs passed between agents and adjusted the task descriptions.",
         "Understood how memory and communication make agents effective."),

        ("9 July 2026",
         "To build an AI Travel Planner using a team of agents.",
         "Designed agents for destination research, itinerary planning, budget estimation, and final report writing, and connected them in a sequential workflow.",
         "Designing and orchestrating a multi-agent workflow.",
         "Coordinating the order of tasks between agents.",
         "Defined clear inputs and expected outputs for each task.",
         "Built the first working version of the travel planner team."),

        ("10 July 2026",
         "To test the travel planner and begin learning Retrieval-Augmented Generation (RAG).",
         "Tested the planner with different destinations and budgets, then studied how RAG combines document retrieval with LLM responses.",
         "Agent testing, the RAG concept, and how retrieval reduces hallucinations.",
         "Budget estimates were inconsistent in some outputs.",
         "Adjusted the budget agent's instructions and re-tested.",
         "Completed the travel planner project and started the RAG module."),

        ("13 July 2026",
         "To learn the types of RAG and how embeddings represent meaning.",
         "Studied Basic, Advanced, Agentic, and Hybrid RAG, and how text is converted into embeddings.",
         "RAG architectures and the idea of embeddings.",
         "Understanding how numbers can capture the meaning of text.",
         "Used simple examples to compare similar and different sentences.",
         "Understood how RAG architectures differ and where each one is used."),

        ("14 July 2026",
         "To understand vector databases and semantic search.",
         "Studied how embeddings are stored in vector databases and searched by similarity, and tried retrieving relevant text for sample questions.",
         "Vector databases, similarity search, and semantic versus keyword search.",
         "Understanding why meaning-based search returns different results from keyword search.",
         "Ran the same query with both approaches and compared the results.",
         "Understood that retrieval is the core of document-based AI applications."),

        ("15 July 2026",
         "To build AI pipelines using the no-code platform Stack AI.",
         "Used the visual workflow builder to connect an input, an LLM, and a knowledge source into a working pipeline.",
         "No-code AI pipeline design, and LLM and knowledge base integration in Stack AI.",
         "Connecting the knowledge source correctly to the model.",
         "Followed the platform's templates and tested the pipeline repeatedly.",
         "Built a first AI pipeline without writing much code."),

        ("16 July 2026",
         "To learn the basics of deploying AI applications and start the PDF Chatbot project.",
         "Studied workflow testing, API configuration, access management, and monitoring, and began designing document upload and retrieval for the PDF Chatbot.",
         "Deployment concepts and designing a document ingestion workflow.",
         "Planning how a document moves from upload to answer.",
         "Drew the workflow in steps before building it.",
         "Completed phase 1 of the PDF Chatbot design."),

        ("17 July 2026",
         "To integrate document retrieval into the PDF Chatbot.",
         "Processed PDF content, created embeddings, stored them, and connected retrieval to the LLM so that answers come from the document.",
         "Document processing, embedding generation, and retrieval integration.",
         "Some answers did not match the document content.",
         "Adjusted how the text was split and tested again with several questions.",
         "The chatbot began answering from the uploaded document."),

        ("20 July 2026",
         "To improve the functionality and accuracy of the PDF Chatbot.",
         "Improved the prompts, handled questions that fall outside the document, and tested the chatbot on multiple PDFs.",
         "Grounded responses and improving retrieval accuracy.",
         "The chatbot sometimes gave answers that the document did not support.",
         "Instructed the model to answer only from retrieved content and to say when the information is unavailable.",
         "Completed the PDF Chatbot project."),

        ("21 July 2026",
         "To understand autonomous AI agents.",
         "Studied goal-oriented behaviour, decision making, tool use, and multi-step execution, and built a simple goal-driven agent.",
         "Autonomous agent design and tool-based decision making.",
         "Keeping the agent focused on its goal.",
         "Defined the goal and limits clearly and reviewed the agent's steps.",
         "Built a goal-driven agent that completes tasks with little guidance."),

        ("22 July 2026",
         "To study how multiple agents collaborate and communicate.",
         "Designed the flow of information between a coordinator agent and specialist agents, including task delegation and result sharing.",
         "Agent communication flow, coordination, and task delegation.",
         "Avoiding repeated or conflicting work between agents.",
         "Gave each agent a separate responsibility and passed results in a fixed order.",
         "Understood how communication design affects a multi-agent system."),

        ("23 July 2026",
         "To learn how AI agents plan and execute tasks.",
         "Practised splitting a large goal into smaller tasks, setting priorities, and tracking progress so the plan can change when needed.",
         "Task decomposition, priority management, and execution monitoring.",
         "Judging the right order of tasks.",
         "Reviewed the plan after each step and corrected the sequence.",
         "Learned how planning lets agents handle complex objectives."),

        ("24 July 2026",
         "To build a Multi-Agent Research Assistant.",
         "Created a research agent to collect information, an analysis agent to evaluate the findings, and a report agent to prepare a summary.",
         "Research automation, data analysis by agents, and automated report generation.",
         "Making the outputs of the three agents fit together.",
         "Defined a shared format for what each agent passes on.",
         "Completed the Multi-Agent Research Assistant mini project."),

        ("27 July 2026",
         "To understand AI customer support systems.",
         "Studied automated query resolution, intelligent chatbots, and ticket categorization and routing, and designed a sample support workflow.",
         "Customer support automation and the use of NLP and LLMs in support systems.",
         "Handling queries that the system cannot answer.",
         "Added a fallback step that passes such queries to a human.",
         "Learned how AI improves response time and support quality."),

        ("28 July 2026",
         "To learn the basics of AI voice assistants.",
         "Studied the pipeline of speech recognition, language understanding, response generation, and text-to-speech.",
         "Speech-to-text, intent understanding, and text-to-speech.",
         "Understanding how the stages connect to each other.",
         "Reviewed the flow with a diagram and examples.",
         "Gained a basic understanding of voice-enabled AI."),

        ("29 July 2026",
         "To apply AI agents to business tasks and improve workflow efficiency.",
         "Automated tasks such as scheduling, report preparation, and email drafting, and reviewed how to reduce steps and errors in the workflows.",
         "Business process automation and workflow optimization.",
         "Finding which steps can be safely automated.",
         "Measured each step and removed the unnecessary ones.",
         "Understood where AI agents add the most value in business processes."),

        ("30 July 2026",
         "To understand end-to-end AI system design and monitoring.",
         "Studied the data, processing, AI, automation, and user interaction layers, and how dashboards track performance, workflow runs, and errors.",
         "AI system architecture, monitoring, error tracking, and logging.",
         "Seeing how all the layers fit together.",
         "Drew a layered diagram of a complete AI solution.",
         "Learned the main parts of a complete AI system."),

        ("31 July 2026",
         "To connect AI with enterprise analytics and finalise the capstone project topic.",
         "Explored enterprise analytics bottlenecks and finalised the capstone project topic: InsightX AI – Autonomous AI Data Analyst & Predictive Decision Intelligence Platform. Outlined the architecture: React, FastAPI, DuckDB, Scikit-Learn, and sqlglot.",
         "Enterprise BI pain points, autonomous data agents, and capstone project scoping.",
         "Deciding how to prevent LLM hallucinations when calculating mathematical metrics.",
         "Formulated the foundational design rule: 'Code Computes, AI Explains' where deterministic code does the math and the LLM provides explanations.",
         "Completed the foundational AI automation training phase and prepared for capstone project engineering."),

        # =====================================================================
        # AUGUST 2026: REWRITTEN FOR INSIGHTX AI CAPSTONE PROJECT
        # =====================================================================
        ("3 August 2026 – Capstone Project Inception, Business Problem Scoping & Architecture",
         "To conceptualize InsightX AI, study modern Business Intelligence (BI) bottlenecks, define the 60-second autonomous pipeline, and establish core architectural boundaries.",
         "Analyzed how business leaders face multi-week backlogs waiting for data engineers to clean messy spreadsheets and build dashboards. Formulated the solution: an autonomous data analyst platform where users upload any dataset (CSV, Excel) and receive a cleaned dataset, domain-adaptive dashboard, and predictive models in under 60 seconds. Formulated the 6 core views (Dashboard, Data Upload, Analysis, Predictions, AI Insights, Settings) and established the 'Code Computes, AI Explains' paradigm to eliminate math hallucinations.",
         "Enterprise BI pain point analysis, autonomous analytical pipeline design, deterministic AI boundaries, and full-stack architecture selection (React 18, TypeScript, FastAPI, DuckDB, Scikit-Learn).",
         "Preventing generative AI models from fabricating numbers and aggregations during analytical querying.",
         "Designed a strict architecture where DuckDB and Python compute all aggregations deterministically, while LLMs only translate questions to SQL and explain computed results.",
         "Established technical specifications, performance targets (<60s time-to-insight), and system architecture for InsightX AI."),

        ("4 August 2026 – Frontend Setup, Streamlined Navigation & Component Architecture",
         "To scaffold the React 18 and TypeScript application with Vite and build the streamlined 6-tab executive navigation layout.",
         "Initialized the Vite React-TypeScript project with Tailwind CSS, Lucide React icons, and Zustand global state management. Built the 6-module navigation sidebar (Dashboard, Data Upload, Analysis, Predictions, AI Insights, Settings) removing extraneous legacy screens. Created responsive layout shells, dark/light executive themes, and type-safe data interfaces for datasets, KPI cards, and chart specifications.",
         "React 18 component design, TypeScript interface modeling, Zustand state management, Tailwind CSS utility styling, and client-side view routing.",
         "Creating a unified state store that syncs uploaded dataset context across dashboards, ML models, and conversational chat views.",
         "Implemented a centralized Zustand store (`useAppStore`) managing active datasets, pipeline progress, themes, and authorization tokens.",
         "Completed the frontend architectural foundation with a clean, executive-ready interface."),

        ("5 August 2026 – High-Performance Analytical Engine with DuckDB & Data Profiling",
         "To embed DuckDB as an in-memory columnar analytical engine and build automated data profiling routines in FastAPI.",
         "Integrated DuckDB in-process within the FastAPI Python backend. Developed automated schema profiling using Pandas to inspect column data types, cardinalities, missing rates, and statistical distributions. Connected DuckDB to query raw Parquet and CSV files directly with sub-10ms query execution.",
         "Columnar OLAP database architecture, vectorized SQL execution, in-memory analytical querying, and statistical data profiling in Python.",
         "Avoiding heavy external database setup while achieving near-instant query speeds on large datasets.",
         "Leveraged DuckDB's zero-dependency in-process C++ engine, allowing analytical queries over 500,000+ rows in single-digit milliseconds.",
         "Established a high-throughput analytical data layer capable of powering real-time dashboard calculations."),

        ("6 August 2026 – Safe Automated Cleaning Pipeline & Data Quality Scoring",
         "To implement safe, low-risk automated data cleaning with reversible audit logging and Data Quality Scoring (DQS).",
         "Engineered an automated preprocessing pipeline that standardizes date formats to ISO-8601, trims whitespace, removes exact duplicate rows, strips currency ($/₹) and percentage (%) symbols, and cleans column headers. Formulated the Data Quality Score (DQS) algorithm to benchmark data cleanliness before and after cleaning. Maintained original raw data immutability for complete reversibility.",
         "Automated data hygiene, reversible preprocessing, regex data cleansing, and data quality quantification algorithms.",
         "Handling ambiguous dates (DD/MM/YYYY vs MM/DD/YYYY) and preventing destructive data loss.",
         "Applied conservative auto-cleaning defaults (only low-risk transforms applied automatically; high-risk actions like outlier drops flagged for review) and preserved raw files immutably.",
         "Built a trustworthy automated data cleaner that resolves messy spreadsheets without manual configuration."),

        ("7 August 2026 – Declarative Dynamic Dashboard Generator & Headline KPIs",
         "To build the rule-based dashboard recommendation engine that synthesizes declarative JSON layouts from data semantics.",
         "Developed the backend Dashboard Generator that detects domain context (Sports, Sales, Finance, HR, Healthcare) and selects 4 grounded headline KPI cards (with deltas and SVG sparklines), 6 to 8 domain-prioritized charts (using Apache ECharts), and a top-N entity leaderboard. Integrated JSON sanitization to replace NaN/Infinity floating values with 0.0 to prevent serialization errors.",
         "Declarative UI generation, semantic column role mapping (metric, dimension, time, ID), rule-based chart recommendation, and Apache ECharts integration.",
         "Preventing fake or empty dashboard widgets when datasets lack specific dimensions (e.g. cricket datasets lacking wins/losses).",
         "Implemented strict data-grounded checks: every widget queries DuckDB directly; widgets without supporting data columns are omitted automatically.",
         "Completed the autonomous dashboard generator capable of rendering customized executive cockpits in seconds."),

        ("10 August 2026 – Automated Machine Learning (AutoML) & What-If Simulator",
         "To build the AutoML predictive modeling engine, feature importance attribution, and interactive sensitivity simulator.",
         "Engineered the AutoML pipeline using Scikit-Learn and XGBoost. Implemented baseline mean comparisons, monotonic feature leakage pruning (excluding cumulative columns like running total of runs), time-series feature engineering (shifted rolling means), permutation feature importance, and an interactive What-If sensitivity simulator with slider and dropdown controls in React.",
         "Automated machine learning (AutoML), feature leakage prevention, chronological train/test splitting, permutation importance, and sensitivity simulation.",
         "Handling datasets where no model beats the baseline average (R² <= 0) without rendering an empty UI.",
         "Derived feature importance from the best non-baseline model with clear 'Weak Evidence' warning banners, and built What-If input controls dynamically from feature metadata.",
         "Delivered an intuitive predictive workbench that enables non-technical executives to simulate business scenarios."),

        ("11 August 2026 – Grounded Conversational Text-to-SQL with sqlglot AST Verification",
         "To develop the 'Ask Your Data' conversational interface using sqlglot Abstract Syntax Tree (AST) validation for hallucination-free querying.",
         "Built the Text-to-SQL agent that translates natural language questions into executable DuckDB SQL. Integrated sqlglot to parse the query AST, verify that it is strictly a read-only SELECT statement, normalize dialect backticks to ANSI double quotes, and intercept SQL injection attempts. Connected query results to an LLM to generate plain-English explanations with a 'Show SQL' audit toggle and provenance badges.",
         "Text-to-SQL semantic translation, Abstract Syntax Tree (AST) parsing, dialect transpilation, SQL injection defense, and query provenance tracking.",
         "Preventing syntax errors caused by column names containing spaces or reserved keywords in DuckDB.",
         "Added automated column identifier quoting (`q_ident()`) and dialect normalization in `sql_validator.py` before execution.",
         "Achieved a 100% verified, hallucination-free natural language querying experience."),

        ("12 August 2026 – Multi-Format Executive Export Services & End-to-End Testing",
         "To engineer multi-format export engines (PDF, PPTX, XLSX) and execute comprehensive automated testing suites.",
         "Implemented server-side export services: Playwright headless Chromium for pixel-perfect A4 landscape PDFs, `python-pptx` for 4-slide board presentations, and `openpyxl` for multi-tab Excel workbooks, guaranteeing exact number parity with on-screen dashboard metrics. Executed the 21-test Pytest backend suite (21/21 passed in 4.82s) and Playwright automated end-to-end browser tests.",
         "Server-side headless browser rendering, programmatic PowerPoint slide generation, Excel automation, and automated test orchestration.",
         "Ensuring numbers in exported PowerPoint and PDF reports match on-screen dashboard figures verbatim.",
         "Shared the single source of truth: export generators fetch computed metric structures directly from the DuckDB analytical cache.",
         "Validated system stability, performance benchmarks (<60s full run), and cross-format numerical consistency."),

        ("13 August 2026 – Technical Project Report, Documentation & Presentation Preparation",
         "To compile the comprehensive industrial training project report, documentation, and executive slide deck.",
         "Authored the complete 35-page Industrial Training Project Report detailing project architecture, problem statement, technology stack (React 18, FastAPI, DuckDB, Scikit-Learn, sqlglot), auto-cleaning algorithms, AutoML benchmarks, and test audits. Embedded high-resolution screenshots of all 6 views and the official DataValley training certificates. Prepared the viva-voce demonstration presentation.",
         "Technical authoring, system documentation, API documentation (Swagger/ReDoc), and technical presentation design.",
         "Presenting complex data engineering and ML concepts in an accessible, executive-friendly format.",
         "Structured explanations around the central theme: 'From Raw Spreadsheets to Executive Boardroom Insights in Under 60 Seconds with Zero Hallucinations'.",
         "Completed all project documentation, report files, and presentation materials for final evaluation."),

        ("14 August 2026 – Capstone Project Demonstration, Viva Voce Defense & Final Submission",
         "To demonstrate InsightX AI to the evaluation panel, defend system design decisions in the viva voce, and submit final training deliverables.",
         "Demonstrated the live InsightX AI platform: uploaded a messy sales dataset, showed real-time auto-cleaning and quality scoring, navigated the generated executive dashboard, executed What-If scenario simulations, demonstrated conversational natural language queries with verified SQL audits, and exported instant PDF and PPTX decks. Defended technical choices (DuckDB vs PostgreSQL, sqlglot AST defense, leakage pruning) and submitted the final project report, daily diary, and repository evidence.",
         "Technical viva defense, live software demonstration, technical communication, and system benchmarking defense.",
         "Answering panel questions on how InsightX AI eliminates LLM calculation errors and handles edge cases.",
         "Walked the panel through the 'Code Computes, AI Explains' architectural pipeline and verified number parity audits.",
         "Successfully defended the Capstone Project and completed the 8-Week Industrial Training with highest commendation.")
    ]

    for d_str, o, s, sk, ch, sol, con in entries:
        add_day_entry(d_str, o, s, sk, ch, sol, con)

    out_path = os.path.abspath(r"c:\Users\datta\OneDrive\Desktop\insighhtX2\InsightX_AI_Daily_Diary_Internship_Logbook.docx")
    doc.save(out_path)
    print(f"Daily Diary successfully generated at: {out_path}")
    print(f"File size: {os.path.getsize(out_path)} bytes")

if __name__ == "__main__":
    create_daily_diary_docx()
