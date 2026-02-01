# Python Scripts Refactoring Plan

## Summary

Reorganize `dev/scripts/sbs/` from a flat structure into logical subdirectories that align with functionality:
- `core/` - Shared utilities and data structures
- `archive/` - Archive tooling (already well-organized, minimal changes)
- `build/` - Build system (break build.py into modules)
- `tests/` - All validation/testing (compliance, validators, rubrics, pytest)

**Design principles preserved:**
- Single command, single purpose (no new args/configs)
- Mandatory tracking (archival cannot be skipped)
- Absolute imports throughout

---

## Target Structure

```
dev/scripts/
├── .pytest_cache/
├── .venv/
├── pytest.ini
├── build.py                      # Entry point (thin wrapper)
├── README.md
└── sbs/
    ├── __init__.py
    ├── __main__.py
    ├── cli.py                    # Main CLI dispatcher
    │
    ├── core/                     # Foundation layer
    │   ├── __init__.py
    │   ├── README.md
    │   ├── utils.py              # Logger, paths, git, subprocess
    │   ├── git_ops.py            # Git operations across repos
    │   └── ledger.py             # Data structures only (BuildMetrics, UnifiedLedger)
    │
    ├── archive/                  # Archive system (minimal changes)
    │   ├── __init__.py
    │   ├── README.md
    │   ├── cmd.py                # CLI commands (from archive_cmd.py)
    │   ├── entry.py
    │   ├── session_data.py
    │   ├── extractor.py
    │   ├── tagger.py
    │   ├── upload.py
    │   ├── icloud_sync.py
    │   ├── visualizations.py
    │   ├── chat_archive.py
    │   └── retroactive.py
    │
    ├── build/                    # Build system
    │   ├── __init__.py
    │   ├── README.md
    │   ├── config.py             # BuildConfig, project detection
    │   ├── orchestrator.py       # BuildOrchestrator class
    │   ├── phases.py             # Build phase implementations
    │   ├── caching.py            # Cache operations
    │   ├── compliance.py         # Mathlib/deps compliance checks
    │   ├── inspect.py            # Build artifact inspection (from inspect_cmd.py)
    │   └── versions.py           # Version checking (from versions.py)
    │
    └── tests/                    # All validation/testing
        ├── __init__.py
        ├── README.md
        │
        ├── compliance/           # Visual compliance
        │   ├── __init__.py
        │   ├── README.md
        │   ├── capture.py        # Screenshot capture
        │   ├── compare.py        # Screenshot comparison
        │   ├── criteria.py       # Compliance criteria definitions
        │   ├── criteria_design.py
        │   ├── mapping.py        # Repo-to-page mapping
        │   ├── validate.py       # Compliance orchestration
        │   └── ledger_ops.py     # Compliance ledger operations
        │
        ├── validators/           # Validator infrastructure
        │   ├── __init__.py
        │   ├── base.py
        │   ├── registry.py
        │   ├── visual.py
        │   ├── timing.py
        │   ├── code_stats.py
        │   ├── git_metrics.py
        │   ├── ledger_health.py
        │   ├── rubric_validator.py
        │   └── design/
        │       ├── __init__.py
        │       ├── css_parser.py
        │       ├── color_match.py
        │       ├── variable_coverage.py
        │       ├── dashboard_clarity.py
        │       ├── toggle_discoverability.py
        │       ├── jarring_check.py
        │       └── professional_score.py
        │
        ├── rubrics/              # Rubric system
        │   ├── __init__.py
        │   ├── rubric.py         # Rubric data structures
        │   └── cmd.py            # CLI commands (from rubric_cmd.py)
        │
        └── pytest/               # Actual pytest tests
            ├── __init__.py
            ├── conftest.py
            ├── test_cli.py
            ├── test_ledger_health.py
            └── validators/
                ├── __init__.py
                ├── test_color_match.py
                ├── test_dashboard_clarity.py
                ├── test_jarring_check.py
                ├── test_professional_score.py
                ├── test_toggle_discoverability.py
                └── test_variable_coverage.py
```

---

## Dependency Flow

```
                    ┌─────────────┐
                    │   core/     │
                    │ (foundation)│
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
   ┌───────────┐    ┌───────────┐    ┌───────────┐
   │  archive/ │    │   build/  │    │   tests/  │
   │           │    │           │    │           │
   └───────────┘    └───────────┘    └───────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    cli.py   │
                    │ (dispatcher)│
                    └─────────────┘
```

**No circular dependencies.** All imports flow downward.

---

## Implementation Waves

### Wave 1: Create `core/` (Foundation)
**Files to create:**
- `sbs/core/__init__.py`
- `sbs/core/README.md`

**Files to move:**
- `sbs/utils.py` → `sbs/core/utils.py`
- `sbs/git_ops.py` → `sbs/core/git_ops.py`

**Files to split:**
- `sbs/ledger.py` → split into:
  - `sbs/core/ledger.py` (data structures: BuildMetrics, UnifiedLedger, get_or_create_unified_ledger)
  - `sbs/tests/compliance/ledger_ops.py` (operations: ComplianceLedger, load_ledger, save_ledger, etc.)

**Import updates:**
- All modules importing from `utils` → `from sbs.core.utils import ...`
- All modules importing from `git_ops` → `from sbs.core.git_ops import ...`

### Wave 2: Create `build/` (Build System)
**Files to create:**
- `sbs/build/__init__.py`
- `sbs/build/README.md`
- `sbs/build/config.py` (extract BuildConfig, detect_project from build.py)
- `sbs/build/orchestrator.py` (extract BuildOrchestrator class)
- `sbs/build/phases.py` (extract phase methods: sync_repos, build_toolchain, etc.)
- `sbs/build/caching.py` (extract cache functions)
- `sbs/build/compliance.py` (extract compliance checks)

**Files to move:**
- `sbs/inspect_cmd.py` → `sbs/build/inspect.py`
- `sbs/versions.py` → `sbs/build/versions.py`

**Entry point update:**
- `dev/scripts/build.py` becomes thin wrapper:
```python
#!/usr/bin/env python3
from sbs.build import main
if __name__ == "__main__":
    sys.exit(main())
```

### Wave 3: Create `tests/compliance/` (Visual Compliance)
**Files to create:**
- `sbs/tests/__init__.py`
- `sbs/tests/README.md`
- `sbs/tests/compliance/__init__.py`
- `sbs/tests/compliance/README.md`

**Files to move:**
- `sbs/capture.py` → `sbs/tests/compliance/capture.py`
- `sbs/compare.py` → `sbs/tests/compliance/compare.py`
- `sbs/criteria.py` → `sbs/tests/compliance/criteria.py`
- `sbs/criteria_design.py` → `sbs/tests/compliance/criteria_design.py`
- `sbs/mapping.py` → `sbs/tests/compliance/mapping.py`
- `sbs/validate.py` → `sbs/tests/compliance/validate.py`

**From Wave 1 split:**
- `sbs/tests/compliance/ledger_ops.py` (ComplianceLedger operations)

### Wave 4: Reorganize `tests/validators/` and `tests/rubrics/`
**Files to move:**
- `sbs/validators/` → `sbs/tests/validators/`
- `sbs/rubric.py` → `sbs/tests/rubrics/rubric.py`
- `sbs/rubric_cmd.py` → `sbs/tests/rubrics/cmd.py`

**Import updates in validators:**
- `from ..core.utils import ...`
- `from ..compliance.criteria import ...`

### Wave 5: Reorganize pytest tests
**Files to move:**
- `sbs/tests/` → `sbs/tests/pytest/`
  - `conftest.py`
  - `test_cli.py`
  - `test_ledger_health.py`
  - `validators/` subdirectory

**Update pytest.ini:**
```ini
[pytest]
testpaths = sbs/tests/pytest
```

### Wave 6: Update `archive/` imports and move cmd
**Files to move:**
- `sbs/archive_cmd.py` → `sbs/archive/cmd.py`

**Import updates:**
- `from sbs.core.utils import ...`
- Update `__init__.py` exports

### Wave 7: Update `cli.py` dispatcher
**Changes:**
- Import commands from new locations
- Update dispatch paths

### Wave 8: Create READMEs
**Files to create:**
- `dev/scripts/README.md` (top-level overview)
- `sbs/core/README.md`
- `sbs/build/README.md`
- `sbs/tests/README.md`
- `sbs/tests/compliance/README.md`

### Wave 9: Documentation updates
**Files to update:**
- `dev/storage/README.md` (update file paths)
- `.claude/agents/sbs-developer.md` (update file paths)
- `CLAUDE.md` (update file paths if needed)

---

## Critical Files

| File | Action | Notes |
|------|--------|-------|
| `sbs/utils.py` | Move to `core/` | Foundation for everything |
| `sbs/ledger.py` | Split | Data structures → core/, Operations → tests/compliance/ |
| `build.py` | Split into modules | config, orchestrator, phases, caching, compliance |
| `sbs/cli.py` | Update imports | Dispatch to new locations |
| `sbs/validators/` | Move to `tests/` | Update all internal imports |
| `pytest.ini` | Update testpaths | Point to `sbs/tests/pytest/` |

---

## Ledger Split Detail

**Current `ledger.py` (1,258 lines) splits into:**

**`sbs/core/ledger.py`** (~400 lines) - Data structures:
```python
@dataclass
class BuildMetrics: ...

@dataclass
class UnifiedLedger: ...

def get_or_create_unified_ledger(...) -> UnifiedLedger: ...
```

**`sbs/tests/compliance/ledger_ops.py`** (~800 lines) - Compliance operations:
```python
@dataclass
class InteractionResult: ...

@dataclass
class PageResult: ...

@dataclass
class ComplianceLedger: ...

def load_ledger(...) -> ComplianceLedger: ...
def save_ledger(...) -> None: ...
def update_page_result(...) -> None: ...
def mark_pages_for_revalidation(...) -> None: ...
def is_fully_compliant(...) -> bool: ...
```

---

## Build.py Split Detail

**Current `build.py` (1,506 lines) splits into:**

| New File | Lines | Contents |
|----------|-------|----------|
| `build/config.py` | ~100 | BuildConfig, Repo dataclasses, detect_project() |
| `build/orchestrator.py` | ~400 | BuildOrchestrator class, run() method, timing tracking |
| `build/phases.py` | ~500 | sync_repos(), update_manifests(), build_toolchain(), generate_site(), etc. |
| `build/caching.py` | ~100 | get_cache_key(), get_cached_build(), save_to_cache(), restore_from_cache() |
| `build/compliance.py` | ~100 | check_mathlib_version(), check_deps_point_to_main(), run_compliance_checks() |
| `build/__init__.py` | ~50 | main() entry point, exports |

**Entry point `dev/scripts/build.py`:**
```python
#!/usr/bin/env python3
import sys
from sbs.build import main
if __name__ == "__main__":
    sys.exit(main())
```

---

## Import Convention

**Absolute imports everywhere:**
```python
# Good
from sbs.core.utils import log, get_sbs_root
from sbs.tests.compliance.criteria import PAGE_CRITERIA

# Bad (relative)
from ..utils import log
from .criteria import PAGE_CRITERIA
```

---

## Verification

### After Each Wave:
```bash
# Check imports resolve
cd /Users/eric/GitHub/Side-By-Side-Blueprint/dev/scripts
python -c "import sbs"

# Run tests
python -m pytest sbs/tests/pytest -v

# Verify CLI works
python -m sbs --help
python -m sbs capture --help
python -m sbs archive --help
```

### Full Verification:
```bash
# 1. Build SBS-Test
cd /Users/eric/GitHub/Side-By-Side-Blueprint/toolchain/SBS-Test
python ../../dev/scripts/build.py --dry-run

# 2. Run capture
cd /Users/eric/GitHub/Side-By-Side-Blueprint/dev/scripts
python -m sbs capture --project SBSTest --dry-run

# 3. Run compliance
python -m sbs compliance --project SBSTest --dry-run

# 4. Run archive upload
python -m sbs archive upload --dry-run

# 5. Full test suite
python -m pytest sbs/tests/pytest -v
```

---

## Future Opportunity: Rubric-Enforced Push Lock

**Documented for future implementation (not in scope):**

Since archive upload is the only path to push code, we could:
1. Add a `--require-rubric <id>` flag to archive upload
2. Before pushing, evaluate the rubric
3. If score < threshold, block the push and report failures
4. Integrate with `/execute` skill to enforce rubric gates

This would enable:
- Quality gates on all code changes
- Automated enforcement of standards
- Traceable compliance history

**Not implementing now** - just documenting the opportunity.

---

## Out of Scope

- Functional changes to build.py (only reorganization)
- New CLI commands
- Changes to archive upload workflow
- Changes to tagging rules/hooks
- Visual compliance criteria changes
