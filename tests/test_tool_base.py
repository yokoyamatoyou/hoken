from dataclasses import dataclass

from src.tools.base import Tool, execute_tool

class LegacyInput:
    def __init__(self, url: str):
        self.url = url
    def dict(self):
        return {"url": self.url}


def test_execute_tool_fallback_dict():
    called = {}

    def func(url: str):
        called['url'] = url
        return 'ok'

    tool = Tool(name="legacy", description="d", func=func, args_schema=LegacyInput)
    result = execute_tool("legacy", {"url": "http://example.com"}, {"legacy": tool})

    assert result == 'ok'
    assert called['url'] == 'http://example.com'


@dataclass
class DCInput:
    url: str


def test_execute_tool_dataclass():
    called = {}

    def func(url: str):
        called['url'] = url
        return 'ok'

    tool = Tool(name="dc", description="d", func=func, args_schema=DCInput)
    result = execute_tool("dc", {"url": "http://example.com"}, {"dc": tool})

    assert result == 'ok'
    assert called['url'] == 'http://example.com'
