# SPEC: DeepFang Evolution Engine (DGM-style Fleet Self-Improvement)

**Status:** SPEC (Plan Phase)
**Repo:** `D:\Dev\repos\deepfang`
**Date:** 2026-05-11
**Ports:** Uses existing 10956–10963 (no new ports)

---

## 1. Rationale

The SOTA fleet has 50+ MCP servers with varying code quality. Improvements are 100% human-driven — someone must notice a bug, write a PR, and deploy. There is no automated mechanism for fleet servers to improve themselves over time.

The Darwin-Gödel Machine (arXiv:2505.22954, Apache 2.0) demonstrates that a simple loop — select an agent, have an LLM modify its code, validate against benchmarks, archive successful variants — can autonomously increase coding agent performance by 2.5× (SWE-bench 20%→50%).

DeepFang is the natural fleet home for this loop because:
- It already has the **sanitize → adjudicate → dispatch** pipeline (structurally identical to select → modify → validate → archive)
- It has an **air-gapped Docker worker** (critical for safe code execution)
- It has **DeepSeek LLM access** (for code generation and evaluation)
- It has **Prometheus/Loki/Grafana** (for monitoring evolution progress)
- It already serves as **RoboFang's security moat** — adding evolution makes it a **self-improving moat**

---

## 2. Architecture

### 2.1 No new services — all within existing Supervisor + Worker

```
                        ┌─────────────────────────────┐
                        │      Supervisor (:10956)      │
                        │  + evolution/ module (NEW)    │
                        │                               │
 MCP clients ──────────►│  deepfang_evolve_server()     │
 (RoboFang,             │  deepfang_archive_list()      │
  Claude Code,          │  deepfang_evolve_step()       │
  Hermes)               │  deepfang_archive_prune()     │
                        └──────────┬───────────────────┘
                                   │
                     ┌─────────────▼──────────────┐
                     │    Worker (:10960)          │
                     │                             │
                     │  /execute  (existing)       │
                     │  /evolve   (NEW endpoint)   │
                     │    → clone repo              │
                     │    → apply code diff         │
                     │    → run test suite          │
                     │    → git branch/commit       │
                     │    → return results          │
                     │                             │
                     │  air-gapped, no WAN egress  │
                     └─────────────────────────────┘

                        ┌─────────────────────────────┐
                        │    Agent Archive             │
                        │    ~/.deepfang/archive/      │
                        │    (JSON + Git-backed)       │
                        └─────────────────────────────┘
```

### 2.2 Data flow — evolution cycle

```
1. SELECT     Supervisor picks a fleet server + parent variant from Archive
2. DIAGNOSE   DeepSeek Bridge analyzes server's current test failures / performance
3. PROPOSE    DeepSeek Bridge generates a code diff (unified diff patch)
4. SANITIZE   Sanitizer checks the diff for dangerous patterns (existing stage 1)
5. ADJUDICATE DeepSeek Bridge evaluates the diff's intent and risk (existing stage 2)
6. EXECUTE    Worker clones repo, applies diff, runs test suite in air-gap
7. VALIDATE   Worker returns: pass/fail, test coverage delta, perf change
8. ARCHIVE    If passed, variant is committed to Archive as new stepping stone
9. REPEAT     Next cycle starts from updated Archive
```

### 2.3 Key design decisions

| Decision | Rationale |
|---|---|
| Diffs, not full rewrites | Minimizes LLM hallucination risk. Human-reviewable. |
| Test-driven validation | Objective pass/fail — no subjective LLM judgment needed |
| Archive is git-backed | Each stepping stone is a branch. Full history, easy rollback. |
| One fleet server per evolution run | Keeps scope manageable. Multiple servers can evolve in parallel. |
| Flat module under Supervisor | Not a new Docker service — keeps ops simple |
| LLM proposes, worker validates | Separation of concerns. LLM has no execution access. |

---

## 3. New Files

### 3.1 `src/deepfang/evolution/__init__.py`
Empty package init.

### 3.2 `src/deepfang/evolution/archive.py` (~150 lines)
```python
class AgentArchive:
    """
    Manages the stepping-stone archive of fleet server variants.

    Storage: ~/.deepfang/archive/{server_name}/
      ├── index.json           # [{variant_id, parent_id, score, timestamp, branch}, ...]
      ├── variants/            # git branches per variant
      └── metrics.json         # per-server aggregate stats

    Key methods:
      - add(variant) → variant_id
      - get(variant_id) → Variant
      - list(server_name) → [VariantSummary]
      - select_parent(server_name, strategy) → Variant   # "best", "novelty", "random"
      - prune(server_name, keep=20) → int  # keep top N by score
      - lineage(variant_id) → [VariantSummary]  # parent chain
    """
```

### 3.3 `src/deepfang/evolution/selector.py` (~80 lines)
```python
class ParentSelector:
    """
    Chooses which variant to evolve next.

    Strategies:
      - greedy: highest score (risk of local optima)
      - novelty_weighted: score * 0.7 + novelty * 0.3
      - epsilon_greedy: 80% best, 20% random
      - quality_diversity: maximize score * architectural diversity

    Uses: archive.index.json scores + diff-based novelty (Jaccard on file changes).
    """
```

### 3.4 `src/deepfang/evolution/modifier.py` (~120 lines)
```python
class CodeModifier:
    """
    Uses DeepSeek Bridge to generate code improvements.

    Flow:
      1. Read current source files of fleet server
      2. Read test failures / lint errors / perf data
      3. Send to DeepSeek with structured prompt:
         - Server name, purpose, current code
         - Known issues / failures
         - Request: propose a minimal code diff that fixes issues
      4. Parse response → unified diff

    Safety:
      - Diff must apply cleanly (rejected otherwise)
      - Diff must only touch files within the server's src/ directory
      - Diff must not delete test files
      - Passes through Sanitizer before execution
    """
```

### 3.5 `src/deepfang/evolution/validator.py` (~100 lines)
```python
class EvolutionValidator:
    """
    Sends modifications to air-gapped worker for validation.

    Uses Worker's /evolve endpoint:
      POST /evolve
      {
        "server_name": "chitchat",
        "variant_id": "abc123",
        "diff": "--- a/src/chitchat/server.py\n+++ b/src/chitchat/server.py\n...",
        "base_branch": "main"
      }

    Worker response:
      {
        "success": true/false,
        "tests_passed": 18/20,
        "tests_previous": 18/20,  // baseline before diff
        "lint_passed": true/false,
        "coverage_delta": +0.02,
        "execution_time_ms": 4200,
        "output": "...",
        "branch": "evolution/chitchat/abc123"
      }
    """
```

### 3.6 `src/deepfang/evolution/orchestrator.py` (~180 lines)
```python
class EvolutionOrchestrator:
    """
    Top-level loop that wires everything together.

    evolution_cycle(server_name: str, max_generations: int = 10):
      for gen in range(max_generations):
        1. parent = selector.select(server_name)
        2. diff = modifier.generate(parent)
        3. sanitize_result = supervisor.sanitize(diff)
           if not sanitize_result.allowed: continue
        4. adjudication = supervisor.adjudicate(diff)
           if adjudication.verdict != "approve": continue
        5. result = validator.validate(server_name, diff, parent)
        6. if result.success:
             archive.add(variant)
        7. log metrics to Prometheus

    Supports:
      - Single-step mode: deepfang_evolve_step(server_name)
      - Continuous mode: deepfang_evolve_server(server_name, max_generations)
    """
```

### 3.7 `src/deepfang/mcp_server.py` — ADD 5 new tools
```python
# In create_mcp_server(), add after existing tool registrations:
_mcp.tool()(deepfang_archive_list)
_mcp.tool()(deepfang_archive_lineage)
_mcp.tool()(deepfang_evolve_step)
_mcp.tool()(deepfang_evolve_server)
_mcp.tool()(deepfang_evolve_status)
```

### 3.8 `containers/worker.py` — ADD `/evolve` endpoint (~80 lines)
```python
@app.post("/evolve")
async def evolve_endpoint(body: dict):
    """
    Clone a fleet repo, apply a diff, run tests, return results.

    1. git clone /repos/{server_name} → /workspace/{server_name}_{variant_id}
    2. git checkout -b evolution/{server_name}/{variant_id}
    3. Apply diff via patch command
    4. Run baseline tests (git stash → test → git stash pop)
    5. Run modified tests
    6. Compare results
    7. If passed: git commit, git branch remains for inspection
       If failed: delete workspace
    8. Return results dict
    """
```

---

## 4. Modified Files

| File | Change |
|---|---|
| `src/deepfang/main.py` | Import evolution module, initialize archive on startup |
| `src/deepfang/mcp_server.py` | Register 5 new MCP tools (§3.7) |
| `containers/worker.py` | Add `/evolve` endpoint (§3.8) |
| `pyproject.toml` | No new deps needed (httpx, FastMCP, pyyaml already present) |

---

## 5. MCP Tool Surface (NEW)

| Tool | Signature | Description |
|---|---|---|
| `deepfang_archive_list` | `(server_name: str \| None = None) → dict` | List stepping stone variants. Filter by server. Returns scores, parent chains, timestamps. |
| `deepfang_archive_lineage` | `(variant_id: str) → dict` | Show full parent→child lineage chain for a variant. |
| `deepfang_evolve_step` | `(server_name: str) → dict` | Run ONE evolution cycle: select→modify→sanitize→adjudicate→validate→archive. Returns {generation, diff, test_result, archived}. |
| `deepfang_evolve_server` | `(server_name: str, max_generations: int = 5) → dict` | Run multiple evolution cycles. Returns {generations_completed, best_score, best_variant_id, lineage}. |
| `deepfang_evolve_status` | `() → dict` | Current evolution state: active servers, generation counts, best scores, archive sizes. |

---

## 6. REST API (NEW)

| Method | Path | Description |
|---|---|---|
| GET | `/api/evolution/archive` | List archive entries (?server= filter) |
| GET | `/api/evolution/archive/{variant_id}` | Get variant details + diff |
| GET | `/api/evolution/lineage/{variant_id}` | Parent chain |
| POST | `/api/evolution/step` | Trigger one evolution step: `{server_name}` |
| POST | `/api/evolution/run` | Start evolution run: `{server_name, max_generations}` |
| GET | `/api/evolution/status` | Current runs + archive stats |

---

## 7. Worker `/evolve` Endpoint (DETAILED)

```
POST /evolve
{
  "server_name": "chitchat",
  "variant_id": "dgm_v_0001",
  "diff": "unified diff string",
  "parent_variant_id": "dgm_v_0000",
  "base_branch": "main"
}

→ Worker:
  1. cd /workspace
  2. git clone file:///repos/{server_name} {server_name}_{variant_id}
     (Clone from local mirror — no WAN needed)
  3. cd {server_name}_{variant_id}
  4. git checkout -b evolution/{server_name}/{variant_id}
  5. echo "$diff" | git apply --check   # verify patch applies
     if fails → return {success: false, error: "patch failed to apply"}
  6. Run BASELINE tests: uv run pytest --json-report 2>&1
  7. echo "$diff" | git apply
  8. Run MODIFIED tests: uv run pytest --json-report 2>&1
  9. Compare: tests_passed / total, coverage delta, lint pass
  10. If improved or same AND no regressions:
        - git add -A && git commit -m "evolution/{variant_id}: auto-improvement"
        - return {success: true, branch: "...", tests_passed: X/Y, ...}
      Else:
        - rm -rf workspace
        - return {success: false, reason: "regression", ...}
```

### Safety constraints in worker
- Max execution time: 300s per evolve request
- Max workspace size: 500MB (enforced in Docker limits)
- Only fleet repos under `/repos/` are cloneable (path traversal blocked)
- Diff must be valid unified diff format (reject binary/encoded payloads)
- No network access at any point (air-gap at Docker network level)

---

## 8. Prompt Template for CodeModifier

```
You are a code improvement agent operating within the DeepFang Evolution
Engine. Your task is to propose a minimal, safe code change to improve a
fleet MCP server.

SERVER: {server_name}
DESCRIPTION: {server_description}
CURRENT SCORE: {score} (test pass rate: {test_rate})

CURRENT CODE:
{source_files}

KNOWN ISSUES:
{test_failures}
{lint_errors}

TASK: Propose ONE minimal code change that addresses one of the known
issues. Do NOT rewrite the entire file. Do NOT add new features. Only
fix bugs, improve error handling, add missing validations, or optimize
a slow path.

OUTPUT FORMAT: A unified diff (git diff format) with a header comment
explaining the change and why it should help.
```

---

## 9. Integration: RoboFang Calls DeepFang Evolution

RoboFang's `federation_map.json` already has deepfang as a connector. Add the new tools:

```json
"deepfang": {
    "enabled": true,
    "mcp_backend": "http://localhost:10956",
    "description": "DeepFang execution isolation + fleet evolution engine",
    "tools": [
        "deepfang_pipeline",
        "deepfang_sanitize",
        "deepfang_adjudicate",
        "deepfang_audit",
        "deepfang_status",
        "deepfang_archive_list",
        "deepfang_evolve_step",
        "deepfang_evolve_server",
        "deepfang_evolve_status"
    ]
}
```

RoboFang can now trigger fleet self-improvement via:
```
deepfang_evolve_server(server_name="chitchat", max_generations=5)
```

Or include it in the Council pipeline — the Council debates which server to improve next.

---

## 10. Dashboard Panel (New)

Add an "Evolution" tab to the existing React dashboard on port 10957:

- **Archive tree**: Visual graph of stepping stones, parent→child arrows, color-coded by score
- **Active runs**: Live status of ongoing evolution cycles
- **Score history**: Line chart of best score per generation
- **Diff viewer**: Side-by-side view of generated diffs before/after
- **Server picker**: Dropdown to select fleet server for evolution

Frontend changes: `dashboard/src/components/Evolution/` (3-4 new TSX files, 1 new route).

---

## 11. Prometheus Metrics (NEW)

| Metric | Type | Description |
|---|---|---|
| `deepfang_evolution_generations_total{server}` | Counter | Total evolution generations run |
| `deepfang_evolution_improvements_total{server}` | Counter | Successful improvements archived |
| `deepfang_evolution_score{server}` | Gauge | Current best score per server |
| `deepfang_evolution_archive_size{server}` | Gauge | Number of variants in archive |
| `deepfang_evolution_test_regressions{server}` | Counter | Times diff caused test failures |
| `deepfang_evolution_cycle_duration_seconds` | Histogram | Time per evolution cycle |

---

## 12. Phase Plan

### Phase 1: Core Loop (3-4 hours)
- [ ] `src/deepfang/evolution/archive.py` — AgentArchive with JSON + git backing
- [ ] `src/deepfang/evolution/orchestrator.py` — EvolutionOrchestrator main loop
- [ ] `src/deepfang/evolution/selector.py` — Parent selection strategies

### Phase 2: Worker Endpoint (2 hours)
- [ ] `containers/worker.py` — `/evolve` endpoint (clone, diff, test, compare)
- [ ] Worker safety constraints (timeout, size limit, path validation)

### Phase 3: MCP + LLM Integration (3 hours)
- [ ] `src/deepfang/evolution/modifier.py` — CodeModifier using DeepSeek Bridge
- [ ] `src/deepfang/evolution/validator.py` — EvolutionValidator calling worker
- [ ] `mcp_server.py` — Register 5 new MCP tools
- [ ] `main.py` — Wire evolution module into supervisor startup

### Phase 4: API + Metrics (1 hour)
- [ ] REST endpoints in `main.py`
- [ ] Prometheus metrics
- [ ] Supervisor startup lifecycle (archive init)

### Phase 5: Dashboard (2 hours)
- [ ] Evolution panel components
- [ ] Archive tree visualization
- [ ] Score history chart

### Phase 6: Test & Dogfood (2 hours)
- [ ] Test with chitchat as first fleet server
- [ ] Run 5-generation evolution, verify no regressions
- [ ] Verify robofang can call evolution tools via federation_map

---

## 13. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| LLM generates harmful diff | Medium | Sanitizer + Adjudicator both screen diff before execution |
| Diff breaks production server | Low | Worker tests on isolated clone, commits to branch only |
| Archive bloat | Low | Prune to 20 variants per server. Git storage is local. |
| Infinite improvement loop | Low | max_generations cap. Score plateau detection (3 gens no improvement → stop). |
| LLM costs | Medium | Only DeepSeek bridge used (cheap). Cache similar requests. |
| Test suite quality | High | Dependent on fleet server having adequate tests. Servers without tests cannot evolve. |

---

## 14. Fleet Server Readiness Checklist

Before a fleet server can be evolved, it must have:
- [ ] `pytest` test suite with ≥80% pass rate (evolving a broken server is pointless)
- [ ] `pyproject.toml` with `[tool.pytest.ini_options]` configured
- [ ] Lint config (ruff settings in pyproject.toml)
- [ ] Git repo accessible at `/repos/{server_name}` (on Goliath/Windows host)

### Fleet servers ready for Phase 6 dogfooding:

| Server | Tests? | Lint? | Notes |
|---|---|---|---|
| chitchat | ✅ pytest | ✅ ruff | Simple, well-tested. Ideal first target. |
| robofang | ✅ pytest | ✅ ruff | Complex — second-stage target |
| deepfang | ✅ pytest | ✅ ruff | Meta: evolve the evolver (Phase 7+) |

---

## 15. Non-Goals (Explicitly Excluded)

- **No DGM-H metacognition** (Phase 1-6). The meta-agent modifying itself is Phase 7+.
- **No cross-domain evolution** (non-code tasks). Stay within Python MCP server improvement.
- **No multi-server parallel evolution** in Phase 1. Serial per-server for safety.
- **No automatic git push to origin**. All changes stay on local branches until human review.
- **No LLM fine-tuning**. Pure prompt-based code generation only.
- **No reward model training**. Validation is purely test-driven.

## 16. Next Implementation Phase (After SPEC Approval)

1. Clone deepfang repo reference for implementation
2. Create `src/deepfang/evolution/` directory
3. Implement archive → selector → orchestrator → modifier → validator → worker endpoint → MCP tools → REST API → metrics
4. Dogfood on chitchat
5. Wire into robofang federation_map
