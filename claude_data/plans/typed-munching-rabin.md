# Plan: Epic #323 Convergence — Complete All Dep Graph QoL Issues

## Context

Waves 1-3 (#324, #325, #326) are implemented but uncommitted across Dress (5 files), Runway (3 files), and dress-blueprint-action (4 files). Three new issues (#327, #328, #329) were just logged. The user wants to converge all 6 sub-issues to completion before any git push, using iterative QA to ensure stability.

**No pushes until everything is verified.** All work stays local.

## Current State

| # | Issue | Status | Implementation |
|---|-------|--------|---------------|
| 324 | Axiom diamond + color | Code complete, uncommitted | Dress (5 files), Runway, CSS |
| 325 | Status filter | Code complete, uncommitted | Runway, JS, CSS |
| 326 | Per-declaration subgraphs | Code complete, uncommitted | Runway (2 files), JS, CSS |
| 329 | SBS-Test overhaul | Not started | SBS-Test Lean + TeX |
| 328 | Dep graph dashboard + static pages | Not started | Runway, JS, CSS |
| 327 | Status dot → modal overlay | Not started | Runway, JS, CSS |

## Execution Order

Issues ordered by dependency:

1. **#329 SBS-Test overhaul** — Must come first. Creates a clean 20-25 node test substrate with axioms, full `@[blueprint]` coverage, and meaningful DAG structure. All subsequent work validates against this.

2. **#328 Dep graph dashboard + static pages** — Replaces `dep_graph.html` with dashboard hub. Generates per-declaration static pages under `dep_graph/`. Needs clean test data from #329.

3. **#327 Status dot → modal overlay** — Converts status dot to clickable button that opens modal subgraph. Links to static pages from #328. Replaces Wave 3 inline toggle.

## Convergence Workflow

Uses `sls_converge` pattern: **Setup → [Eval → Fix → Rebuild]×N → Report**

The convergence goal is not just "pages load" — it's "all 6 issues fully implemented, builds clean, visual QA passes."

### Phase 0: Stabilize Waves 1-3 (pre-convergence)

**Goal:** Verify existing uncommitted work is stable before building on it.

1. Build Dress → Build Runway → Regenerate SBS-Test site
2. Visual QA: verify dep_graph.html has legend, filter bar, data attributes
3. Visual QA: verify chapter pages have toggle buttons and embedded JSON
4. If failures → fix before proceeding

**Gate:** Dress builds clean, Runway builds clean, SBS-Test generates with 40 nodes, all 3 new features visible in HTML output.

### Phase 1: SBS-Test Overhaul (#329)

**Goal:** 20-25 declarations, 1+ axiom, 100% `@[blueprint]`, meaningful DAG.

**Execution:**
1. `sbs-developer` agent: Redesign SBS-Test declarations
   - Strip demo chapters (bracket, delimiter, security, statement-attribute)
   - Keep 3-4 chapters with themed mathematical content
   - Add at least 1 `axiom` declaration
   - Every declaration gets `@[blueprint]` with varied statuses
   - Design a meaningful DAG (not linear — branching, merging)
   - Update `blueprint.tex`, `SBSTest/Blueprint.lean`, `SBSTest/Paper.lean`
2. Build SBS-Test (`lake build`)
3. Regenerate site (`lake exe runway ...`)
4. **Eval:** Verify node count (20-25), axiom present (diamond in SVG), all statuses represented, dep graph has edges

**Gate:** `lake build` clean, site generates, dep graph has 20-25 nodes with at least 1 diamond, filter bar works, chapter pages have toggle buttons.

### Phase 2: Dep Graph Dashboard (#328)

**Goal:** Dashboard hub replaces dep_graph.html. Static pages for each declaration.

**Execution:**
1. `sbs-developer` agent(s) — up to 2 parallel (Lean + JS/CSS):
   - **Lean (Runway):** New `DepGraph.lean` functions for dashboard HTML (stats section, declaration list table). New function to generate individual graph pages. Update `Main.lean` or `Theme.lean` to emit `dep_graph/` directory with N+1 pages. Move full graph to `dep_graph/full.html`.
   - **Assets (JS/CSS):** Dashboard styling reusing index.html patterns. Individual page JS (subgraph renderer from Wave 3, adapted for standalone page). Breadcrumb navigation.
2. Build Runway → Regenerate SBS-Test
3. **Eval:** Dashboard loads at `dep_graph.html` with stats and declaration list. Full graph accessible at `dep_graph/full.html`. At least 1 individual page exists (e.g., `dep_graph/foundation.html`). Sidebar link works.

**Gate:** All pages generate and load. Declaration list has correct count. Individual pages render subgraph SVG. Full graph retains filter bar and legend.

### Phase 3: Modal Overlay (#327)

**Goal:** Status dot becomes clickable button opening modal with subgraph.

**Execution:**
1. `sbs-developer` agent:
   - Modify `Runway/Render.lean`: status dot span → button element
   - Remove/replace Wave 3 inline toggle (`.node-graph-toggle`) with modal trigger
   - Add modal HTML structure (backdrop, close button, mode toggle, viewport)
   - JS: modal open/close logic, subgraph rendering inside modal, mode switching
   - CSS: modal styles (overlay, centered panel, responsive)
   - Link from modal to individual static page ("View full graph →")
2. Build Runway → Regenerate SBS-Test
3. **Eval:** Status dot is clickable. Modal opens with neighborhood subgraph. Mode toggle works. Close button/escape/backdrop dismiss. Link to static page navigates correctly.

**Gate:** Modal renders on all chapter pages. Subgraph shows correct neighbors. No JS errors in console.

### Phase 4: Full QA Convergence

**Goal:** All 6 issues verified end-to-end. System stable.

**Method:** `sls_converge` with custom eval criteria.

**Eval checklist (all must pass):**
1. `lake build` succeeds for Dress, Runway, SBS-Test
2. SBS-Test site generates with correct node count
3. Dashboard page loads with stats and full declaration list
4. Full graph page loads with filter bar, legend, diamonds
5. At least 3 individual graph pages load with subgraphs
6. At least 2 chapter pages load with modal-triggerable status dots
7. Filter bar toggles correctly hide/show nodes + edges
8. Modal opens/closes without JS errors
9. Subgraph mode toggle (neighborhood ↔ ancestry) works
10. Links between dashboard → individual pages → chapter pages all resolve

**Iteration:** If any check fails → spawn `sbs-developer` to fix → rebuild → re-evaluate. Max 3 iterations.

**USER CHECKPOINT:** After the first QA eval cycle completes, pause and present results to the user before continuing with fix iterations. This lets the user assess whether the convergence direction is correct and provide course corrections.

**Exit conditions:**
- **Converged:** All 10 checks pass
- **Plateau:** Pass rate doesn't improve between iterations
- **Max iterations:** 3 attempts exhausted

### Phase 5: User Review

**Goal:** User reviews all changes before any commit or push.

1. Present summary of all changes across repos (file list + high-level diff)
2. Launch local server for user to inspect visually
3. User approves or requests adjustments
4. Commit and push only after explicit user approval

## Files Modified (Cumulative)

| Repo | Files | Issues |
|------|-------|--------|
| Dress | Build, Json, Layout, Svg, Types | #324 |
| Runway | DepGraph, Render, Theme, Main | #324-328 |
| dress-blueprint-action | blueprint.css, common.css, dep_graph.css, verso-code.js | #324-328 |
| SBS-Test | Lean sources, blueprint.tex, Blueprint.lean, Paper.lean | #329 |

## Build/Rebuild Command

```bash
# Build chain (used at each eval point)
cd Dress && lake build
cd Runway && lake build
cd SBS-Test && lake build
cd Runway && lake exe runway --build-dir SBS-Test/.lake/build --output SBS-Test/.lake/build/runway SBS-Test/runway.json
```

## Risk Mitigation

- **Runway API changes:** If dashboard restructuring breaks existing page generation, the full graph is preserved as a separate route (`dep_graph/full.html`)
- **SBS-Test content:** If 20-25 declarations is insufficient to test all features, we can add more incrementally
- **Modal JS complexity:** If modal interaction is brittle, we keep the inline toggle as fallback and add modal as progressive enhancement
- **Large graph performance:** Individual pages embed only their subgraph data, not the full JSON
