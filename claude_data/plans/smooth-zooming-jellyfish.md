# Task 3: Gate Enforcement, Test-Catalog Integration, and Archive Invariant Tests

## Summary

Three objectives that stress-test the tooling's ability to handle its own complexity:

1. **Pre-Transition Gate Validation** - Move gate enforcement from agent compliance to code enforcement
2. **Test-Catalog Integration** - Make TEST_CATALOG.md a first-class artifact in the Oracle and documentation
3. **Archive Invariant Tests** - Pin down nebulous concepts from Archive_Orchestration_and_Agent_Harmony.md with testable assertions

**Meta-goal:** If we can write tests for concepts like "agent harmony" and enforce gates in code, the system demonstrates it can specify and validate non-trivial requirements.

---

## Design Decisions

### Task 1: Pre-Transition Gate Validation

| Question | Decision | Rationale |
|----------|----------|-----------|
| Where do gates live? | Parse from active plan file | Plans already contain YAML gate definitions; no new indirection |
| No gates defined? | Permissive (allow with warning) | Don't break existing paths; not all transitions need gates |
| Override mechanism? | `--force` flag | Emergency escape hatch; logged prominently |
| Which transitions? | Only `/task` execution→finalization | `/update-and-archive` has different semantics |

### Task 2: Test-Catalog Integration

- Add `dev/storage/TEST_CATALOG.md` to Oracle's ROOT_FILES
- Document in CLAUDE.md, sbs-developer.md, dev/storage/README.md

### Task 3: Archive Invariant Tests

Tests categorized by confidence level:

| Category | Needs Agent? | Examples |
|----------|--------------|----------|
| High-confidence | No | Entry immutability, schema consistency, single-skill invariant, phase ordering |
| Medium-confidence | No | Epoch summary presence, tagging rules, ledger correspondence |
| Low-confidence | Yes (hybrid) | Context injection relevance, "natural checkpoint" quality |

---

## Execution Waves

### Wave 1: Foundation (Parallel-safe, single agent)

**Task 2 implementation:**
- `dev/scripts/sbs/oracle/compiler.py` - Add TEST_CATALOG.md to ROOT_FILES
- `CLAUDE.md` - Add TEST_CATALOG.md to Reference Documents table
- `.claude/agents/sbs-developer.md` - Add to tooling section
- `dev/storage/README.md` - Add link in Related Documentation

**Validation:** `sbs oracle compile` includes TEST_CATALOG concepts

### Wave 2: Gate Implementation (Sequential, single agent)

**Step 2A: Gate module**
- New file: `dev/scripts/sbs/archive/gates.py`
  - `GateDefinition` dataclass
  - `parse_gates_from_plan()` - Extract YAML gates section
  - `evaluate_test_gate()` - Run pytest, check threshold
  - `evaluate_quality_gate()` - Run validators, check scores
  - `check_gates()` - Combined evaluation

**Step 2B: Upload integration**
- Modify: `dev/scripts/sbs/archive/upload.py` (around line 402)
  - Add `force` parameter
  - Before `execution→finalization` transition:
    - If `global_state.skill == "task"` and transitioning to finalization
    - And not `force` flag
    - Run gate checks; block if any fail

**Step 2C: CLI flag**
- Modify: `dev/scripts/sbs/archive/cmd.py`
  - Add `--force` argument to upload subcommand

**Validation:**
- `sbs archive upload --help` shows `--force` flag
- Gate failure blocks transition (test with intentional failure)

### Wave 3: Test Suite (Single agent)

**New file: `dev/scripts/sbs/tests/pytest/test_archive_invariants.py`**

```python
@pytest.mark.evergreen
class TestEntryImmutability:
    """Entries should not change after creation."""
    def test_entry_hash_stable_after_save_reload()
    def test_entry_fields_unchanged_after_index_reload()

@pytest.mark.evergreen
class TestSchemaConsistency:
    """All entries must conform to ArchiveEntry schema."""
    def test_required_fields_present()
    def test_optional_fields_valid_types()
    def test_state_fields_valid_enum_values()

@pytest.mark.evergreen
class TestSingleActiveSkillInvariant:
    """Only one skill can be active at a time."""
    def test_new_skill_requires_idle_state()
    def test_phase_end_clears_global_state()

@pytest.mark.evergreen
class TestPhaseTransitionOrdering:
    """Phase transitions must follow valid sequence."""
    def test_alignment_before_planning()
    def test_planning_before_execution()
    def test_execution_before_finalization()

@pytest.mark.evergreen
class TestStateValueValidation:
    """global_state must be null OR valid {skill, substate} dict."""
    def test_null_is_valid_state()
    def test_valid_skill_substate_dict()
    def test_invalid_skill_name_rejected()

@pytest.mark.evergreen
class TestEpochSemantics:
    """Epoch closing entries must include epoch_summary."""
    def test_skill_trigger_includes_epoch_summary()
    def test_last_epoch_entry_updated_on_close()
```

**New file: `dev/scripts/sbs/tests/pytest/test_gates.py`**

```python
@pytest.mark.evergreen
class TestGateParsing:
    def test_parse_complete_gate()
    def test_parse_minimal_gate()
    def test_parse_no_gates_section()

@pytest.mark.evergreen
class TestGateEvaluation:
    def test_all_pass_requirement()
    def test_threshold_requirement()
    def test_quality_score_gate()

@pytest.mark.evergreen
class TestGateEnforcement:
    def test_gate_failure_blocks_transition()
    def test_force_flag_bypasses_gate()
    def test_non_task_skill_skips_gates()
```

**Validation:** All new tests pass

### Wave 4: Integration Testing (Orchestrator)

Manual validation by orchestrator:
1. Create plan with gates that will fail
2. Attempt transition without `--force` → should block
3. Attempt transition with `--force` → should succeed with warning
4. Run full test suite: `sbs_run_tests()`

---

## Gates

```yaml
gates:
  tests: all_pass
  quality:
    T1: >= 1.0    # CLI commands work
    T2: >= 0.9    # Ledger population
  regression: >= 0
```

---

## Key Files

**New Files:**
- `dev/scripts/sbs/archive/gates.py` - Gate validation logic
- `dev/scripts/sbs/tests/pytest/test_archive_invariants.py` - Archive semantic tests
- `dev/scripts/sbs/tests/pytest/test_gates.py` - Gate validation tests

**Modified Files:**
- `dev/scripts/sbs/oracle/compiler.py` - Add TEST_CATALOG.md (line 32-34)
- `dev/scripts/sbs/archive/upload.py` - Gate checking (around line 402)
- `dev/scripts/sbs/archive/cmd.py` - Add --force flag
- `dev/scripts/sbs/tests/pytest/conftest.py` - New fixtures if needed
- `CLAUDE.md` - Document TEST_CATALOG.md
- `.claude/agents/sbs-developer.md` - Document TEST_CATALOG.md
- `dev/storage/README.md` - Link to TEST_CATALOG.md

**Reference Files:**
- `dev/scripts/sbs/archive/entry.py` - ArchiveEntry/ArchiveIndex schema
- `dev/markdowns/permanent/Archive_Orchestration_and_Agent_Harmony.md` - Source of invariants
- `.claude/skills/task/SKILL.md` - Gate format (lines 88-99)

---

## Verification

| Wave | Check | Command |
|------|-------|---------|
| 1 | TEST_CATALOG in Oracle | `sbs oracle compile && grep TEST_CATALOG .claude/agents/sbs-oracle.md` |
| 2 | Force flag exists | `sbs archive upload --help \| grep force` |
| 2 | Gates block transition | Manual test with failing gate |
| 3 | Invariant tests pass | `pytest test_archive_invariants.py -v` |
| 3 | Gate tests pass | `pytest test_gates.py -v` |
| 4 | Full suite | `sbs_run_tests()` - all pass |

---

## Success Criteria

1. Gate enforcement moved from agent compliance to code enforcement
2. TEST_CATALOG.md integrated into Oracle and documented
3. Archive invariants from harmony doc have automated tests
4. All tests pass (283+ existing + new tests)
5. `--force` override available for emergencies
