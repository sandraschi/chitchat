# chitchat — MCP Server Capabilities

## Server Overview

Chitchat is a FastMCP 3.2 server that serves curated conversation starters organized into 8 categories (64 topics total), persists chat archives to a JSON file, and cross-links to the fleet MCP Central Docs (mcp-central-docs) for semantic documentation search. It runs as a dual FastAPI + FastMCP server on port 10974 (backend) with a Vite frontend on port 10975. The server provides a REST API for the web dashboard and an MCP interface for Claude Desktop / Cursor. It is designed as a conversational companion — ideal for breaking the ice, generating discussion topics, saving memorable chats, and discovering fleet standards via fleet docs search.

The server exposes 4 MCP tools (chitchat_welcome, chitchat_topics, chitchat_archive, chitchat_search_docs) and two FastMCP 3.2 native prompts. It also exposes 10 REST API endpoints under /api/ for the webapp. Data is stored in a JSON file (chitchat_archive.json) in the archive/ directory. The fleet docs crosslink connects to the docsops Starlette REST API on port 10795 (mcp-central-docs backend).

## Tools

### chitchat_welcome
**Purpose**: Return a warm welcome with a random conversation starter. No parameters required. Ideal as the first tool call in a new session to break the ice.
**Return Format**: {"success": bool, "welcome": str, "topic": {"category": str, "emoji": str, "topic": str}, "total_topics": int}
**Examples**:
- chitchat_welcome()

### chitchat_topics
**Purpose**: Browse curated chitchat conversation starters. Supports filtering by category and random selection.
**Parameters**:
- category (str | None): Filter by category name. Valid values: "Ice Breakers", "Tech & Tools", "Deep Thoughts", "Vienna & Local", "Creative & Weird", "Work & Life", "Food & Drink", "Hypotheticals".
- random (bool): If True, return a single random topic.
**Return Format**: {"success": bool, "topics": list, "categories": list}
**Examples**:
- chitchat_topics()
- chitchat_topics(category="Tech & Tools")
- chitchat_topics(random=True)

### chitchat_archive
**Purpose**: Manage archived chitchat conversations. Supports add, list, get, delete, and stats actions.
**Parameters**:
- action (str, required): One of "add", "list", "get", "delete", "stats".
- topic (str | None): Required for action="add".
- response (str | None): Required for action="add".
- entry_id (str | None): Required for action="get" and action="delete".
- tag (str | None): Optional filter for action="list".
- limit (int, default=50): Max entries for action="list".
**Return Format**: {"success": bool, "action": str, "data": ...}
**Examples**:
- chitchat_archive(action="add", topic="Best coffee?", response="Kaffee Alt Wien")
- chitchat_archive(action="list", tag="vienna")
- chitchat_archive(action="get", entry_id="abc123")
- chitchat_archive(action="stats")

### chitchat_search_docs
**Purpose**: Semantic search across the MCP fleet documentation via docsops. Cross-links to mcp-central-docs for discovering standards, patterns, and fleet-wide knowledge.
**Parameters**:
- query (str, required): Semantic search query.
- limit (int, default=5): Max results to return.
**Return Format**: {"success": bool, "query": str, "results": list, "message": str}
**Examples**:
- chitchat_search_docs(query="FastMCP portmanteau pattern")
- chitchat_search_docs(query="start.ps1 port clearing", limit=3)

## Prompts (FastMCP 3.2 Native)
The server registers 2 native prompts:
1. **ice_breaker**: "Start a new conversation with a random chitchat topic."
2. **fleet_knowledge**: "Search fleet documentation for best practices on a topic."

## REST API Endpoints

### GET /api/health
Returns server health and topic count.
Response: {"status": "ok", "version": "0.1.0", "topics_loaded": 64}

### GET /api/welcome
Returns a warm welcome with a random topic.
Response: {"welcome": str, "topic": dict, "total_topics": int}

### GET /api/topics
Query params: category (str | None), random (bool).
Returns topics list and categories metadata.

### GET /api/archive
Query params: tag (str | None), limit (int, default=50, max=200).
Returns paginated archived entries.

### GET /api/archive/{entry_id}
Returns a single archived entry by UUID.

### POST /api/archive
Body: {"topic": str, "response": str, "tags": list[str]}.
Creates a new archive entry. Returns the entry with id and created_at.

### DELETE /api/archive/{entry_id}
Deletes an entry by UUID. Returns {"deleted": true}.

### GET /api/archive/stats/summary
Returns archive statistics: total_entries, tags breakdown, archive path.

### GET /api/docs/search
Query params: query (str, required), limit (int, default=5, max=20).
Searches fleet documentation via docsops bridge.

### GET /api/docs/health
Returns docsops server reachability status.

## Configuration

### Environment Variables
- CHITCHAT_PORT (int, default=10974): Backend/HTTP port for the FastAPI server.
- CHITCHAT_FRONTEND_PORT (int, default=10975): Vite frontend dev server port.
- CHITCHAT_HOST (str, default="127.0.0.1"): Bind address for the FastAPI server.
- CHITCHAT_ARCHIVE_DIR (str): Custom path for the archive JSON file. Defaults to archive/ under the repo root.
- CHITCHAT_DOCSOPS_BASE (str, default="http://127.0.0.1:10795"): Base URL for the mcp-central-docs docsops REST API.
- CHITCHAT_LOG_LEVEL (str, default="info"): Logging level for uvicorn.

### CLI Arguments
- --serve: Start the HTTP/FastAPI server (not just stdio MCP).
- --port: Override backend port.

## Data Sources

### Conversation Topics
64 hardcoded conversation starters organized into 8 categories:
1. Ice Breakers (8 topics): Light, fun questions to start conversations.
2. Tech & Tools (8 topics): Programming, software, workflows, keyboard shortcuts.
3. Deep Thoughts (8 topics): Philosophical, future-focused, reflective questions.
4. Vienna & Local (8 topics): Vienna-specific culture, Kaffeehaus, U-Bahn, Heuriger.
5. Creative & Weird (8 topics): Imaginative, hypothetical, artistic prompts.
6. Work & Life (8 topics): Career advice, productivity, work habits.
7. Food & Drink (8 topics): Culinary opinions, cooking experiences, restaurant talk.
8. Hypotheticals (8 topics): Mind-bending scenarios and thought experiments.

### Archive Storage
JSON file at config.archive_dir / "chitchat_archive.json". Each entry has:
- id: 12-char hex UUID.
- topic: The conversation topic text.
- response: The saved response.
- tags: Optional list of string tags.
- created_at: ISO 8601 UTC timestamp.

### Fleet Docs Integration
Connects to mcp-central-docs Starlette REST API at 127.0.0.1:10795. Searches the fleet documentation index (LanceDB + SQLite FTS5) for semantic matches. Returns filename, score, content snippet, and relative_path for each match.

## Integration Points
- **mcp-central-docs**: Fleet documentation hub for cross-referencing standards.
- **Fleet web dashboard**: Vite React frontend at port 10975 consumes all /api/ endpoints.
- **Claude Desktop / Cursor**: Connects via stdio MCP transport for conversation and archive tools.

## Error Handling
All tools return structured dicts with "success" bool. On failure, an "error" key provides a human-readable message. REST API returns appropriate HTTP status codes (404 for missing entries, 400 for validation errors).

## Security
- CORS middleware allows all origins (development configuration).
- No authentication is enforced (design for local use).
- Archive file is stored as plain JSON — no encryption.
- Docsops bridge uses localhost HTTP with no authentication.

## Tool Parameter Reference

### chitchat_welcome Parameter Details
This tool takes no parameters. It is the simplest entry point — ideal for initial session greeting and discovering a random conversation starter. The response includes a human-readable welcome string, a structured topic object with category metadata (category name, category emoji, topic text), and a total_topics count showing available content across all categories.

### chitchat_topics Parameter Details
The category parameter accepts one of the 8 predefined category names. Matching is case-insensitive. When category is None, all 64 topics across all categories are returned in order. When random is True, a single topic is selected uniformly at random from the specified category (or from all categories if category is None). If the specified category name does not match any known category, an empty topics list is returned along with the full categories list — the caller can inspect categories to find valid names.

### chitchat_archive Parameter Details
The action parameter is a required string discriminator. Each action has distinct parameter requirements:
- "add": Requires topic (str) and response (str). Tags may be passed via the now-deprecated tag parameter or omitted. Returns the created entry with id, topic, response, tags, and created_at.
- "list": Optional tag (str) for filtering by tag substring matching. Optional limit (int, default 50, max 200) for pagination. Returns entries sorted by created_at descending.
- "get": Requires entry_id (str) — the 12-character hex UUID assigned at creation time. Returns the entry dict or null/None if not found.
- "delete": Requires entry_id (str). Returns {"deleted": true/false}.
- "stats": No additional parameters. Returns total_entries count, tags dict with per-tag usage counts, and archive_path.

### chitchat_search_docs Parameter Details
The query parameter is a free-text semantic search string passed to the docsops server. The limit parameter caps the results returned to the caller (default 5, max 20). The underlying docsops service uses LanceDB vector search with BAAI/bge-small-en-v1.5 embeddings combined with SQLite FTS5 BM25 ranking via reciprocal-rank fusion. Results include filename, BM25+vector hybrid score (0.0-1.0), a content snippet, and the relative file path within the fleet documentation repository. If the docsops server is unreachable, a clear error message is returned with instructions to start the mcp-central-docs server on port 10795.

## Data Flow Architecture

The chitchat server operates in two parallel modes:
1. **MCP Mode (stdio)**: Tools are called directly via FastMCP JSON-RPC over stdin/stdout. Used by Claude Desktop, Cursor, and other MCP-compatible IDE clients. The FastMCP server handles serialization and transport.
2. **HTTP Mode (FastAPI)**: The FastAPI app wraps the same tool logic behind REST endpoints. The FastMCP server is mounted at /mcp for HTTP MCP transport. The REST API at /api/* is consumed by the Vite React web dashboard.

The server startup flow is:
1. Config is loaded from environment variables with sensible defaults.
2. Archive directory is created if it does not exist.
3. The FastAPI lifespan context manager initializes the FastMCP HTTP app.
4. The uvicorn server binds to the configured host:port.

When chitchat_search_docs is called, the flow is:
1. An HTTP GET is sent to the docsops server (default http://127.0.0.1:10795/api/search) with the query.
2. The docsops server searches its LanceDB vector index and SQLite FTS5 index.
3. Results are returned as a scored list of document snippets.
4. If the docsops server is unreachable, the error is caught and a helpful message is returned.

## Category Reference

The 8 predefined topic categories each contain 8 hand-curated conversation starters:

1. **Ice Breakers** (emoji: ice): Light, universally accessible questions designed to start conversations with minimal friction. Example: "What's the most unexpectedly useful skill you've picked up?"
2. **Tech & Tools** (emoji: tools): Programming, software, and technology-focused questions. Covers tools, workflows, keyboard shortcuts, and tech opinions. Example: "What tool or workflow improved your life the most this year?"
3. **Deep Thoughts** (emoji: think): Philosophical, reflective questions about humanity, knowledge, beliefs, and future challenges. Example: "What problem does humanity need to solve in the next 50 years?"
4. **Vienna & Local** (emoji: castle): Vienna-specific questions about local culture, Kaffeehaus culture, U-Bahn stations, Heuriger, and neighborhood tips. Example: "What's the most underrated spot in Vienna that tourists never find?"
5. **Creative & Weird** (emoji: art): Imaginative, speculative, and artistic prompts. Includes movie pitches, conspiracy theories, fake words, and holiday design. Example: "If you could pitch a movie and get it greenlit tomorrow, what's the premise?"
6. **Work & Life** (emoji: scale): Career advice, productivity habits, deep work strategies, and workplace culture questions. Example: "What's the best career advice you've ever received?"
7. **Food & Drink** (emoji: plate): Culinary opinions, cooking experiences, restaurant recommendations, and food debates. Example: "What's your desert island meal — one dish forever?"
8. **Hypotheticals** (emoji: crystal_ball): Mind-bending scenarios, simulation theory, teleportation, mind-reading, and alternate reality questions. Example: "You get 100 million euros but someone you don't know dies. Your move?"

## Performance Considerations
- The topic list is hardcoded and loaded from memory — no I/O or database overhead.
- Archive operations use synchronous file I/O on a JSON file. For archives with more than 10,000 entries, consider periodic compaction.
- Docsops search has a 10-second HTTP timeout. Slow responses return an empty result set rather than blocking indefinitely.
- The FastAPI server uses standard uvicorn workers with no special async tuning. For high traffic, increase uvicorn worker count.
- There is no connection pooling or caching layer — each search_docs call makes a fresh HTTP connection to the docsops server.

## Deployment Options
The chitchat server supports multiple deployment configurations depending on the use case. For local development, use `uv run python -m chitchat` which starts the server in stdio mode (JSON-RPC over stdin/stdout). For integration with the web dashboard, use `uv run python -m chitchat --serve` which starts the FastAPI HTTP server on port 10974 with the MCP surface mounted at /mcp. For production deployment, consider running behind a reverse proxy (nginx, Caddy) for TLS termination and rate limiting. The server is stateless in terms of topics (loaded from memory) but stateful for archive data (stored as a JSON file). For multi-instance deployments, the archive JSON file must be shared via a network filesystem or replaced with a database backend. The server can also be containerized using Docker: build an image with the source code and dependencies, mount the archive directory as a volume, and expose the appropriate ports. The small footprint (~50MB with dependencies) makes it suitable for deployment on low-resource environments like Raspberry Pi or cloud VMs with 256MB RAM.

## Fleet Integration Architecture
chitchat is designed as part of the larger Sandra MCP fleet ecosystem. It integrates with mcp-central-docs (docsops server on port 10795) for cross-referencing fleet documentation standards, patterns, and guidelines. The fleet docs search bridges chitchat with the broader fleet knowledge base, making it a conversational entry point for discovering fleet-wide information. When the docsops server is running, chitchat becomes a natural-language interface to the entire fleet documentation corpus. Future integration plans include connection to the fleet-agent-mcp for automated documentation updates, and to the depot-mcp for storing and retrieving conversation archives across sessions. The port allocation follows fleet convention: backend on 10974, frontend on 10975 (adjacent even-odd pair within the 10700-11500 fleet range). The server registers with the MetaMCP orchestrator for fleet health monitoring and automatic discovery.

## Logging and Monitoring
The server uses Python's standard logging module with configurable log level via CHITCHAT_LOG_LEVEL (default "info"). Log output goes to stderr in standard format: "%(asctime)s [%(name)s] %(levelname)s: %(message)s". The FastMCP LoggingMiddleware captures all MCP tool calls and responses, logging method names, parameters, and execution outcomes. For production monitoring, configure log aggregation via the fleet's Loki/Grafana stack (ports 12000-12006). Key metrics to monitor include: chitchat_welcome calls (session starts), chitchat_topics calls (discovery patterns), chitchat_archive operations (data growth rate), docs search success rate vs. connection errors, and archive file size growth. The in-memory nature of topics means no database connection monitoring is needed. Archive file I/O errors (permissions, disk full) are logged at ERROR level and should trigger alerts.

## Error Recovery Procedures
When chitchat_search_docs returns a connection error ("Fleet docs server is not running"), start the mcp-central-docs server: `cd D:\Dev\repos\mcp-central-docs && uv run python -m docs_mcp.server`. This binds to port 10795. If the archive file becomes corrupted (JSON decode error), the archive module returns an empty list and logs a warning. The corrupt file is not overwritten — fix or remove it manually. If the server fails to start due to a port conflict, identify the process on the target port with `Get-NetTCPConnection -LocalPort 10974` and terminate it with `Stop-Process -Id $pid -Force`. For persistent startup issues, check that the archive directory is writable and that the Python environment has all required dependencies installed.

## Example Session Flows

### Flow 1: Getting Started
A new user opens the chitchat server for the first time. They call chitchat_welcome() and receive a random topic from the Ice Breakers category. The welcome message includes the topic text, its category with emoji, and a count of all available topics. The user then explores by category with chitchat_topics(category="Vienna & Local") to find location-specific conversation starters. After a discussion, they save the conversation with chitchat_archive(action="add", topic="Best Heuriger?", response="Weingut Fuhrgassl-Huber in Neustift"). Later that week, they review their saved conversations with chitchat_archive(action="list") and check how many entries they have with chitchat_archive(action="stats").

### Flow 2: Fleet Documentation Research
A fleet developer is implementing a Tauri NSIS installer for a new MCP server. They use chitchat_search_docs(query="Tauri NSIS build pipeline") to find the relevant fleet standard documentation. The search returns the top results from mcp-central-docs with relevance scores. They refine with chitchat_search_docs(query="NSIS installer hooks", limit=3) to find specific hook patterns. After implementing the installer, they save a note about what they learned with chitchat_archive(action="add", topic="Tauri build learnings", response="Use PREINSTALL hooks to kill both operator and backend processes", tags=["technical", "tauri"]).

### Flow 3: Daily Team Warm-Up
Every morning, a team lead calls chitchat_topics(category="Ice Breakers", random=True) to get a conversation starter for the daily standup. They save the best responses to the archive with the "standup" tag. Over months, they build a searchable archive of team discussions, personal insights, and shared experiences. When a new team member joins, the lead shares archived topics tagged "best-of" to help them get to know the team culture.

## Comparison with Other Fleet Tools
chitchat occupies a unique niche in the fleet ecosystem. Unlike meta-mcp (orchestration and fleet management), arxiv-mcp (research paper discovery), or calibre-mcp (ebook library management), chitchat is purely conversational with no domain-specific data source. It is the fleet's social layer, providing ice breakers, conversation starters, and a chat archive. The fleet docs search is a secondary feature that provides a conversational entry point into the mcp-central-docs documentation corpus. For dedicated documentation search, the docsops MCP server (port 10795) provides more comprehensive search capabilities with direct access to the full documentation index.

## Tool Composition and Sequencing
chitchat tools can be composed into multi-step workflows. A typical conversational flow starts with chitchat_welcome() to get an initial topic, then chitchat_topics(category="Deep Thoughts", random=True) for a deeper follow-up, then chitchat_archive(action="add") to save the best responses, then chitchat_search_docs to find supporting fleet documentation, and finally chitchat_archive(action="stats") to review the accumulated knowledge. This pattern creates a rich, searchable archive that grows more valuable over time. The archive serves as both a personal journal and a team knowledge base. The docs search feature bridges conversational content with formal fleet documentation, creating a feedback loop where conversations inspire documentation searches and documentation inspires new conversations. The categories are designed to support different conversational contexts: ice breakers for new groups, tech topics for professional discussions, deep thoughts for reflective conversations, Vienna topics for location-specific chat, creative prompts for brainstorming, work topics for professional development, food topics for social settings, and hypotheticals for imaginative exploration.

## Server Architecture Details
The chitchat server is built on FastMCP 3.2 with dual transport support. The FastMCP instance is created in server.py with logging middleware and MCP tool decorators. The FastAPI app in app.py mounts the FastMCP HTTP surface at /mcp and adds REST endpoints under /api/. The lifespan context manager initializes and tears down the FastMCP HTTP router. REST endpoints mirror the MCP tools but add HTTP-specific features like Query parameters, path parameters, and request body validation. The CORS middleware is configured to allow all origins for development flexibility. The archive module uses synchronous file I/O with JSON serialization — for high-concurrency scenarios, replace with an async database backend. The topics module is entirely in-memory with no I/O dependencies. The search module uses httpx for async HTTP calls to the docsops server with configurable timeout and error handling.

## Content Moderation
The chitchat server performs no content moderation on archive entries or search queries. All text is stored and transmitted as-is. Users are responsible for the content they save and search for. The archive file is stored locally and is not shared with any external service. The docs search feature sends queries to a local docsops server — no third-party services are involved. If content moderation is desired, implement a middleware that filters archive content before storage or display. The server does not log the content of individual search queries beyond what the standard logging module captures. For compliance with data protection regulations, implement a cleanup policy that automatically removes archive entries older than a configurable retention period.

## Backup and Recovery
The chitchat archive file should be included in regular system backups. To back up the archive, copy the chitchat_archive.json file from the configured CHITCHAT_ARCHIVE_DIR to a backup location. The server can continue running during backup since it reads the file fresh on each operation. To restore from backup, stop the server, replace the archive file with the backup copy, and restart the server. The topics are hardcoded and require no backup. To migrate the archive to a new server, copy the archive file to the new machine's CHITCHAT_ARCHIVE_DIR and start the server. The server creates the archive file automatically if it does not exist. For disaster recovery, maintain at least three backup copies: one local, one on a different drive, and one offsite (cloud storage or physical media). Test backup restoration periodically to verify data integrity.

## Rate Limiting and Resource Management
The chitchat server has no built-in rate limiting. In multi-user scenarios, consider adding rate limiting middleware to the FastAPI app. The archive file grows linearly with each saved conversation — for high-volume use, implement archive rotation or database-backed storage. The docs search HTTP client has a 10-second timeout — multiple concurrent searches may exhaust the connection pool. The default httpx.AsyncClient has a connection pool limit of 10 concurrent connections. For production deployments, increase this limit or add connection pooling. The JSON archive file is read entirely into memory on each operation — files larger than 100MB will cause significant latency. Monitor archive file size with the stats operation and implement archiving or compaction as needed.

## Development and Testing
To develop chitchat locally, clone the repository and run `uv sync` to install dependencies. The server can be tested in stdio mode by running `uv run python -m chitchat` and sending JSON-RPC messages via stdin. For HTTP testing, run `uv run python -m chitchat --serve` and use curl or the web dashboard. The tests are located in tests/ and can be run with `uv run pytest`. Key test areas include topic selection (random, by category, edge cases), archive CRUD operations (add with missing parameters, delete nonexistent entry, list with tag filter), and docs search (successful results, connection error). The FastAPI test client can be used for REST API integration tests without starting the server.

## Version History and Changelog
- 0.1.0 (2026-06-19): Initial release. 64 conversation starters in 8 categories. Archive JSON storage with add/list/get/delete/stats. Fleet docs search via docsops bridge. FastAPI REST API with 10 endpoints. FastMCP 3.2 MCP surface with 4 tools and 2 native prompts. CORS enabled for all origins.

## Extension Points
- **Adding new topics**: Edit the CATEGORIES list in src/topics.py. Each TopicCategory needs a name, emoji, and list of topic strings. No code changes beyond data.
- **Adding new archive backends**: The archive.py module abstracts file storage behind function calls. Replace with a SQLite or PostgreSQL backend by implementing the same interface.
- **Integrating additional docs sources**: The search.py module can be extended to query additional documentation repositories by adding new search providers.
- **Custom frontends**: Any HTTP client can consume the REST API. The OpenAPI schema is available at /docs when the server is running.
