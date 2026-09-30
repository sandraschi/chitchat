"""FastMCP server - registers chitchat tools."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.server.middleware.logging import LoggingMiddleware

from . import __version__
from .archive import add_entry, delete_entry, get_entry, list_entries, stats
from .search import search_fleet_docs
from .topics import get_categories, get_topics, random_topic, topic_count

mcp = FastMCP(
    name="chitchat",
    version=__version__,
)

mcp.add_middleware(LoggingMiddleware())


@mcp.tool(name="chitchat_welcome", annotations={"readOnlyHint": True})
async def chitchat_welcome() -> dict:
    """Return a warm welcome with a random conversation starter.

    ## Return Format
    {"success": true, "welcome": str, "topic": {"category": str, "emoji": str, "topic": str}}
    """
    topic = random_topic()
    return {
        "success": True,
        "welcome": "Hey Sandra! Ready for a chitchat?",
        "topic": topic,
        "total_topics": topic_count(),
    }


@mcp.tool(name="chitchat_topics", annotations={"readOnlyHint": True})
async def chitchat_topics(
    category: str | None = None,
    random: bool = False,
) -> dict:
    """Browse curated chitchat conversation starters.

    ## Return Format
    {"success": true, "topics": [{"category": str, "emoji": str, "topic": str}, ...],
     "categories": [{"name": str, "emoji": str, "count": int}, ...]}

    ## Examples
    - chitchat_topics()
    - chitchat_topics(category="Tech & Tools")
    - chitchat_topics(random=true)
    """
    if random:
        topic = random_topic(category)
        return {
            "success": True,
            "topics": [topic] if topic else [],
            "categories": get_categories(),
        }

    topics = get_topics(category)
    return {
        "success": True,
        "topics": topics,
        "categories": get_categories(),
    }


@mcp.tool(name="chitchat_archive", annotations={"readOnlyHint": False})
async def chitchat_archive(
    action: str,
    topic: str | None = None,
    response: str | None = None,
    entry_id: str | None = None,
    tag: str | None = None,
    limit: int = 50,
) -> dict:
    """Manage archived chitchat conversations.

    Actions: 'add' (save a chat), 'list' (browse archive), 'get' (retrieve one),
    'delete' (remove one), 'stats' (archive summary).

    ## Return Format
    {"success": true, "action": str, "data": ...}

    ## Examples
    - chitchat_archive(action="add", topic="Best coffee?", response="Kaffee Alt Wien")
    - chitchat_archive(action="list", tag="vienna")
    - chitchat_archive(action="stats")
    """
    if action == "add":
        if not topic or not response:
            return {"success": False, "error": "topic and response required for add"}
        entry = add_entry(topic, response)
        return {"success": True, "action": "add", "data": entry}

    if action == "list":
        entries = list_entries(tag=tag, limit=limit)
        return {"success": True, "action": "list", "count": len(entries), "data": entries}

    if action == "get":
        if not entry_id:
            return {"success": False, "error": "entry_id required for get"}
        entry = get_entry(entry_id)
        return {"success": entry is not None, "action": "get", "data": entry}

    if action == "delete":
        if not entry_id:
            return {"success": False, "error": "entry_id required for delete"}
        deleted = delete_entry(entry_id)
        return {"success": deleted, "action": "delete", "deleted": deleted}

    if action == "stats":
        return {"success": True, "action": "stats", "data": stats()}

    return {"success": False, "error": f"Unknown action: {action}"}


@mcp.tool(name="chitchat_search_docs", annotations={"readOnlyHint": True})
async def chitchat_search_docs(
    query: str,
    limit: int = 5,
) -> dict:
    """Semantic search across the MCP fleet documentation via docsops.

    Cross-links to mcp-central-docs for discovering standards, patterns,
    and fleet-wide knowledge.

    ## Return Format
    {"success": true, "query": str, "results": [{"score": float, "content": str, ...}]}

    ## Examples
    - chitchat_search_docs(query="FastMCP portmanteau pattern")
    - chitchat_search_docs(query="start.ps1 port clearing", limit=3)
    """
    result = await search_fleet_docs(query=query, limit=limit)
    result["query"] = query
    return result
