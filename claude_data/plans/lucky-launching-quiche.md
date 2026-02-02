# Plan: Archive Orchestration & Markdown Refactoring

## Goal

1. Create `Archive_Orchestration_and_Agent_Harmony.md` documenting archive workflows and agent interactions
2. Aggressively reduce CLAUDE.md by leveraging sbs-oracle and delegating to sbs-developer.md
3. Fix documentation gaps around triggers, validators, and rubric lifecycle

---

## Analysis Summary

### Script-Agent Interaction Findings

From deep exploration of `build.py`, `sbs` CLI, and skill files:

| Pattern | Description | Design Status |
|---------|-------------|---------------|
| **Clean separation** | Scripts are standalone CLI tools; agents invoke via Bash | Intentional, enforced |
| **Hybrid compliance** | Script generates prompts, agent does AI validation | Intentional, critical |
| **Trigger metadata** | `--trigger` flag tracks provenance, not behavior | Intentional, simple |
| **Automatic archive** | `build.py` always calls `archive upload` at completion | By design |

### Documentation Gaps

| Gap | Should Document In |
|-----|-------------------|
| Script-agent boundary principle | Archive_Orchestration doc |
| Hybrid compliance pattern explanation | task/SKILL.md |
| Trigger semantics (provenance tracking) | update-and-archive/SKILL.md |
| Validator ↔ T1-T8 mapping | task/SKILL.md |
| Data flow diagrams | Archive_Orchestration doc |

### Target File Responsibilities

| File | Owns | Delegates To |
|------|------|--------------|
| CLAUDE.md | Orchestration, prefs, when to spawn | sbs-developer.md, sbs-oracle |
| sbs-developer.md | Implementation details, patterns, file locations | (keeps technical content) |
| task/SKILL.md | Workflow phases, validators, rubric lifecycle | (self-contained) |
| update-and-archive/SKILL.md | Archive triggers, Oracle regen, porcelain | (self-contained) |
| sbs-oracle.md | Compiled knowledge indices | (auto-generated) |

---

## Wave 1: Create Archive_Orchestration_and_Agent_Harmony.md

**Agent 1: Write the tracking document**

Create `dev/markdowns/Archive_Orchestration_and_Agent_Harmony.md` with:

### 1. Design Principles

Document the intentional architecture:
- **Script-Agent Boundary**: Scripts are standalone CLI tools. They produce output and modify state. They never invoke Claude APIs or spawn agents.
- **Agent Orchestration**: Agents invoke scripts via Bash, parse output, make decisions. Agents never bypass scripts for state changes.
- **Hybrid Patterns**: Some workflows (compliance) have scripts prepare work and agents perform AI validation. Document why.

### 2. Archive Workflow Diagrams (text-based)

```
build.py completion ──┬── trigger="build" ──┐
                      │                      │
/update-and-archive ──┼── trigger="skill" ──┼──► sbs archive upload ──► ArchiveEntry
                      │                      │
manual CLI ───────────┴── trigger=none ─────┘
```

Also document:
- Build → archive upload → iCloud sync (automatic)
- /task → /update-and-archive → archive upload (skill-triggered)
- Manual standalone invocations

### 3. Trigger Semantics Table

| Trigger | Invoked By | What Happens | Purpose |
|---------|-----------|--------------|---------|
| `--trigger build` | `build.py` | Extract session, apply tags, sync | Provenance: automated build |
| `--trigger skill` | `/update-and-archive` | Same behavior | Provenance: skill invocation |
| Manual (no flag) | User CLI | Same behavior | Provenance: manual |

**Key insight**: Trigger affects metadata only, not behavior. Archive always does the same thing.

### 4. Hybrid Compliance Pattern

Explain the bidirectional flow:
1. Agent runs `sbs compliance`
2. Script computes pages, generates prompts with screenshot paths
3. Agent reads screenshots with vision, provides JSON validation
4. Script (or agent) updates ledger with results

**Why this pattern**: Scripts don't call AI APIs. Agents don't bypass scripts for state. This is the intersection point.

### 5. Validator ↔ T1-T8 Mapping

| Tests | Category | Type | Description |
|-------|----------|------|-------------|
| T1-T2 | CLI | Deterministic | CLI execution, ledger population |
| T3-T4 | Dashboard | AI Vision | Dashboard clarity, toggle discoverability |
| T5-T6 | Design | Deterministic | Status color match, CSS variable coverage |
| T7-T8 | Polish | AI Vision | Jarring-free check, professional score |

### 6. Rubric Lifecycle

| Phase | Trigger | What Happens |
|-------|---------|--------------|
| Creation | `/task --grab-bag` Phase 3 | User approves metrics, rubric saved to `dev/storage/rubrics/` |
| Evaluation | Execution loop | Each metric evaluated, results tracked |
| Invalidation | Repo changes | Scores marked stale via REPO_SCORE_MAPPING |
| Reuse | `/task --rubric <id>` | Load existing rubric for new evaluation |

### 7. File Responsibility Matrix

Cross-reference to which file documents what, with links.

**Files:** `dev/markdowns/Archive_Orchestration_and_Agent_Harmony.md` (new)

---

## Wave 2: Documentation Refactoring

**Agent 2: Consolidate all documentation updates**

This wave combines: skill gap fixes + CLAUDE.md reduction + conflict resolution.

### 2A: update-and-archive/SKILL.md

Add/update:
- Trigger semantics section (provenance tracking, not behavior)
- Clarify when Oracle regeneration happens (Part 3, after README updates)
- Document the `sbs archive upload` call in Part 4

### 2B: task/SKILL.md

Add/update:
- Validator → T1-T8 mapping table
- Hybrid compliance pattern explanation (script prepares, agent validates)
- Document rubric invalidation (REPO_SCORE_MAPPING triggers staleness)
- Clarify `/task --rubric <id>` behavior

### 2C: CLAUDE.md Aggressive Reduction

**Target**: ~1019 lines → ~500-600 lines

**Move to sbs-developer.md** (if not already there):
1. "Key Implementation Details" section (~108 lines)
2. "Key File Locations by Repository" section (~38 lines)
3. Detailed "Build Pipeline Phases" (~50 lines)
4. Detailed "Configuration Files" examples (~40 lines)

**Replace with cross-references**:
```markdown
## Technical Details

For implementation details, file locations, and build internals, see:
- [sbs-developer.md](.claude/agents/sbs-developer.md) - Implementation patterns
- [sbs-oracle](.claude/agents/sbs-oracle.md) - Codebase knowledge (use Task tool to query)
```

**Remove entirely** (duplicated or cross-ref):
- Build Script Steps (already in dev/storage/README.md)
- Visual Testing workflow details (cross-ref to dev/storage/README.md)
- Detailed archive system description (now in Archive_Orchestration doc)

### 2D: Reconcile Conflicts

During the reduction:
1. Verify actual line counts with `wc -l`
2. Update any remaining shared content to match exactly
3. Ensure cross-references use correct paths

**Files:**
- `.claude/skills/update-and-archive/SKILL.md`
- `.claude/skills/task/SKILL.md`
- `CLAUDE.md`
- `.claude/agents/sbs-developer.md`

---

## Wave 3: Finalization

**Agent 3: Oracle regeneration and verification**

### 3A: Regenerate Oracle

```bash
cd /Users/eric/GitHub/Side-By-Side-Blueprint/dev/scripts
python3 -m sbs oracle compile
```

Verify Oracle includes:
- New Archive_Orchestration document content
- Updated file responsibility matrix
- Validator → T1-T8 mapping
- Hybrid compliance pattern

### 3B: Verification Checks

1. CLAUDE.md line count (target: ~500-600)
2. No broken cross-references (grep for dead links)
3. No duplicated content between CLAUDE.md and sbs-developer.md
4. Trigger semantics documented in update-and-archive skill
5. Validator mapping documented in task skill
6. Archive_Orchestration document complete and accurate

---

## Critical Files

| File | Action |
|------|--------|
| `dev/markdowns/Archive_Orchestration_and_Agent_Harmony.md` | Create (new) |
| `CLAUDE.md` | Aggressive reduction (~50% smaller) |
| `.claude/agents/sbs-developer.md` | Receives moved content |
| `.claude/skills/task/SKILL.md` | Add validator mapping, hybrid compliance, rubric lifecycle |
| `.claude/skills/update-and-archive/SKILL.md` | Add trigger semantics |
| `.claude/agents/sbs-oracle.md` | Regenerate |

---

## Success Criteria

1. ✅ Archive_Orchestration_and_Agent_Harmony.md exists with:
   - Design principles (script-agent boundary)
   - Workflow diagrams
   - Trigger semantics
   - Hybrid compliance pattern
   - Validator ↔ T1-T8 mapping
   - Rubric lifecycle
   - File responsibility matrix

2. ✅ CLAUDE.md reduced to ~500-600 lines

3. ✅ No duplicated content between CLAUDE.md and sbs-developer.md

4. ✅ Trigger semantics documented in update-and-archive/SKILL.md

5. ✅ Validator mapping + hybrid compliance in task/SKILL.md

6. ✅ Oracle regenerated with new content

7. ✅ All cross-references work (no broken links)
