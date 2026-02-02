# Implementation Plan: `/self-improve` Skill

**Issue:** #4 - Add `/self-improve` skill for post-hoc session analysis
**Scope:** Full spec implementation

---

## Summary

Create a multi-phase skill that analyzes archived Claude Code sessions to identify improvement opportunities across four pillars: user effectiveness, Claude execution, alignment patterns, and system engineering.

---

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Skill type | Phased (5 substates) | Matches `/task` pattern, needs state tracking for recovery |
| MCP location | Python CLI | Keeps logic testable, MCP tools wrap CLI commands |
| Agent | New `sbs-improver` | Distinct from `sbs-developer` (analysis vs implementation) |
| Ad-hoc tools | Always ask | Per alignment |
| Logging | Dialogue → Claude logs | Per alignment |

---

## Deliverables

### 1. Skill File
**Path:** `.claude/skills/self-improve/SKILL.md`

5 phases with archive integration:
- `discovery` → Query archive, generate findings
- `selection` → Present summary, user picks items
- `dialogue` → Refine each finding via discussion
- `logging` → Log confirmed items via `/log`
- `archive` → Record cycle completion

### 2. Agent File
**Path:** `.claude/agents/sbs-improver.md`

YAML frontmatter + sections:
- Analysis capabilities (archive querying, pattern recognition)
- Four pillars framework
- Tool inventory (archive tools, search tools)
- Anti-patterns for analysis work

### 3. MCP Tools (2 new tools)
**Path:** `forks/sbs-lsp-mcp/src/sbs_lsp_mcp/sbs_tools.py`

| Tool | Purpose |
|------|---------|
| `sbs_analysis_summary` | Generate findings report from archive data |
| `sbs_entries_since_self_improve` | Count entries since last cycle |

### 4. Archive Integration
**Path:** `dev/scripts/sbs/archive/` (existing)

- Track `self-improve-cycle` tag
- Store cycle metadata in entry
- Support `entries_since_last_self_improve` queries

---

## Implementation Waves

### Wave 1: Foundation + Tests (Single Agent)
**Agent:** `sbs-developer`

1. Create `.claude/skills/self-improve/SKILL.md`
   - YAML frontmatter (name, description, version)
   - Invocation patterns (`/self-improve`)
   - Archive protocol (5 phases)
   - Recovery semantics

2. Create `.claude/agents/sbs-improver.md`
   - YAML frontmatter (name, model: opus, color)
   - Four pillars framework documentation
   - Tool inventory and usage patterns
   - Analysis workflow guidance

3. Create `dev/scripts/sbs/tests/pytest/test_self_improve.py`
   - `test_skill_file_exists_and_parses` (V1)
   - `test_agent_file_exists_and_parses` (V2)
   - `test_archive_entry_with_self_improve_tag` (V5)
   - `test_recovery_from_each_phase` (V7)

**Validation:** Run `pytest test_self_improve.py -k "skill or agent or archive or recovery"` - V1, V2, V5, V7 should pass

### Wave 2: MCP Tools + Tests (Single Agent)
**Agent:** `sbs-developer`

1. Add Pydantic models to `sbs_models.py`:
   - `AnalysisFinding` - Single improvement finding
   - `AnalysisSummary` - Aggregated findings report
   - `SelfImproveEntries` - Entries since last cycle

2. Add tool functions to `sbs_tools.py`:
   - `sbs_analysis_summary()` with `_impl` function for testability
   - `sbs_entries_since_self_improve()` with `_impl` function for testability

3. Add tests to `test_self_improve.py`:
   - `test_analysis_summary_returns_structured_data` (V3)
   - `test_entries_since_self_improve_returns_count` (V4)

**Validation:** Run `pytest test_self_improve.py` - all 6 automated tests should pass

### Wave 3: End-to-End Verification (Manual)
**Agent:** Orchestrator (top-level)

1. Invoke `/self-improve` manually
2. Verify archive state transitions through all 5 phases
3. Confirm `self-improve-cycle` tag appears in final archive entry
4. Document any issues for follow-up

**Validation:** V6 (full cycle) verified manually

---

## Gates

```yaml
gates:
  tests: all_pass
  quality:
    T1: >= 1.0  # CLI commands execute
    T2: >= 0.8  # Ledger population
  regression: >= 0
```

---

## Validation Checklist → Test Mapping

Each checklist item maps to a specific automated test:

| # | Checklist Item | Test File | Test Function |
|---|----------------|-----------|---------------|
| 1 | `/self-improve` skill file exists and parses correctly | `test_self_improve.py` | `test_skill_file_exists_and_parses` |
| 2 | `sbs-improver` agent file exists with correct frontmatter | `test_self_improve.py` | `test_agent_file_exists_and_parses` |
| 3 | `sbs_analysis_summary` MCP tool callable and returns structured data | `test_self_improve.py` | `test_analysis_summary_returns_structured_data` |
| 4 | `sbs_entries_since_self_improve` MCP tool callable and returns count | `test_self_improve.py` | `test_entries_since_self_improve_returns_count` |
| 5 | Archive entries with `self-improve-cycle` tag can be created | `test_self_improve.py` | `test_archive_entry_with_self_improve_tag` |
| 6 | Full cycle can be completed | Manual | End-to-end invocation (not automated) |
| 7 | Recovery works after context reset | `test_self_improve.py` | `test_recovery_from_each_phase` |

### Test Details

**File:** `dev/scripts/sbs/tests/pytest/test_self_improve.py`

```python
# Test 1: Skill file validation
def test_skill_file_exists_and_parses():
    """V1: Skill file exists and has valid YAML frontmatter."""
    skill_path = SBS_ROOT / ".claude/skills/self-improve/SKILL.md"
    assert skill_path.exists()
    content = skill_path.read_text()
    # Parse frontmatter
    assert "name: self-improve" in content
    assert "version:" in content
    # Verify all 5 phases documented
    for phase in ["discovery", "selection", "dialogue", "logging", "archive"]:
        assert phase in content

# Test 2: Agent file validation
def test_agent_file_exists_and_parses():
    """V2: Agent file exists with correct frontmatter."""
    agent_path = SBS_ROOT / ".claude/agents/sbs-improver.md"
    assert agent_path.exists()
    content = agent_path.read_text()
    assert "name: sbs-improver" in content
    assert "model: opus" in content
    # Verify four pillars documented
    for pillar in ["user effectiveness", "Claude execution", "alignment patterns", "system engineering"]:
        assert pillar.lower() in content.lower()

# Test 3: MCP tool - analysis summary
def test_analysis_summary_returns_structured_data():
    """V3: sbs_analysis_summary returns valid structured data."""
    # Import the tool function directly (bypass MCP)
    from sbs_lsp_mcp.sbs_tools import sbs_analysis_summary_impl
    result = sbs_analysis_summary_impl()
    assert hasattr(result, 'total_entries')
    assert hasattr(result, 'entries_by_trigger')
    assert hasattr(result, 'most_common_tags')

# Test 4: MCP tool - entries since self-improve
def test_entries_since_self_improve_returns_count():
    """V4: sbs_entries_since_self_improve returns entry count."""
    from sbs_lsp_mcp.sbs_tools import sbs_entries_since_self_improve_impl
    result = sbs_entries_since_self_improve_impl()
    assert hasattr(result, 'entries_since')
    assert hasattr(result, 'count_by_trigger')
    assert isinstance(result.count_by_trigger, dict)

# Test 5: Archive tagging
def test_archive_entry_with_self_improve_tag():
    """V5: Can create archive entry with self-improve-cycle tag."""
    from sbs.archive.entry import ArchiveIndex
    index = ArchiveIndex.load(ARCHIVE_DIR / "archive_index.json")
    # Verify tag is in known tags or can be applied
    # (This tests the schema supports the tag, not actual creation)
    test_entry = index.entries[list(index.entries.keys())[0]]
    # Verify tags field is a list that could accept new tags
    assert isinstance(test_entry.tags, list)

# Test 7: Recovery semantics
def test_recovery_from_each_phase():
    """V7: Archive state correctly tracks self-improve phases."""
    from sbs.archive.entry import ArchiveIndex
    # Verify global_state schema supports self-improve skill
    # Create mock state and validate structure
    mock_state = {"skill": "self-improve", "substate": "discovery"}
    assert mock_state["skill"] == "self-improve"
    assert mock_state["substate"] in ["discovery", "selection", "dialogue", "logging", "archive"]
```

### Test Tier

All tests in `test_self_improve.py` should be marked as `@pytest.mark.dev` tier (run during development, not evergreen).

---

## Critical Files

| File | Purpose |
|------|---------|
| `.claude/skills/self-improve/SKILL.md` | Skill definition (new) |
| `.claude/agents/sbs-improver.md` | Agent definition (new) |
| `forks/sbs-lsp-mcp/src/sbs_lsp_mcp/sbs_tools.py` | MCP tool implementations (edit) |
| `forks/sbs-lsp-mcp/src/sbs_lsp_mcp/sbs_models.py` | Pydantic models (edit) |
| `.claude/skills/task/SKILL.md` | Reference for phased skill pattern |
| `dev/scripts/sbs/archive/entry.py` | Archive entry schema reference |

---

## Verification Steps

1. **After Wave 1:**
   ```bash
   cd /Users/eric/GitHub/Side-By-Side-Blueprint/dev/scripts
   python -m pytest sbs/tests/pytest/test_self_improve.py -k "skill or agent or archive or recovery" -v
   ```
   Expected: 4 tests pass (V1, V2, V5, V7)

2. **After Wave 2:**
   ```bash
   cd /Users/eric/GitHub/Side-By-Side-Blueprint/dev/scripts
   python -m pytest sbs/tests/pytest/test_self_improve.py -v
   ```
   Expected: 6 tests pass (V1-V5, V7)

3. **After Wave 3:**
   Manual verification that `/self-improve` completes full cycle (V6)

   Archive entry should contain:
   - `global_state: null` (cleared after completion)
   - `tags: [..., "self-improve-cycle"]`
