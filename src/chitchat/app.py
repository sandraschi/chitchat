"""FastAPI application - REST API for chitchat webapp."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .archive import add_entry, delete_entry, get_entry, list_entries, stats
from .search import health_check, search_fleet_docs
from .server import mcp
from .topics import get_categories, get_topics, random_topic, topic_count

_mcp_http_app = mcp.http_app(path="/")


@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging

    logger = logging.getLogger("chitchat")
    async with _mcp_http_app.router.lifespan_context(_mcp_http_app):
        logger.info("Chitchat is ready - conversation starters loaded (%d topics)", topic_count())
        yield


app = FastAPI(
    title="Chitchat",
    description="Conversation starters, archive, and fleet docs crosslink",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Welcome / Status ────────────────────────────────────────────────


@app.get("/api/health")
async def api_health():
    return {"status": "ok", "version": __version__, "topics_loaded": topic_count()}


@app.get("/api/welcome")
async def api_welcome():
    topic = random_topic()
    return {
        "welcome": "Hey! Ready for a chitchat?",
        "topic": topic,
        "total_topics": topic_count(),
    }


# ── Topics ──────────────────────────────────────────────────────────


@app.get("/api/topics")
async def api_topics(
    category: str | None = Query(None),
    random: bool = Query(False),
):
    if random:
        topic = random_topic(category)
        return {"topics": [topic] if topic else [], "categories": get_categories()}
    return {"topics": get_topics(category), "categories": get_categories()}


# ── Archive ─────────────────────────────────────────────────────────


@app.get("/api/archive")
async def api_archive_list(
    tag: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    entries = list_entries(tag=tag, limit=limit)
    return {"entries": entries, "count": len(entries)}


@app.get("/api/archive/{entry_id}")
async def api_archive_get(entry_id: str):
    entry = get_entry(entry_id)
    if not entry:
        return {"error": "Not found"}, 404
    return entry


@app.post("/api/archive")
async def api_archive_add(body: dict):
    topic = body.get("topic", "")
    response = body.get("response", "")
    tags = body.get("tags", [])
    if not topic or not response:
        return {"error": "topic and response required"}, 400
    entry = add_entry(topic, response, tags)
    return entry


@app.delete("/api/archive/{entry_id}")
async def api_archive_delete(entry_id: str):
    deleted = delete_entry(entry_id)
    if not deleted:
        return {"error": "Not found"}, 404
    return {"deleted": True}


@app.get("/api/archive/stats/summary")
async def api_archive_stats():
    return stats()


# ── Fleet Docs Crosslink ────────────────────────────────────────────


@app.get("/api/docs/search")
async def api_docs_search(
    query: str = Query(...),
    limit: int = Query(5, ge=1, le=20),
):
    result = await search_fleet_docs(query, limit)
    return result


@app.get("/api/docs/health")
async def api_docs_health():
    return await health_check()


# ── Mount MCP ───────────────────────────────────────────────────────

app.mount("/mcp", _mcp_http_app)
