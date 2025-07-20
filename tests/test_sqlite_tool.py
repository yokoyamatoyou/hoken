import sqlite3
from src.tools.sqlite_tool import run_sqlite_query


def test_run_sqlite_query(tmp_path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE items(id INTEGER PRIMARY KEY, name TEXT)")
    conn.executemany("INSERT INTO items(name) VALUES(?)", [("apple",), ("banana",)])
    conn.commit()
    conn.close()

    result = run_sqlite_query(str(db_path), "SELECT name FROM items ORDER BY id")
    assert "apple" in result and "banana" in result
