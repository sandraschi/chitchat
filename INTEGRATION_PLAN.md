# Hermes Agent — Fleet Integration Plan

> Phase 0 complete: chitchat migrated to 10974/10975. Hermes **0.15.1** installed in WSL2
> with built-in dashboard on 10972 (`hermes dashboard`). Fleet MCP config written.
>
> **Windows→WSL2 networking**: WSL2 uses NAT networking, so `localhost` from Windows
> does NOT forward to WSL2. Use the WSL2 VM IP directly (e.g. `http://172.23.171.21:10972/`).
> The IP changes on WSL2 reboot. Fix: `hermes_portproxy.ps1` (needs admin).
>
> **WSL2→Windows networking**: Fleet servers must bind to `0.0.0.0` (not `127.0.0.1`)
> to be reachable from WSL2. Chitchat config updated with `CHITCHAT_HOST=0.0.0.0` support.
> Gateway IP from WSL2: `172.23.160.1` (verify via `ip route show default`).
>
> **Provider block**: Hermes needs an LLM provider configured (`hermes model`).
> No API keys detected in env. Options: Nous Portal OAuth, OpenRouter API key,
> Anthropic API key, or local Ollama model.
**Date:** 2026-05-11
**Repo:** `D:\Dev\repos\chitchat` (but plan covers fleet-wide integration)

---

## 1. Strategic Rationale

Hermes Agent (NousResearch, 144k stars, MIT) fills a gap the current fleet does not cover:
a **persistent, self-improving agent** with cross-session memory, multi-platform messaging,
skill acquisition, and automated cron scheduling. The fleet has 50+ domain-specific MCP servers
but no coordinator agent that remembers context across sessions or can be reached from a phone.

Hermes becomes the **fleet conductor** — it connects to fleet MCP servers, learns their
capabilities over time, and provides a unified interface via CLI, TUI, web UI, and messaging
apps (Telegram, Discord, etc.).

### What it adds

| Capability | Current Fleet | With Hermes |
|---|---|---|
| Cross-session memory | Per-repo at best (AGENTS.md) | Automatic: skills, honcho user model, FTS5 recall |
| Messaging bridge | discord-mcp, individual bots | 20+ platforms from one gateway |
| Scheduled tasks | None (adhoc only) | Cron with natural language, platform delivery |
| Skill acquisition | Manual per-server | Auto-created from experience, self-improving |
| Mobile access | None (desktop-only) | Telegram, WhatsApp, Signal + web UI via Tailscale |
| Agent coordination | Manual (human orchestration) | Subagents, delegate_task, parallel workstreams |

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      HERMES AGENT                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │  CLI/TUI  │  │ Gateway  │  │ MCP Serve│  │  WebUI     │ │
│  │ (hermes)  │  │(Telegram,│  │ (stdio)  │  │(hermes-    │ │
│  │  port: —  │  │ Discord, │  │  port: — │  │ webui)     │ │
│  │           │  │ etc.)    │  │          │  │port: 10973 │ │
│  └─────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘ │
│        │             │             │               │        │
│        └─────────────┼─────────────┘               │        │
│                      │                             │        │
│              ┌───────┴───────┐                     │        │
│              │  Agent Core   │                     │        │
│              │  (Python 3.11)│                     │        │
│              │  ~/.hermes/   │                     │        │
│              └───────┬───────┘                     │        │
│                      │                             │        │
│        ┌─────────────┼─────────────┐               │        │
│        ▼             ▼             ▼               │        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐           │        │
│  │ Fleet MCP│ │ Fleet MCP│ │ Fleet MCP│  ...50+   │        │
│  │ Server 1 │ │ Server 2 │ │ Server N │           │        │
│  └──────────┘ └──────────┘ └──────────┘           │        │
│  (filesystem) (discord)   (chitchat)               │        │
│  port:10742   port:10756   port:10966              │        │
└─────────────────────────────────────────────────────┘
```

### Key integration surfaces

1. **Hermes → Fleet MCP servers**: Hermes's `mcp_servers` config connects to fleet servers
   via HTTP (for servers with HTTP MCP endpoints like chitchat on 10966) or stdio.
2. **Fleet tools → Hermes**: `hermes mcp serve` exposes Hermes's messaging/conversation
   tools as an MCP server — Claude Code, Cursor, or any fleet tool can read/send messages
   through Hermes's gateway.
3. **Hermes WebUI**: Browser-based interface for the agent, accessible locally or via
   Tailscale from phone.
4. **Skills Hub**: Fleet-specific skills published to `agentskills.io` for discovery.

---

## 3. Port Allocation

From the fleet port reservoir (10700-11000), assign adjacent ports for Hermes components:

| Port | Component | Purpose |
|---|---|---|
| **10972** | Hermes WebUI | hermes-webui server (unified Python + static, single port) |
| **10973** | Hermes (reserved) | Reserved for future Hermes service (gateway, voice, etc.) |

*Note: Hermes CLI/TUI and `hermes mcp serve` use stdio — no ports needed. The gateway
uses platform-specific webhook ports (not in fleet range).*

Adjacency rule: 10972/10973 are kept together as a project pair.

Check: No conflicts in `WEBAPP_PORTS.md` or `webapp-registry.json` with 10972/10973.

---

## 4. Installation Strategy

### Decision: WSL2 (not native Windows)

Hermes's native Windows support is **early beta** (per their own docs). The browser-based
dashboard pane explicitly requires WSL2 for the POSIX PTY. Recommendation: install inside
**WSL2** where Hermes is battle-tested.

```bash
# Inside WSL2:
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc
hermes setup   # interactive config wizard
```

### Provider selection

For the fleet, the default provider should be **OpenRouter** (model-agnostic) or
**Nous Portal** (subscription, zero-config). Anthropic API key is already available
across the fleet for Claude-based tools.

### Git Bash note

The native Windows installer bundles MinGit — but for WSL2 this is irrelevant. All
shell execution happens inside WSL2's native bash.

---

## 5. MCP Integration (Hermes ← Fleet)

Configure `~/.hermes/config.yaml` with fleet MCP servers Hermes should have access to:

```yaml
mcp_servers:
  # --- Core infrastructure ---
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/sandra"]
  # Or via fleet MCP server if it exposes HTTP MCP:
  # filesystem_fleet:
  #   url: "http://127.0.0.1:10742/mcp"

  # --- Fleet servers with HTTP MCP endpoints ---
  chitchat:
    url: "http://127.0.0.1:10974/mcp"
    tools:
      include: [chitchat_welcome, chitchat_topics, chitchat_search_docs]

  discord:
    url: "http://127.0.0.1:10756/mcp"
    tools:
      exclude: [delete_message, ban_user]

  docsops:
    url: "http://172.23.160.1:10795/mcp/"
    tools:
      include: [search_docs, get_document, ask_docs]

  # --- Tools Hermes should NOT see (dangerous/sensitive) ---
  # windows_ops:
  #   url: "http://127.0.0.1:10748/mcp"
  #   enabled: false   # explicit deny for admin-level tools
```

### Phased rollout

| Phase | Servers connected | Rationale |
|---|---|---|
| 1 (MVP) | chitchat, docsops | Read-only, low-risk, immediate value |
| 2 | filesystem, discord | Medium risk, high utility |
| 3 | Hand-picked fleet servers | Curated by category, after phase 1-2 confidence |
| 4 | Full fleet | All HTTP MCP endpoints, strict tool filtering |

---

## 6. MCP Integration (Fleet ← Hermes)

Run Hermes as an MCP server so fleet tools can use Hermes's messaging capabilities:

```bash
hermes mcp serve
```

This exposes 10 tools to any MCP client (Claude Code, fleet servers, etc.):

| Tool | Use case |
|---|---|
| `conversations_list` | See active chats across all platforms |
| `messages_read` | Read message history |
| `messages_send` | Send through Telegram/Discord/etc. |
| `events_poll` / `events_wait` | Near-real-time message awareness |
| `channels_list` | Discover available messaging targets |

Example: a fleet monitoring MCP server could send alerts to your phone via
`messages_send(target="telegram:123456", ...)` through Hermes.

### Claude Code integration

```json
// ~/.claude/claude_desktop_config.json (or equivalent)
{
  "mcpServers": {
    "hermes": {
      "command": "wsl",
      "args": ["hermes", "mcp", "serve"]
    }
  }
}
```

---

## 7. Hermes WebUI

Deploy `nesquena/hermes-webui` (6.6k stars, MIT) as the browser interface:

```bash
cd ~/repos
git clone https://github.com/nesquena/hermes-webui.git
cd hermes-webui
HERMES_WEBUI_PORT=10973 python3 bootstrap.py
```

### Access patterns

| Method | Setup | Use case |
|---|---|---|
| Local browser | `http://localhost:10973` | Desktop dev |
| SSH tunnel | `ssh -N -L 10973:127.0.0.1:10973 user@host` | Remote VPS |
| Tailscale | `http://<tailscale-ip>:10973` + password | Phone (add to home screen) |

### Password protection (mandatory for non-localhost)

```bash
HERMES_WEBUI_PASSWORD=<strong-password> HERMES_WEBUI_HOST=0.0.0.0 ./start.sh 10973
```

---

## 8. Startup Scripts

Following SOTA fleet patterns (`start.ps1` + `start.bat`):

### WSL2 bootstrap (`start.ps1` — run from Windows host)

```powershell
# Hermes Fleet Launcher
# Starts: WSL2 Hermes agent + WebUI on fleet ports
param([switch]$Headless)

$WebPort = 10973

# Kill any stale process on the port
npx --yes kill-port $WebPort 2>$null

# Ensure WSL2 is running and launch Hermes WebUI
wsl bash -c @"
  export HERMES_WEBUI_PORT=$WebPort
  export HERMES_WEBUI_HOST=0.0.0.0
  cd ~/repos/hermes-webui
  nohup ./start.sh --no-browser > ~/.hermes/webui_startup.log 2>&1 &
  echo "Hermes WebUI starting on port $WebPort..."
"@

# Wait for health endpoint
do {
  Start-Sleep -Milliseconds 500
  try { $r = Invoke-WebRequest "http://localhost:$WebPort/health" -UseBasicParsing; $ready = $true } catch { $ready = $false }
} until ($ready)

if (-not $Headless) {
  Start-Process "http://localhost:$WebPort"
}
```

---

## 9. Fleet-Specific Skills

Skills Hermes should auto-acquire or be pre-loaded with for fleet context:

| Skill | Description | Priority |
|---|---|---|
| `fleet-port-resolver` | Look up ports from `WEBAPP_PORTS.md` / `webapp-registry.json` | P0 |
| `fleet-server-start` | Start/stop/status any fleet MCP server by name | P1 |
| `fleet-health-check` | Poll all registered fleet servers, report status | P1 |
| `fleet-docs-search` | Semantic search across `mcp-central-docs` via docsops | P0 |
| `chitchat-topics` | Browse and suggest conversation starters from chitchat | P2 |

These should be published to `agentskills.io` for community reuse.

---

## 10. Windows-Specific Notes

### Known limitations

- **Browser dashboard**: The Hermes-native browser chat pane requires a POSIX PTY
  (WSL2 only, not native Windows).
- **Native Windows beta**: The PowerShell installer works but is marked "early beta."
  WSL2 is the recommended path for stability.
- **Voice mode**: `faster-whisper` dependencies may need WSL2 (GPU passthrough via
  WSL2 works for CUDA-based transcription).

### File system bridge

Hermes inside WSL2 can access Windows files via `/mnt/d/Dev/repos/...`. Configure
workspace root:

```bash
hermes config set workspace.default /mnt/d/Dev/repos
```

This lets Hermes navigate the entire fleet repo tree from within WSL2.

---

## 11. Chitchat-Specific Integration

Chitchat is the natural "social layer" for Hermes in the fleet:

1. **MCP tool exposure**: Chitchat's `chitchat_welcome`, `chitchat_topics`, and
   `chitchat_search_docs` tools are exposed to Hermes via MCP (see §5).
2. **Conversation priming**: Hermes can use chitchat topics to start conversations
   on messaging platforms — e.g., a daily cron job that posts a random icebreaker
   to a Telegram group.
3. **Archive enrichment**: Conversations Hermes has on messaging platforms can be
   saved back to chitchat's archive via the REST API.
4. **Fleet docs context**: Hermes uses chitchat's `chitchat_search_docs` tool
   (which wraps docsops) to answer fleet documentation questions in any chat.

### Example cron (Hermes + Chitchat)

```yaml
# In Hermes cron config (via natural language):
# "Every weekday at 9am Vienna time, grab a random tech topic from chitchat,
#  add a witty intro, and post it to the #dev-chat Discord channel."
```

---

## 12. Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Windows native instability | Medium | Use WSL2 exclusively |
| MCP server overload (50+ tools) | Medium | Phased rollout, strict tool filtering |
| Hermes rapid release churn | Medium | Pin to stable releases, test before update |
| Credential sprawl (API keys in `~/.hermes/.env`) | Low | Reuse existing fleet credential patterns |
| Hermes gaining too much autonomy | Low | Command approval mode, tool filtering, container isolation |
| Port conflict (10966/10967 already claimed by qcad-mcp) | Resolved | Migrated chitchat to 10974/10975 |

---

## 13. Immediate Action Items

> ~~**CRITICAL BLOCKER:** chitchat ports (10966/10967) conflict with qcad-mcp allocation.
> Fix chitchat config to 10974 (backend) / 10975 (frontend) before proceeding.~~ **DONE**

1. **~~Fix port conflict~~**: **DONE** — migrated chitchat from 10966/10967 → 10974/10975
2. **Allocate Hermes ports**: Register 10972/10973 in `webapp-registry.json` and `WEBAPP_PORTS.md`
3. **Install WSL2 Hermes**: Run the curl installer, configure OpenRouter provider
4. **Phase 1 MCP**: Connect Hermes to chitchat + docsops (read-only, low risk)
5. **Deploy WebUI**: Clone hermes-webui, configure on port 10973, test via browser
6. **Create fleet skills**: `fleet-port-resolver` and `fleet-docs-search` as starting skills
7. **Test messaging**: Configure Telegram gateway, verify cross-platform continuity

---

## 14. Phase Timeline

| Phase | Scope | Effort | Depends on |
|---|---|---|---|
| **0 — Port Fix** | chitchat port migration to 10974/10975 | 30 min | — |
| **1 — Core Install** | Hermes in WSL2, provider config, CLI test | 1 hour | Phase 0 |
| **2 — MCP Connect** | Hermes ↔ chitchat + docsops MCP | 1 hour | Phase 1 |
| **3 — WebUI** | hermes-webui on 10973, browser + Tailscale | 1 hour | Phase 1 |
| **4 — Gateway** | Telegram/Discord bots, cross-platform test | 2 hours | Phase 2 |
| **5 — Fleet Skills** | Publish 2-3 fleet skills to agentskills.io | 2 hours | Phase 2 |
| **6 — Cron Integration** | Scheduled fleet health checks + chitchat posts | 1 hour | Phase 4 |
| **7 — Full Fleet** | Gradual MCP rollout to remaining fleet servers | Ongoing | Phase 5 |

---

## Appendix A: Fleet MCP Servers (Hermes-Capable)

Servers in the fleet that expose HTTP MCP endpoints and are candidates for Hermes connection:

| Server | MCP URL | Category | Risk |
|---|---|---|---|
| chitchat | `http://127.0.0.1:10974/mcp` | Social | Low |
| docsops (mcp-central-docs) | `http://127.0.0.1:10795/mcp/` | Knowledge | Low |
| filesystem | `http://127.0.0.1:10742/mcp` | Infra | Medium |
| discord | `http://127.0.0.1:10756/mcp` | Social | Medium |
| depot | `http://127.0.0.1:10727/mcp` | Infra | Medium |
| windows-operations | `http://127.0.0.1:10748/mcp` | Infra | High |

## Appendix B: Hermes vs Fleet Tools (Overlap Analysis)

| Fleet Tool | Hermes Overlap | Resolution |
|---|---|---|
| discord-mcp | Hermes has native Discord gateway | Use Hermes gateway for messaging, fleet server for bot management |
| advanced-memory-mcp | Hermes has built-in memory (Honcho) | Complementary: fleet memory is structured, Hermes is conversational |
| monitoring-mcp | Hermes has cron + health checks | Hermes schedules, monitoring-mcp collects |
| openmanus-mcp | Both are agent frameworks | Hermes as coordinator, OpenManus for specialized agent tasks |
| colony-mcp | Both do agent orchestration | Evaluate after Phase 3 — potential redundancy |

## Appendix C: Chitchat Port Migration Checklist

> **Before any Hermes install, chitchat must vacate 10966/10967 (claimed by qcad-mcp).**

- [ ] Update `src/chitchat/config.py`: `10966` → `10974`, `10967` → `10975`
- [ ] Update `README.md` port references
- [ ] Update `web_sota/vite.config.ts` proxy target
- [ ] Update `start.ps1` / `start.bat` kill-port commands
- [ ] Update `webapp-registry.json` (add chitchat:10974/10975, remove old)
- [ ] Update `WEBAPP_PORTS.md`
- [ ] Test full startup sequence
- [ ] Run tests: `uv run pytest`
