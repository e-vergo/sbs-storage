# Plan: Chebyshev T Polynomial Orthogonality Proof

## Goal
Write a proof in `scratch.lean` showing orthogonality of Chebyshev polynomials of the first kind using the substitution approach.

## Mathematical Statement
For m ≠ n:
```
∫_{-1}^{1} T_m(x) T_n(x) / √(1-x²) dx = 0
```

Using substitution x = cos(θ), this becomes:
```
∫_0^π cos(mθ) cos(nθ) dθ = 0   (for m ≠ n)
```

## File to Modify
- `/Users/eric/GitHub/Balanced_Vectors/scratch.lean`

## Implementation Steps

### Step 1: Set up imports
```lean
import Mathlib.RingTheory.Polynomial.Chebyshev
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Chebyshev.Basic
import Mathlib.MeasureTheory.Integral.IntervalIntegral
import Mathlib.Analysis.SpecialFunctions.Integrals
```

### Step 2: Prove cosine orthogonality lemma
Prove the fundamental result:
```lean
theorem integral_cos_mul_cos (m n : ℤ) (hmn : m ≠ n) :
    ∫ θ in (0 : ℝ)..π, Real.cos (m * θ) * Real.cos (n * θ) = 0
```

This uses the product-to-sum formula:
```
cos(mθ)cos(nθ) = ½[cos((m-n)θ) + cos((m+n)θ)]
```

The integral of cos(kθ) over [0,π] is 0 for k ≠ 0 (since sin(kπ) = 0 for integer k).

### Step 3: State the Chebyshev orthogonality theorem
```lean
theorem chebyshev_T_orthogonal (m n : ℤ) (hmn : m ≠ n) :
    ∫ θ in (0 : ℝ)..π,
      (Polynomial.Chebyshev.T ℝ m).eval (Real.cos θ) *
      (Polynomial.Chebyshev.T ℝ n).eval (Real.cos θ) = 0
```

### Step 4: Prove by rewriting using T_real_cos
Use the key Mathlib theorem:
```lean
Polynomial.Chebyshev.T_real_cos : (T ℝ n).eval (cos θ) = cos (n * θ)
```

The proof:
1. Rewrite both `T m` and `T n` evaluations using `T_real_cos`
2. Apply `integral_cos_mul_cos` from Step 2

## Key Mathlib Theorems Used
- `Polynomial.Chebyshev.T` - Chebyshev polynomial of first kind
- `Polynomial.Chebyshev.T_real_cos` - evaluation at cos(θ) equals cos(nθ)
- `intervalIntegral.integral_cos` - basic cosine integral
- Trigonometric identities from `Mathlib.Analysis.SpecialFunctions.Trigonometric`

## Notes
- The project already has Mathlib configured in `lakefile.toml`
- Lean version: 4.27.0-rc1
- No new environment setup needed - just write to `scratch.lean`
