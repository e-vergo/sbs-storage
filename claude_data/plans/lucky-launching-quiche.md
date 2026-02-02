# Plan: sbs-lsp-mcp - Custom MCP Server MVP

## Goal

Fork lean-lsp-mcp, add 11 SBS-specific tools while preserving all Lean proof-writing capabilities. Create comprehensive test suite.

---

## Architecture

```
lean-lsp-mcp (upstream: 3,525 lines, 18 tools)
     │
     └── sbs-lsp-mcp (fork in forks/)
         ├── All Lean tools preserved (18 tools)
         └── SBS tools added (11 tools)
```

**Location:** `forks/sbs-lsp-mcp/`

**Framework:** FastMCP (Python), same as upstream

**Integration:** Uses existing `sbs` Python modules via imports

---

## MVP Tools (11)

### Core Archive Tools (4)

| Tool | Input | Output | Tests |
|------|-------|--------|-------|
| `sbs_oracle_query` | `{query: str}` | `{matches: [...], concepts: [...]}` | 5 |
| `sbs_archive_state` | `{}` | `{global_state, last_epoch, entries_count}` | 4 |
| `sbs_epoch_summary` | `{epoch_id?: str}` | `{entries, builds, visual_changes, ...}` | 4 |
| `sbs_context` | `{include?: [...]}` | `{context_block: str}` | 3 |

### Testing/Validation Tools (2)

| Tool | Input | Output | Tests |
|------|-------|--------|-------|
| `sbs_run_tests` | `{path?, filter?}` | `{passed, failed, failures: [...]}` | 4 |
| `sbs_validate_project` | `{project, validators?}` | `{overall_score, results: {...}}` | 4 |

### Build/Serve Tools (2)

| Tool | Input | Output | Tests |
|------|-------|--------|-------|
| `sbs_build_project` | `{project, dry_run?}` | `{success, duration, errors}` | 3 |
| `sbs_serve_project` | `{project, action}` | `{running, url, pid}` | 4 |

### Investigation Tools (3)

| Tool | Input | Output | Tests |
|------|-------|--------|-------|
| `sbs_last_screenshot` | `{project, page}` | `{image_path, captured_at, hash}` | 4 |
| `sbs_visual_history` | `{project, page, limit?}` | `{history: [...]}` | 3 |
| `sbs_search_entries` | `{tags?, project?, since?}` | `{entries: [...], total}` | 5 |

**Total: 11 tools, 43 tests**

---

## Wave 0: Fork Setup

### Task 0A: Create fork directory structure

```
forks/sbs-lsp-mcp/
├── src/
│   └── sbs_lsp_mcp/
│       ├── __init__.py          # CLI entry point
│       ├── __main__.py          # Module execution
│       ├── server.py            # Main server + all tools
│       ├── sbs_tools.py         # SBS-specific tool implementations
│       ├── models.py            # Pydantic output models
│       └── utils.py             # Helper functions
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_oracle_tools.py     # Oracle query tests
│   ├── test_archive_tools.py    # Archive state/epoch tests
│   ├── test_build_tools.py      # Build/serve tests
│   ├── test_visual_tools.py     # Screenshot/history tests
│   └── test_search_tools.py     # Entry search tests
├── pyproject.toml               # Package config
├── README.md                    # Documentation
└── LICENSE                      # MIT (same as upstream)
```

### Task 0B: Copy and adapt upstream code

1. Copy `lean-lsp-mcp` source structure
2. Rename package to `sbs_lsp_mcp`
3. Update imports and entry points
4. Verify Lean tools still work

---

## Wave 1: Core Infrastructure

### Task 1A: Create Pydantic models (`models.py`)

```python
# Output models for SBS tools
class OracleMatch(BaseModel):
    file: str
    lines: Optional[str]
    context: str
    relevance: float

class OracleQueryResult(BaseModel):
    matches: list[OracleMatch]
    concepts: list[dict]

class ArchiveStateResult(BaseModel):
    global_state: Optional[dict]
    last_epoch_entry: Optional[str]
    last_epoch_timestamp: Optional[str]
    entries_in_current_epoch: int

class EpochSummaryResult(BaseModel):
    epoch_id: str
    started_at: str
    entries: int
    builds: int
    visual_changes: list[dict]
    tags_used: list[str]

class ContextResult(BaseModel):
    context_block: str

class TestResult(BaseModel):
    passed: int
    failed: int
    errors: int
    duration_seconds: float
    failures: list[dict]

class ValidationResult(BaseModel):
    overall_score: float
    results: dict[str, dict]

class BuildResult(BaseModel):
    success: bool
    duration_seconds: float
    build_run_id: Optional[str]
    errors: list[str]

class ServeResult(BaseModel):
    running: bool
    url: Optional[str]
    pid: Optional[int]

class ScreenshotResult(BaseModel):
    image_path: str
    entry_id: str
    captured_at: str
    hash: Optional[str]

class VisualHistoryResult(BaseModel):
    history: list[dict]

class SearchResult(BaseModel):
    entries: list[dict]
    total_count: int
```

### Task 1B: Create SBS utility functions (`utils.py`)

```python
# Integration with existing sbs modules
from sbs.archive.entry import ArchiveIndex
from sbs.core.utils import ARCHIVE_DIR, SBS_ROOT

def load_archive_index() -> ArchiveIndex:
    """Load the archive index."""
    return ArchiveIndex.load(ARCHIVE_DIR / "archive_index.json")

def load_oracle_content() -> str:
    """Load compiled oracle markdown."""
    oracle_path = SBS_ROOT / ".claude" / "agents" / "sbs-oracle.md"
    return oracle_path.read_text()

def get_screenshot_path(project: str, page: str) -> Path:
    """Get path to latest screenshot for a page."""
    return ARCHIVE_DIR / project / "latest" / f"{page}.png"

def parse_oracle_sections(content: str) -> dict:
    """Parse oracle markdown into searchable sections."""
    # Extract YAML frontmatter + sections
    ...
```

---

## Wave 2: Core Archive Tools

### Task 2A: Implement `sbs_oracle_query`

```python
@mcp.tool("sbs_oracle_query")
async def sbs_oracle_query(
    ctx: Context,
    query: Annotated[str, Field(description="Natural language query")]
) -> OracleQueryResult:
    """Query the SBS Oracle for file/concept information."""
    content = load_oracle_content()
    sections = parse_oracle_sections(content)

    matches = fuzzy_search_files(query, sections["file_map"])
    concepts = search_concepts(query, sections["concept_index"])

    return OracleQueryResult(matches=matches, concepts=concepts)
```

### Task 2B: Implement `sbs_archive_state`

```python
@mcp.tool("sbs_archive_state")
async def sbs_archive_state(ctx: Context) -> ArchiveStateResult:
    """Get current orchestration state from archive."""
    index = load_archive_index()

    # Count entries since last epoch
    entries_count = 0
    if index.last_epoch_entry:
        for eid in index.entries:
            if eid > index.last_epoch_entry:
                entries_count += 1

    return ArchiveStateResult(
        global_state=index.global_state,
        last_epoch_entry=index.last_epoch_entry,
        last_epoch_timestamp=get_entry_timestamp(index, index.last_epoch_entry),
        entries_in_current_epoch=entries_count
    )
```

### Task 2C: Implement `sbs_epoch_summary`

```python
@mcp.tool("sbs_epoch_summary")
async def sbs_epoch_summary(
    ctx: Context,
    epoch_entry_id: Annotated[Optional[str], Field(...)] = None
) -> EpochSummaryResult:
    """Get aggregate statistics for an epoch."""
    index = load_archive_index()

    # Get entries in epoch
    epoch_entries = get_epoch_entries(index, epoch_entry_id)

    return EpochSummaryResult(
        epoch_id=epoch_entry_id or "current",
        started_at=epoch_entries[0].created_at if epoch_entries else "",
        entries=len(epoch_entries),
        builds=sum(1 for e in epoch_entries if e.trigger == "build"),
        visual_changes=aggregate_visual_changes(epoch_entries),
        tags_used=collect_tags(epoch_entries)
    )
```

### Task 2D: Implement `sbs_context`

```python
@mcp.tool("sbs_context")
async def sbs_context(
    ctx: Context,
    include: Annotated[Optional[list[str]], Field(...)] = None
) -> ContextResult:
    """Build formatted context block for agent injection."""
    include = include or ["state", "epoch", "quality"]

    blocks = []
    if "state" in include:
        state = await sbs_archive_state(ctx)
        blocks.append(format_state_block(state))
    if "epoch" in include:
        epoch = await sbs_epoch_summary(ctx)
        blocks.append(format_epoch_block(epoch))
    # ...

    return ContextResult(context_block="\n\n".join(blocks))
```

---

## Wave 3: Testing/Build Tools

### Task 3A: Implement `sbs_run_tests`

```python
@mcp.tool("sbs_run_tests")
async def sbs_run_tests(
    ctx: Context,
    path: Annotated[Optional[str], Field(...)] = None,
    filter: Annotated[Optional[str], Field(...)] = None,
    verbose: Annotated[bool, Field(...)] = False
) -> TestResult:
    """Run pytest suite and return structured results."""
    cmd = ["pytest", "--json-report", "--json-report-file=-"]
    if path:
        cmd.append(path)
    if filter:
        cmd.extend(["-k", filter])
    if verbose:
        cmd.append("-v")

    result = subprocess.run(cmd, capture_output=True, cwd=SBS_ROOT / "dev/scripts")
    report = json.loads(result.stdout)

    return TestResult(
        passed=report["summary"]["passed"],
        failed=report["summary"]["failed"],
        errors=report["summary"]["errors"],
        duration_seconds=report["duration"],
        failures=extract_failures(report)
    )
```

### Task 3B: Implement `sbs_validate_project`

```python
@mcp.tool("sbs_validate_project")
async def sbs_validate_project(
    ctx: Context,
    project: Annotated[str, Field(description="Project name")],
    validators: Annotated[Optional[list[str]], Field(...)] = None
) -> ValidationResult:
    """Run T1-T8 validators on a project."""
    from sbs.validators import discover_validators, registry

    discover_validators()
    validators = validators or ["T5", "T6"]  # Default to deterministic

    results = {}
    for v in validators:
        validator = registry.get(v)
        result = validator.validate(ValidationContext(project=project))
        results[v] = {"score": result.score, "passed": result.passed, "findings": result.findings}

    overall = sum(r["score"] for r in results.values()) / len(results)
    return ValidationResult(overall_score=overall, results=results)
```

### Task 3C: Implement `sbs_build_project`

```python
@mcp.tool("sbs_build_project")
async def sbs_build_project(
    ctx: Context,
    project: Annotated[str, Field(description="Project name")],
    dry_run: Annotated[bool, Field(...)] = False,
    skip_cache: Annotated[bool, Field(...)] = False
) -> BuildResult:
    """Trigger build.py for a project."""
    cmd = ["python3", "build.py"]
    if dry_run:
        cmd.append("--dry-run")
    if skip_cache:
        cmd.append("--skip-cache")

    start = time.time()
    result = subprocess.run(cmd, capture_output=True, cwd=get_project_path(project))
    duration = time.time() - start

    return BuildResult(
        success=result.returncode == 0,
        duration_seconds=duration,
        build_run_id=extract_build_id(result.stdout),
        errors=extract_errors(result.stderr)
    )
```

### Task 3D: Implement `sbs_serve_project`

```python
@mcp.tool("sbs_serve_project")
async def sbs_serve_project(
    ctx: Context,
    project: Annotated[str, Field(description="Project name")],
    action: Annotated[str, Field(description="start|stop|status")],
    port: Annotated[int, Field(...)] = 8000
) -> ServeResult:
    """Start or check status of local dev server."""
    # Implementation uses subprocess for python http.server
    # Tracks PIDs in a state file
    ...
```

---

## Wave 4: Investigation Tools

### Task 4A: Implement `sbs_last_screenshot`

```python
@mcp.tool("sbs_last_screenshot")
async def sbs_last_screenshot(
    ctx: Context,
    project: Annotated[str, Field(description="Project name")],
    page: Annotated[str, Field(description="Page name (dashboard, dep_graph, etc.)")]
) -> ScreenshotResult:
    """Get most recent screenshot for a page WITHOUT building."""
    screenshot_path = get_screenshot_path(project, page)

    if not screenshot_path.exists():
        raise ValueError(f"No screenshot found for {project}/{page}")

    # Get metadata from capture.json
    capture_json = screenshot_path.parent / "capture.json"
    metadata = json.loads(capture_json.read_text())

    return ScreenshotResult(
        image_path=str(screenshot_path),
        entry_id=get_latest_entry_id(project),
        captured_at=metadata["timestamp"],
        hash=compute_hash(screenshot_path) if screenshot_path.exists() else None
    )
```

### Task 4B: Implement `sbs_visual_history`

```python
@mcp.tool("sbs_visual_history")
async def sbs_visual_history(
    ctx: Context,
    project: Annotated[str, Field(description="Project name")],
    page: Annotated[str, Field(description="Page name")],
    limit: Annotated[int, Field(...)] = 5
) -> VisualHistoryResult:
    """See how a page looked across recent entries."""
    index = load_archive_index()
    entries = index.get_entries_by_project(project)[-limit:]

    history = []
    prev_hash = None
    for entry in entries:
        screenshot_path = get_archived_screenshot(project, entry.entry_id, page)
        current_hash = compute_hash(screenshot_path) if screenshot_path.exists() else None

        history.append({
            "entry_id": entry.entry_id,
            "timestamp": entry.created_at,
            "image_path": str(screenshot_path) if screenshot_path.exists() else None,
            "hash": current_hash,
            "changed_from_previous": current_hash != prev_hash if prev_hash else None
        })
        prev_hash = current_hash

    return VisualHistoryResult(history=history)
```

### Task 4C: Implement `sbs_search_entries`

```python
@mcp.tool("sbs_search_entries")
async def sbs_search_entries(
    ctx: Context,
    project: Annotated[Optional[str], Field(...)] = None,
    tags: Annotated[Optional[list[str]], Field(...)] = None,
    since: Annotated[Optional[str], Field(...)] = None,
    trigger: Annotated[Optional[str], Field(...)] = None,
    limit: Annotated[int, Field(...)] = 20
) -> SearchResult:
    """Search archive entries by various criteria."""
    index = load_archive_index()

    # Filter entries
    results = list(index.entries.values())
    if project:
        results = [e for e in results if e.project == project]
    if tags:
        results = [e for e in results if any(t in e.tags + e.auto_tags for t in tags)]
    if since:
        results = [e for e in results if e.entry_id > since]
    if trigger:
        results = [e for e in results if e.trigger == trigger]

    # Sort by entry_id (timestamp) descending, limit
    results = sorted(results, key=lambda e: e.entry_id, reverse=True)[:limit]

    return SearchResult(
        entries=[summarize_entry(e) for e in results],
        total_count=len(results)
    )
```

---

## Wave 5: Test Suite

### Task 5A: Test fixtures (`conftest.py`)

```python
import pytest
from pathlib import Path
from sbs_lsp_mcp.utils import load_archive_index

@pytest.fixture
def mock_archive_index(tmp_path):
    """Create a mock archive index for testing."""
    ...

@pytest.fixture
def mock_oracle_content():
    """Return mock oracle markdown content."""
    ...

@pytest.fixture
def mock_screenshot_dir(tmp_path):
    """Create mock screenshot directory structure."""
    ...
```

### Task 5B: Oracle tool tests (`test_oracle_tools.py`)

```python
class TestOracleQuery:
    def test_query_returns_matches(self):
        """Query should return file matches."""

    def test_query_returns_concepts(self):
        """Query should return concept matches."""

    def test_query_empty_returns_empty(self):
        """Empty query returns empty results."""

    def test_query_fuzzy_matching(self):
        """Fuzzy matching works for partial terms."""

    def test_query_case_insensitive(self):
        """Query is case insensitive."""
```

### Task 5C: Archive tool tests (`test_archive_tools.py`)

```python
class TestArchiveState:
    def test_returns_global_state(self):
        """Returns current global_state."""

    def test_returns_epoch_info(self):
        """Returns last epoch entry and timestamp."""

    def test_counts_entries_in_epoch(self):
        """Correctly counts entries since last epoch."""

    def test_handles_no_epoch(self):
        """Handles case with no previous epoch."""

class TestEpochSummary:
    def test_aggregates_build_count(self):
        """Correctly counts build entries."""

    def test_aggregates_visual_changes(self):
        """Aggregates visual change data."""

    def test_collects_tags(self):
        """Collects all tags used in epoch."""

    def test_specific_epoch_id(self):
        """Can query specific epoch by ID."""
```

### Task 5D: Build tool tests (`test_build_tools.py`)

```python
class TestRunTests:
    def test_runs_all_tests(self):
        """Runs full test suite."""

    def test_filter_by_path(self):
        """Can filter to specific path."""

    def test_filter_by_keyword(self):
        """Can filter by keyword."""

    def test_returns_failures(self):
        """Returns failure details on failure."""

class TestValidateProject:
    def test_runs_validators(self):
        """Runs specified validators."""

    def test_returns_scores(self):
        """Returns scores for each validator."""

    def test_calculates_overall(self):
        """Calculates overall score correctly."""

    def test_default_validators(self):
        """Uses default validators when none specified."""

class TestBuildProject:
    def test_triggers_build(self):
        """Triggers build.py subprocess."""

    def test_dry_run_mode(self):
        """Dry run doesn't actually build."""

    def test_returns_duration(self):
        """Returns build duration."""
```

### Task 5E: Visual tool tests (`test_visual_tools.py`)

```python
class TestLastScreenshot:
    def test_returns_screenshot_path(self):
        """Returns path to latest screenshot."""

    def test_returns_metadata(self):
        """Returns capture metadata."""

    def test_handles_missing_screenshot(self):
        """Raises error for missing screenshot."""

    def test_computes_hash(self):
        """Computes hash for screenshot."""

class TestVisualHistory:
    def test_returns_history(self):
        """Returns history of screenshots."""

    def test_detects_changes(self):
        """Detects visual changes between entries."""

    def test_respects_limit(self):
        """Respects limit parameter."""
```

### Task 5F: Search tool tests (`test_search_tools.py`)

```python
class TestSearchEntries:
    def test_filter_by_project(self):
        """Filters by project name."""

    def test_filter_by_tags(self):
        """Filters by tags."""

    def test_filter_by_since(self):
        """Filters entries after timestamp."""

    def test_filter_by_trigger(self):
        """Filters by trigger type."""

    def test_respects_limit(self):
        """Respects limit parameter."""
```

---

## Wave 6: Integration & Validation

### Task 6A: Server integration

1. Register all SBS tools in `server.py`
2. Add SBS tools to MCP tool list
3. Ensure Lean tools still work
4. Test full server startup

### Task 6B: Package configuration

```toml
# pyproject.toml
[project]
name = "sbs-lsp-mcp"
version = "0.1.0"
description = "SBS-extended Lean LSP MCP server"
dependencies = [
    "lean-lsp-mcp>=0.19.0",  # Upstream dependency
    # SBS modules accessed via path
]

[project.scripts]
sbs-lsp-mcp = "sbs_lsp_mcp:main"
```

### Task 6C: Claude Code configuration

Update `~/.claude/settings.json`:
```json
{
  "mcpServers": {
    "sbs-lsp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/forks/sbs-lsp-mcp", "sbs-lsp-mcp"]
    }
  }
}
```

### Task 6D: Full validation

1. Run all 43 tests: `pytest tests/ -v`
2. Manual testing via Claude Code:
   - `sbs_oracle_query("CSS theming")`
   - `sbs_archive_state()`
   - `sbs_last_screenshot({project: "SBSTest", page: "dashboard"})`
3. Verify Lean tools still work:
   - `lean_goal`, `lean_diagnostic_messages`, etc.

---

## Critical Files

| File | Wave | Action |
|------|------|--------|
| `forks/sbs-lsp-mcp/` | 0 | Create directory |
| `src/sbs_lsp_mcp/server.py` | 0-4 | Main server with all tools |
| `src/sbs_lsp_mcp/sbs_tools.py` | 2-4 | SBS tool implementations |
| `src/sbs_lsp_mcp/models.py` | 1 | Pydantic output models |
| `src/sbs_lsp_mcp/utils.py` | 1 | Helper functions |
| `tests/conftest.py` | 5 | Test fixtures |
| `tests/test_*.py` | 5 | Test files (5 files) |
| `pyproject.toml` | 6 | Package config |
| `README.md` | 6 | Documentation |

---

## Execution Summary

```
Wave 0: Fork Setup
  └── sbs-developer: Create directory, copy upstream, rename package

Wave 1: Core Infrastructure
  └── sbs-developer: Pydantic models, utility functions

Wave 2: Core Archive Tools (4 tools)
  └── sbs-developer: oracle_query, archive_state, epoch_summary, context

Wave 3: Testing/Build Tools (4 tools)
  └── sbs-developer: run_tests, validate_project, build_project, serve_project

Wave 4: Investigation Tools (3 tools)
  └── sbs-developer: last_screenshot, visual_history, search_entries

Wave 5: Test Suite (43 tests)
  └── sbs-developer: All test files and fixtures

Wave 6: Integration & Validation
  └── sbs-developer: Package config, Claude Code setup, full validation
```

**Total: 7 waves, 11 tools, 43 tests**

---

## Success Criteria

1. ✅ Fork created at `forks/sbs-lsp-mcp/`
2. ✅ All 18 Lean tools still functional
3. ✅ All 11 SBS tools implemented and working
4. ✅ 43 tests passing
5. ✅ Claude Code can use `sbs_*` tools
6. ✅ `sbs_last_screenshot` returns images without building
7. ✅ `sbs_archive_state` returns correct global_state
8. ✅ `sbs_oracle_query` finds files and concepts
9. ✅ `sbs_run_tests` returns structured test results
10. ✅ Package installable via `uv run`
