# Plan: Chebyshev Polynomial Orthogonality Proof (First Kind)

## Goal
Quick scratch file proving orthogonality of Chebyshev polynomials T_n with respect to weight `1/√(1-x²)` on `(-1, 1)`.

## Files to Modify/Create
1. `lakefile.toml` - Add Mathlib dependency
2. `scratch.lean` - The proof file (standalone, not part of TAIL lib)

## Setup Changes

### lakefile.toml addition
```toml
[[require]]
name = "mathlib"
scope = "leanprover-community"
```

## Mathematical Approach
The substitution `x = cos(θ)` transforms:
- `∫_{-1}^{1} T_m(x) T_n(x) / √(1-x²) dx` → `∫_0^π cos(mθ) cos(nθ) dθ`

Mathlib's `Polynomial.Chebyshev.T_cos`: `T_n(cos(θ)) = cos(n*θ)`

## scratch.lean Structure

```lean
import Mathlib.Tactic
import Mathlib.Analysis.SpecialFunctions.Polynomials.Chebyshev
import Mathlib.MeasureTheory.Integral.IntervalIntegral
import Mathlib.Analysis.SpecialFunctions.Integrals

open MeasureTheory Set Real Polynomial.Chebyshev intervalIntegral

/-! ## Chebyshev T_n Orthogonality -/

-- Main theorem: For m ≠ n, ∫_{-1}^{1} T_m(x) T_n(x) / √(1-x²) dx = 0
theorem chebyshev_T_orthogonal (m n : ℕ) (hmn : m ≠ n) :
    ∫ x in Set.Ioo (-1 : ℝ) 1,
      (T ℝ m).eval x * (T ℝ n).eval x / Real.sqrt (1 - x^2) = 0 := by
  sorry
```

## Implementation Steps
1. Add Mathlib to `lakefile.toml`
2. Run `lake update` to fetch Mathlib
3. Create `scratch.lean` with imports
4. Write the orthogonality theorem statement
5. Prove using substitution x = cos(θ) and trig orthogonality
