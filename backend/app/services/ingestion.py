import re
import os
import io
import json
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import openpyxl

from backend.app.config import settings

def clean_indian_or_currency_number(val: Any) -> Any:
    """Clean currency strings, percentages, and Indian numbering (lakhs, crores)."""
    if pd.isna(val) or val is None or val == "":
        return np.nan
    if isinstance(val, (int, float)):
        return val
        
    s = str(val).strip()
    
    # Check percentage
    is_percent = False
    if s.endswith("%"):
        is_percent = True
        s = s[:-1].strip()
        
    # Remove currency symbols and formatting commas
    # Matches $, €, £, ₹, ¥, etc.
    s = re.sub(r"[$\u20AC\u00A3\u20B9\u00A5Rs\.INR\s]", "", s)
    
    # Check for words like lakh, crore, million, billion
    multiplier = 1.0
    s_lower = s.lower()
    if "crore" in s_lower or "cr" in s_lower:
        multiplier = 10000000.0
        s = re.sub(r"(crores?|cr)", "", s, flags=re.IGNORECASE).strip()
    elif "lakh" in s_lower or "lac" in s_lower:
        multiplier = 100000.0
        s = re.sub(r"(lakhs?|lacs?)", "", s, flags=re.IGNORECASE).strip()
    elif "million" in s_lower or "m" in s_lower and not s_lower.endswith("am") and not s_lower.endswith("pm"):
        multiplier = 1000000.0
        s = re.sub(r"(millions?|m)", "", s, flags=re.IGNORECASE).strip()
    elif "billion" in s_lower or "b" in s_lower:
        multiplier = 1000000000.0
        s = re.sub(r"(billions?|b)", "", s, flags=re.IGNORECASE).strip()
        
    # Strip remaining commas (handles standard 1,000,000 and Indian 1,00,000)
    s = s.replace(",", "")
    
    # Try parsing float
    try:
        num = float(s) * multiplier
        if is_percent:
            num = num / 100.0
        return num
    except (ValueError, TypeError):
        return val

def parse_mixed_dates(series: pd.Series) -> pd.Series:
    """Parse mixed date formats (DD/MM/YYYY, MM/DD/YYYY, ISO, etc.)."""
    if series.empty:
        return series
        
    # Try direct pandas datetime parsing first
    try:
        parsed = pd.to_datetime(series, errors="coerce", format="mixed")
        # If over 60% successfully parsed, adopt it
        if parsed.notna().mean() >= 0.6:
            return parsed
    except Exception:
        pass
    return series

def detect_subtotal_rows(df: pd.DataFrame) -> List[int]:
    """Detect total, subtotal, grand total rows that skew aggregations."""
    subtotal_indices = []
    keywords = ["total", "grand total", "subtotal", "sub-total", "average", "summary"]
    
    for idx, row in df.iterrows():
        row_str = " ".join([str(v).lower() for v in row.values if pd.notna(v)])
        if any(kw in row_str for kw in keywords):
            # Check if this row is mostly empty or summary-like
            subtotal_indices.append(idx)
    return subtotal_indices

def parse_messy_excel(file_path: str, sheet_name: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Parses messy Excel files with:
    - merged cells unmerged and filled
    - multi-row headers flattened
    - hidden sheets inspected
    - subtotal rows detected
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    all_sheets = wb.sheetnames
    
    target_sheet = sheet_name or all_sheets[0]
    ws = wb[target_sheet]
    
    # Unmerge cells and propagate values
    for merge_range in list(ws.merged_cells.ranges):
        min_col, min_row, max_col, max_row = merge_range.bounds
        top_left_val = ws.cell(row=min_row, column=min_col).value
        ws.unmerge_cells(str(merge_range))
        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                ws.cell(row=r, column=c).value = top_left_val
                
    # Read into rows
    data = []
    for row in ws.iter_rows(values_only=True):
        data.append(list(row))
        
    if not data:
        return pd.DataFrame(), {"sheets": all_sheets, "subtotals_removed": 0}
        
    # Detect header row: find row with the maximum number of distinct string headers
    best_header_idx = 0
    max_distinct_valid = 0
    for i, r in enumerate(data[:8]):
        non_empty = [str(c).strip() for c in r if c is not None and str(c).strip() != ""]
        unique_strings = set(non_empty)
        # Avoid title banner rows that span all columns or rows with few unique names
        if len(unique_strings) > max_distinct_valid and len(unique_strings) >= 3:
            max_distinct_valid = len(unique_strings)
            best_header_idx = i
            
    header_idx = best_header_idx
    headers = [str(c).strip() if c is not None and str(c).strip() != "" else f"Col_{j+1}" for j, c in enumerate(data[header_idx])]
    
    # Handle duplicate header names
    seen = {}
    unique_headers = []
    for h in headers:
        if not h or h.lower() == "none":
            h = "Column"
        if h in seen:
            seen[h] += 1
            unique_headers.append(f"{h}_{seen[h]}")
        else:
            seen[h] = 0
            unique_headers.append(h)
            
    rows = data[header_idx + 1:]
    # Pad or trim rows to match headers length
    normalized_rows = []
    for r in rows:
        if all(c is None or str(c).strip() == "" for c in r):
            continue  # skip completely blank rows
        if len(r) < len(unique_headers):
            r = r + [None] * (len(unique_headers) - len(r))
        else:
            r = r[:len(unique_headers)]
        normalized_rows.append(r)
        
    df = pd.DataFrame(normalized_rows, columns=unique_headers)
    
    # Detect subtotal/total rows
    subtotal_rows = detect_subtotal_rows(df)
    subtotals_count = len(subtotal_rows)
    if subtotal_rows:
        df = df.drop(index=subtotal_rows).reset_index(drop=True)
        
    # Clean numeric columns with currency or Indian numbering
    for col in df.columns:
        # Test sample to see if it looks numeric or currency
        sample = df[col].dropna().head(20)
        cleaned_sample = [clean_indian_or_currency_number(v) for v in sample]
        num_count = sum(1 for v in cleaned_sample if isinstance(v, (int, float)) and not pd.isna(v))
        if len(sample) > 0 and (num_count / len(sample)) >= 0.7:
            df[col] = df[col].apply(clean_indian_or_currency_number)
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
    meta = {
        "sheets": all_sheets,
        "active_sheet": target_sheet,
        "subtotals_removed": subtotals_count,
        "total_rows": len(df),
        "total_cols": len(df.columns)
    }
    return df, meta

def load_dataset_file(file_path: str, file_type: str, sheet_name: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Loads any supported file format into a pandas DataFrame."""
    ext = file_type.lower().replace(".", "")
    meta: Dict[str, Any] = {}
    
    if ext in ["xlsx", "xls", "xlsm"]:
        df, meta = parse_messy_excel(file_path, sheet_name)
    elif ext in ["csv", "tsv", "txt"]:
        sep = "\t" if ext == "tsv" else None  # None allows python engine to auto-detect delimiter
        try:
            df = pd.read_csv(file_path, sep=sep, engine="python", encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, sep=sep, engine="python", encoding="latin1")
            
        # Clean currency & Indian numbers
        for col in df.columns:
            if df[col].dtype == object:
                sample = df[col].dropna().head(20)
                cleaned = [clean_indian_or_currency_number(v) for v in sample]
                num_count = sum(1 for v in cleaned if isinstance(v, (int, float)) and not pd.isna(v))
                if len(sample) > 0 and (num_count / len(sample)) >= 0.7:
                    df[col] = df[col].apply(clean_indian_or_currency_number)
                    df[col] = pd.to_numeric(df[col], errors="coerce")
        meta = {"format": "csv", "delimiter": sep or ","}
    elif ext == "json":
        try:
            df = pd.read_json(file_path)
        except ValueError:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            df = pd.json_normalize(data)
        meta = {"format": "json"}
    elif ext == "parquet":
        df = pd.read_parquet(file_path)
        meta = {"format": "parquet"}
    elif ext in ["sqlite", "db", "sqlite3"]:
        conn = sqlite3.connect(file_path)
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)["name"].tolist()
        target_table = sheet_name or (tables[0] if tables else "")
        if target_table:
            df = pd.read_sql(f"SELECT * FROM `{target_table}`", conn)
        else:
            df = pd.DataFrame()
        meta = {"format": "sqlite", "tables": tables, "active_table": target_table}
        conn.close()
    else:
        raise ValueError(f"Unsupported file format: {ext}")
        
    # Flatten column names & remove extra whitespaces
    df.columns = [re.sub(r"\s+", " ", str(c).strip()) for c in df.columns]
    
    return df, meta

def save_to_parquet(df: pd.DataFrame, dataset_id: str, version: int) -> str:
    """Save dataframe as Parquet in the parquet storage directory."""
    parquet_filename = f"{dataset_id}_v{version}.parquet"
    out_path = settings.PARQUET_DIR / parquet_filename
    
    # Ensure all datetime columns are timezone-naive or properly typed
    df_clean = df.copy()
    for col in df_clean.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
        df_clean[col] = df_clean[col].dt.tz_localize(None)
        
    df_clean.to_parquet(str(out_path), index=False, engine="pyarrow")
    return str(out_path)
