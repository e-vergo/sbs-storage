# Task 2: Test Organization and Gate Validation

## Summary

Two major objectives:
1. **Test Organization Infrastructure** - Three-tier system + tool catalog
2. **Gate Validation Exercise** - Prove gates work (and understand their limits)

**Critical Finding:** Gate enforcement is 100% agent-side. No code prevents bypassing gates - enforcement relies entirely on the agent following documented protocol.

---

## Part A: Test Organization Infrastructure

### A1: Three-Tier Test System

Add pytest markers to classify tests:

| Tier | Marker | Behavior | Examples |
|------|--------|----------|----------|
| **Evergreen** | `@pytest.mark.evergreen` | Always run, never skip | Core functionality, CLI basics |
| **Dev** | `@pytest.mark.dev` | Toggle-able, state-clampable | Active development, WIP |
| **Temporary** | `@pytest.mark.temporary` | Explicit discard flag | Experiments, debugging |

**Files to modify:**
- `dev/scripts/sbs/tests/pytest/conftest.py` - Add marker registration and filtering
- `dev/scripts/sbs/tests/pytest/test_*.py` - Apply markers to existing tests (default: evergreen)

### A2: Tool Catalog Command

New CLI command: `sbs test-catalog`

```bash
sbs test-catalog              # List all testable components
sbs test-catalog --json       # Machine-readable output
sbs test-catalog --tier dev   # Filter by tier
```

**Output format:**
```
=== SBS Test Catalog ===

MCP Tools (11):
  [✓] sbs_archive_state     Orchestration   Read-only
  [✓] sbs_run_tests         Testing         Read-only
  ...

Pytest Tests (283):
  [evergreen] test_cli.py::test_archive_list_basic
  [evergreen] test_cli.py::test_archive_list_empty
  [dev]       test_new_feature.py::test_wip
  ...

CLI Commands (15):
  [✓] sbs archive upload
  [✓] sbs capture
  ...
```

**Files to create/modify:**
- `dev/scripts/sbs/test_catalog/` - New module
- `dev/scripts/sbs/cli.py` - Register command

### A3: Tier-Aware Test Runner Enhancement

Enhance `sbs_run_tests` MCP tool to support tier filtering:

```python
sbs_run_tests(tier="evergreen")  # Only evergreen tests
sbs_run_tests(tier="all")        # All tests including dev/temporary
```

**File to modify:**
- `forks/sbs-lsp-mcp/src/sbs_lsp_mcp/sbs_tools.py` - Add tier parameter

---

## Part B: Gate Validation Exercise

### B1: Intentionally Fail `sbs_run_tests`

**Setup:**
1. Create a temporary failing test: `test_intentional_fail.py`
   ```python
   import pytest

   @pytest.mark.temporary
   def test_intentional_gate_failure():
       """This test exists to validate gate enforcement."""
       assert False, "Intentional failure for gate validation"
   ```

**Exercise:**
1. Run `sbs_run_tests()` - confirm failure reported
2. Check that task skill would pause (manual verification)
3. Inspect archive via `sbs_archive_state()` - confirm state still in `execution`
4. Inspect `sbs_search_entries(tags=["from-skill"])` - verify entry captured

**Verification:**
- [ ] Test failure detected by `sbs_run_tests`
- [ ] Archive state shows `{skill: "task", substate: "execution"}`
- [ ] No transition to `finalization` occurred

### B2: Intentionally Fail `sbs_validate_project`

**Setup:**
1. Define plan gate: `quality: {T5: >= 1.0}` (impossible threshold)
2. Run `sbs_validate_project(project="SBSTest", validators=["T5"])`

**Exercise:**
1. Confirm T5 returns < 1.0 (normal score)
2. Compare against plan threshold - gate fails
3. Verify task would pause

**Verification:**
- [ ] Validator returns score < 1.0
- [ ] Gate comparison logic would fail
- [ ] Manual: agent should ask user for approval

### B3: Archive Inspection

After each failure, manually verify:

1. **`sbs_archive_state()`** - Confirm:
   - `global_state.skill == "task"`
   - `global_state.substate == "execution"` (not `finalization`)

2. **`sbs_search_entries(trigger="skill")`** - Confirm:
   - Entry exists for current task
   - No `state_transition: "phase_end"` entry yet

3. **`sbs_epoch_summary()`** - Confirm:
   - Entry count reflects current work
   - No epoch closure

### B4: Attempted Bypass (Limited Scope)

**Goal:** Demonstrate that bypass IS possible (no code enforcement), document the gap.

**Exercise:**
1. With gates still failing, manually call:
   ```bash
   python3 -m sbs archive upload --trigger skill \
     --global-state '{"skill":"task","substate":"finalization"}' \
     --state-transition phase_start
   ```
2. Check `sbs_archive_state()` - confirm state changed to `finalization`
3. **Conclusion:** Archive system accepts the transition despite failed gates

**This proves:** Gate enforcement is a contract, not a technical barrier.

### B5: Cleanup

1. Delete `test_intentional_fail.py`
2. Reset archive state:
   ```bash
   python3 -m sbs archive upload --trigger skill --state-transition phase_end
   ```
3. Verify `global_state` is `null`

---

## Execution Strategy

**Wave 1:** Test infrastructure (A1, A2, A3) - Single sbs-developer agent
**Wave 2:** Gate validation (B1-B5) - Manual execution with orchestrator

Wave 2 is intentionally NOT delegated to an agent - the orchestrator (top-level chat) should perform the validation exercise directly to properly verify behavior.

---

## Gates

```yaml
gates:
  tests: all_pass  # After removing intentional failure
  regression: >= 0
```

---

## Verification

1. `sbs test-catalog` command works
2. Pytest markers applied and filterable
3. Gate validation exercise documented with findings
4. Intentional failure test deleted
5. Archive state returned to `null`

---

## Key Files

**Test Infrastructure:**
- `dev/scripts/sbs/tests/pytest/conftest.py`
- `dev/scripts/sbs/test_catalog/__init__.py` (new)
- `dev/scripts/sbs/test_catalog/catalog.py` (new)
- `dev/scripts/sbs/cli.py`
- `forks/sbs-lsp-mcp/src/sbs_lsp_mcp/sbs_tools.py`

**Gate Validation:**
- `dev/scripts/sbs/tests/pytest/test_intentional_fail.py` (temporary)
- Archive inspection via MCP tools
