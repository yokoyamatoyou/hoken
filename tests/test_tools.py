import src.tools as tools


def test_get_default_tools():
    all_names = {t.name for t in tools.get_default_tools()}
    assert 'web_scraper' in all_names
    assert 'sqlite_query' in all_names

