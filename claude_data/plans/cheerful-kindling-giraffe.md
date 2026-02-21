# Exclude Auto-Generated Declarations from Coverage Count

## Context

`computeCoverage` counts all eligible project declarations toward coverage, including auto-generated ones (from `@[simps]`, `@[to_additive]`, `@[ext]`, structure companions, etc.) that share source positions with their parent declarations. These can't be independently tagged, inflating the uncovered count. FLT shows 1136 uncovered but only 113 were actually taggable.

## Approach: Source-Position Grouping

Group declarations by `(moduleName, selectionRange.pos.line)`. If ANY declaration in a group has `@[blueprint]`, the entire group is covered. Declarations without `DeclarationRanges` are excluded entirely.

This correctly handles:
- `@[simps]` generating `foo_apply` at the same line as `@[blueprint] def foo` → group is covered
- `@[to_additive]` generating additive twin at same line → group is covered
- `.ctorIdx` and other rangeless compiler artifacts → excluded from count
- Multiple independent declarations on separate lines → each counted independently

## Changes — `Dress/Dress/Graph/Build.lean`

**Change `computeCoverage` from `Id.run` to `CoreM`** (both callers are already in `CoreM`):

```lean
def computeCoverage (env : Lean.Environment) (projectModules : Array Lean.Name)
    : CoreM CoverageResult := do
```

**Two-pass algorithm:**

Pass 1 (same as now): Collect all eligible declarations with their `findDeclarationRanges?` info:
- Skip declarations with no `DeclarationRanges` (rangeless compiler artifacts)
- For each declaration, record: name, module, kind, covered status, and `(moduleName, selectionRange.pos.line)` as group key

Pass 2: Group by `(moduleName, line)`:
- If any member of a group is covered → entire group is covered
- Count groups (not individual declarations) toward `totalDeclarations` and `coveredDeclarations`
- Uncovered list: one entry per uncovered group (pick representative name)

**Update callers:**
- `Main.lean:214`: add `←` (`let coverage ← Graph.computeCoverage ...`)
- `AutoTag.lean:298`: add `←` (`let coverage ← Graph.computeCoverage ...`)

## Verification

1. `lake build` in Dress — compiles
2. Run auto-tag dry-run on FLT: total should drop significantly (from 2480), uncovered should drop proportionally
3. Coverage % should increase since denominator shrinks more than numerator
