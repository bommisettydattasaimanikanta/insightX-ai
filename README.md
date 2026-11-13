# InsightX AI: Autonomous AI Data Analyst & Predictive Decision Intelligence Platform

[![GitHub Repository](https://img.shields.io/badge/GitHub-bommisettydattasaimanikanta%2FinsightX--ai-181717?style=flat&logo=github)](https://github.com/bommisettydattasaimanikanta/insightX-ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.3.1-61DAFB.svg?logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6.svg?logo=typescript)](https://www.typescriptlang.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-In--Memory%20Columnar-FFF000.svg?logo=duckdb)](https://duckdb.org/)
[![Text-to-SQL Benchmark](https://img.shields.io/badge/Text--to--SQL%20Eval-100%25%20(30%2F30)-emerald)](docs/text_to_sql_eval_results.md)
[![Security Gate](https://img.shields.io/badge/sqlglot-AST%20Protected-blue)](docs/architecture.md)

**InsightX AI** is an end-to-end autonomous AI data analyst and decision intelligence platform. Users can ingest any complex, messy dataset (CSV, Excel, Parquet) or connect live SQL databases, and within **60 seconds** receive automated schema cleaning, a verified semantic layer, interactive declarative dashboards, statistical hypothesis evaluations, and machine learning predictive forecasts.

---

## 👨‍💻 Student & Project Information

- **Author / Developer**: **B. Datta Sai Manikanta**
- **University Registration / Roll No**: **72311633**
- **Degree**: Bachelor of Technology (B.Tech) — Computer Science and Engineering (AI & DS)
- **Institution**: **CT University, Ludhiana (Punjab), India**
- **Industrial Training Partner**: **DataValley Pvt. Ltd.** (In collaboration with APSCHE)
- **Internship Supervisor**: **Mr. Shaik Arshad / Shaik Nazeerb** (Project Coordinator & Data Analyst)
- **Official GitHub Repository**: [https://github.com/bommisettydattasaimanikanta/insightX-ai](https://github.com/bommisettydattasaimanikanta/insightX-ai)

---

## ⚡ Non-Negotiable Core Principles

1. **Code computes, AI explains**: The LLM never hallucinates numbers. Every metric, chart coordinate, and KPI originates from deterministic SQL (DuckDB), SciPy, or scikit-learn models, equipped with a reproducible **"Show how"** formula link.
2. **Honest labels**: Every card, chart, and sentence carries an explicit badge:
   - `[Computed]` (SQL/mathematical aggregation)
   - `[Statistical test]` (ANOVA, FDR-corrected p-values, Pearson/Spearman)
   - `[ML prediction]` (XGBoost, Holt-Winters, Optuna, Scikit-learn)
   - `[AI-generated]` (Qualitative explanations and strategic recommendations)
3. **Non-destructive Parquet data lake**: Raw uploads are immutable. All transformations are versioned Parquet steps with full diff, restore, and audit logs.
4. **Dual Execution Modes**:
   - **Autopilot mode**: End-to-end automated cleaning, semantic induction, and dashboard synthesis in < 60s.
   - **Review mode**: Step-by-step approval with impact previews ("affects 3.2% of rows").
5. **Unified Semantic Layer**: The dashboard, insights engine, and Safe Text-to-SQL agent all read from a single editable semantic registry, guaranteeing metric consistency across the entire platform.

---

## 🛠️ Complete Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui tokens, Apache ECharts (`echarts-for-react`), TanStack Table, Zustand, Framer Motion, Lucide Icons.
- **Backend**: Python 3.11, FastAPI, DuckDB (In-Memory columnar SQL engine), `sqlglot` AST parser, PyArrow, pandas, NumPy, SciPy, statsmodels, scikit-learn, XGBoost, Optuna, SQLAlchemy, ReportLab.
- **Storage**: SQLite for metadata & audit logs; Parquet for datasets.
- **AI & Security**: Swappable LLM adapters (Google Gemini default, OpenAI / Claude via `.env`), backend-only API keys, PII masking Privacy Mode, zero network access in sandbox.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.11+
- Node.js v18+ & npm
- Git

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/bommisettydattasaimanikanta/insightX-ai.git
cd insightX-ai

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate # Linux / macOS

# Install backend dependencies
pip install -r backend/requirements.txt

# Start FastAPI backend server
uvicorn backend.app.main:app --reload --port 8000
```
API Documentation will be live at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Interactive Web Application will be live at: [http://localhost:5173](http://localhost:5173)

### 4. Default Demo Credentials
- **Email**: `demo@insightx.ai` (or `demo@insightforge.ai`)
- **Password**: `insightx123` (or click **"Use Demo Credentials"** on the login screen)

---

## 🧪 Quality Gates & Evaluation Benchmark

### 1. Run Complete Test Suite
```bash
# Run all unit tests, integration tests, and Text-to-SQL benchmarks
python -m pytest tests/backend/ -v
```

### 2. 30-Question Text-to-SQL Evaluation Benchmark
Our `sqlglot`-validated Text-to-SQL agent was evaluated across 30 analytical queries:
- **Benchmark Target**: $\ge 90.0\%$
- **Achieved Score**: **100.0% (30/30 Passed)**
- **Average Query Latency**: **8.2 ms** (DuckDB In-Memory execution)
- **Security Validation**: 100% of queries parsed and validated with `sqlglot` AST gate.

Read the full evaluation report in [`docs/text_to_sql_eval_results.md`](docs/text_to_sql_eval_results.md).

---

## 📂 Deliverables & Sample Datasets

1. **Industrial Training Project Report**:
   - [`InsightX_AI_Industrial_Training_Project_Report.pdf`](InsightX_AI_Industrial_Training_Project_Report.pdf) (29 Pages, Formal `#1E3A8A` Borders, Real Certificates & Project Screenshots)
   - [`InsightX_AI_Industrial_Training_Project_Report.docx`](InsightX_AI_Industrial_Training_Project_Report.docx)
2. **Internship Daily Diary / Log Book**:
   - [`InsightX_AI_Daily_Diary_Internship_Logbook.pdf`](InsightX_AI_Daily_Diary_Internship_Logbook.pdf) (12 Pages, CT University Header, Log entries from 18 June to 14 August)
   - [`InsightX_AI_Daily_Diary_Internship_Logbook.docx`](InsightX_AI_Daily_Diary_Internship_Logbook.docx)
3. **Messy Sales Excel (`sample_data/messy_sales_data.xlsx`)**:
   - Intentional multi-row merged banners, subtotal/grand total rows, mixed date formats, Indian currency formatting, and Unicode names.
4. **Relational Database (`sample_data/retail_operations.sqlite`)**:
   - Normalized schema connecting `customers`, `products`, `orders`, and `order_items`.
5. **Time-Series Dataset (`sample_data/web_traffic_timeseries.csv`)**:
   - 180 days of daily visitors, bounce rates, conversions, and revenues.
6. **System Architecture Specification**:
   - Complete technical specification in [`docs/architecture.md`](docs/architecture.md).

---

## 🔒 Security & Data Governance

- **Prompt-Injection Defense**: User cell data and column names are treated strictly as query parameters, never as executable LLM prompt instructions.
- **Read-Only Database Enforcement**: AST checks block all DDL and DML operations (`DROP`, `ALTER`, `UPDATE`, `INSERT`, `DELETE`).
- **Privacy Mode**: PII detection identifies emails, phone numbers, and IDs, masking them with hashes before model synthesis.
- **30-Day Trash & Permanent Wipe**: Soft deletes allow instant restoration; permanent deletion requires typing the exact dataset name to wipe Parquet lake storage and caches.

---

## 📜 License & Acknowledgements

This project was developed by **B. Datta Sai Manikanta** (`72311633`) as part of the Industrial Training curriculum at **CT University**, under the guidance of **DataValley Pvt. Ltd.** Released under the [MIT License](LICENSE).
