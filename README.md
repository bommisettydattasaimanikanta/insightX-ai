# InsightForge AI: Autonomous AI Data Analyst & Dashboard Platform (v2)

![InsightForge AI Architecture](https://img.shields.io/badge/Architecture-FastAPI%20%2B%20DuckDB%20%2B%20React-indigo)
![Evaluation Benchmark](https://img.shields.io/badge/Text--to--SQL%20Eval-100%25%20(30%2F30)-emerald)
![Security Gate](https://img.shields.io/badge/sqlglot-AST%20Protected-blue)

**InsightForge AI** is an enterprise autonomous data analyst platform. Users can upload any raw, messy dataset or connect a live database, and within **60 seconds** receive cleaned data, a declarative interactive dashboard, ranked strategic insights, and predictive models.

---

## ⚡ Non-Negotiable Core Principles

1. **Code computes, AI explains**: The LLM never hallucinates numbers. Every number on every card, chart, and insight originates from deterministic SQL (DuckDB), SciPy, or scikit-learn models, equipped with a reproducible **"Show how"** formula link.
2. **Honest labels**: Every card, chart, and sentence carries one explicit transparent badge:
   - `[Computed]` (SQL/mathematical aggregation)
   - `[Statistical test]` (ANOVA, FDR-corrected p-values, Pearson/Spearman)
   - `[ML prediction]` (XGBoost, Holt-Winters, Optuna, Scikit-learn)
   - `[AI-generated]` (Qualitative explanations and strategic recommendations)
3. **Non-destructive Parquet data lake**: Raw uploads are immutable. All transformations are versioned Parquet steps with full diff, restore, and audit logs.
4. **Human in control**:
   - **Autopilot mode**: End-to-end execution and dashboard synthesis.
   - **Review mode**: Step-by-step approval with impact previews ("affects 3.2% of rows").
5. **Unified Semantic Layer**: The dashboard, insights engine, and chatbot all read from a single editable semantic registry, guaranteeing that numbers always match across the entire platform.

---

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui tokens, Apache ECharts, TanStack Table, Zustand, Framer Motion.
- **Backend**: Python 3.11, FastAPI, DuckDB, `sqlglot` AST parser, PyArrow, pandas, NumPy, SciPy, statsmodels, scikit-learn, XGBoost, Optuna, SQLAlchemy, ReportLab.
- **Storage**: SQLite for metadata & audit logs; Parquet for datasets.
- **AI & Security**: Provider-agnostic LLM adapters (Gemini default, OpenAI / Claude swappable via `.env`), backend-only API keys, PII masking Privacy Mode, zero network access in sandbox.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.11+
- Node.js v18+ & npm

### 2. Backend Setup
```bash
# Optional: create a virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Start FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```
API Documentation will be live at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Interactive Web UI will be live at: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Quality Gates & Evaluation Benchmark

### 1. Run Complete Test Suite
```bash
# Run all unit tests, integration tests, and Text-to-SQL benchmarks
python -m pytest tests/backend/ -v
```

### 2. 30-Question Text-to-SQL Evaluation Benchmark
Our `sqlglot`-validated Text-to-SQL agent was evaluated across 30 realistic analytical queries:
- **Benchmark Target**: $\ge 90.0\%$
- **Achieved Score**: **100.0% (30/30 Passed)**
- **Average Execution Latency**: **8.2 ms**

Read the full evaluation report in [`docs/text_to_sql_eval_results.md`](docs/text_to_sql_eval_results.md).

---

## 📂 Deliverables Included

1. **Messy Sales Excel (`sample_data/messy_sales_data.xlsx`)**:
   - Intentional multi-row merged banners, subtotal/grand total rows, mixed date formats (`DD/MM/YYYY`, `MM/DD/YYYY`, `YYYY-MM-DD`), Indian number formats (`1.5 Lakh`, `₹2,50,000`), currency strings, and Unicode names (`Aarav Sharma (आरव)`).
2. **Multi-Table Relational Database (`sample_data/retail_operations.sqlite`)**:
   - Relational schema connecting `customers`, `products`, `orders`, and `order_items`.
3. **Time-Series Dataset (`sample_data/web_traffic_timeseries.csv`)**:
   - 180 days of daily visitors, bounce rates, conversions, and revenues.
4. **Jupyter Notebook Export**:
   - Download reproducible analytical notebooks directly from `/api/reports/{id}/notebook`.
5. **Executive Summary PDF Export**:
   - Generate one-page executive intelligence summaries via `/api/reports/{id}/pdf`.
6. **System Architecture**:
   - Available in [`docs/architecture.md`](docs/architecture.md).

---

## 🔒 Security & Data Governance

- **Prompt-Injection Defense**: User cell data and column names are treated strictly as query parameters, never as executable LLM prompt instructions.
- **Read-Only Database Enforcement**: AST checks block all DDL and DML operations (`DROP`, `ALTER`, `UPDATE`, `INSERT`, `DELETE`).
- **Privacy Mode**: PII detection identifies emails, phone numbers, and IDs, masking them with hashes before model synthesis.
- **30-Day Trash & Permanent Wipe**: Soft deletes allow instant restoration; permanent deletion requires typing the exact dataset name to wipe Parquet lake storage and caches.
