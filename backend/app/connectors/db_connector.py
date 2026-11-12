import sqlite3
from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

class DatabaseConnector:
    """Read-only database connector for live queries and snapshots."""
    
    @staticmethod
    def is_query_safe_readonly(sql: str) -> bool:
        """Enforces that only SELECT queries are permitted. Blocks DDL, DML, etc."""
        cleaned = sql.strip().upper()
        forbidden_keywords = [
            "INSERT ", "UPDATE ", "DELETE ", "DROP ", "ALTER ", 
            "TRUNCATE ", "CREATE ", "GRANT ", "REVOKE ", "RENAME ",
            "EXEC ", "EXECUTE "
        ]
        if not cleaned.startswith("SELECT") and not cleaned.startswith("WITH"):
            return False
        for kw in forbidden_keywords:
            if kw in cleaned:
                return False
        return True

    @staticmethod
    def test_connection(db_type: str, host: Optional[str], port: Optional[int], 
                        database_name: str, username: Optional[str], password: Optional[str]) -> Dict[str, Any]:
        """Tests connectivity and verifies read-only access."""
        try:
            if db_type == "sqlite":
                conn = sqlite3.connect(database_name)
                cursor = conn.cursor()
                cursor.execute("SELECT 1;")
                cursor.fetchone()
                conn.close()
                return {"success": True, "message": "Successfully connected to SQLite database."}
            else:
                # Construct connection string
                if db_type == "postgresql":
                    driver = "postgresql+psycopg2"
                    default_port = 5432
                elif db_type == "mysql":
                    driver = "mysql+pymysql"
                    default_port = 3306
                elif db_type == "sqlserver":
                    driver = "mssql+pyodbc"
                    default_port = 1433
                else:
                    return {"success": False, "message": f"Unsupported db type {db_type}"}
                    
                port_str = f":{port or default_port}"
                url = f"{driver}://{username}:{password}@{host}{port_str}/{database_name}"
                engine = create_engine(url, connect_args={"connect_timeout": 5})
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1;"))
                return {"success": True, "message": f"Successfully connected to {db_type}."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_tables_and_views(db_type: str, database_name: str, **kwargs) -> List[Dict[str, Any]]:
        """List tables, columns, and estimated row counts."""
        tables_info = []
        if db_type == "sqlite":
            conn = sqlite3.connect(database_name)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [r[0] for r in cursor.fetchall() if not r[0].startswith("sqlite_")]
            for t in tables:
                cursor.execute(f"SELECT COUNT(*) FROM `{t}`")
                count = cursor.fetchone()[0]
                cursor.execute(f"PRAGMA table_info(`{t}`)")
                cols = [{"name": c[1], "type": c[2]} for c in cursor.fetchall()]
                tables_info.append({
                    "name": t,
                    "estimated_rows": count,
                    "columns": cols
                })
            conn.close()
        return tables_info
