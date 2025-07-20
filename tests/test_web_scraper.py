from src.tools import web_scraper
import threading
import logging

scrape_website_content = web_scraper.scrape_website_content


def test_scrape_local_html(tmp_path, monkeypatch):
    html = "<html><body><main><p>Hello</p><p>World</p></main></body></html>"
    file = tmp_path / "index.html"
    file.write_text(html, encoding="utf-8")

    def mock_get(url, **kwargs):
        class Resp:
            status_code = 200

            def __init__(self, content):
                self._content = content

            def raise_for_status(self):
                pass

            @property
            def content(self):
                return self._content.encode("utf-8")

            @property
            def text(self):
                return self._content

        if url.endswith("robots.txt"):
            return Resp("User-agent: *\nAllow: /")
        return Resp(html)

    import requests
    monkeypatch.setattr(requests, "get", mock_get)
    web_scraper._CACHE.clear()
    web_scraper._ROBOTS.clear()
    text = scrape_website_content("http://example.com")
    assert text == "Hello World"


def test_scrape_removes_noise(tmp_path, monkeypatch):
    html = (
        "<html><body><main><script>var x=1;</script>"
        "<p>Hi</p><footer>foot</footer></main></body></html>"
    )
    file = tmp_path / "index.html"
    file.write_text(html, encoding="utf-8")

    def mock_get(url, **kwargs):
        class Resp:
            status_code = 200

            def __init__(self, content):
                self._content = content

            def raise_for_status(self):
                pass

            @property
            def content(self):
                return self._content.encode("utf-8")

            @property
            def text(self):
                return self._content

        if url.endswith("robots.txt"):
            return Resp("User-agent: *\nAllow: /")
        return Resp(html)

    import requests
    monkeypatch.setattr(requests, "get", mock_get)
    web_scraper._CACHE.clear()
    web_scraper._ROBOTS.clear()
    text = scrape_website_content("http://example.com")
    assert text == "Hi"


def test_respects_robots(monkeypatch):
    call_count = {"n": 0}

    def mock_get(url, **kwargs):
        call_count["n"] += 1

        class Resp:
            status_code = 200

            def __init__(self, content):
                self._content = content

            def raise_for_status(self):
                pass

            @property
            def content(self):
                return self._content.encode("utf-8")

            @property
            def text(self):
                return self._content

        if url.endswith("robots.txt"):
            return Resp("User-agent: *\nDisallow: /")
        return Resp("<html><body><main>Hi</main></body></html>")

    web_scraper._CACHE.clear()
    web_scraper._ROBOTS.clear()
    import requests
    monkeypatch.setattr(requests, "get", mock_get)
    text = scrape_website_content("http://example.com/page")
    assert "Disallowed" in text
    # Should only fetch robots since page is disallowed
    assert call_count["n"] == 1


def test_caching(monkeypatch):
    call_count = {"n": 0}

    def mock_get(url, **kwargs):
        call_count["n"] += 1

        class Resp:
            status_code = 200

            def __init__(self, content):
                self._content = content

            def raise_for_status(self):
                pass

            @property
            def content(self):
                return self._content.encode("utf-8")

            @property
            def text(self):
                return self._content

        if url.endswith("robots.txt"):
            return Resp("User-agent: *\nAllow: /")
        return Resp("<html><body><main>Hi</main></body></html>")

    web_scraper._CACHE.clear()
    web_scraper._ROBOTS.clear()
    import requests
    monkeypatch.setattr(requests, "get", mock_get)
    a = scrape_website_content("http://example.com")
    b = scrape_website_content("http://example.com")
    assert a == b == "Hi"
    # Should have fetched robots once and page once
    assert call_count["n"] == 2


def test_custom_user_agent(monkeypatch):
    expected = "MyAgent/2.0"

    def mock_get(url, **kwargs):
        assert kwargs["headers"]["User-Agent"] == expected

        class Resp:
            status_code = 200

            def __init__(self, content):
                self._content = content

            def raise_for_status(self):
                pass

            @property
            def content(self):
                return self._content.encode("utf-8")

            @property
            def text(self):
                return self._content

        if url.endswith("robots.txt"):
            return Resp("User-agent: *\nAllow: /")
        return Resp("<html><body><main>Test</main></body></html>")

    import requests
    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setenv("WEB_SCRAPER_USER_AGENT", expected)
    web_scraper._CACHE.clear()
    web_scraper._ROBOTS.clear()
    web_scraper.load_settings()

    try:
        text = web_scraper.scrape_website_content("http://example.com")
        assert text == "Test"
    finally:
        monkeypatch.delenv("WEB_SCRAPER_USER_AGENT", raising=False)
        web_scraper.load_settings()


def test_custom_timeout(monkeypatch):
    expected = 5.5

    def mock_get(url, **kwargs):
        assert kwargs["timeout"] == expected

        class Resp:
            status_code = 200

            def __init__(self, content):
                self._content = content

            def raise_for_status(self):
                pass

            @property
            def content(self):
                return self._content.encode("utf-8")

            @property
            def text(self):
                return self._content

        if url.endswith("robots.txt"):
            return Resp("User-agent: *\nAllow: /")
        return Resp("<html><body><main>Hi</main></body></html>")

    import requests
    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setenv("WEB_SCRAPER_TIMEOUT", str(expected))
    web_scraper._CACHE.clear()
    web_scraper._ROBOTS.clear()
    web_scraper.load_settings()

    try:
        text = web_scraper.scrape_website_content("http://example.com")
        assert text == "Hi"
    finally:
        monkeypatch.delenv("WEB_SCRAPER_TIMEOUT", raising=False)
        web_scraper.load_settings()


def test_concurrent_calls(monkeypatch):
    html = "<html><body><main>Hi</main></body></html>"
    call_count = {"n": 0}

    def mock_get(url, **kwargs):
        call_count["n"] += 1

        class Resp:
            status_code = 200

            def __init__(self, content):
                self._content = content

            def raise_for_status(self):
                pass

            @property
            def content(self):
                return self._content.encode("utf-8")

            @property
            def text(self):
                return self._content

        if url.endswith("robots.txt"):
            return Resp("User-agent: *\nAllow: /")
        return Resp(html)

    import requests
    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setenv("WEB_SCRAPER_DELAY", "0")
    web_scraper.load_settings()
    web_scraper._CACHE.clear()
    web_scraper._ROBOTS.clear()
    web_scraper._LAST_REQUEST_TIME = 0

    results = []

    def worker():
        results.append(web_scraper.scrape_website_content("http://example.com"))

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 5
    assert all(r == "Hi" for r in results)
    # robots and page should be fetched once each
    assert call_count["n"] == 2
    web_scraper.load_settings()


def test_invalid_settings_fall_back(monkeypatch, caplog):
    caplog.set_level(logging.WARNING)
    monkeypatch.setenv("WEB_SCRAPER_CACHE_TTL", "oops")
    monkeypatch.setenv("WEB_SCRAPER_DELAY", "bad")

    web_scraper.load_settings()

    assert web_scraper._CACHE_TTL == 3600
    assert web_scraper._DELAY == 1.0
    assert "Invalid WEB_SCRAPER_CACHE_TTL" in caplog.text
    assert "Invalid WEB_SCRAPER_DELAY" in caplog.text

    monkeypatch.delenv("WEB_SCRAPER_CACHE_TTL", raising=False)
    monkeypatch.delenv("WEB_SCRAPER_DELAY", raising=False)
    web_scraper.load_settings()
