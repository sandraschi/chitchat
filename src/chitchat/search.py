"""Crosslink to MCP Central Docs for semantic search of fleet documentation.

Calls the docs_mcp Starlette REST API on port 10795 (mcp-central-docs backend).
"""

from __future__ import annotations

from typing import Any

import httpx

from .config import config

DOCSOPS_BASE = config.docsops_base
DOCSOPS_REPO = "D:\\Dev\\repos\\mcp-central-docs"


async def search_fleet_docs(query: str, limit: int = 5) -> dict[str, Any]:
    """Search fleet documentation via the docsops Starlette API."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{DOCSOPS_BASE}/api/search",
                params={"q": query},
            )
            resp.raise_for_status()
            raw = resp.json()

            if isinstance(raw, list) and len(raw) > 0:
                data = []
                for r in raw[:limit]:
                    score = max(0.0, r.get("score", 0.0))
                    data.append(
                        {
                            "filename": r.get("filename", "unknown"),
                            "score": score,
                            "content": r.get("content", ""),
                            "relative_path": r.get("relative_path", "unknown"),
                        }
                    )
                return {
                    "success": True,
                    "query": query,
                    "message": f"Found {len(data)} results from fleet docs.",
                    "data": data,
                }

            return {"success": True, "query": query, "message": "No results found.", "data": []}

    except httpx.ConnectError:
        return {
            "success": False,
            "query": query,
            "message": "Fleet docs server is not running. Start it with:\n"
            f"  cd {DOCSOPS_REPO} && uv run python -m docs_mcp.server",
            "data": [],
        }
    except httpx.HTTPError as exc:
        return {"success": False, "message": f"Docsops error: {exc}", "data": []}
    except Exception as exc:
        return {"success": False, "message": f"Search error: {exc}", "data": []}


async def health_check() -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{DOCSOPS_BASE}/health")
            return {"reachable": resp.is_success, "status": resp.status_code}
    except Exception:
        return {"reachable": False, "status": None}
