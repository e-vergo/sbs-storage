# Axiom Transparency and Dashboard Integration

Implementation plan for issue #357: Add axiom tracking badge → dedicated page → graph link, following the blueprint coverage pattern exactly.

## Overview

Pattern: Badge on dashboard → Dedicated page → Link from graph page (identical to coverage/untagged flow)

## Workstream Breakdown

### WS1: Data Layer (Dress/Graph/Types.lean)

**File**: `/Users/eric/GitHub/SLS-Strange-Loop-Station/Side-By-Side-Blueprint/toolchain/Dress/Dress/Graph/Types.lean`

**Changes**:
1. After line 207 (end of `UncoveredDecl`), add:
```lean
/-- An axiom declaration in the project -/
structure AxiomDecl where
  /-- Fully qualified Lean name -/
  name : String
  /-- Module the axiom belongs to -/
  moduleName : String
  /-- Whether this is a standard Lean axiom (propext, funext, quot.sound, choice) -/
  isStandard : Bool
  deriving Repr, Inhabited, ToJson, FromJson
```

2. After line 219 (end of `CoverageResult`), add:
```lean
/-- Axiom tracking results for a project -/
structure AxiomResult where
  /-- Total number of axioms detected -/
  totalAxioms : Nat
  /-- Number of standard Lean axioms -/
  standardAxioms : Nat
  /-- Number of project-specific axioms -/
  customAxioms : Nat
  /-- List of all axioms in the project -/
  axioms : Array AxiomDecl
  deriving Repr, Inhabited
```

3. Modify `CheckResults` structure (line 222):
   - After line 236 (`coverage : Option CoverageResult := none`), add:
```lean
  /-- Axiom detection and classification results -/
  axiomTracking : Option AxiomResult := none
```

**Dependencies**: None

---

### WS2: Axiom Collection Function (Dress/Graph/Build.lean)

**File**: `/Users/eric/GitHub/SLS-Strange-Loop-Station/Side-By-Side-Blueprint/toolchain/Dress/Dress/Graph/Build.lean`

**Changes**:
1. After line 519 (end of `computeCoverage`), add:
```lean
/-- Collect all axioms from the environment.
    Distinguishes between standard Lean axioms and project-specific ones. -/
def collectAxioms (env : Lean.Environment) (projectModules : Array Lean.Name)
    : AxiomResult := Id.run do
  let mut totalAxioms : Nat := 0
  let mut standardAxioms : Nat := 0
  let mut customAxioms : Nat := 0
  let mut axioms : Array AxiomDecl := #[]

  -- Standard Lean axioms (well-known foundational axioms)
  let standardAxiomNames : Std.HashSet Lean.Name := .ofArray #[
    `propext,
    `Quot.sound,
    `Classical.choice,
    `funext
  ]

  -- Iterate ALL loaded modules
  for h : idx in [:env.header.moduleData.size] do
    let moduleData := env.header.moduleData[idx]
    let modName := env.header.moduleNames[idx]!

    for name in moduleData.constNames do
      let some ci := env.find? name | continue
      match ci with
      | .axiomInfo _ =>
        totalAxioms := totalAxioms + 1
        let isStandard := standardAxiomNames.contains name
        if isStandard then
          standardAxioms := standardAxioms + 1
        else
          -- Only count as custom if it's in project modules
          if isProjectModule modName projectModules then
            customAxioms := customAxioms + 1
        axioms := axioms.push {
          name := name.toString
          moduleName := modName.toString
          isStandard := isStandard
        }
      | _ => continue

  { totalAxioms, standardAxioms, customAxioms, axioms }
```

**Pattern reused**: `computeCoverage` (lines 487-519) — module iteration, project filtering, array accumulation

**Dependencies**: WS1 (AxiomResult type)

---

### WS3: Invoke Collection in Manifest Build (Dress/Main.lean)

**File**: `/Users/eric/GitHub/SLS-Strange-Loop-Station/Side-By-Side-Blueprint/toolchain/Dress/Main.lean`

**Changes**:
1. Modify `buildEnhancedManifest` signature (line 21):
```lean
def buildEnhancedManifest (graph : Graph.Graph)
    (soundnessResults : Array Graph.SoundnessResult := #[])
    (coverage : Option Graph.CoverageResult := none)
    (axiomTracking : Option Graph.AxiomResult := none) : Json :=
```

2. After line 29 (where coverage is added to checks), add axiomTracking:
```lean
  let checks := { checks with soundnessResults := soundnessResults, coverage := coverage, axiomTracking := axiomTracking }
```

3. Find the call site in Main.lean where `buildEnhancedManifest` is invoked (search for "buildEnhancedManifest") and:
   - Add axiom collection call before manifest build
   - Pass result to `buildEnhancedManifest`

**Pattern reused**: Coverage parameter flow (line 23, line 29)

**Dependencies**: WS1 (AxiomResult type), WS2 (collectAxioms function)

---

### WS4: JSON Serialization (Dress/Graph/Json.lean + Runway/Dress/Load.lean)

**File 1**: `/Users/eric/GitHub/SLS-Strange-Loop-Station/Side-By-Side-Blueprint/toolchain/Dress/Dress/Graph/Json.lean`

**Changes**:
1. After line 123 (end of CheckResults ToJson), update to include axiomTracking:
```lean
instance : ToJson CheckResults where
  toJson c := Json.mkObj [
    ("isConnected", .bool c.isConnected),
    ("numComponents", .num c.numComponents),
    ("componentSizes", toJson c.componentSizes),
    ("cycles", toJson c.cycles),
    ("kernelVerified", toJson c.kernelVerified),
    ("soundnessResults", toJson c.soundnessResults),
    ("coverage", toJson c.coverage),
    ("axiomTracking", toJson c.axiomTracking)
  ]
```

2. Add ToJson instances for AxiomDecl and AxiomResult (after CoverageResult ToJson):
```lean
instance : ToJson AxiomDecl where
  toJson a := Json.mkObj [
    ("name", .str a.name),
    ("moduleName", .str a.moduleName),
    ("isStandard", .bool a.isStandard)
  ]

instance : ToJson AxiomResult where
  toJson a := Json.mkObj [
    ("totalAxioms", .num a.totalAxioms),
    ("standardAxioms", .num a.standardAxioms),
    ("customAxioms", .num a.customAxioms),
    ("axioms", toJson a.axioms)
  ]
```

**File 2**: `/Users/eric/GitHub/SLS-Strange-Loop-Station/Side-By-Side-Blueprint/toolchain/Runway/Runway/Dress/Load.lean`

**Changes**:
1. After line 271 (end of CheckResults FromJson), update to include axiomTracking:
```lean
instance : Lean.FromJson CheckResults where
  fromJson? j := do
    let isConnected ← j.getObjValAs? Bool "isConnected"
    let numComponents ← j.getObjValAs? Nat "numComponents"
    let componentSizes ← j.getObjValAs? (Array Nat) "componentSizes"
    let cycles ← j.getObjValAs? (Array (Array String)) "cycles"
    let kernelVerified := match j.getObjValAs? Bool "kernelVerified" with
      | .ok v => some v
      | .error _ => none
    let soundnessResults := match j.getObjValAs? (Array SoundnessResult) "soundnessResults" with
      | .ok v => v
      | .error _ => #[]
    let coverage : Option CoverageResult := match j.getObjValAs? CoverageResult "coverage" with
      | .ok v => some v
      | .error _ => none
    let axiomTracking : Option AxiomResult := match j.getObjValAs? AxiomResult "axiomTracking" with
      | .ok v => some v
      | .error _ => none
    return { isConnected, numComponents, componentSizes, cycles, kernelVerified, soundnessResults, coverage, axiomTracking }
```

2. Add FromJson instances for AxiomDecl and AxiomResult (after CoverageResult FromJson):
```lean
instance : Lean.FromJson AxiomDecl where
  fromJson? j := do
    let name ← j.getObjValAs? String "name"
    let moduleName ← j.getObjValAs? String "moduleName"
    let isStandard ← j.getObjValAs? Bool "isStandard"
    return { name, moduleName, isStandard }

instance : Lean.FromJson AxiomResult where
  fromJson? j := do
    let totalAxioms ← j.getObjValAs? Nat "totalAxioms"
    let standardAxioms ← j.getObjValAs? Nat "standardAxioms"
    let customAxioms ← j.getObjValAs? Nat "customAxioms"
    let axioms ← j.getObjValAs? (Array AxiomDecl) "axioms"
    return { totalAxioms, standardAxioms, customAxioms, axioms }
```

**Pattern reused**: Coverage JSON serialization pattern

**Dependencies**: WS1 (types), WS3 (manifest flow)

---

### WS5: Dashboard Badge (Runway/Render.lean)

**File**: `/Users/eric/GitHub/SLS-Strange-Loop-Station/Side-By-Side-Blueprint/toolchain/Runway/Runway/Render.lean`

**Changes**:
1. After line 577 (end of coverage badge), add axiom tracking badge:
```lean
      -- Axiom Tracking
      (match checks.axiomTracking with
       | some ax =>
         let cls := if ax.customAxioms == 0 then "check-pass" else "check-warn"
         let icon := if ax.customAxioms == 0 then "✓" else "⚠"
         let text := s!"Axioms: {ax.standardAxioms} standard, {ax.customAxioms} custom"
         renderCheckItem cls icon text
           (href := if !ax.axioms.isEmpty then some "dep_graph/axioms.html" else none)
       | none =>
         renderCheckItem "check-pending" "○" "Axiom Tracking"
           (extra := spanClass "check-status" (Html.text true "Not computed"))) ++
```

**Pattern reused**: Coverage badge pattern (lines 555-577) — class/icon logic, href to dedicated page

**Dependencies**: WS1 (AxiomResult type), WS4 (JSON flow)

---

### WS6: Dedicated Axiom Page (Runway/DepGraph.lean)

**File**: `/Users/eric/GitHub/SLS-Strange-Loop-Station/Side-By-Side-Blueprint/toolchain/Runway/Runway/DepGraph.lean`

**Changes**:
1. After line 890 (end of untaggedPage), add:
```lean
/-! ## Axiom Declarations Page -/

/-- Render a table of axiom declarations for a single module. -/
private def axiomTableBody (decls : Array Dress.AxiomDecl) : Html :=
  let rows := decls.map fun decl =>
    .tag "tr" #[] (
      .tag "td" #[] (Html.text true decl.name) ++
      .tag "td" #[("class", "dg-module-cell")] (Html.text true decl.moduleName)
    )
  .tag "div" #[("class", "dg-table-wrapper")] (
    .tag "table" #[("class", "dg-declaration-table")] (
      .tag "thead" #[] (
        .tag "tr" #[] (
          .tag "th" #[] (Html.text true "Name") ++
          .tag "th" #[] (Html.text true "Module")
        )
      ) ++
      .tag "tbody" #[] (.seq rows)
    )
  )

/-- Render a module group as a collapsible section for axiom declarations. -/
private def axiomModuleGroup (moduleName : String) (decls : Array Dress.AxiomDecl) (groupType : String) : Html :=
  let countStr := if decls.size == 1 then "1 axiom" else s!"{decls.size} axioms"
  .tag "div" #[("class", "dg-chapter-group")] (
    .tag "details" #[("open", "")] (
      .tag "summary" #[("class", "dg-chapter-summary")] (
        .tag "span" #[("class", "dg-chapter-title")] (Html.text true moduleName) ++
        .tag "span" #[("class", "dg-chapter-count")] (Html.text true countStr)
      ) ++
      .tag "div" #[("class", "dg-chapter-table-wrapper")] (
        axiomTableBody decls
      )
    )
  )

/-- Create the axiom declarations page listing all axioms in the project.
    Groups axioms into "Standard" (green) and "Project" (purple) sections. -/
def axiomPage (axioms : Array Dress.AxiomDecl) (standardCount customCount : Nat)
    (config : Option Config := none) (sidebar : Option Html := none) : Html :=
  let sidebar := sidebar.getD Html.empty

  -- Split into standard and custom
  let standardAxioms := axioms.filter (·.isStandard)
  let customAxioms := axioms.filter (!·.isStandard)

  -- Group by module name
  let groupByModule (axs : Array Dress.AxiomDecl) : Std.HashMap String (Array Dress.AxiomDecl) := Id.run do
    let mut m : Std.HashMap String (Array Dress.AxiomDecl) := {}
    for ax in axs do
      let key := if ax.moduleName.isEmpty then "Unknown" else ax.moduleName
      let existing := m.getD key #[]
      m := m.insert key (existing.push ax)
    return m

  let standardGrouped := groupByModule standardAxioms
  let customGrouped := groupByModule customAxioms

  -- Sort module names
  let standardModules := standardGrouped.toArray.map (·.1) |>.qsort (· < ·)
  let customModules := customGrouped.toArray.map (·.1) |>.qsort (· < ·)

  let standardSection :=
    if standardCount > 0 then
      .tag "div" #[("class", "axiom-section")] (
        .tag "h2" #[("class", "axiom-section-title axiom-section-standard")]
          (Html.text true s!"Standard Axioms ({standardCount})") ++
        .tag "p" #[("class", "axiom-section-desc")]
          (Html.text true "Foundational Lean axioms (propext, funext, quot.sound, choice)") ++
        .tag "div" #[("class", "dg-chapter-groups")] (
          .seq (standardModules.map fun modName =>
            axiomModuleGroup modName (standardGrouped.getD modName #[]) "standard")
        )
      )
    else Html.empty

  let customSection :=
    if customCount > 0 then
      .tag "div" #[("class", "axiom-section")] (
        .tag "h2" #[("class", "axiom-section-title axiom-section-custom")]
          (Html.text true s!"Project Axioms ({customCount})") ++
        .tag "p" #[("class", "axiom-section-desc")]
          (Html.text true "Project-specific axioms defined in this blueprint") ++
        .tag "div" #[("class", "dg-chapter-groups")] (
          .seq (customModules.map fun modName =>
            axiomModuleGroup modName (customGrouped.getD modName #[]) "custom")
        )
      )
    else Html.empty

  let content :=
    breadcrumb #[("Dashboard", some "../dep_graph.html"), ("Axioms", none)] ++
    .tag "h1" #[("class", "dg-dashboard-title")]
      (Html.text true "Axiom Declarations") ++
    .tag "p" #[("class", "dg-axiom-summary")]
      (Html.text true s!"{standardCount} standard, {customCount} custom") ++
    standardSection ++
    customSection

  pageShell "Axiom Declarations" "dg-dashboard-page" "../" config sidebar content
```

**Pattern reused**: 
- `untaggedPage` structure (lines 860-890)
- `untaggedModuleGroup` collapsible sections (lines 844-856)
- `untaggedTableBody` table rendering (lines 823-841)

**CSS classes needed** (will add in WS8):
- `.axiom-section` — container for standard/custom sections
- `.axiom-section-title` — section header
- `.axiom-section-standard` — green accent
- `.axiom-section-custom` — purple accent
- `.axiom-section-desc` — description text

**Dependencies**: WS1 (AxiomDecl type)

---

### WS7: Graph Link (Runway/DepGraph.lean)

**File**: `/Users/eric/GitHub/SLS-Strange-Loop-Station/Side-By-Side-Blueprint/toolchain/Runway/Runway/DepGraph.lean`

**Changes**:
1. Modify `dashboardPage` signature (line 657):
```lean
def dashboardPage (nodes : Array NodeInfo) (stats : StatusCounts) (config : Option Config := none)
    (sidebar : Option Html := none) (chapters : Array ChapterInfo := #[])
    (untaggedCount : Nat := 0) (axiomCount : Nat := 0) : Html :=
```

2. After line 664 (untaggedLink definition), add:
```lean
  let axiomLink := if axiomCount > 0 then
    .tag "a" #[("href", "dep_graph/axioms.html"), ("class", "dg-full-graph-link")]
      (Html.text true s!"View Axiom Declarations ({axiomCount})")
    else Html.empty
```

3. Update link row (line 667-671):
```lean
    .tag "div" #[("class", "dg-full-graph-link-row")] (
      .tag "a" #[("href", "dep_graph/full.html"), ("class", "dg-full-graph-link")]
        (Html.text true "View Full Interactive Graph") ++
      untaggedLink ++
      axiomLink
    ) ++
```

**Pattern reused**: Untagged link pattern (lines 661-664, 670)

**Dependencies**: WS6 (axiomPage function)

---

### WS8: Page Generation (Runway/Theme.lean)

**File**: `/Users/eric/GitHub/SLS-Strange-Loop-Station/Side-By-Side-Blueprint/toolchain/Runway/Runway/Theme.lean`

**Changes**:
1. After line 579 (end of untagged page generation), add:
```lean
  -- 6. Axiom declarations page -> dep_graph/axioms.html
  match site.checks with
  | some checks =>
    match checks.axiomTracking with
    | some ax =>
      if !ax.axioms.isEmpty then
        let axiomSidebar := DefaultTheme.renderSidebar site.chapters (some "dep_graph") "../" site.config availDocs
        let axiomHtml := DepGraph.axiomPage ax.axioms ax.standardAxioms ax.customAxioms
          (config := some site.config) (sidebar := some axiomSidebar)
        IO.FS.writeFile (depGraphDir / "axioms.html") (Html.doctype ++ "\n" ++ axiomHtml.asString)
        IO.println s!"  Generated dep_graph/axioms.html ({ax.totalAxioms} axioms: {ax.standardAxioms} standard, {ax.customAxioms} custom)"
    | none => pure ()
  | none => pure ()
```

2. Update dashboard page generation call (search for "dashboardPage") to pass axiomCount:
```lean
let axiomCount := match site.checks with
  | some checks => match checks.axiomTracking with
    | some ax => ax.totalAxioms
    | none => 0
  | none => 0

-- Then in the dashboardPage call:
DepGraph.dashboardPage nodes stats (config := some site.config)
  (sidebar := some sidebar) (chapters := site.chapters)
  (untaggedCount := untaggedCount) (axiomCount := axiomCount)
```

**Pattern reused**: Untagged page generation (lines 567-579)

**Dependencies**: WS6 (axiomPage), WS7 (dashboardPage axiomCount param)

---

### WS9: CSS Styling (dress-blueprint-action/assets/dep_graph.css)

**File**: `/Users/eric/GitHub/SLS-Strange-Loop-Station/Side-By-Side-Blueprint/toolchain/dress-blueprint-action/assets/dep_graph.css`

**Changes**:
Add after existing module group styles (around line 821):
```css
/* Axiom page section styling */
.axiom-section {
  margin-bottom: 2rem;
}

.axiom-section-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid currentColor;
}

.axiom-section-standard {
  color: var(--sbs-status-proven);  /* Medium Green */
}

.axiom-section-custom {
  color: var(--sbs-status-axiom);  /* Vivid Purple */
}

.axiom-section-desc {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: 1rem;
}

.dg-axiom-summary {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}
```

**Dependencies**: None (uses existing CSS variables)

---

### WS10: fullyProven Investigation

**Approach**: Build SBS-Test and examine generated graph JSON to diagnose the fullyProven computation for axiom-dependent nodes.

**Steps**:
1. Build SBS-Test: `./dev/build-sbs-test.sh`
2. Examine `manifest.json` or `graph.json` in output directory
3. Look for `choice_axiom` (id: should be axiom status)
4. Look for `elem_self` (id: should be proven, depends on choice_axiom)
5. Look for `subset_refl` (id: should be proven, depends on elem_self)
6. Check fullyProven status propagation:
   - Is `elem_self` marked as `fullyProven`? (Expected: yes, since axioms don't block)
   - Is `subset_refl` marked as `fullyProven`? (Expected: yes, transitive)

**Hypothesis validation**:
- If fullyProven is NOT set: The issue is in `computeFullyProven` algorithm
- If edges are missing: The issue is in edge construction (untagged axioms filtered out)
- If status is wrong: The issue is in status computation

**Diagnosis locations**:
- `Dress/Graph/Build.lean` lines 168-243: `computeFullyProven` algorithm
- `Dress/Graph/Output.lean` lines 55-62: `inferUses` edge filtering
- `Dress/Graph/Build.lean` lines 50-53: `addEdge` endpoint validation

**Expected finding**: Static analysis suggests algorithm is correct. Likely outcome is "works as designed" but needs visual confirmation.

**Dependencies**: WS1-WS8 complete (fresh build with axiom tracking)

---

## Execution Sequence

```
WS1 (Types) → WS2 (Collection) → WS3 (Manifest) → WS4 (JSON) → WS5 (Badge)
                                                              ↘
                                                                WS6 (Page) → WS7 (Link) → WS8 (Generation)
                                                                          ↘
                                                                            WS9 (CSS)

WS10 (Investigation) runs after WS1-WS8 complete and build succeeds
```

**Parallelization**:
- WS5, WS6, WS9 can run in parallel after WS4 completes
- WS7 depends on WS6
- WS8 depends on WS6 and WS7
- WS10 depends on full build after WS8

---

## Testing Plan

1. **Build SBS-Test** with axiom tracking enabled
2. **Verify badge** shows "Axioms: 3 standard, 0 custom" (SBS-Test has choice_axiom as custom)
   - **Correction**: choice_axiom is project-defined, so should be "Axioms: 3 standard, 1 custom" if counting all Lean axioms globally, or "Axioms: 0 standard, 1 custom" if only counting project modules
3. **Click badge** → navigates to `dep_graph/axioms.html`
4. **Verify page** shows:
   - "Standard Axioms" section with propext, funext, Quot.sound, Classical.choice
   - "Project Axioms" section with choice_axiom (or empty if we filter to project-only)
5. **Graph page link** shows "View Axiom Declarations (N)" in link row
6. **fullyProven check**: elem_self and subset_refl should be fullyProven despite depending on axiom

---

## Edge Cases

1. **No axioms**: Badge shows "○ Axiom Tracking" (pending), no link
2. **Only standard axioms**: Badge shows check-pass (green), page shows only Standard section
3. **Project axioms present**: Badge shows check-warn (yellow), page shows both sections
4. **Empty module names**: Group under "Unknown" (existing pattern)
5. **Large axiom lists**: Module groups are collapsible (existing pattern)

---

## Files Modified Summary

| File | Lines | Change Type |
|------|-------|-------------|
| Dress/Graph/Types.lean | +15 | Add AxiomDecl, AxiomResult, axiomTracking field |
| Dress/Graph/Build.lean | +40 | Add collectAxioms function |
| Dress/Main.lean | ~5 | Add axiomTracking parameter and pass-through |
| Dress/Graph/Json.lean | +20 | Add ToJson instances |
| Runway/Dress/Load.lean | +20 | Add FromJson instances |
| Runway/Render.lean | +10 | Add axiom tracking badge |
| Runway/DepGraph.lean | +80 | Add axiomPage function |
| Runway/DepGraph.lean | +5 | Modify dashboardPage signature and link row |
| Runway/Theme.lean | +15 | Add axiom page generation |
| dress-blueprint-action/assets/dep_graph.css | +30 | Add axiom section styling |

**Total**: ~240 lines added/modified across 10 files

