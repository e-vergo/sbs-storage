# AJAX Modal Fix + Showcase Audit + Tagging + SBS-on-SBS

## Context

OSforGFF CI generates a **34 GB site** (O(n^2) modal embedding). The AJAX modal fix is already implemented locally in Runway, DepGraph.lean, and verso-code.js -- verified working with SBS-Test (3.4MB output, 21 modal fragments). This plan covers shipping the fix, auditing all showcase repos, tagging releases, and making Dress/Runway self-documenting with SBS.

## Phase 1: Ship AJAX Fix

**Goal:** Commit and push the AJAX modal changes to main on each affected submodule.

### Step 1.1: Commit + push dress-blueprint-action
- `cd Side-By-Side-Blueprint/toolchain/dress-blueprint-action`
- `git add assets/verso-code.js && git commit -m "feat: AJAX modal loading for dep graph pages"`
- Push to `e-vergo/dress-blueprint-action` main

### Step 1.2: Commit + push Runway
- `cd Side-By-Side-Blueprint/toolchain/Runway`
- `git add Runway/Theme.lean Runway/DepGraph.lean && git commit -m "feat: write individual modal fragments, remove bulk embedding"`
- Push to `e-vergo/Runway` main

### Step 1.3: Update SBS parent pointer
- `cd Side-By-Side-Blueprint`
- `git add toolchain/Runway toolchain/dress-blueprint-action`
- `git commit -m "chore: update Runway + dress-blueprint-action (AJAX modal loading)"`
- Push to `e-vergo/Side-By-Side-Blueprint` main

### Step 1.4: Update SLS pointer
- `cd /Users/eric/GitHub/SLS-Strange-Loop-Station`
- `git add Side-By-Side-Blueprint && git commit -m "chore: update SBS submodule (AJAX modal fix)"`

## Phase 2: Showcase Audit

**Goal:** Update all 8 showcase repos to latest tooling, push, trigger CI.

### Current State

| Repo | Dress Rev | Behind HEAD | LeanArchitect | CI Workflow |
|------|-----------|-------------|---------------|-------------|
| FLT | `48b3c36` | 0 (current) | `760c6d7` (current) | `sbs-blueprint.yml` |
| OSforGFF | `48b3c36` | 0 (current) | `760c6d7` (current) | `full-blueprint-build-and-deploy.yml` |
| GCR | `75275cc` | 7 behind | `760c6d7` (current) | `full-blueprint-build-and-deploy.yml` |
| PNT | `75275cc` | 7 behind | `760c6d7` (current) | `full-blueprint-build-and-deploy.yml` |
| ChebyshevCircles | `75275cc` | 7 behind | `760c6d7` (current) | `full-blueprint-build-and-deploy.yml` |
| TDCSG | `75275cc` | 7 behind | `760c6d7` (current) | `blueprint.yml` |
| Quine | `9d24fa6` | 35 behind | `d421f49` (behind) | `full-blueprint-build-and-deploy.yml` |
| ReductiveGroups | `b8353f3` | 14 behind | `760c6d7` (current) | `full-blueprint-build-and-deploy.yml` |

All repos use `e-vergo/dress-blueprint-action@main` in CI, so the JS fix propagates automatically. The Dress/LeanArchitect deps need `lake update` + commit + push.

### Execution (parallel agents, 4 max)

**Wave 1** (4 agents):
- Agent A: FLT + OSforGFF (already current -- verify CI triggers, check for stale PRs/issues)
- Agent B: GCR + PNT (`lake update Dress`, commit, push)
- Agent C: ChebyshevCircles + TDCSG (`lake update Dress`, commit, push)
- Agent D: Quine + ReductiveGroups (`lake update Dress LeanArchitect`, commit, push)

Each agent per repo:
1. `lake update Dress` (and `LeanArchitect` if behind)
2. Verify `lake-manifest.json` now points to `48b3c36` (Dress) and `760c6d7` (LA)
3. `git add lake-manifest.json && git commit -m "chore: update Dress to 48b3c36 (AJAX modal fix)"`
4. Push to main
5. Check for stale open PRs/issues on GH (`gh pr list`, `gh issue list`)
6. Trigger or verify CI run (`gh workflow run` or push triggers it)

### Post-Wave: Verify CI
- Monitor CI runs across all 8 repos
- OSforGFF is the critical test (1649 nodes, was 34GB, should now be ~100MB)

## Phase 3: Tag Dress + Runway

**Goal:** Semantic version tags on Dress and Runway after CI green.

### Prerequisites
- All showcase CI runs green (Phase 2 complete)
- No regressions in any showcase build

### Step 3.1: Tag Dress
- `cd Side-By-Side-Blueprint/toolchain/Dress`
- Determine version (check if any prior tags exist -- currently none)
- First release: `v0.1.0`
- `git tag -a v0.1.0 -m "First release: 7-status model, auto-tagger, axiom transparency"`
- Push tag

### Step 3.2: Tag Runway
- `cd Side-By-Side-Blueprint/toolchain/Runway`
- First release: `v0.1.0`
- `git tag -a v0.1.0 -m "First release: AJAX modals, dashboard, axiom page, dep graph"`
- Push tag

## Phase 4: SBS-on-SBS

**Goal:** Use the SBS blueprint toolchain to document Dress and Runway themselves. Both already have `@[blueprint]` attributes and `blueprint.tex`.

### Constraint
Blueprint status attributes must only use: `wip`, `proven`, `fullyProven`, `axiom`, `sorry`. **Never** use `ready`, `notReady`, or `mathlibReady` -- those are for mathematical formalization projects, not tooling.

### Step 4.1: Audit existing blueprint content

**Parallel agents** (2):
- Agent A: Audit Dress `@[blueprint]` attributes across 21 files
  - Check status values used (must not be `ready`/`notReady`/`mathlibReady`)
  - Review quality of `description`, `note`, `reference` fields
  - Check `blueprint.tex` sections and coverage
- Agent B: Audit Runway `@[blueprint]` attributes
  - Same checks as Dress
  - Verify `blueprint.tex` structure

### Step 4.2: Content improvement (parallel agents, up to 4)

Based on audit findings, spawn agents to:
- Fix any forbidden status values
- Improve `description` fields to be genuinely expository
- Ensure `blueprint.tex` provides coherent narrative
- Add missing `@[blueprint]` attributes to key declarations

### Step 4.3: Build + deploy
- Build both projects with `lake build runway` + run Runway site generator
- Verify blueprint sites render correctly
- Push changes, trigger CI

## Verification

| Phase | Verification |
|-------|-------------|
| 1 | `git log` in each repo shows commits pushed to main |
| 2 | `gh run list` shows green CI for all 8 showcase repos; OSforGFF site < 200MB |
| 3 | `git tag -l` shows `v0.1.0` on Dress and Runway |
| 4 | Blueprint sites for Dress and Runway render, no forbidden status values, expository content present |

## Files Modified

| Phase | Repo | Files |
|-------|------|-------|
| 1 | dress-blueprint-action | `assets/verso-code.js` (already done) |
| 1 | Runway | `Runway/Theme.lean`, `Runway/DepGraph.lean` (already done) |
| 2 | All 8 showcase repos | `lake-manifest.json` |
| 4 | Dress | Various `.lean` files with `@[blueprint]`, `blueprint.tex` |
| 4 | Runway | Various `.lean` files with `@[blueprint]`, `blueprint.tex` |
