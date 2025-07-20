import json
import sqlite3
from pydantic import BaseModel, Field

from .base import Tool

class SQLiteQueryInput(BaseModel):
    path: str = Field(description="SQLiteデータベースファイルのパス")
    query: str = Field(description="実行するSQLクエリ")

def run_sqlite_query(path: str, query: str) -> str:
    """Run a SQL query against a SQLite database and return results as JSON."""
    conn = sqlite3.connect(path)
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return json.dumps(rows, ensure_ascii=False)
    except Exception as e:
        return f"Error querying database: {e}"
    finally:
        conn.close()

def get_tool() -> Tool:
    return Tool(
        name="sqlite_query",
        description="SQLiteデータベースに対してSQLクエリを実行するツール。入力はデータベースのパスとSQLクエリ。",
        func=run_sqlite_query,
        args_schema=SQLiteQueryInput,
    )
