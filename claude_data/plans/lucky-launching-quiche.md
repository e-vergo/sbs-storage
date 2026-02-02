# Plan: Cement Archive-as-Orchestration-Substrate Architecture

## Goal

Establish the stable foundation for the archive system with three roles:
1. **Event Log**: Append-only entries, regularized schema, source of truth
2. **State Machine**: Global state + substate tracking for skills
3. **Context Provider**: MCP tools for auto-injecting context to agents

Plus: Fix critical bugs, simplify skill definitions, refactor storage structure.

---

## Decisions Baked In

| Decision | Choice |
|----------|--------|
| Epochs | 1:1 correspondence with `/update-and-archive` |
| Context injection | Via custom MCP (sbs-lsp-mcp fork) |
| Hash storage | In archive entries (not separate files) |
| Single-agent constraint | Architectural foundation |
| Philosophy | General-purpose tools, not hyper-specific agents |
| Grab-bag mode | Removed from /task skill |
| Rubric infrastructure | Removed entirely |

---

## Wave 0: Documentation (Parallel)

Four documentation tasks that can run in parallel (no code changes).

### Task 0A: Create TAXONOMY.md

**File:** `dev/markdowns/permanent/TAXONOMY.md`

Define the document classification system:
- **Permanent**: Architectural bedrock, changes = months+
- **Living**: Current state and plans, changes = normal iteration
- **Generated**: Auto-produced, never manually edited

Include semantic meaning of changes and file location conventions.

### Task 0B: Update Archive_Orchestration_and_Agent_Harmony.md

**File:** `dev/markdowns/permanent/Archive_Orchestration_and_Agent_Harmony.md`

Major expansion to include:
- Three roles of archive (event log, state machine, context provider)
- State machine model with `global_state` and `state_transition`
- Epoch semantics (1:1 with update-and-archive)
- MCP fork philosophy (sbs-lsp-mcp extending lean-lsp-mcp)
- Context injection patterns
- Updated ArchiveEntry schema
- Skill substates documentation

### Task 0C: Update dev/storage/README.md

**File:** `dev/storage/README.md`

- Document new directory structure
- Remove rubric CLI documentation
- Add state machine fields documentation
- Add epoch semantics

### Task 0D: Create dev/markdowns/living/README.md

**File:** `dev/markdowns/living/README.md`

**Purpose:** This document is read by agents at key moments. It must clearly establish the dual nature of this repository.

Content to include:
1. **Monorepo Purpose Statement**: This monorepo is the primary location for development of the Side-by-Side Blueprint project.
2. **Dual Nature**: The project has multiple distinct but interwoven purposes, and so does this repository:
   - **Tool Development**: A coherent, compact, and dedicated environment for developing the Side-by-Side Blueprint tool itself
   - **Meta-Tooling Development**: The active development environment for agentic and project-specific development tools
3. **Why This Matters for Agents**: Agents working in this codebase are simultaneously:
   - Building the product (SBS tool)
   - Building the tools that build the product (archive system, validators, MCP tools)
   - Being tracked by the tools they're building (strange loops)

This embedding ensures agents understand the recursive/self-referential nature of this project.

**Spawn:** Single `sbs-developer` agent with all four tasks (docs only).

---

## Wave 1: Fix Critical Bug

### Task 1A: Fix archive path in ledger_ops.py

**File:** `dev/scripts/sbs/tests/compliance/ledger_ops.py`

**Bug:** Line 65-67 returns wrong path:
```python
def get_archive_root() -> Path:
    return get_sbs_root() / "archive"  # WRONG
```

**Fix:** Import and use `ARCHIVE_DIR` from `sbs.core.utils`:
```python
from sbs.core.utils import ARCHIVE_DIR

def get_archive_root() -> Path:
    return ARCHIVE_DIR  # dev/storage
```

Update dependent functions: `get_images_dir()`, `get_project_dir()`, `get_ledger_path()`, etc.

### Task 1B: Delete stale /archive directory

**Location:** `/Users/eric/GitHub/Side-By-Side-Blueprint/archive/`

Delete the entire directory (contains duplicate compliance artifacts created by the bug).

**Spawn:** Single `sbs-developer` agent.

---

## Wave 2: Schema Enhancement

### Task 2A: Add state machine fields to ArchiveEntry

**File:** `dev/scripts/sbs/archive/entry.py`

Add to `ArchiveEntry` dataclass:
```python
# State machine fields (new)
global_state: Optional[dict] = None  # {skill: str, substate: str} or null when idle
state_transition: Optional[str] = None  # "phase_start" | "phase_end" | null
epoch_summary: Optional[dict] = None  # Computed on skill-triggered entries
```

Update `to_dict()` and `from_dict()` methods to handle new fields.

Bump `ArchiveIndex.version` to `"1.1"`.

### Task 2B: Add global_state to ArchiveIndex

**File:** `dev/scripts/sbs/archive/entry.py`

Add to `ArchiveIndex` dataclass:
```python
# Global orchestration state
global_state: Optional[dict] = None  # Current {skill, substate} or null when idle
last_epoch_entry: Optional[str] = None  # Entry ID of last epoch close
```

### Task 2C: Update upload.py for state fields

**File:** `dev/scripts/sbs/archive/upload.py`

Modify `archive_upload()` to accept and populate state machine fields:
- Accept `global_state`, `state_transition` parameters
- Compute `epoch_summary` for skill-triggered entries
- Update index `global_state` on state transitions

**Spawn:** Single `sbs-developer` agent.

---

## Wave 3: Skill Updates

### Task 3A: Simplify /task SKILL.md

**File:** `.claude/skills/task/SKILL.md`

Changes:
1. **Remove entire Grab-Bag Mode section** (lines ~151-305)
2. Remove all rubric references from main workflow
3. Add **Task Agent Model** section explaining:
   - `/task` invocation spawns a dedicated task agent
   - Agent becomes "center stage" (directly beneath top-level)
   - Agent survives compactions via archive state reconstruction
   - All dev work should go through `/task` for data collection
4. Add **Substates** documentation:
   - `alignment` → `planning` → `execution` → `finalization`
5. Document phase archival: each phase transition archives state

### Task 3B: Update /update-and-archive SKILL.md

**File:** `.claude/skills/update-and-archive/SKILL.md`

Changes:
1. Add **Substates** documentation:
   - `readme-wave` → `oracle-regen` → `porcelain` → `archive-upload`
2. Document **Epoch Semantics**:
   - This skill closes epochs
   - Entry gets `epoch_summary` with aggregated data
3. Update required reading paths for new markdown locations

**Spawn:** Single `sbs-developer` agent.

---

## Wave 4: Storage Cleanup

### Task 4A: Remove deprecated items

**Delete:**
- `dev/storage/manifests/` directory (deprecated, data in compliance_ledger)
- `dev/storage/lifetime_stats.json` (all zeros, never populated)
- `dev/storage/rubrics/` directory (grab-bag removal)
- `dev/storage/caches/` directory (empty placeholder)
- `dev/storage/mathlib-pins/` directory (empty placeholder)

### Task 4B: Fix SBSTest nested structure anomaly

**Investigate:** `dev/storage/SBSTest/archive/2026-02-01_21-00-26/latest/`

This appears to be a nested capture anomaly. Either flatten or remove.

### Task 4C: Create baselines.json

**File:** `dev/storage/baselines.json`

Create the baseline pointer registry:
```json
{
  "version": "1.0",
  "baselines": {},
  "history": []
}
```

**Spawn:** Single `sbs-developer` agent.

---

## Wave 5: Code Cleanup

### Task 5A: Remove rubric-related code

**Files to modify/remove:**
- `dev/scripts/sbs/tests/rubrics/` - Delete entire directory or gut
- `dev/scripts/sbs/tests/validators/rubric_validator.py` - Remove or stub
- `dev/scripts/sbs/cli.py` - Remove `sbs rubric *` command group

**Note:** Careful dependency analysis first. May need to retain stubs if other code imports.

**Spawn:** Single `sbs-developer` agent.

---

## Wave 6: Validation

### Task 6A: Run test suite

```bash
cd /Users/eric/GitHub/Side-By-Side-Blueprint/dev/scripts
/opt/homebrew/bin/pytest sbs/tests/pytest/ -v
```

Verify:
- No regressions from path changes
- No import errors from rubric removal
- Archive schema changes work

### Task 6B: Build and verify

```bash
./dev/build-sbs-test.sh
```

Verify:
- Build completes without error
- Archive upload creates entry with new fields
- No stale `/archive` directory created
- State machine fields populated (if triggered via skill)

### Task 6C: Visual spot check

- Check `dev/storage/archive_index.json` structure
- Verify no duplicate `archive/` at repo root
- Confirm rubric files removed

**Spawn:** Single `sbs-developer` agent (or handle inline).

---

## Critical Files Summary

| File | Wave | Action |
|------|------|--------|
| `dev/markdowns/permanent/TAXONOMY.md` | 0 | Create |
| `dev/markdowns/permanent/Archive_Orchestration_and_Agent_Harmony.md` | 0 | Major update |
| `dev/storage/README.md` | 0 | Update |
| `dev/markdowns/living/README.md` | 0 | Create (monorepo purpose statement) |
| `dev/scripts/sbs/tests/compliance/ledger_ops.py` | 1 | Fix path bug |
| `/archive/` (repo root) | 1 | Delete |
| `dev/scripts/sbs/archive/entry.py` | 2 | Add state fields |
| `dev/scripts/sbs/archive/upload.py` | 2 | Populate state fields |
| `.claude/skills/task/SKILL.md` | 3 | Remove grab-bag, add task-agent model |
| `.claude/skills/update-and-archive/SKILL.md` | 3 | Add substates, epoch docs |
| `dev/storage/manifests/` | 4 | Delete |
| `dev/storage/rubrics/` | 4 | Delete |
| `dev/storage/baselines.json` | 4 | Create |
| `dev/scripts/sbs/cli.py` | 5 | Remove rubric commands |

---

## Execution Summary

```
Wave 0 (Parallel): Documentation
  └── sbs-developer: TAXONOMY.md, Architecture doc, storage/README.md, living/README.md

Wave 1 (Sequential): Critical Bug Fix
  └── sbs-developer: Fix ledger_ops.py, delete /archive

Wave 2 (Sequential): Schema Enhancement
  └── sbs-developer: entry.py fields, upload.py population

Wave 3 (Sequential): Skill Updates
  └── sbs-developer: Simplify /task, update /update-and-archive

Wave 4 (Sequential): Storage Cleanup
  └── sbs-developer: Delete deprecated, fix anomaly, create baselines.json

Wave 5 (Sequential): Code Cleanup
  └── sbs-developer: Remove rubric code from CLI

Wave 6 (Sequential): Validation
  └── sbs-developer or inline: Tests, build, spot check
```

**Total agents:** 6-7 (one per wave)

---

## Success Criteria

1. ✅ `dev/markdowns/permanent/TAXONOMY.md` exists with categories defined
2. ✅ `dev/markdowns/living/README.md` exists with dual-purpose monorepo statement
3. ✅ Architecture doc updated with three roles, state machine, epochs
4. ✅ No stale `/archive` directory at repo root after build
5. ✅ `ArchiveEntry` has `global_state`, `state_transition`, `epoch_summary` fields
6. ✅ `/task` skill has no grab-bag section, has task-agent model docs
7. ✅ `/update-and-archive` skill has substates and epoch documentation
8. ✅ No `rubrics/`, `manifests/`, `lifetime_stats.json` in dev/storage
9. ✅ `baselines.json` created
10. ✅ Test suite passes
11. ✅ Build completes without error
