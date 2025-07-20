from .base import Tool, execute_tool

def get_web_scraper():
    from .web_scraper import get_tool
    return get_tool()

def get_sqlite_tool():
    from .sqlite_tool import get_tool
    return get_tool()

def get_mermaid_tool():
    from .mermaid_tool import get_tool
    return get_tool()

def get_graphviz_tool():
    from .graphviz_tool import get_tool
    return get_tool()


def get_default_tools() -> list[Tool]:
    """Return the default built-in tools for the command line interface."""

    return [get_web_scraper(), get_sqlite_tool()]

__all__ = [
    "get_web_scraper",
    "get_sqlite_tool",
    "get_mermaid_tool",
    "get_graphviz_tool",
    "get_default_tools",
    "Tool",
    "execute_tool",
]
