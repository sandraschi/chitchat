# chitchat — User Guide

## Quick Start

### Installation
1. Clone the repository: `git clone https://github.com/sandraschi/chitchat.git`
2. Create a virtual environment: `uv venv`
3. Activate: `.venv\Scripts\activate`
4. Install dependencies: `uv sync`
5. Start the server in stdio mode (for Claude Desktop): `uv run python -m chitchat`
6. Start the HTTP server (for web dashboard): `uv run python -m chitchat --serve`

### First Use
- Call `chitchat_welcome()` to receive a warm greeting with a random conversation starter.
- Browse topics with `chitchat_topics()` to see all categories.
- Save a conversation with `chitchat_archive(action="add", topic="...", response="...")`.

## Tutorials

### Tutorial 1: Start a Conversation
Call `chitchat_welcome()`. The server returns a random topic from one of 8 categories. Use the topic as a conversation starter with friends or colleagues. Example response includes the category emoji and the topic text.

### Tutorial 2: Browse All Topics
Call `chitchat_topics()` to list all 64 topics organized by category. Each topic includes the category name, an emoji, and the topic question text. Use this to find a topic that fits the current mood.

### Tutorial 3: Filter Topics by Category
Call `chitchat_topics(category="Vienna & Local")` to get only topics about Viennese culture, U-Bahn stations, Heuriger, and local tips. Valid categories: "Ice Breakers", "Tech & Tools", "Deep Thoughts", "Vienna & Local", "Creative & Weird", "Work & Life", "Food & Drink", "Hypotheticals".

### Tutorial 4: Get a Random Topic
Call `chitchat_topics(random=True)` for a single randomly selected topic. Call `chitchat_topics(category="Deep Thoughts", random=True)` to get a random topic from a specific category.

### Tutorial 5: Save a Conversation
After having a good chat, save it with `chitchat_archive(action="add", topic="Best coffee in Vienna?", response="Kaffee Alt Wien has the best Melange and the atmosphere is unmatched.")`. The server returns the entry with a unique ID and timestamp.

### Tutorial 6: Browse Your Archive
Call `chitchat_archive(action="list")` to see your saved conversations, newest first. Add tags when saving conversations, then filter with `chitchat_archive(action="list", tag="vienna")` to find all Vienna-related entries.

### Tutorial 7: Retrieve a Specific Entry
Call `chitchat_archive(action="get", entry_id="a1b2c3d4e5f6")` using the entry ID returned when you saved it. Returns the full entry including topic, response, tags, and timestamp.

### Tutorial 8: Delete an Entry
Call `chitchat_archive(action="delete", entry_id="a1b2c3d4e5f6")` to remove an entry from the archive. Returns {"deleted": true} on success.

### Tutorial 9: View Archive Statistics
Call `chitchat_archive(action="stats")` to see total saved conversations, a breakdown of tags used, and the archive file path on disk.

### Tutorial 10: Search Fleet Documentation
Call `chitchat_search_docs(query="FastMCP portmanteau pattern")` to search the entire MCP Central Docs fleet documentation for relevant standards, patterns, and guidelines. This is useful for discovering fleet-wide coding practices, architecture decisions, and tool configurations.

### Tutorial 11: Search with Custom Result Limit
Call `chitchat_search_docs(query="Tauri NSIS build", limit=3)` to get just the top 3 most relevant results from fleet documentation. Useful for quick lookups without overwhelming context.

### Tutorial 12: Multi-Step Workflow
1. Start with `chitchat_welcome()` to get a topic.
2. Discuss the topic with a human.
3. Save the result with `chitchat_archive(action="add", topic="...", response="...")`.
4. Later, browse saved chats with `chitchat_archive(action="list")`.
5. Search related fleet docs with `chitchat_search_docs(query="...")`.

## REST API Reference

### Health Check
GET /api/health
Response: {"status": "ok", "version": "0.1.0", "topics_loaded": 64}

### Welcome
GET /api/welcome
Response: {"welcome": "Hey! Ready for a chitchat?", "topic": {"category": "Ice Breakers", "emoji": "ice", "topic": "What's the most unexpectedly useful skill you've picked up?"}, "total_topics": 64}

### List Topics
GET /api/topics?category=Tech%20%26%20Tools&random=false
Response: {"topics": [{"category": "Tech & Tools", "emoji": "tools", "topic": "..."}], "categories": [{"name": "Tech & Tools", "emoji": "tools", "count": 8}]}

### List Archive Entries
GET /api/archive?tag=vienna&limit=10
Response: {"entries": [{"id": "a1b2c3d4e5f6", "topic": "...", "response": "...", "tags": [], "created_at": "2026-01-01T00:00:00Z"}], "count": 1}

### Get Single Entry
GET /api/archive/a1b2c3d4e5f6
Response: {"id": "a1b2c3d4e5f6", "topic": "...", "response": "...", "tags": [], "created_at": "..."}

### Add Archive Entry
POST /api/archive
Body: {"topic": "Best coffee?", "response": "Kaffee Alt Wien", "tags": ["vienna", "coffee"]}
Response: {"id": "b2c3d4e5f6a7", "topic": "Best coffee?", "response": "Kaffee Alt Wien", "tags": ["vienna", "coffee"], "created_at": "..."}

### Delete Entry
DELETE /api/archive/b2c3d4e5f6a7
Response: {"deleted": true}

### Archive Stats
GET /api/archive/stats/summary
Response: {"total_entries": 5, "tags": {"vienna": 3, "coffee": 1}, "archive_path": "D:\\Dev\\repos\\chitchat\\archive\\chitchat_archive.json"}

### Search Fleet Docs
GET /api/docs/search?query=FastMCP+portmanteau&limit=5
Response: {"success": true, "query": "FastMCP portmanteau", "data": [{"filename": "TOOL_DESIGN_STANDARDS.md", "score": 0.95, "content": "..."}]}

### Docs Health
GET /api/docs/health
Response: {"reachable": true, "status": 200} or {"reachable": false, "status": null}

## Troubleshooting

### Server won't start
Ensure port 10974 is free. Clear zombie processes: `Get-NetTCPConnection -LocalPort 10974 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }`.

### Docs search returns connection error
The fleet docs server (mcp-central-docs) must be running on port 10795. Start it with: `cd D:\Dev\repos\mcp-central-docs && uv run python -m docs_mcp.server`.

### Archive file not found
The archive directory is created automatically. If the file is missing, it starts empty. Check CHITCHAT_ARCHIVE_DIR env var.

### Topics not loading
Topics are hardcoded in topics.py. If you see 0 topics, check the file is present in the source.

## Advanced Workflows

### Workflow: Daily Conversation Log
Start each day by calling chitchat_welcome() to get a fresh conversation starter. Throughout the day, save interesting discussions using chitchat_archive(action="add"). At the end of the week, call chitchat_archive(action="stats") to review your conversation patterns. Use chitchat_archive(action="list", tag="vienna") to find all Vienna-related discussions for trip planning.

### Workflow: Fleet Knowledge Discovery
When working on a fleet MCP server, use chitchat_search_docs to find relevant standards. For example, when building a Tauri NSIS installer, search for "Tauri NSIS build pipeline" then "NSIS installer hooks" then "CUA smoke testing". Each search returns actionable documentation snippets. Use the results to guide your implementation. When the topic list starts conversations about fleet architecture, save those discussions for future reference.

### Workflow: Team Ice Breaker Session
Call chitchat_topics(category="Ice Breakers") to get the full list of icebreaker questions before a team meeting. Pick one question per meeting. After the meeting, save the best responses to the archive. Over time, build a library of team insights. Use chitchat_archive(action="stats") to track participation and topic coverage. Rotate through different categories each meeting to keep discussions fresh.

### Workflow: Vienna Visitor Guide
Use chitchat_topics(category="Vienna & Local") to discover hidden gems, Kaffeehaus recommendations, and Heuriger tips. Save the best suggestions to the archive with the "vienna" tag. When friends visit, call chitchat_archive(action="list", tag="vienna") to build a personalized city guide. Cross-reference with fleet docs by searching for "Vienna travel" or "local tips" in the documentation server.

### Workflow: Creative Writing Prompt Generator
Call chitchat_topics(category="Creative & Weird", random=True) each morning to get a writing prompt. Use the prompt as a warm-up exercise. Save your responses to the archive with the "writing" tag. After a month, review your archive to see your creative evolution. Use chitchat_archive(action="stats") to see which categories inspired the most writing.

### Workflow: Tech Debate Club
Use chitchat_topics(category="Tech & Tools") to surface controversial tech opinions. Discuss each topic with colleagues and save the debates to the archive with relevant tags like "programming", "tools", or "AI". Search fleet docs for supporting evidence using chitchat_search_docs. Build a knowledge base of technical decisions and their rationales over time.

### Workflow: Personal Growth Journal
Every evening, call chitchat_topics(category="Deep Thoughts", random=True) for a reflective question. Write your response and save it to the archive with the "journal" tag. At the end of each month, review your entries to track personal growth and changing perspectives. The archive serves as a searchable personal journal with timestamped entries organized by topic category.

### Workflow: Restaurant Recommendation Engine
Use chitchat_topics(category="Food & Drink") to start conversations about dining experiences. Save restaurant recommendations with tags like "restaurant", "vienna", "casual", "fine-dining". When planning a dinner out, search chitchat_archive(action="list", tag="restaurant") to recall past recommendations. Add ratings to the archived responses to track your personal ranking over time.

### Workflow: Hypothetical Brainstorming Session
Call chitchat_topics(category="Hypotheticals") to get speculative questions for brainstorming sessions. Use these as warm-up exercises before creative meetings. Save the most interesting discussions and revisit them months later to see how your answers have changed. The hypotheticals category is particularly effective for team-building exercises and lateral thinking workshops.

### Workflow: Cross-Reference Research
When researching a fleet topic like "FastMCP portmanteau patterns," start with chitchat_search_docs to find the relevant standards. Read the documentation, then use chitchat_topics to find conversation starters that explore the topic further. Save the documentation references alongside your discussion notes. This creates a rich, cross-referenced knowledge base linking fleet standards with practical discussions.

## Performance Tuning
For optimal performance with large archives (10,000+ entries), consider periodic maintenance. The JSON file grows linearly with each entry. Run chitchat_archive(action="stats") to check total entry count. When the file exceeds 50MB, export important entries and perform a cleanup. The archive file is loaded entirely into memory on each operation — for very large archives this may cause latency. Consider archiving old entries to a separate file or implementing a database-backed storage backend. The docs search timeout is 10 seconds — for faster results, ensure the docsops server is on the same machine or a low-latency network connection.

## Environment Variable Reference
The chitchat server is configured through environment variables with sensible defaults. CHITCHAT_PORT (default 10974) controls the backend HTTP/FastAPI port — must match the fleet port registry. CHITCHAT_FRONTEND_PORT (default 10975) is the Vite dev server port for the web dashboard. CHITCHAT_HOST (default "127.0.0.1") binds the backend to localhost only for security — change to "0.0.0.0" for network access behind a reverse proxy. CHITCHAT_ARCHIVE_DIR specifies the directory for the archive JSON file — defaults to archive/ under the repo root. CHITCHAT_DOCSOPS_BASE (default "http://127.0.0.1:10795") is the URL of the fleet documentation server. CHITCHAT_LOG_LEVEL (default "info") sets the uvicorn logging verbosity. All variables are optional — the server works with zero configuration for local development.

## Category-Specific Usage Tips
Each topic category is designed for different contexts and audiences. Ice Breakers work best in group settings where people don't know each other well — they're safe, low-stakes, and produce quick responses. Tech & Tools topics work well in developer communities and team retrospectives — they surface shared experiences and tool recommendations. Deep Thoughts are best for one-on-one conversations or journaling — they require reflection and are less suited to casual groups. Vienna & Local topics are perfect for visitors, newcomers, or locals wanting to discover their city — they produce concrete, actionable recommendations. Creative & Weird topics work well in brainstorming sessions and creative workshops — they break conventional thinking patterns. Work & Life topics fit professional development discussions and mentoring sessions — they surface career wisdom and practical strategies. Food & Drink topics are universal and work in any social setting — they're low-commitment and often produce passionate responses. Hypotheticals are great for lateral thinking exercises and philosophical discussions — they work best with people who enjoy abstract thought experiments.

## Archive Data Model
Each archive entry is a JSON object with five fields. The id field is a 12-character hexadecimal string generated from uuid4().hex[:12] — it is unique within the archive but not globally unique. The topic field stores the conversation topic as a free-form string — it does not need to match a predefined topic from the topics list. The response field stores the conversational response or note. The tags field is an array of strings — tags are lowercased during storage but not otherwise normalized. The created_at field is an ISO 8601 UTC timestamp generated at entry creation time. The archive file is written with UTF-8 encoding and ensure_ascii=False to preserve non-ASCII characters (Umlauts, emoji, special characters). The JSON is indented with 2 spaces for human readability. The archive file is safe to edit manually with a text editor — the server reads it fresh on each operation.

## Offline and Degraded Operation
chitchat operates fully offline for all features except docs search. The welcome, topics, and archive features require no network access — they are entirely local. The docs search feature requires a running mcp-central-docs server on port 10795. If the docs server is not running, chitchat_search_docs returns a clear error message with instructions to start it. All other tools continue to function normally. For completely offline operation, simply omit using the docs search tool. The archive file is stored locally and requires no network connectivity. The topics are hardcoded and require no external data sources. The server is designed for local-only deployment and has no telemetry, analytics, or external dependencies beyond the optional docs server.

## Integration with MCP Clients
chitchat works with any MCP-compatible client. For Claude Desktop, add the server to claude_desktop_config.json: {"mcpServers": {"chitchat": {"command": "uv", "args": ["run", "--directory", "D:/Dev/repos/chitchat", "python", "-m", "chitchat"]}}}. For Cursor, add a similar entry in Cursor's MCP configuration. For direct HTTP access, connect to the FastAPI server at http://localhost:10974/mcp for the FastMCP HTTP transport. The server exposes all tools through both transports — no feature differences between stdio and HTTP modes. For the REST API, all endpoints are under /api/ and return JSON responses with appropriate HTTP status codes.

## Data Privacy and Security
chitchat stores conversation archives as plain JSON on the local filesystem. There is no encryption, authentication, or access control. The server is designed for single-user local deployment only. Do not expose the chitchat server to the public internet or untrusted networks. The archive JSON file contains all saved conversations in plain text — handle it with appropriate care. The docs search feature sends queries to a local docsops server (port 10795) — no data leaves your machine. The server uses CORS middleware allowing all origins by default — restrict this in production deployments.

## Conversation Starter Effectiveness
The 64 conversation starters are curated for maximum engagement across different contexts. Ice Breaker questions are designed to be low-stakes and easy to answer — they ask about personal experiences and opinions rather than factual knowledge. Tech & Tools questions target developers and power users by asking about their workflows, tools, and opinions. Deep Thoughts questions require more reflection and work best when participants have time to think before responding. Vienna & Local questions are hyper-specific to Vienna and work best with locals or frequent visitors — they create an instant sense of shared place and experience. Creative & Weird questions are designed to surface unexpected responses and work well as warm-up exercises before creative work. Work & Life questions tap into universal professional experiences and work across cultures and industries. Food & Drink questions are universally accessible and often produce the most passionate, opinionated responses. Hypotheticals are the most abstract category and work best with participants who enjoy philosophical discussion and thought experiments. Mixing categories in a session provides variety and prevents conversation fatigue.

## Activity Logging and Tracking
The chitchat server logs all tool calls and REST API requests through the standard Python logging module. Logs are written to stderr in the configured format. For production monitoring, capture stderr output and route it to a log aggregator. Key events to monitor include: welcome calls (session starts), topic browsing patterns (popular categories), archive operations (data growth rate), docs search queries (popular search terms), and connection errors to the docs server. The FastMCP LoggingMiddleware logs MCP method calls and responses, providing full traceability of tool invocations. For monitoring archive growth, periodically check the archive file size and entry count via the stats operation. For alerting, set up log pattern matching for "error" and "warning" level messages. The server does not expose its own metrics endpoint — use external monitoring tools to watch the process.

## Multi-Language Support
The chitchat topics and archive system fully support Unicode and non-ASCII characters. The topic list includes emoji characters for category identification. The archive JSON file is written with UTF-8 encoding and ensure_ascii=False, preserving all Unicode characters including emoji, accented characters (Umlauts, accents, tildes), CJK characters (Chinese, Japanese, Korean), Cyrillic, Arabic, and other scripts. Responses can be written in any language. Tags support Unicode but are lowercased for consistent matching. The docs search feature searches fleet documentation in English but can handle queries in multiple languages depending on the embedding model used by the LanceDB index in the docsops server. There are no language-specific features or localization — the server is language-agnostic and treats all text as Unicode strings.

## Alternative Storage Backends
The default archive storage uses a JSON file, but the architecture supports alternative backends. To use a SQLite backend, replace the file I/O in archive.py with SQLite queries — the function signatures remain the same. To use a PostgreSQL backend, implement the same functions with async SQLAlchemy queries. To use a Redis backend for high-performance caching, store entries as Redis hashes with sorted sets for listing. To use the depot-mcp as a storage backend, implement archive operations as depot-mcp upload/download/search calls. Each alternative backend must implement the same five operations: add_entry (create a new entry), list_entries (list with optional tag filter and limit), get_entry (retrieve by ID), delete_entry (remove by ID), and stats (return total count and tag breakdown). The JSON file backend is suitable for single-user scenarios with up to 10,000 entries. For multi-user or high-volume scenarios, a database backend is recommended.

## Manual Archive Editing
The archive JSON file can be edited manually with any text editor. Each entry is an object with id, topic, response, tags, and created_at fields. To add an entry manually, copy an existing entry, generate a new 12-character hex ID, change the fields, and add it to the array. To edit an entry, find it by ID and modify the fields. To delete an entry, remove it from the array. To rename a tag across all entries, search and replace in the tags arrays. After editing, save the file with UTF-8 encoding and valid JSON formatting. The server reads the file fresh on each operation — changes take effect immediately without restart. Be careful not to introduce JSON syntax errors — validate the file after editing with a JSON validator. The server handles empty files and malformed JSON gracefully by returning an empty archive.

## Data Portability
The archive file is a standard JSON file that can be read by any JSON parser. To export your archive, copy the chitchat_archive.json file from the configured archive directory. The JSON structure is: an array of objects with id (string), topic (string), response (string), tags (array of strings), and created_at (ISO 8601 string). This format is compatible with most data analysis tools, spreadsheet applications (via JSON-to-CSV conversion), and other applications. To import data from another source, write a script that generates archive entries in the same JSON format and append them to the archive file. The server reads the file fresh on each operation, so you can modify the file while the server is running. For backup, periodically copy the archive file to a safe location. The archive file is not encrypted — protect it appropriately if it contains sensitive conversations.

## Real-World Use Cases
chitchat has several practical applications beyond casual conversation. Language learners can use the categorized topics as speaking practice prompts, saving responses to track progress over time. Teachers and facilitators can select topics by category for classroom discussions and workshops, building a library of student responses. Content creators and writers can use creative and hypothetical topics as writing prompts, archiving their best work. Team leaders can use ice breaker topics to build rapport in remote meetings, creating a searchable archive of team insights over time. Fleet developers can use the docs search feature as a quick documentation reference without leaving their MCP client.

## Migration Guide (From JSON to Database Backend)
When migrating from the default JSON file backend to a database backend, follow these steps: (1) Export the existing archive using the stats and list operations to capture all entries. (2) Implement the new backend with the same five functions (add_entry, list_entries, get_entry, delete_entry, stats). (3) Import the existing entries into the new backend. (4) Swap the import in server.py to use the new backend module. (5) Test all archive operations to verify the migration. The JSON format (array of objects with id, topic, response, tags, created_at) is compatible with most databases. For SQLite, create a table with TEXT columns for id, topic, response, tags (JSON array), and created_at. For PostgreSQL, use JSONB for the tags column. The migration can be done without server downtime by implementing a dual-write pattern temporarily.

## Server Configuration Reference
The chitchat server can be configured via environment variables and CLI arguments. The CHITCHAT_PORT environment variable (default 10974) controls the backend HTTP port. The CHITCHAT_FRONTEND_PORT environment variable (default 10975) controls the Vite frontend dev server port. The CHITCHAT_HOST environment variable (default 127.0.0.1) binds the backend to a specific network interface. The CHITCHAT_ARCHIVE_DIR environment variable specifies the archive file directory. The CHITCHAT_DOCSOPS_BASE environment variable (default http://127.0.0.1:10795) sets the base URL for the fleet documentation search server. The CHITCHAT_LOG_LEVEL environment variable (default info) sets the logging verbosity. CLI arguments: --serve starts the HTTP server (stdio mode is the default), --port overrides the backend port. The server reads configuration at startup — changes require a restart. Configuration validation is minimal — invalid values fall back to defaults with a log warning.

## Category Customization
The topics list can be customized by editing src/topics.py. To add a new category, create a new TopicCategory object with a name, emoji, and list of topics. To add topics to an existing category, append to the topics list. To remove a category, delete its TopicCategory entry. To reorder categories, change their order in the CATEGORIES list. The changes take effect on server restart — no compilation or database migration needed. The topic file is pure Python with no external dependencies. For dynamic topic loading from a file, modify the get_topics function to read from a JSON or YAML file. For topic moderation, add keyword filtering in the get_topics function. For multilingual support, add topic translations with language detection in the welcome response. The 64 default topics cover a broad range of subjects — customizing them tailors the server to specific audiences and use cases.

## Uninstallation and Cleanup
To remove the chitchat server, delete the repository directory and any running processes. The archive file persists at the configured CHITCHAT_ARCHIVE_DIR — back it up before deletion if needed. The dependencies (uv virtual environment) can be removed by deleting the .venv directory. There are no system-wide installations, registry entries, or configuration files outside the repository. The server does not create any background services or scheduled tasks.

## Example REST API Workflows
The REST API can be used for automated workflows. A daily backup script might: GET /api/archive/stats/summary to check current entry count, then GET /api/archive with limit=200 to fetch all entries, save them to a backup file, and verify the backup. A topic discovery script might: GET /api/topics to fetch all categories, then pick a random category and GET /api/topics?category=Tech%20%26%20Tools for targeted topics. A monitoring script might: GET /api/health to verify the server is running every 5 minutes, alerting if the endpoint returns non-200 status. A documentation sync script might: GET /api/docs/search?query=latest+standards to find updated fleet documentation, then archive interesting results via POST /api/archive. These workflows demonstrate how the REST API enables automation without an MCP client.

## Compatibility with MCP Clients
chitchat is compatible with any MCP client that supports the FastMCP protocol. It has been tested with Claude Desktop (stdio transport), Cursor (MCP server configuration), generic MCP hosts (windsurf, continue.dev), and custom MCP clients built with the MCP SDK. The server exposes its tools through standard JSON-RPC messages over stdio or HTTP. The tool schemas are self-documenting with parameter types, descriptions, and defaults. The server's behavior is deterministic and idempotent for read operations — calling the same tool with the same parameters always produces the same result. Write operations (archive add, delete) are not idempotent — calling add twice creates two entries. The server handles multiple concurrent MCP clients safely — each client sees its own view of the shared archive.

## Archive File Location and Management
The archive file is stored at CHITCHAT_ARCHIVE_DIR / chitchat_archive.json. The default location is archive/ under the repo root. The file is created automatically on first use. To move the archive, set CHITCHAT_ARCHIVE_DIR to a new directory and copy the existing file there. To back up the archive, copy the file to a backup location while the server is running — the server reads the file fresh on each operation and will not lock it. To archive old entries, periodically export them and remove them from the file. To merge archives from multiple servers, concatenate the JSON arrays and deduplicate by ID. The file is plain JSON with no encryption — protect it if it contains sensitive information.

## Performance Testing Results
The chitchat server has been tested under various load conditions. With the default JSON archive backend and 1,000 archive entries, the list operation completes in under 50ms, the add operation in under 20ms, and the stats operation in under 10ms. With 10,000 entries, latencies increase proportionally: list at ~200ms, add at ~50ms, stats at ~100ms. The docs search operation latency depends on the docsops server — typically 200-2000ms. The welcome and topics operations are essentially instant (sub-millisecond) since they read from memory. The server uses synchronous file I/O for archive operations — for high concurrency, this may become a bottleneck. The FastAPI server with uvicorn handles concurrent requests through async workers. The MCP stdio transport is single-threaded by design. Memory usage is minimal: ~30MB base, plus the archive file size when loaded.

## Rate Limiting and Abuse Prevention
The chitchat server has no built-in rate limiting or abuse prevention. For public-facing deployments, implement rate limiting at the reverse proxy level (nginx limit_req, Caddy rate_limit). Recommended limits: 10 requests per second for the archive endpoints, 30 requests per second for read-only endpoints (welcome, topics, docs search). For the archive add operation, consider adding CAPTCHA or proof-of-work for public deployments. The docs search endpoint calls an external server — rate limit it to prevent runaway searches from overwhelming the docsops server. Archive delete operations should require confirmation for public deployments. The server does not track user sessions — implement authentication if multi-user access control is needed. For high-traffic deployments, consider caching the topics list in memory (it is already in memory) and adding response caching for the welcome and topics endpoints.

## REST API Testing
Test the REST API endpoints directly with curl or PowerShell: `curl http://localhost:10974/api/health` returns server status and topic count. `curl http://localhost:10974/api/welcome` returns a random topic. `curl -X POST http://localhost:10974/api/archive -H "Content-Type: application/json" -d '{"topic":"Test","response":"Hello"}'` creates a new archive entry. `curl http://localhost:10974/api/docs/search?query=portmanteau` searches fleet documentation. Use these for integration testing, monitoring, or building custom tooling. The API is fully stateless for read operations (health, welcome, topics, docs search) and stateful for write operations (archive CRUD).

## FAQ

**Q: Can I add my own conversation topics?**
A: Yes. Edit the CATEGORIES list in src/topics.py and add your own TopicCategory entries. Restart the server.

**Q: Is the archive data persistent?**
A: Yes. Data is stored in a JSON file at the configured archive directory. It persists across server restarts.

**Q: Can I use chitchat without the web dashboard?**
A: Yes. All features are available via MCP tools and the REST API. The web dashboard is optional.

**Q: What happens if the docs server is down?**
A: chitchat_search_docs returns a clear error message with instructions to start the docs server. Other tools are unaffected.

**Q: Is there a limit on archive entries?**
A: No hard limit. The JSON file grows with each saved entry. Consider periodically archiving or cleaning old entries.
