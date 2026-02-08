# Overnight Execution Plan: 23 Issues Across 7 Waves

## Context

27 open issues on the SBS monorepo. 4 require user involvement (#266, #223, #209, #244) and 2 are epic trackers (#224, #259). The remaining 23 issues are autonomously executable. This plan organizes them into 7 sequential waves, each executed via `/task` skill (direct to main, no PRs). Fix-or-block strategy: spend up to 30 min debugging failures before moving on.

## Alignment Decisions (Locked In)

- **Scope:** Tiers 1-3 (all autonomous issues)
- **Rebuilds:** All OK including showcase (GCR ~5 min, PNT ~20 min)
- **KaTeX:** Do the full rebuild pipeline
- **Branching:** Direct to main via archive upload (no PRs)
- **Execution:** `/task` for every wave
- **Failures:** Fix-or-block (30 min per failure)
- **#272:** Full introspection hierarchy implementation, adapted from parallel-orbiting-pinwheel plan
- **#267/#271:** Merged into one task, close both when fixed
- **#270:** Debug up to 30 min if showcase builds fail
- **#231:** Keep open

## Deferred Issues (Not In Scope)

| # | Title | Reason |
|---|-------|--------|
| 266 | Separate SBS from SLS monorepo | Major architectural decision |
| 223 | Reductive Groups showcase | Math domain decisions |
| 209 | HTML/CSS design intent workflow | Needs user exploration |
| 244 | Restructure SBS grid layout | Major visual, needs user eyes |
| 224 | Epic: SBS Rewrite | Tracker only |
| 259 | Epic: L3 Process Improvements | Tracker only |

---

## Wave 1: MCP Bug Fixes (#277, #260)

**Issues:** #277 (DuckDB index), #260 (label pre-validation)
**Risk:** Low
**Files:** `forks/sbs-lsp-mcp/src/sbs_lsp_mcp/duckdb_layer.py`, `sbs_tools.py`

### #277: DuckDB Index Not Indexing Post-Jan 31

**Root cause identified:** Entry IDs changed format from `YYYYMMDDHHMMSS` (14 chars) to Unix timestamps like `1770409605` (10 chars). In `get_entries()` at duckdb_layer.py:629, `entry_id > ?` does lexicographic string comparison. Since `"1770..." < "2026..."`, all Unix-timestamp entries sort BELOW date-format entries and are missed by both:
- Unfiltered queries (ORDER BY entry_id DESC returns date-format entries first, limit fills before reaching Unix entries)
- `since` filter (ISO date converted to YYYYMMDDHHMMSS format, Unix timestamps never match `> "20260205..."`)

**Fix:**
1. In `get_entries()` (duckdb_layer.py:628-630): Replace `entry_id > ?` with `created_at > ?` for timestamp-based filtering. The `since` parameter should be parsed to a datetime and compared against the `created_at` column.
2. In `sbs_search_entries()` (sbs_tools.py:1242-1249): Pass the `since` value as an ISO timestamp to `get_entries()` instead of converting to entry_id format.
3. Fix the ORDER BY clause in `get_entries()` (line 639): Change `ORDER BY entry_id DESC` to `ORDER BY created_at DESC` for consistent chronological ordering regardless of ID format.
4. Apply the same fix to `get_epoch_entries()` (line 643+) if it uses entry_id ordering.

**Verification:** Call `sbs_search_entries(since="2026-02-05T22:00:00", limit=50)` and verify it returns entries. Run `sbs_run_tests(repo="mcp")`.

### #260: Label Pre-Validation in sbs_issue_create

**Fix:**
1. Add a helper `_get_repo_labels()` in sbs_tools.py that caches repo labels via `gh label list --repo ... --json name --limit 200`
2. In `sbs_issue_create()` (sbs_tools.py:~1526) and `sbs_issue_log()`: Before `gh issue create`, validate each label exists. If invalid labels found, fail fast with a message listing invalid labels and suggesting closest matches (simple substring/prefix matching against cached labels).
3. Same validation in `sbs_issue_log()`.

**Verification:** Call `sbs_issue_create` with a known-bad label and verify it fails with helpful message. Run MCP tests.

---

## Wave 2: LeanArchitect + Infoview Fixes (#268, #267/#271)

**Issues:** #268 (RPC status derivation), #267+#271 (KaTeX rendering)
**Risk:** Medium (Lean changes require rebuild)
**Files:** `forks/LeanArchitect/Architect/RPC.lean`, `forks/vscode-lean4/lean4-infoview/src/infoview/blueprintPanel.tsx`

### #268: Blueprint Infoview Shows notReady for Proven Declarations

**Investigation reveals:** Already fixed. Looking at RPC.lean:77, `nodeToInfo` already calls `deriveStatus env node` (line 79: `status := nodeStatusToString (deriveStatus env node)`). The `deriveStatus` function exists at lines 60-75. This fix was implemented during the Epic #224 work.

**Action:** Verify the fix is working by rebuilding SBS-Test and checking the infoview. If the fix is confirmed working, close the issue. If not working, debug the `deriveStatus` implementation.

### #267/#271: KaTeX Math Rendering in Blueprint Infoview

**Root cause:** Extension dist is stale — missing KaTeX library. The infoview was rebuilt with KaTeX but the extension webpack wasn't re-run to copy the updated bundle.

**Fix sequence:**
1. `cd forks/vscode-lean4/lean4-infoview && npm run build` — rebuild infoview bundle with KaTeX
2. `cd forks/vscode-lean4/vscode-lean4 && npm run build` — rebuild extension (copies infoview dist)
3. `cd forks/vscode-lean4/vscode-lean4 && npm run package` — create .vsix
4. Copy the new bundle to installed extension: `cp -r dist/lean4-infoview/ ~/.vscode/extensions/leanprover.lean4-0.0.222/dist/lean4-infoview/`
5. Verify: grep for `katex` in the installed bundle to confirm it's present

**Additional investigation:** If KaTeX is in the bundle but still not rendering, the `MathStatement` component may need debugging. Add `console.warn` logging to diagnose runtime behavior. Check if `katex` default import resolves correctly in the bundled context.

**Post-fix:** User restarts VSCode to see changes.

**Lean rebuild:** After LeanArchitect changes are confirmed, rebuild SBS-Test:
```bash
cd /Users/eric/GitHub/Side-By-Side-Blueprint/toolchain/SBS-Test
python3 ../../dev/scripts/build.py
```

---

## Wave 3: Showcase Project Update (#270)

**Issue:** #270 (Coordinated Dress + SubVerso update for GCR, PNT)
**Risk:** High (long builds, previous failures)
**Files:** `showcase/*/lake-manifest.json`, `toolchain/Dress/Dress/Capture/InfoTree.lean`

**Current state:**
- SBS-Test works with Dress `fd18878` + SubVerso `160bb35d`
- GCR has old SubVerso `550d0a89` (incompatible with new Dress)
- PNT has correct SubVerso but old Dress `a89e3a5a`
- Both were reverted after build failures (16 SubVerso API errors)

**Strategy:**
1. Start with GCR (faster build ~5 min)
2. Update GCR's `lake-manifest.json` to match SBS-Test's Dress and SubVerso versions
3. Run `python3 ../../dev/scripts/build.py --force-lake` in GCR
4. If build fails: investigate `Dress/Capture/InfoTree.lean` API mismatches (30 min max)
   - Common failures: `buildStandaloneSuffixIndex`, `lazyHighlightIncludingUnparsed`, `HighlightResult` struct changes
   - May need to also update mathlib version to pull in compatible SubVerso transitively
5. If GCR succeeds: repeat for PNT (~20 min build)
6. If GCR fails after 30 min debugging: revert GCR, skip PNT, log findings on #270

**Key insight:** The SubVerso API changes are in `InfoTree.lean` (named parameters, struct fields, function signatures). The fix may require updating `lakefile.lean` or `lake-manifest.json` in each showcase project to pin compatible versions across the dependency chain (SubVerso → LeanArchitect → Dress).

---

## Wave 4: MCP Features (#243, #262, #276)

**Issues:** #243 (auto-run T5/T6), #262 (L3 findings → issues), #276 (block-wait enforcement)
**Risk:** Low
**Files:** `forks/sbs-lsp-mcp/src/sbs_lsp_mcp/skill_tools.py`, `CLAUDE.md`, `.claude/agents/sbs-developer.md`

### #243: Auto-Run T5/T6 Validators in Visual Verification Gate

**Implementation:**
1. In `skill_tools.py`, find the visual verification gate logic (within task finalization phase)
2. When visual change tags are detected (CSS/template/layout changes), auto-invoke T5 (status color match) and T6 (CSS variable coverage) validators
3. Use the validator runner: `from sbs.tests.validators.runner import run_validators`
4. Call `run_validators(project=..., metric_ids=["t5-color-match", "t6-css-coverage"], skip_heuristic=True)`
5. Record scores in the archive entry's `quality_scores` field
6. Gate remains soft — warn on failures but don't block

**Key files:** `dev/scripts/sbs/tests/validators/runner.py` (existing orchestration), `dev/scripts/sbs/tests/validators/design/color_match.py` (T5), `dev/scripts/sbs/tests/validators/design/variable_coverage.py` (T6)

### #262: L3 Findings Auto-Create GitHub Issues

**Implementation:**
1. In `skill_tools.py`, within the `sbs_introspect` tool's `archive` phase for L3+:
2. After writing the synthesis summary, parse findings into actionable items
3. Create an epic issue summarizing the L3 cycle
4. Create individual issues for each actionable finding (max 5 per cycle)
5. Link to epic, apply `origin:self-improve` label
6. De-duplicate: check existing open issues for similar titles before creating

### #276: Block-Wait Enforcement for Agents

**Implementation:**
1. Add a warning to `CLAUDE.md` orchestration section: "NEVER use `run_in_background=true` for sbs-developer agents"
2. Add the same warning to `.claude/agents/sbs-developer.md` header
3. This is documentation/convention enforcement only — no code change needed per the issue

**Verification:** Run `sbs_run_tests(repo="mcp")`. Grep CLAUDE.md for block-wait pattern.

---

## Wave 5: Test Suite + CI (#264, #242)

**Issues:** #264 (post-crush test suite update), #242 (CI cache strategy)
**Risk:** Low-Medium
**Files:** `dev/scripts/sbs/tests/pytest/`, `toolchain/dress-blueprint-action/action.yml`, `dev/markdowns/living/VSCODE_EXT_SPEC.md`

### #264: Post-Crush Test Suite Update

**Scope:**
1. Audit test suite against crush session changes (Crush 1: #245-#249, Crush 2: #250-#254, Crush 3: #255-#258)
2. Update tests that assume two-pass build (now single-pass via Lake-native Dress)
3. Remove obsolete tests tied to `BLUEPRINT_DRESS` env-var gating
4. Add new tests for:
   - Single-pass Dress integration behavior
   - Statement validation (completeness + cross-referencing from #249)
   - Infoview RPC data correctness (from #253)
5. Run convergence pass on `VSCODE_EXT_SPEC.md`: verify spec matches implemented reality
6. Mark the 97 unmarked tests with appropriate tier markers where obvious

**Approach:** Run full test suite first to establish baseline. Then make targeted updates. Re-run to confirm no regressions.

### #242: CI Cache Strategy

**Implementation in `toolchain/dress-blueprint-action/action.yml`:**
1. Existing caches (lines 129-140, 190-201, 248-258) already cover toolchain, Lake, and graph
2. Optimize cache keys:
   - Toolchain: `toolchain-{os}-{hash(lean-toolchain)}` (already exists)
   - Lake: Add `hashFiles('**/lakefile.lean', '**/lakefile.toml')` to key
   - Graph: Change from `github.sha` to `hashFiles('**/manifest.json')` for content-addressed caching
3. Add cache-hit output checks to skip redundant build steps
4. Document expected savings in the issue

**Verification:** The CI action changes can be tested by examining the YAML for correctness. Full CI testing requires a push (will happen via archive upload).

---

## Wave 6: Introspection Hierarchy (#272)

**Issue:** #272 (Full implementation of geometric decay L0-L3 system)
**Risk:** Medium-High (largest feature, touches multiple files)
**Reference plan:** `dev/storage/claude_data/plans/parallel-orbiting-pinwheel.md` (adapted)

### Sub-Wave 6A: MCP Layer

**Files:** `duckdb_layer.py`, `sbs_models.py`, `skill_tools.py`

1. **`sbs_models.py`** — Add `SelfImproveContext` model:
   ```python
   class SelfImproveContext(BaseModel):
       level: int
       multiplier: int = 4
       session_transcript_path: Optional[str]
       entries_since_last_level: List[Dict]
       lower_level_findings: List[str]
       open_issues: List[Dict]
       improvement_captures: List[Dict]
       archive_state: Dict
   ```

2. **`duckdb_layer.py`** — Add `compute_self_improve_level()`:
   - Query entries with `"self-improve"` trigger and `"level:LN"` tags
   - Count L0s since last L1, L1s since last L2, etc.
   - Return highest level where count >= multiplier (default 4)
   - Place near existing `entries_since_self_improve()` at ~line 823

3. **`skill_tools.py`** — Add `sbs_self_improve()` MCP tool:
   - Calls `compute_self_improve_level()` to determine level
   - For L0: locates latest session JSONL
   - For L1+: locates L(N-1) finding documents in `dev/storage/archive/self-improve/`
   - Fetches open issues for correlation
   - Returns `SelfImproveContext`

### Sub-Wave 6B: Agent Definition

**File:** `.claude/agents/sbs-self-improve.md` (new)

Create agent definition with:
- L0 workflow: Read session transcript -> extract patterns -> correlate with issues -> log via `sbs_issue_log` -> write finding to `dev/storage/archive/self-improve/L0-<id>.md`
- L1 workflow: Run L0 first -> synthesize all L0 findings since last L1 -> write L1 finding
- L2+ workflow: Cascade down -> meta-analyze -> write L(N) finding
- Autonomous: No `AskUserQuestion`, no user interaction
- Background-safe: Failure is silent, logged but doesn't block

### Sub-Wave 6C: Documentation Updates

**Files:** `CLAUDE.md`, `dev/markdowns/permanent/SLS_EXTENSION.md`, `dev/markdowns/permanent/Archive_Orchestration_and_Agent_Harmony.md`

1. Add `sbs_self_improve` to CLAUDE.md capability/tools tables
2. Add trigger protocol: spawn `sbs-self-improve` after every `/task` completion
3. Update SLS_EXTENSION.md with auto-trigger spec
4. Update Archive_Orchestration with agent roster

**Verification:** `sbs_run_tests(repo="mcp")`. Verify `compute_self_improve_level()` returns 0 with no prior L0 entries, returns 1 with 4+ L0 entries.

---

## Wave 7: Documentation Batch (#278, #274, #273, #275, #279, #261, #263, #269, #231)

**Issues:** 9 documentation/process tasks
**Risk:** Low
**Approach:** These can be parallelized across up to 4 `sbs-developer` agents since they target non-overlapping files.

### Agent 1: Developer Guide Updates (#278, #275)

**#278** — Add Lean Gotchas section to `.claude/agents/sbs-developer.md`:
```
### Lean Namespace Gotchas
- `def X.foo` inside `namespace X` creates `X.X.foo`
- Always verify fully qualified names with `#check @X.foo`
- For RPC methods: verify string matches what client uses
```

**#275** — Document dual rendering paths in `sbs-developer.md`:
- Structured AST path (`Html/Render.lean`) for standalone LaTeX
- Traverse path (`Traverse.lean` -> `Render.lean` -> `SideBySide.lean`) for blueprint chapters
- Add checklist: any Node/NodeInfo field addition must update BOTH paths

### Agent 2: Test/Validation Standards (#274, #273, #279)

**#274** — Add threshold-based assertion guidelines to `dev/storage/TEST_CATALOG.md`:
- When to use threshold vs exact assertions
- Pattern: `>= 1rem` for spacing, `>= 90%` for coverage
- Examples from `test_sbs_alignment.py`

**#273** — Audit artifact encoding paths in Dress:
- Enumerate all output paths: HTML direct, TeX/base64, hover JSON, signature HTML
- Add regression tests that verify no raw delimiter markers in any output
- Consider centralized sanitization point

**#279** — Design synchronization completeness metric:
- Define fan-out point mappings
- Implement metric in build.py validation phase
- Track paths enumerated vs paths updated ratio

### Agent 3: Process Documentation (#261, #263, #269)

**#261** — Add explore-before-decompose to `/task` alignment:
- Document the pattern in CLAUDE.md or sbs-developer.md
- When task is scoping/planning, spawn Explore agent first

**#263** — Document AskUserQuestion taxonomy effectiveness:
- Query `sbs_question_stats` and `sbs_question_analysis` for patterns
- Document which headers/option counts lead to fastest resolution
- Add findings to CLAUDE.md AskUserQuestion section

**#269** — Document VSCode MCP servers in CLAUDE.md:
- Add `vscode` and `vscode-mcp` to MCP tool tables
- Document when to use VSCode MCP tools vs existing sbs-lsp tools
- Update sbs-developer.md with new tool references

### Agent 4: #231 Investigation

**#231** — Determine remaining work for GitHub Issues VSCode integration:
- Check if extension is properly configured and functional
- Verify custom queries, commit message autocomplete, TODO triggers
- If fully working, document the setup; if gaps exist, document what's missing

---

## Execution Sequence

```
Wave 1 (/task) → Wave 2 (/task) → Wave 3 (/task) → Wave 4 (/task) → Wave 5 (/task) → Wave 6 (/task) → Wave 7 (/task)
```

Each wave follows: skill_start → alignment (minimal, pre-aligned) → planning → execution → finalization → update-and-archive

Between waves: run `pytest sbs/tests/pytest -m evergreen --tb=short` to verify no regressions.

## Global Verification

After all waves complete:
1. `sbs_run_tests(tier="evergreen")` — 719+ tests pass
2. `sbs_run_tests(repo="mcp")` — MCP tests pass
3. `sbs_validate_project(project="SBSTest")` — T1-T8 scores
4. Verify `sbs_search_entries(since="2026-02-05T22:00:00")` returns entries (#277 fix)
5. Verify SBS-Test builds successfully
6. If Wave 3 succeeded: verify GCR and PNT build
7. Archive upload captures all work

## Risk Factors

| Risk | Mitigation |
|------|------------|
| Showcase builds fail (#270) | Revert after 30 min, log findings |
| KaTeX still broken after rebuild (#267/#271) | Log diagnostic findings, leave for interactive debugging |
| Introspection hierarchy scope creep (#272) | Foundation-only fallback if 6C documentation runs long |
| Test suite changes break evergreen tests (#264) | Run suite before and after, revert any regressions |
| Lean build failures | Check `lean_diagnostic_messages` after edits, fix or revert |
