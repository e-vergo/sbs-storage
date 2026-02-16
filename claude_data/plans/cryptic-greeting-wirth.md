# Plan: Issues #355 + #356 — Untagged Declarations Page & Axiom Count Fix

## Context

Two issues filed today against SBS:

1. **#356 (Bug):** The pie chart on the dashboard shows "0 axiom" in the legend but renders a phantom axiom slice. Root cause: Dress auto-derives `ToJson` for `StatusCounts`, serializing `axiom_` as `"axiom_"` (with underscore). Runway's `parseStatusCounts` reads `"axiom"` (no underscore), gets 0. Additionally, Dress has a redundant `numAxioms` field.

2. **#355 (Feature):** The dashboard Checks tile lists untagged declarations inline as a `<ul>`, which is messy. Move the list to a dedicated static page at `dep_graph/untagged.html`, keep the badge, and make it link to the new page.

## Execution: Two Parallel Agents

These issues touch non-overlapping files (Dress vs Runway), so both agents run concurrently in a single spawn.

---

### Agent 1: Issue #356 — Axiom Count Fix (Dress)

**File:** `Dress/Dress/Graph/Types.lean`

**Changes:**

1. **Remove `numAxioms` field** from `StatusCounts` (line 80)
2. **Replace `deriving ToJson, FromJson`** with custom instances that serialize `axiom_` as `"axiom"` (matching Runway's parser). Pattern: identical to Runway's `StatusCounts` instances at `Site.lean:266-276`.
3. **Remove `numAxioms` counting** from `computeStatusCounts` (lines 154-156) — the `axiom_` count via the `.axiom` match arm (line 160) already handles it.

**No Runway changes needed** — `parseStatusCounts` at `Main.lean:504` already reads `"axiom"`.

---

### Agent 2: Issue #355 — Untagged Declarations Page (Runway)

**Three files:**

#### 1. `Runway/Runway/Render.lean` (lines 570-580)

- Remove the inline `<ul>` listing (`divClass "coverage-detail" (...)` block)
- Add `href := "dep_graph/untagged.html"` to the `renderCheckItem` call (parameter already supported, confirmed at line 491-492)
- Add compact extra text: `"N untagged"` linking to the page

#### 2. `Runway/Runway/DepGraph.lean` (insert before end of namespace, ~line 814)

- Add `untaggedPage` function that:
  - Takes `Array Dress.UncoveredDecl`, optional config/sidebar
  - Groups declarations by module using `Std.HashMap`
  - Renders each module group as a collapsible `<details>` with a table (reuse CSS classes from `chapterGroup`: `dg-chapter-group`, `dg-chapter-summary`, `dg-declaration-table`)
  - Uses `breadcrumb` for navigation: Dashboard → Untagged Declarations
  - Wraps in `pageShell` with `toRoot := "../"` (page lives at `dep_graph/untagged.html`)
- Types available via existing import chain: `Runway.Site` → `Runway.Dress.Load` → `Dress.UncoveredDecl`
- May need to add `import Runway.Dress.Load` explicitly if namespace isn't accessible

#### 3. `Runway/Runway/Theme.lean` (after line 554)

- Add step 5 in `generateDepGraphPages`:
  - Pattern-match on `site.checks` → `checks.coverage` → `cov.uncovered`
  - Generate `dep_graph/untagged.html` using `DepGraph.untaggedPage`
  - Use same sidebar pattern as other dep_graph pages: `DefaultTheme.renderSidebar ... "../"`

---

## Verification

After both agents complete:

1. **Build SBS-Test:** `./dev/build-sbs-test.sh` — confirms Dress + Runway compile
2. **Check diagnostics:** `lean_diagnostic_messages` on all 4 modified files
3. **Inspect manifest:** Verify `manifest.json` contains `"axiom"` key (not `"axiom_"`) in stats
4. **Inspect output:** Verify `dep_graph/untagged.html` exists in build output
5. **Visual QA (if time permits):** Serve site, check pie chart axiom count and coverage badge link
