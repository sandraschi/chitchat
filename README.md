# Chitchat

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
  <a href="https://glama.ai/mcp/servers"><img src="https://img.shields.io/badge/Glama-MCP_server-7c5cfc?style=flat-square" alt="Glama"></a>
</p>


> 📖 **[Installation Guide](INSTALL.md)** — quick start, manual setup, and troubleshooting

Conversation starters, archive, and fleet docs crosslink — a FastAPI + FastMCP webapp.

> **Tone:** Honest opinions welcome. Rants, no. We're AI out and proud — keep it constructive.

### Quick Install

```bash
# Claude Desktop / Cursor — install as MCP server
uvx mcpb install sandraschi/chitchat
```

### Sample Starters

| Category | Prompt |
|----------|--------|
| Ice Breakers | "If you could have dinner with any fictional character, who and why?" |
| Tech & Tools | "What dev tool changed your life that nobody talks about?" |
| Vienna & Local | "Best Kaffeehaus in Vienna that tourists haven't ruined yet?" |
| Hypotheticals | "You wake up as the opposite sex — first three things you do?" |
| Deep Thoughts | "What did you believe at 20 that you've completely reversed on?" |
| Food & Drink | "Desert island: one meal forever, what is it?" |

**Ports:** 10974 (backend) / 10975 (frontend) | Hermes dashboard: **10972** (WSL2)

**Fleet docs (docsops):** REST + MCP on **10795** (`mcp-central-docs` backend). Do not use **10791** — that port is fleet starts UI; avatar-mcp Prometheus metrics use **10790**.

## Quick Start

```powershell
git clone https://github.com/sandraschi/chitchat
cd chitchat
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap` to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup

If you don't have `just` installed:
.\web_sota\start.ps1
Or via root:
.\start.ps1
The backend starts in a hidden window on port 10974. The Vite frontend opens on port 10975. Your default browser opens automatically.

## What It Does

### Welcome & Topics
Browse **64 curated conversation starters** across 8 categories:

| Category | Topics |
|----------|--------|
| Ice Breakers | First-meeting openers |
| Tech & Tools | Dev workflows, hot takes, keyboard shortcuts |
| Deep Thoughts | Philosophy, future predictions, unlearning |
| Vienna & Local | Kaffeehaus, U-Bahn, Heuriger, Donauinsel |
| Creative & Weird | Movie pitches, fake words, animal rankings |
| Work & Life | Career advice, saying no, deep work |
| Food & Drink | Desert island meals, overrated trends, hangover cures |
| Hypotheticals | Teleportation, alien diplomacy, simulation theory |

### Archive
Save conversations with topics, responses, and tags. Browse, filter, and delete entries. JSON-backed in `archive/chitchat_archive.json`.

### Fleet Docs Crosslink
Semantic search across mcp-central-docs via the **docs_mcp** backend on port **10795** (`CHITCHAT_DOCSOPS_BASE`). Search standards, patterns, port registries, and fleet-wide documentation.

### Hermes Agent
Fleet conductor runs in WSL2. Start the dashboard from repo root:

```powershell
.\start_hermes.ps1
```

Hermes MCP connects to chitchat at `http://<windows-gateway>:10974/mcp` and docsops at `http://<windows-gateway>:10795/mcp` (gateway IP from WSL: `ip route show default`). Template: `hermes-fleet-config.yaml`.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Server health |
| GET | `/api/welcome` | Welcome message + random topic |
| GET | `/api/topics` | Browse topics (optional `?category=` and `?random=true`) |
| GET | `/api/archive` | List archived chats (`?tag=` filter) |
| GET | `/api/archive/{id}` | Get one entry |
| POST | `/api/archive` | Add entry `{topic, response, tags}` |
| DELETE | `/api/archive/{id}` | Delete entry |
| GET | `/api/archive/stats/summary` | Archive statistics |
| GET | `/api/docs/search?query=` | Fleet docs search |
| GET | `/api/docs/health` | Docsops availability check |

## MCP Tools

| Tool | Description |
|------|-------------|
| `chitchat_welcome` | Random topic greeting |
| `chitchat_topics` | Browse topics by category |
| `chitchat_archive` | Full archive CRUD |
| `chitchat_search_docs` | Crosslink to fleet docs |

## Project Structure

```
chitchat/
├── src/chitchat/
│   ├── __init__.py         # Package metadata
│   ├── __main__.py         # CLI entry: uv run chitchat --serve
│   ├── server.py           # FastMCP server + @mcp.tool() tools
│   ├── app.py              # FastAPI app + REST routes
│   ├── config.py           # Configuration (ports, paths)
│   ├── topics.py           # 64 curated topics across 8 categories
│   ├── archive.py          # JSON file-backed chat archive
│   └── search.py           # Docsops semantic search client
├── web_sota/
│   ├── src/
│   │   ├── App.tsx         # React app (welcome, topics, archive, docs tabs)
│   │   ├── main.tsx        # Entry point
│   │   └── index.css       # Dark theme
│   ├── index.html
│   ├── vite.config.ts      # Proxies /api → backend :10974
│   ├── package.json
│   ├── tsconfig.json
│   ├── start.ps1           # Port clearing + backend + frontend + browser
│   └── start.bat
├── archive/                 # Archived conversations (JSON)
├── tests/
├── pyproject.toml
├── start.ps1
├── start.bat
└── README.md
```

## Fleet Integration

- Ports from reserved range (10700-11000)
- Single-backend pattern: one FastAPI process serves REST + MCP at `/mcp`
- Crosslinks to `mcp-central-docs` via `docsops` semantic search
- `start.ps1` follows SOTA standard: port clearing, backend readiness poll, browser open
