# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed

- **Port conflict (10791)**: Fleet docs REST client now targets **docs_mcp backend on 10795** (`CHITCHAT_DOCSOPS_BASE` default). Port 10791 was incorrectly shared with avatar-mcp Prometheus metrics and the fleet starts UI.
- **MCP HTTP mount**: FastMCP streamable HTTP at `/mcp` — added lifespan context and `http_app(path="/")` so Hermes and other HTTP MCP clients connect on the correct path.

### Changed

- **Hermes integration**: Updated for Hermes Agent **0.15.1** built-in dashboard (`hermes dashboard` on **10972**); legacy `hermes-webui` bootstrap deprecated in `start_hermes.ps1`.

## [0.1.0] - 2026-05

Initial release: conversation starters, archive, fleet docs crosslink, FastAPI + FastMCP webapp on ports **10974/10975**.
