# Plan: Axiom Reduction Assessment

## Status: COMPLETED (Partial Success)

**Result:** Reduced from 11 to 7 axioms by converting definition-axioms to actual definitions.

---

# Analysis: Manual Copy of ArtificialTheorems

## Executive Summary

**RECOMMENDATION: Do NOT attempt manual copy**

The cost-benefit analysis strongly favors keeping the current 7 axioms.

---

## Why Manual Copy is Impractical

### 1. Source Code Issues
- **Incomplete:** SGD.lean has `sorry` at line 4014 (main theorem unfinished)
- **Massive scope:** ~8,000 lines to copy (RobbinsSiegmund.lean + SGD.lean)
- **80+ declarations** with complex interdependencies

### 2. Version Incompatibility
- **30-50 compilation errors** expected from v4.20.1 vs v4.23.0
- **High-risk modules:**
  - `Mathlib.Probability.Martingale.Basic` - restructured between versions
  - Filtration API (100+ occurrences)
  - Conditional expectation notation `μ[·|·]` (50+ uses)

### 3. Expertise Requirements
- Advanced probability theory (martingales, adapted processes)
- Measure theory (σ-algebras, filtrations)
- Stochastic analysis (Robbins-Siegmund supermartingales)
- **Estimated effort:** 3-4 weeks for expert

### 4. Cost-Benefit
| Approach | Effort | Axiom Reduction | Value |
|----------|--------|-----------------|-------|
| Keep axioms | 0 | 0 | High (clean, working) |
| Manual copy | 3-4 weeks | 3-4 axioms | Low (incomplete source) |

---

## Recommendation

**Keep the current 7 axioms.** The pragmatic philosophy in CLAUDE.md already documents convergence proofs as out-of-scope:

> "Convergence proofs for SGD are out of scope per project specification"

### Future Opportunity
When SciLean upgrades to Lean 4.23.0+:
1. Add ArtificialTheorems as dependency (simple)
2. Import proven theorems directly
3. Eliminate 4 convergence axioms automatically

---

## Final State

| Category | Count | Status |
|----------|-------|--------|
| Definition predicates | 0 | Converted to `def`/`opaque` |
| Convergence theorem axioms | 4 | Out of scope (literature references) |
| Array bijection axioms | 2 | Blocked by SciLean DataArray.ext |
| Float bridge axiom | 1 | No Float arithmetic theory |
| **Total axioms** | **7** | **Reduced from 11 (36% reduction)** |

---

## Decision: User chose to keep 7 axioms

Manual copy deemed impractical. Current axiom count is acceptable for research project.

---

## ARCHIVED: Original Axiom Inventory (11 total, now 7)

| # | Axiom | Category | Provability | Effort |
|---|-------|----------|-------------|--------|
| 1 | `IsSmooth` | Convergence def | HARD | Definition, not theorem |
| 2 | `IsStronglyConvex` | Convergence def | HARD | Definition, not theorem |
| 3 | `HasBoundedVariance` | Convergence def | IMPOSSIBLE | Needs probability theory |
| 4 | `HasBoundedGradient` | Convergence def | **EASY** | Use PiLp norm |
| 5 | `sgd_converges_strongly_convex` | Convergence thm | **AVAILABLE** | In ArtificialTheorems |
| 6 | `sgd_converges_convex` | Convergence thm | **AVAILABLE** | In ArtificialTheorems |
| 7 | `sgd_finds_stationary_point_nonconvex` | Convergence thm | **AVAILABLE** | In ArtificialTheorems |
| 8 | `batch_size_reduces_variance` | Convergence thm | **EASY** | Statistical result |
| 9 | `unflatten_flatten_id` | Array bijection | BLOCKED | SciLean DataArray.ext |
| 10 | `flatten_unflatten_id` | Array bijection | BLOCKED | SciLean DataArray.ext |
| 11 | `float_crossEntropy_preserves_nonneg` | Float bridge | IMPOSSIBLE | No Float theory |

---

## Reduction Strategies

### Strategy A: Import ArtificialTheorems (High Impact, High Risk)

**Eliminates:** Axioms 5, 6, 7 (possibly 1, 2, 4, 8 with adaptation)
**Reduction:** 11 -> 4-7 axioms

**Challenge:** Version mismatch
- Our project: Lean 4.20.1, mathlib v4.20.1 (locked by SciLean)
- ArtificialTheorems: Lean 4.23.0, mathlib v4.23.0

**Options:**
1. **Upgrade LEAN_mnist to v4.23.0** - May break SciLean compatibility
2. **Copy proofs manually** - Extract ~500 lines of core SGD theorems, adapt to v4.20.1
3. **Wait for SciLean upgrade** - Not actionable now

### Strategy B: Prove Easy Axioms (Low Impact, Low Risk)

**Eliminates:** Axioms 4, 8
**Reduction:** 11 -> 9 axioms

**Axiom 4 (HasBoundedGradient):**
```lean
-- Current: axiom HasBoundedGradient {n : ℕ} (f : (Fin n → ℝ) → ℝ) (G : ℝ) : Prop
-- Replace with definition using PiLp norm:
def HasBoundedGradient {n : ℕ} (f : (Fin n → ℝ) → ℝ) (G : ℝ) : Prop :=
  ∀ x, ‖gradient f x‖ ≤ G
```

**Axiom 8 (batch_size_reduces_variance):**
```lean
-- Standard statistical result: Var[mean] = Var[single] / n
-- Can prove using Finset.sum properties
```

### Strategy C: Reclassify Definitions vs Theorems

**Impact:** Conceptual clarity, not axiom reduction

Axioms 1-4 are actually **predicate definitions** (return `Prop`), not claims.
They could be renamed from `axiom` to `def` without changing semantics:
```lean
-- From:
axiom IsSmooth {n : ℕ} (f : (Fin n → ℝ) → ℝ) (L : ℝ) : Prop
-- To:
def IsSmooth {n : ℕ} (f : (Fin n → ℝ) → ℝ) (L : ℝ) : Prop := sorry
-- Or better, actual definition:
def IsSmooth {n : ℕ} (f : (Fin n → ℝ) → ℝ) (L : ℝ) : Prop :=
  ∀ x y, ‖gradient f x - gradient f y‖ ≤ L * ‖x - y‖
```

This would reduce "axiom" count from 11 to 7 (keeping 5-8 as theorem axioms, 9-11 as implementation axioms).

---

## SELECTED APPROACH: Full Integration + Reclassification

### Phase 1: Version Upgrade Assessment

1. **Backup current state**
   ```bash
   git checkout -b axiom-reduction
   cp lean-toolchain lean-toolchain.backup
   cp lakefile.toml lakefile.toml.backup
   ```

2. **Test Lean 4.23.0 upgrade**
   ```bash
   echo "leanprover/lean4:v4.23.0" > lean-toolchain
   lake update
   lake build
   ```

3. **Evaluate results:**
   - If builds: Proceed to Phase 2
   - If fails: Assess SciLean breakage, decide whether to fix or revert

### Phase 2: Add ArtificialTheorems Dependency

4. **Add to lakefile.toml:**
   ```toml
   [[require]]
   name = "ArtificialTheorems"
   git = "https://github.com/GasStationManager/ArtificialTheorems.git"
   rev = "main"
   ```

5. **Update and rebuild:**
   ```bash
   lake update
   lake exe cache get  # Get mathlib cache for v4.23.0
   lake build
   ```

### Phase 3: Reclassify Definition-Axioms

6. **File: `VerifiedNN/Verification/Convergence/Axioms.lean`**

   Convert these axioms to definitions:
   ```lean
   -- FROM:
   axiom IsSmooth {n : ℕ} (f : (Fin n → ℝ) → ℝ) (L : ℝ) : Prop

   -- TO:
   def IsSmooth {n : ℕ} (f : (Fin n → ℝ) → ℝ) (L : ℝ) : Prop :=
     Differentiable ℝ f ∧ LipschitzWith L (fderiv ℝ f)
   ```

   Definitions to convert:
   - `IsSmooth` -> Lipschitz gradient definition
   - `IsStronglyConvex` -> Standard convexity inequality
   - `HasBoundedGradient` -> Norm bound on gradient
   - `HasBoundedVariance` -> Opaque def (can't express without probability)

### Phase 4: Replace Theorem-Axioms with Imports

7. **Import SGD convergence from ArtificialTheorems:**
   ```lean
   import ArtificialTheorems.Opt.SGD
   import ArtificialTheorems.Opt.SGDUniqueMin
   ```

8. **Replace axioms with proven theorems:**
   - `sgd_converges_strongly_convex` -> Use `convergence_stochastic_gradient_method`
   - `sgd_converges_convex` -> Derive from general SGD theorem
   - `sgd_finds_stationary_point_nonconvex` -> May need adaptation
   - `batch_size_reduces_variance` -> Prove using Finset lemmas

### Phase 5: Prove Easy Axioms

9. **Prove `HasBoundedGradient` instances for our activations:**
   - ReLU: gradient bounded by 1
   - Sigmoid: gradient bounded by 0.25
   - Dense layer: gradient bounded by weight norm

10. **Prove `batch_size_reduces_variance`:**
    ```lean
    theorem batch_size_reduces_variance ... :=
      Finset.sum_div_card_sq_le_sum_sq_div_card ...
    ```

### Phase 6: Documentation Update

11. **Update `documentation/VERIFICATION.md`:**
    - New axiom count (target: 4-5)
    - Document which axioms became definitions
    - Document which axioms became proven theorems
    - List irreducible axioms with justification

### Fallback: If Version Upgrade Fails

If SciLean breaks on Lean 4.23.0:
- Revert to v4.20.1
- Manually copy key theorems from ArtificialTheorems
- Adapt imports to local mathlib version
- Still do Phase 3 (reclassification) and Phase 5 (easy proofs)

---

## Files to Modify

| File | Changes |
|------|---------|
| `lakefile.toml` | (Phase 3) Add ArtificialTheorems dependency |
| `lean-toolchain` | (Phase 3) Upgrade to v4.23.0 if compatible |
| `Convergence/Axioms.lean` | Convert axioms 1-4 to defs, prove 4, 8 |
| `documentation/VERIFICATION.md` | Update axiom counts and categories |

---

## Expected Outcome (SELECTED APPROACH)

| Phase | Axiom Count | Description |
|-------|-------------|-------------|
| Current | 11 | 4 def-axioms, 4 thm-axioms, 3 impl-axioms |
| After Phase 3 | 7 | Convert 4 def-axioms to actual definitions |
| After Phase 4-5 | 4-5 | Import/prove convergence theorems |
| **Final Target** | **4** | Only irreducible axioms remain |

**Final Axiom State (Target):**
- `unflatten_flatten_id` - Blocked by SciLean (keep)
- `flatten_unflatten_id` - Blocked by SciLean (keep)
- `float_crossEntropy_preserves_nonneg` - No Float theory (keep)
- `HasBoundedVariance` - Needs probability theory (keep as opaque def or axiom)

**Eliminated:**
- 4 definition-axioms -> actual definitions
- 3 convergence theorem-axioms -> proven via ArtificialTheorems

---

## Irreducible Axioms (Cannot Eliminate)

These 3-4 axioms are fundamentally blocked:

1. **`HasBoundedVariance`** - Requires probability theory formalization (~10K LOC)
2. **`unflatten_flatten_id`** - Blocked by SciLean DataArray.ext (upstream issue)
3. **`flatten_unflatten_id`** - Same as above
4. **`float_crossEntropy_preserves_nonneg`** - Requires Float arithmetic theory (Flocq-equivalent)

---

## Decision Points for User

1. **Priority:** Focus on quick wins (Phase 1-2) or attempt full integration (Phase 3)?
2. **Risk tolerance:** Willing to try Lean 4.23.0 upgrade (may break build)?
3. **Scope:** Is reclassifying def-axioms valuable, or only actual proof reduction?
