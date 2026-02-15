# Plan: Quine Runtime Verification + Dashboard Checks

## Context

The Quine showcase project exists and builds successfully. It has a kernel-verified proof (`rfl`) that the quine formula equals the source file, plus self-reference proofs. **The gap:** the `main` function's actual runtime behavior is not empirically verified, and the dashboard's "Kernel Verification" and "Soundness Checks" tiles are hardcoded placeholders.

This plan closes the loop: add a runtime verification harness (in Lean, inside Quine.lean itself), wire the results to the Dress manifest, and render them on the Runway dashboard. The verification harness is part of the quined output — maximum self-reference.

## Trust Hierarchy (what this achieves)

| Layer | Verification | Status |
|-------|-------------|--------|
| Kernel (`rfl`) | `quine_formula! = include_str!` | Already done |
| Self-reference | Source contains proof text | Already done |
| **Kernel Verification (dashboard)** | All key declarations fullyProven | **NEW** |
| **Runtime Verification (dashboard)** | `./quine` stdout = source file | **NEW** |
| **Verification self-reference** | Source contains verification code | **NEW** |

## File Changes Summary

| File | Change |
|------|--------|
| `showcase/Quine/Quine.lean` | Add `verifyQuine`, change `main` sig, add `verify_self_ref` theorem, re-bootstrap `d` |
| `toolchain/Dress/Dress/Graph/Types.lean` | Add `SoundnessResult` struct, extend `CheckResults` |
| `toolchain/Dress/Dress/Graph/Json.lean` | Update `ToJson CheckResults` with new fields |
| `toolchain/Dress/Dress/Graph/Build.lean` | Update `computeCheckResults` to compute `kernelVerified` |
| `toolchain/Dress/Main.lean` | Read `soundness.json`, pass to manifest builder |
| `toolchain/Runway/Runway/Dress/Load.lean` | Mirror `SoundnessResult` + `CheckResults` extension, update FromJson/ToJson |
| `toolchain/Runway/Runway/Render.lean` | Replace placeholder rendering (lines 528-539) with data-driven checks |
| `showcase/Quine/blueprint/src/blueprint.tex` | Add section for verification nodes |

---

## Wave 1: Quine.lean Expansion

**Agent:** single `sbs-developer`

### Changes to Quine.lean

**New file structure** (order matters for elaboration):
```
Section 1: Imports
Section 2: Utilities (findSubstr, elaborators)
Section 3: Data (def d := "...")
Section 4: Verification Harness (verifyQuine)     ← NEW
Section 5: Executable (main with --verify)         ← MODIFIED
Section 6: Proofs (existing + verify_self_ref)     ← EXTENDED
Section 7: Post-Elaboration (initialize)
```

**New declaration: `verifyQuine`**
```lean
@[blueprint "verify_quine"
  (title := "Runtime Verification")
  (statement := /-- Executes the quine binary and verifies its output matches the source.
  Closes the empirical loop: the compiled binary actually outputs itself.
  \uses{quine_correct} -/)
  (uses := ["quine_correct"])]
def verifyQuine : IO Bool := do
  let output ← IO.Process.output { cmd := ".lake/build/bin/quine" }
  let source ← IO.FS.readFile "Quine.lean"
  return output.stdout == source
```

**Modified: `main`** — now accepts args, returns UInt32
```lean
def _root_.main (args : List String) : IO UInt32 := do
  if args.contains "--verify" then
    let passed ← Quine.verifyQuine
    if passed then
      IO.println "✓ Quine output matches source"
      -- Write soundness results for Dress manifest
      IO.FS.createDirAll ".lake/build"
      IO.FS.writeFile ".lake/build/soundness.json"
        "{\"checks\":[{\"name\":\"Runtime Verification\",\"passed\":true,\"detail\":\"Executable output matches source file\"}]}"
      return 0
    else
      IO.println "✗ Quine output does NOT match source"
      IO.FS.createDirAll ".lake/build"
      IO.FS.writeFile ".lake/build/soundness.json"
        "{\"checks\":[{\"name\":\"Runtime Verification\",\"passed\":false,\"detail\":\"Output mismatch\"}]}"
      return 1
  else
    -- Quine mode: output source
    let file := include_str! "Quine.lean"
    let marker := "def d := \""
    let pfx := (file.take ((findSubstr file marker).get! + marker.length - 1)).toString
    IO.print pfx
    IO.print d.quote
    IO.print d
    return 0
```

**New theorem: `verify_self_referential`**
```lean
@[blueprint "verify_self_ref"
  (title := "Verification Self-Reference")
  (statement := /-- The source file contains its own runtime verification code.
  The verification harness is part of the quined output. \uses{verify_quine} -/)
  (proof := /-- Elaboration-time check plus \texttt{rfl}. -/)
  (uses := ["verify_quine"])]
theorem verify_self_referential :
    (file_contains! "Quine.lean", "def verifyQuine") = true := rfl
```

**Re-bootstrap `d`:** After all code changes, run the Python bootstrapping script:
1. Write file with `def d := "PLACEHOLDER"`
2. Extract suffix (everything after closing `"` of `def d := "..."` to EOF)
3. Lean-escape the suffix
4. Write back: `prefix + escaped_suffix + '"' + suffix`
5. Verify: `lake build Quine && lake build quine`
6. Check: `.lake/build/bin/quine | diff Quine.lean -` (must be empty)
7. Check: `.lake/build/bin/quine --verify` (must pass)

### Updated Dependency Graph (8 nodes)
```
find_substr ─── quine_data ──┬── quine_main
                              │
                              └── quine_correct (capstone)
                                      │
                              ┌───────┼────────┐
                              │       │        │
                          self_ref  verify_quine  annotations_ref
                                    │
                              verify_self_ref
```

### Verify
- `lake build Quine` succeeds
- `lake build quine` builds executable
- `.lake/build/bin/quine | diff Quine.lean -` = empty
- `.lake/build/bin/quine --verify` prints "✓" and writes `soundness.json`

---

## Wave 2: Dress Extension

**Agent:** single `sbs-developer`

### Types.lean (`toolchain/Dress/Dress/Graph/Types.lean`)

Add before `CheckResults` (around line 131):
```lean
/-- Result of a single soundness check -/
structure SoundnessResult where
  /-- Name of the check -/
  name : String
  /-- Whether the check passed -/
  passed : Bool
  /-- Optional detail message -/
  detail : String := ""
  deriving Repr, Inhabited, ToJson, FromJson
```

Extend `CheckResults` with two new optional fields (defaults preserve backward compatibility):
```lean
structure CheckResults where
  isConnected : Bool
  numComponents : Nat
  componentSizes : Array Nat
  cycles : Array (Array String)
  kernelVerified : Option Bool := none
  soundnessResults : Array SoundnessResult := #[]
  deriving Repr, Inhabited, ToJson, FromJson
```

### Json.lean (`toolchain/Dress/Dress/Graph/Json.lean`)

Update the manual `ToJson CheckResults` instance (lines 84-91) to include new fields:
```lean
instance : ToJson CheckResults where
  toJson c := Json.mkObj [
    ("isConnected", .bool c.isConnected),
    ("numComponents", .num c.numComponents),
    ("componentSizes", toJson c.componentSizes),
    ("cycles", toJson c.cycles),
    ("kernelVerified", toJson c.kernelVerified),
    ("soundnessResults", toJson c.soundnessResults)
  ]
```

**Note:** Types.lean has `deriving ToJson, FromJson` AND Json.lean has a manual instance. Check for compilation errors — may need to remove the `deriving` clause for ToJson/FromJson from CheckResults and keep only the manual instance, or remove the manual instance and rely on deriving. Resolve whichever approach compiles.

### Build.lean (`toolchain/Dress/Dress/Graph/Build.lean`)

Update `computeCheckResults` (line 371) to compute `kernelVerified`:
```lean
def computeCheckResults (g : Graph) : CheckResults :=
  let components := findComponents g
  let componentSizes := components.map (·.size)
  let cycles := detectCycles g
  let keyDecls := g.nodes.filter (·.keyDeclaration)
  let kernelVerified := if keyDecls.isEmpty then none
    else some (keyDecls.all (·.status == .fullyProven))
  { isConnected := components.size <= 1
    numComponents := components.size
    componentSizes := componentSizes
    cycles := cycles
    kernelVerified := kernelVerified }
```

### Main.lean (`toolchain/Dress/Main.lean`)

1. Change `buildEnhancedManifest` signature to accept soundness results:
```lean
def buildEnhancedManifest (graph : Graph.Graph)
    (soundnessResults : Array Graph.SoundnessResult := #[]) : Json :=
```

2. Pass soundness results to check computation:
```lean
  let checks := Graph.computeCheckResults graph
  let checks := { checks with soundnessResults := soundnessResults }
```

3. In `runGraphCmd` (line 147), add soundness.json reading before manifest generation:
```lean
    -- Read soundness results if present
    let soundnessResults ← do
      let soundnessPath : System.FilePath := buildDir / "soundness.json"
      if ← soundnessPath.pathExists then
        let content ← IO.FS.readFile soundnessPath
        match Json.parse content with
        | .ok json =>
          match json.getObjValAs? (Array Graph.SoundnessResult) "checks" with
          | .ok results => pure results
          | .error _ => pure #[]
        | .error _ => pure #[]
      else
        pure #[]

    let manifestJson := buildEnhancedManifest reducedGraph soundnessResults
```

### Verify
- `cd toolchain/Dress && lake build` succeeds
- Generate manifest for existing project (SBS-Test): verify backward compat (new fields default to `none`/`#[]`)

---

## Wave 3: Runway Extension

**Agent:** single `sbs-developer`

### Load.lean (`toolchain/Runway/Runway/Dress/Load.lean`)

Add `SoundnessResult` structure (mirror Dress definition):
```lean
structure SoundnessResult where
  name : String
  passed : Bool
  detail : String := ""
  deriving Repr, Inhabited
```

Add FromJson/ToJson instances for SoundnessResult.

Extend `CheckResults` (lines 158-168):
```lean
structure CheckResults where
  isConnected : Bool
  numComponents : Nat
  componentSizes : Array Nat
  cycles : Array (Array String)
  kernelVerified : Option Bool := none
  soundnessResults : Array SoundnessResult := #[]
  deriving Repr, Inhabited
```

Update `FromJson CheckResults` to handle new fields (backward-compatible — use `getObjValAs?` with fallbacks):
```lean
instance : Lean.FromJson CheckResults where
  fromJson? j := do
    let isConnected ← j.getObjValAs? Bool "isConnected"
    let numComponents ← j.getObjValAs? Nat "numComponents"
    let componentSizes ← j.getObjValAs? (Array Nat) "componentSizes"
    let cycles ← j.getObjValAs? (Array (Array String)) "cycles"
    let kernelVerified := (j.getObjValAs? (Option Bool) "kernelVerified").toOption.join
    let soundnessResults := (j.getObjValAs? (Array SoundnessResult) "soundnessResults").toOption.getD #[]
    return { isConnected, numComponents, componentSizes, cycles, kernelVerified, soundnessResults }
```

Update `ToJson CheckResults` similarly.

### Render.lean (`toolchain/Runway/Runway/Render.lean`)

Replace lines 528-539 (the two hardcoded placeholders) with data-driven rendering:

```lean
      -- Kernel Verification
      (match checks.kernelVerified with
       | some true =>
         divClass "check-item check-pass" (
           spanClass "check-icon" (Html.text true "✓") ++
           spanClass "check-text" (Html.text true "Kernel Verification")
         )
       | some false =>
         divClass "check-item check-fail" (
           spanClass "check-icon" (Html.text true "✗") ++
           spanClass "check-text" (Html.text true "Kernel verification failed")
         )
       | none =>
         divClass "check-item check-pending" (
           spanClass "check-icon" (Html.text true "○") ++
           spanClass "check-text" (Html.text true "Kernel Verification") ++
           spanClass "check-status" (Html.text true "Not implemented")
         )) ++
      -- Soundness Checks
      (if checks.soundnessResults.isEmpty then
         divClass "check-item check-pending" (
           spanClass "check-icon" (Html.text true "○") ++
           spanClass "check-text" (Html.text true "Soundness Checks") ++
           spanClass "check-status" (Html.text true "Not implemented")
         )
       else
         checks.soundnessResults.foldl (fun acc result =>
           let cls := if result.passed then "check-pass" else "check-fail"
           let icon := if result.passed then "✓" else "✗"
           acc ++ divClass s!"check-item {cls}" (
             spanClass "check-icon" (Html.text true icon) ++
             spanClass "check-text" (Html.text true result.name)
           )
         ) Html.empty)
```

### Verify
- `cd toolchain/Runway && lake build` succeeds
- Existing projects (SBS-Test, GCR) render dashboard unchanged (checks show "Not implemented" as before)

---

## Wave 4: Integration + Blueprint

**Agent:** single `sbs-developer`

### Blueprint.tex Update
Add verification nodes to `blueprint/src/blueprint.tex`:
- New chapter or extend existing "Correctness" chapter
- `\inputleannode{verify_quine}` and `\inputleannode{verify_self_ref}`

### Full Pipeline
```bash
cd Side-By-Side-Blueprint/showcase/Quine

# 1. Build Lean + executable
lake build Quine && lake build quine

# 2. Run runtime verification (writes soundness.json)
.lake/build/bin/quine --verify

# 3. Build blueprint artifacts
lake build :blueprint

# 4. Extract graph + manifest (reads soundness.json)
lake env ../../toolchain/Dress/.lake/build/bin/extract_blueprint graph --build .lake/build Quine

# 5. Build site
lake env ../../toolchain/Runway/.lake/build/bin/runway --build-dir .lake/build --output .lake/build/runway build runway.json
```

### Verify
- Dashboard shows: ✓ Graph is connected, ✓ No circular dependencies, ✓ Kernel Verification, ✓ Runtime Verification
- 8 nodes in dependency graph, all fullyProven (forest green)
- `.lake/build/bin/quine | diff Quine.lean -` = empty

---

## Risks

| Risk | Mitigation |
|------|-----------|
| `deriving ToJson` conflicts with manual `ToJson` in Dress | Remove `ToJson, FromJson` from `deriving` clause if conflict arises; keep manual instances |
| `IO.Process.output` in verifyQuine fails (binary not found) | Verify binary exists before calling; provide clear error message |
| Bootstrapping `d` corrupts file | Use PLACEHOLDER approach; verify with `lake build` before proceeding |
| New fields break existing project manifests | All new fields have defaults (`none`/`#[]`); Runway FromJson uses fallbacks |
| SBS-Test/GCR dashboard regresses | Wave 3 verify step checks existing projects render unchanged |

## Critical Files

| File | Lines to Modify |
|------|----------------|
| `showcase/Quine/Quine.lean` | Add ~30 lines (verifyQuine, main changes, theorem), re-bootstrap d |
| `toolchain/Dress/Dress/Graph/Types.lean` | Lines 131-141: extend CheckResults, add SoundnessResult |
| `toolchain/Dress/Dress/Graph/Json.lean` | Lines 84-91: update ToJson |
| `toolchain/Dress/Dress/Graph/Build.lean` | Lines 371-375: update computeCheckResults |
| `toolchain/Dress/Main.lean` | Lines 19, 147-184: add parameter + soundness reading |
| `toolchain/Runway/Runway/Dress/Load.lean` | Lines 158-184, 294-298: mirror types + update FromJson |
| `toolchain/Runway/Runway/Render.lean` | Lines 528-539: replace placeholders |
| `showcase/Quine/blueprint/src/blueprint.tex` | Add verification chapter |
