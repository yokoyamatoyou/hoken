from src.vector_memory import VectorMemory


def test_search_returns_similar_messages():
    mem = VectorMemory()
    mem.add("user", "今日は良い天気です")
    mem.add("assistant", "はい、晴れています")
    mem.add("user", "昨日は雨でした")

    results = mem.search("天気", top_k=2)
    assert any("天気" in r or "晴れ" in r for r in results)


def test_save_and_load(tmp_path):
    mem = VectorMemory()
    mem.add("user", "hello")
    file = tmp_path / "vec.json"
    mem.save(file)
    other = VectorMemory()
    other.load(file)
    assert other.messages == mem.messages


def test_save_creates_directory(tmp_path):
    mem = VectorMemory()
    mem.add("user", "hello")
    file = tmp_path / "nested" / "vec.json"
    mem.save(file)
    assert file.exists()


def test_save_filename_no_directory(tmp_path, monkeypatch):
    mem = VectorMemory()
    mem.add("user", "hello")
    monkeypatch.chdir(tmp_path)
    mem.save("vec.json")
    assert (tmp_path / "vec.json").exists()
