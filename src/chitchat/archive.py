"""Conversation archive - JSON file-backed storage for chitchat sessions."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

from .config import config

ARCHIVE_FILE = config.archive_dir / "chitchat_archive.json"


def _load() -> list[dict]:
    if not ARCHIVE_FILE.exists():
        return []
    try:
        return json.loads(ARCHIVE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(entries: list[dict]) -> None:
    ARCHIVE_FILE.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def add_entry(topic: str, response: str, tags: list[str] | None = None) -> dict:
    entry = {
        "id": uuid4().hex[:12],
        "topic": topic,
        "response": response,
        "tags": tags or [],
        "created_at": datetime.now(UTC).isoformat(),
    }
    entries = _load()
    entries.append(entry)
    _save(entries)
    return entry


def list_entries(tag: str | None = None, limit: int = 50) -> list[dict]:
    entries = _load()
    if tag:
        entries = [e for e in entries if tag.lower() in [t.lower() for t in e.get("tags", [])]]
    return sorted(entries, key=lambda e: e["created_at"], reverse=True)[:limit]


def get_entry(entry_id: str) -> dict | None:
    entries = _load()
    for e in entries:
        if e["id"] == entry_id:
            return e
    return None


def delete_entry(entry_id: str) -> bool:
    entries = _load()
    before = len(entries)
    entries = [e for e in entries if e["id"] != entry_id]
    if len(entries) == before:
        return False
    _save(entries)
    return True


def stats() -> dict:
    entries = _load()
    tags: dict[str, int] = {}
    for e in entries:
        for t in e.get("tags", []):
            tags[t] = tags.get(t, 0) + 1
    return {
        "total_entries": len(entries),
        "tags": tags,
        "archive_path": str(ARCHIVE_FILE),
    }
