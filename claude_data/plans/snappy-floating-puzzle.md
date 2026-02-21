# Axiom Transparency and Dashboard Integration (Issue #357)

## Context

Axioms are invisible in the current SBS dashboard — users have no way to see what foundational axioms their project depends on. This matters for formal verification projects where axiom hygiene is a quality signal. The fix replicates the established blueprint coverage pattern: **badge on dashboard -> dedicated page -> link from graph page**.

Additionally, the `computeFullyProven` algorithm reportedly fails to promote nodes that transitively depend on axioms, despite the code appearing correct. This needs runtime investigation.

## Design Decisions (from alignment)

- **Badge format:** "Axioms: N standard, M custom" — green if 0 custom, yellow if >0 custom
- **Page scope:** All axioms, grouped into "Standard" (green) and "Project" (purple) sections
- **Graph link:** In the link row alongside "View Full Graph" and untagged links
- **fullyProven bug:** Investigate via build output, same task

## Implementation

### Wave 1: Data Layer (Dress)

**File: `toolchain/Dress/Dress/Graph/Types.lean`** (after line 207)

Add new types following `UncoveredDecl`/`CoverageResult` pattern:

```lean
inductive AxiomKind where
  | standard  -- propext, funext, Quot.sound, Classical.choice
  | project   -- project-defined axioms
  deriving Repr, Inhabited, BEq

structure AxiomDecl where
  name : String
  moduleName : String
  kind : AxiomKind
  deriving Repr, Inhabited

structure AxiomResult where
  standardAxioms : Array AxiomDecl
  projectAxioms : Array AxiomDecl
  deriving Repr, Inhabited
```

Add `ToJson`/`FromJson` instances for all three types (follow `CoverageResult` pattern at lines 222-236).

Extend `CheckResults` (line 236): add `axiomTracking : Option AxiomResult := none`

Update `CheckResults` ToJson/FromJson instances (lines 256-282) to include the new field.

**File: `toolchain/Dress/Dress/Graph/Build.lean`** (after `computeCoverage` at line 519)

Add `collectAxioms` following the `computeCoverage` iteration pattern:

```lean
def collectAxioms (env : Lean.Environment) (projectModules : Array Lean.Name)
    : AxiomResult := Id.run do
  let standardNames : Array String := #[
    "propext", "funext", "Quot.sound", "Classical.choice"
  ]
  let mut standard : Array AxiomDecl := #[]
  let mut project : Array AxiomDecl := #[]

  for h : idx in [:env.header.moduleData.size] do
    let moduleData := env.header.moduleData[idx]
    let modName := env.header.moduleNames[idx]!
    for name in moduleData.constNames do
      let some ci := env.find? name | continue
      match ci with
      | .axiomInfo _ =>
        let decl := { name := name.toString, moduleName := modName.toString,
                       kind := if standardNames.contains name.toString
                               then .standard else .project }
        if decl.kind == .standard then standard := standard.push decl
        else if isProjectModule modName projectModules then
          project := project.push decl
      | _ => continue

  { standardAxioms := standard, projectAxioms := project }
```

Key: Only collect project axioms from project modules, but collect standard axioms from anywhere (they'll be in Lean core modules).

**File: `toolchain/Dress/Main.lean`**

- Update `buildEnhancedManifest` signature (line 21): add `axiomTracking : Option Graph.AxiomResult := none`
- Pass axiom data into `checks`: `let checks := { checks with soundnessResults, coverage, axiomTracking }`
- At call site (line 239): compute axioms and pass:
  ```lean
  let axiomTracking := Graph.collectAxioms (← getEnv) modules
  let manifestJson := buildEnhancedManifest reducedGraph soundnessResults (some coverage) (some axiomTracking)
  ```

### Wave 2: Deserialization (Runway)

**File: `toolchain/Runway/Runway/Dress/Load.lean`**

This file has its own copies of `CoverageResult` and `CheckResults` for JSON deserialization. Mirror the new types here:

- Add `AxiomKind`, `AxiomDecl`, `AxiomResult` structures (after `CoverageResult`)
- Add their `FromJson` instances
- Extend `CheckResults` with `axiomTracking : Option AxiomResult := none` (around line 253)
- Update `CheckResults.FromJson` to parse the new field (around line 268)

### Wave 3: UI — Badge (Runway)

**File: `toolchain/Runway/Runway/Render.lean`** (after coverage badge, line 577)

Add axiom badge following the coverage badge pattern:

```lean
-- Axiom Tracking
(match checks.axiomTracking with
 | some ax =>
   let hasCustom := !ax.projectAxioms.isEmpty
   let axClass := if hasCustom then "check-warn" else "check-pass"
   let axIcon := if hasCustom then "⚠" else "✓"
   let axText := s!"Axioms: {ax.standardAxioms.size} standard, {ax.projectAxioms.size} custom"
   renderCheckItem axClass axIcon axText
     (href := some "dep_graph/axioms.html")
 | none =>
   renderCheckItem "check-pending" "○" "Axiom Tracking"
     (extra := spanClass "check-status" (Html.text true "Not computed"))) ++
```

### Wave 4: UI — Dedicated Page (Runway)

**File: `toolchain/Runway/Runway/DepGraph.lean`**

Add after `untaggedPage` (after line 890):

1. `axiomTableBody` — table rows for axiom declarations (Name, Module columns)
2. `axiomModuleGroup` — collapsible module group (reuse `dg-chapter-group` classes)
3. `axiomSection` — section with color-coded header ("Standard Axioms" with green accent, "Project Axioms" with purple accent)
4. `axiomPage` — full page with breadcrumb "Dashboard / Axioms", two sections, `pageShell` wrapper

CSS: Use existing `.check-pass` border-left for standard section, add `.axiom-section-project` with `border-left: 3px solid var(--sbs-status-axiom)` in `blueprint.css`.

**File: `toolchain/Runway/Runway/DepGraph.lean`** — `dashboardPage` function (line 657)

Add parameter: `axiomCount : Nat := 0`

Add axiom link alongside untagged link (after line 663):
```lean
let axiomLink := if axiomCount > 0 then
  .tag "a" #[("href", "dep_graph/axioms.html"), ("class", "dg-full-graph-link")]
    (Html.text true s!"View Axioms ({axiomCount})")
  else Html.empty
```

Add `axiomLink` to the link row div (line 667-670).

### Wave 5: UI — Page Generation (Runway)

**File: `toolchain/Runway/Runway/Theme.lean`** (after line 579)

Add axiom page generation alongside untagged page:

```lean
-- 6. Axioms page -> dep_graph/axioms.html
match site.checks with
| some checks =>
  match checks.axiomTracking with
  | some ax =>
    let axiomSidebar := DefaultTheme.renderSidebar site.chapters (some "dep_graph") "../" site.config availDocs
    let axiomHtml := DepGraph.axiomPage ax
      (config := some site.config) (sidebar := some axiomSidebar)
    IO.FS.writeFile (depGraphDir / "axioms.html") (Html.doctype ++ "\n" ++ axiomHtml.asString)
    let total := ax.standardAxioms.size + ax.projectAxioms.size
    IO.println s!"  Generated dep_graph/axioms.html ({total} axioms)"
  | none => pure ()
| none => pure ()
```

Update the `dashboardPage` call site to pass axiom count.

### Wave 6: CSS (minimal)

**File: `toolchain/dress-blueprint-action/assets/blueprint.css`**

Add after existing check-item styles (~line 1130):

```css
.axiom-section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  font-weight: 600;
  font-size: 1rem;
}
.axiom-section-standard .axiom-section-header {
  border-left: 3px solid var(--sbs-success);
  background-color: var(--sbs-check-pass-bg);
}
.axiom-section-project .axiom-section-header {
  border-left: 3px solid var(--sbs-status-axiom);
  background-color: var(--sbs-check-warn-bg);
}
```

### Wave 7: fullyProven Investigation

This is diagnostic, not code changes:

1. Build SBS-Test: `./dev/build-sbs-test.sh`
2. Examine generated graph JSON at `SBS-Test/.lake/build/dressed/dep-graph.json`
3. Check: Does `choice_axiom` node exist? What's its status? Are edges to/from it present?
4. If the bug is confirmed, trace through `computeFullyProven` logic with the actual data
5. Fix based on findings (likely in axiom detection or edge construction)

## Files Modified (summary)

| File | Change |
|------|--------|
| `Dress/Dress/Graph/Types.lean` | Add AxiomKind, AxiomDecl, AxiomResult; extend CheckResults |
| `Dress/Dress/Graph/Build.lean` | Add collectAxioms function |
| `Dress/Main.lean` | Call collectAxioms, pass to manifest |
| `Runway/Runway/Dress/Load.lean` | Mirror new types + deserialization |
| `Runway/Runway/Render.lean` | Add axiom badge in renderChecks |
| `Runway/Runway/DepGraph.lean` | Add axiomPage + axiomCount param to dashboardPage |
| `Runway/Runway/Theme.lean` | Generate axioms.html |
| `dress-blueprint-action/assets/blueprint.css` | Axiom section header styles |

## Verification

1. **Build:** `./dev/build-sbs-test.sh` — must complete without errors
2. **Check manifest:** Verify `manifest.json` contains `axiomTracking` field with standard + project arrays
3. **Check pages:** Verify `dep_graph/axioms.html` is generated
4. **Visual:** Serve site and confirm dashboard badge appears with correct counts, links to axioms page, axioms page renders with two sections
5. **fullyProven:** Examine graph JSON for `choice_axiom` node status and edge presence
6. **Lean diagnostics:** `lean_diagnostic_messages` on all modified files — zero errors
