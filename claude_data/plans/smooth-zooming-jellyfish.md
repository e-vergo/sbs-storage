# MVP Dry Run: Systems Validation

## Context

This is a pre-MVP validation task. The MVP goal is releasing the SBS toolchain to the Lean formalization community, where it has already attracted attention from the FRO (Formalization Research Organization).

**Focus:** Validate development infrastructure is solid before pivoting 100% to tool polish.

---

## Validation Objectives

1. **Test Suite** - All tests pass
2. **Quality Validators** - T1-T8 scores acceptable
3. **Build Pipeline** - SBSTest builds successfully
4. **Archive System** - Extraction, tagging, iCloud sync working
5. **Gate System** - Gates evaluate correctly

---

## Execution Plan

### Wave 1: Test Suite Validation (Orchestrator)

Run the full test suite and verify pass rate.

**Commands:**
```bash
sbs_run_tests()  # via MCP
```

**Gate:** All tests pass (or known failures documented)

### Wave 2: Quality Validators (Orchestrator)

Run T1-T8 validators against SBSTest.

**Commands:**
```bash
sbs_validate_project(project="SBSTest")  # via MCP
```

**Gate:** T5, T6 pass (deterministic tests)

### Wave 3: Build Pipeline (Orchestrator)

Verify a clean build completes successfully.

**Commands:**
```bash
sbs_build_project(project="SBSTest", dry_run=True)  # Verify pipeline
```

**Gate:** Dry run succeeds without errors

### Wave 4: iCloud Sync Verification (Orchestrator)

Confirm full archive backup is working.

**Checks:**
- Archive index synced
- Sessions synced (111 expected)
- Project screenshots present
- Claude data directories present

---

## Gates

```yaml
gates:
  tests: all_pass
  quality:
    T5: >= 0.8
    T6: >= 0.8
```

---

## Success Criteria

1. Test suite passes
2. Quality validators show acceptable scores
3. Build pipeline functional
4. iCloud sync complete
5. No blocking issues identified

---

## Post-Validation

If validation passes, the system is ready for the MVP push. Focus shifts entirely to the 8 MVP success criteria from `dev/markdowns/living/MVP.md`:

1. Side-by-side display works
2. Dual authoring modes work (TeX + Verso)
3. Dependency graph works
4. Status colors work (6-color model)
5. Dashboard works
6. Paper generation works
7. CI/CD works
8. Visual quality - professional, no jarring elements
