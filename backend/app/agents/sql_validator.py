import re
import sqlglot
from sqlglot import exp
from typing import Tuple, Optional, Set

class SafeSQLValidator:
    """
    Validates generated SQL queries using sqlglot AST parsing to guarantee:
    1. Only SELECT / WITH statements (zero DDL/DML)
    2. Only allowed virtual tables ('data', 'dataset')
    3. Forced LIMIT (capped at max 10,000 rows to prevent DoS)
    4. Prohibits system or file-reading functions (e.g. read_csv, read_parquet, copy)
    """

    ALLOWED_TABLES: Set[str] = {"data", "dataset"}
    FORBIDDEN_FUNCTIONS: Set[str] = {
        "read_csv", "read_parquet", "read_json", "read_blob", 
        "write_csv", "copy", "load", "install", "attach", "import"
    }

    @classmethod
    def validate_and_sanitize(cls, sql_query: str, max_limit: int = 1000) -> Tuple[bool, str, Optional[str]]:
        """
        Parses SQL AST. Returns (is_valid, sanitized_sql, error_message).
        """
        cleaned_sql = sql_query.strip().rstrip(";")
        # Normalize MySQL-style backticks to double quotes for standard SQL / DuckDB AST
        cleaned_sql = re.sub(r"`([^`]+)`", r'"\1"', cleaned_sql)
        
        try:
            parsed = sqlglot.parse_one(cleaned_sql, read="duckdb")
        except Exception:
            try:
                parsed = sqlglot.parse_one(cleaned_sql)
            except Exception as e:
                return False, cleaned_sql, f"SQL Syntax Parsing Error: {str(e)}"
            
        # 1. Enforce SELECT or CTE (WITH)
        if not isinstance(parsed, (exp.Select, exp.Union)):
            return False, cleaned_sql, "Security Violation: Only SELECT or UNION queries are permitted."

        # 2. Inspect all table references
        tables = [t.name.lower() for t in parsed.find_all(exp.Table) if t.name]
        for tbl in tables:
            # If table is part of a CTE (WITH clause), allow it
            ctes = [cte.alias_or_name.lower() for cte in parsed.find_all(exp.CTE)]
            if tbl not in cls.ALLOWED_TABLES and tbl not in ctes:
                return False, cleaned_sql, f"Security Violation: Access to unauthorized table or source '{tbl}' is blocked."

        # 3. Check for dangerous function calls
        for func in parsed.find_all(exp.Anonymous):
            if func.name.lower() in cls.FORBIDDEN_FUNCTIONS:
                return False, cleaned_sql, f"Security Violation: Execution of dangerous function '{func.name}' is prohibited."

        # 4. Enforce LIMIT
        limit_node = parsed.find(exp.Limit)
        if limit_node:
            try:
                curr_limit = int(limit_node.expression.this)
                if curr_limit > max_limit:
                    limit_node.set("expression", exp.Literal.number(max_limit))
            except Exception:
                limit_node.set("expression", exp.Literal.number(max_limit))
        else:
            # Append LIMIT max_limit
            parsed = parsed.limit(max_limit)

        sanitized_sql = parsed.sql(dialect="duckdb")
        return True, sanitized_sql, None
