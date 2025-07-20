from src.agent import ReActAgent
from src.tools.sqlite_tool import get_tool


def test_agent_uses_sqlite_query_tool(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE items(id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO items(name) VALUES('apple')")
    conn.commit()
    conn.close()

    outputs = [
        "思考: データベースを調べます\n行動: sqlite_query: {\"path\": \"%s\", \"query\": \"SELECT name FROM items\"}" % db_path,
        "最終的な答え: done",
    ]

    def fake_llm(prompt: str) -> str:
        return outputs.pop(0)

    agent = ReActAgent(fake_llm, [get_tool()])

    answer = agent.run("?")
    assert answer == "done"
