# Plan: Convert 4 Convergence Theorem Placeholders to Axioms

## File to Modify
`/Users/eric/GitHub/LEAN_mnist/VerifiedNN/Verification/Convergence/Axioms.lean`

## Transformations Required

### 1. `sgd_converges_strongly_convex` (lines 160-221)

**Before (lines 160-221):**
```lean
set_option linter.unusedVariables false in
/-- **Axiom 5: SGD convergence for strongly convex functions** ... -/
theorem sgd_converges_strongly_convex
  {n : ℕ}
  (f : (Fin n → ℝ) → ℝ)
  (μ L : ℝ)
  (h_strongly_convex : IsStronglyConvex f μ)
  (h_smooth : IsSmooth f L)
  (h_μ_pos : 0 < μ)
  (h_L_pos : 0 < L)
  (stochasticGrad : (Fin n → ℝ) → (Fin n → ℝ))
  (σ_sq : ℝ)
  (h_variance : HasBoundedVariance f stochasticGrad σ_sq)
  (α : ℝ)
  (h_lr_lower : 0 < α)
  (h_lr_upper : α < 2 / (μ + L))
  (θ₀ θ_opt : (Fin n → ℝ))
  (h_opt : ∀ θ, f θ_opt ≤ f θ) :
  True := by
  -- Placeholder for complete convergence statement with norm notation.
  -- Full statement would require: 𝔼[‖θ_t - θ*‖²] ≤ (1 - α·μ)^t · ‖θ_0 - θ*‖² + (α·σ²)/μ
  -- Cannot be proven because IsStronglyConvex, IsSmooth, HasBoundedVariance are axiomatized.
  -- Per verified-nn-spec.md Section 5.4, convergence proofs are explicitly out of scope.
  trivial
```

**After:**
```lean
/-- **Axiom 5: SGD convergence for strongly convex functions** ... -/
axiom sgd_converges_strongly_convex
  {n : ℕ}
  (f : (Fin n → ℝ) → ℝ)
  (μ L : ℝ)
  (h_strongly_convex : IsStronglyConvex f μ)
  (h_smooth : IsSmooth f L)
  (h_μ_pos : 0 < μ)
  (h_L_pos : 0 < L)
  (stochasticGrad : (Fin n → ℝ) → (Fin n → ℝ))
  (σ_sq : ℝ)
  (h_variance : HasBoundedVariance f stochasticGrad σ_sq)
  (α : ℝ)
  (h_lr_lower : 0 < α)
  (h_lr_upper : α < 2 / (μ + L))
  (θ₀ θ_opt : (Fin n → ℝ))
  (h_opt : ∀ θ, f θ_opt ≤ f θ) :
  Prop
```

### 2. `sgd_converges_convex` (lines 223-278)

**Before (lines 223-278):**
```lean
set_option linter.unusedVariables false in
/-- **Axiom 6: SGD convergence for convex (not strongly convex) functions** ... -/
theorem sgd_converges_convex
  {n : ℕ}
  (f : (Fin n → ℝ) → ℝ)
  (L : ℝ)
  (h_convex : ConvexOn ℝ Set.univ f)
  (h_smooth : IsSmooth f L)
  (stochasticGrad : (Fin n → ℝ) → (Fin n → ℝ))
  (σ_sq : ℝ)
  (h_variance : HasBoundedVariance f stochasticGrad σ_sq)
  (θ₀ θ_opt : (Fin n → ℝ))
  (h_opt : ∀ θ, f θ_opt ≤ f θ) :
  True := by
  -- Placeholder for convergence statement.
  -- Full statement would require: 𝔼[f(θ_avg_t) - f(θ*)] ≤ O(1/√t)
  -- Cannot be proven because IsSmooth, HasBoundedVariance are axiomatized.
  -- Per verified-nn-spec.md Section 5.4, convergence proofs are explicitly out of scope.
  trivial
```

**After:**
```lean
/-- **Axiom 6: SGD convergence for convex (not strongly convex) functions** ... -/
axiom sgd_converges_convex
  {n : ℕ}
  (f : (Fin n → ℝ) → ℝ)
  (L : ℝ)
  (h_convex : ConvexOn ℝ Set.univ f)
  (h_smooth : IsSmooth f L)
  (stochasticGrad : (Fin n → ℝ) → (Fin n → ℝ))
  (σ_sq : ℝ)
  (h_variance : HasBoundedVariance f stochasticGrad σ_sq)
  (θ₀ θ_opt : (Fin n → ℝ))
  (h_opt : ∀ θ, f θ_opt ≤ f θ) :
  Prop
```

### 3. `sgd_finds_stationary_point_nonconvex` (lines 280-353)

**Before (lines 280-353):**
```lean
set_option linter.unusedVariables false in
/-- **Axiom 7: SGD finds stationary points in non-convex optimization** ... -/
theorem sgd_finds_stationary_point_nonconvex
  {n : ℕ}
  (f : (Fin n → ℝ) → ℝ)
  (L : ℝ)
  (h_smooth : IsSmooth f L)
  (f_min : ℝ)
  (h_bounded_below : ∀ θ, f_min ≤ f θ)
  (G : ℝ)
  (h_bounded_grad : HasBoundedGradient f G)
  (stochasticGrad : (Fin n → ℝ) → (Fin n → ℝ))
  (σ_sq : ℝ)
  (h_variance : HasBoundedVariance f stochasticGrad σ_sq)
  (α : ℝ)
  (h_lr_pos : 0 < α)
  (h_lr_small : α < 1 / L)
  (θ₀ : (Fin n → ℝ))
  (T : ℕ)
  (h_T_pos : 0 < T) :
  True := by
  -- Placeholder for stationary point convergence statement.
  -- Full statement: min_{t=1..T} ‖∇f(θ_t)‖² ≤ 2(f(θ₀) - f_min)/(α·T) + 2α·L·σ²
  -- Cannot be proven because IsSmooth, HasBoundedGradient, HasBoundedVariance are axiomatized.
  -- Per verified-nn-spec.md Section 5.4, convergence proofs are explicitly out of scope.
  trivial
```

**After:**
```lean
/-- **Axiom 7: SGD finds stationary points in non-convex optimization** ... -/
axiom sgd_finds_stationary_point_nonconvex
  {n : ℕ}
  (f : (Fin n → ℝ) → ℝ)
  (L : ℝ)
  (h_smooth : IsSmooth f L)
  (f_min : ℝ)
  (h_bounded_below : ∀ θ, f_min ≤ f θ)
  (G : ℝ)
  (h_bounded_grad : HasBoundedGradient f G)
  (stochasticGrad : (Fin n → ℝ) → (Fin n → ℝ))
  (σ_sq : ℝ)
  (h_variance : HasBoundedVariance f stochasticGrad σ_sq)
  (α : ℝ)
  (h_lr_pos : 0 < α)
  (h_lr_small : α < 1 / L)
  (θ₀ : (Fin n → ℝ))
  (T : ℕ)
  (h_T_pos : 0 < T) :
  Prop
```

### 4. `batch_size_reduces_variance` (lines 355-405)

**Before (lines 355-405):**
```lean
set_option linter.unusedVariables false in
/-- **Axiom 8: Variance reduction through larger batch sizes** ... -/
theorem batch_size_reduces_variance
  {n : ℕ}
  (f : (Fin n → ℝ) → ℝ)
  (single_sample_variance : ℝ)
  (b : ℕ)
  (h_b_pos : 0 < b) :
  True := by
  -- Placeholder for variance reduction statement.
  -- Full statement: Var[∇_batch f] = Var[∇_single f] / b
  -- Cannot be proven because HasBoundedVariance is axiomatized and we lack probability theory.
  -- Per verified-nn-spec.md Section 5.4, convergence proofs are explicitly out of scope.
  trivial
```

**After:**
```lean
/-- **Axiom 8: Variance reduction through larger batch sizes** ... -/
axiom batch_size_reduces_variance
  {n : ℕ}
  (f : (Fin n → ℝ) → ℝ)
  (single_sample_variance : ℝ)
  (b : ℕ)
  (h_b_pos : 0 < b) :
  Prop
```

## Summary of Changes for Each Theorem

| Theorem | Change | Details |
|---------|--------|---------|
| 1. `sgd_converges_strongly_convex` | theorem → axiom | Remove `set_option` prefix, change `True := by trivial` to `Prop` |
| 2. `sgd_converges_convex` | theorem → axiom | Remove `set_option` prefix, change `True := by trivial` to `Prop` |
| 3. `sgd_finds_stationary_point_nonconvex` | theorem → axiom | Remove `set_option` prefix, change `True := by trivial` to `Prop` |
| 4. `batch_size_reduces_variance` | theorem → axiom | Remove `set_option` prefix, change `True := by trivial` to `Prop` |

## Verification Step

After making the edits, run:
```bash
lake build VerifiedNN.Verification.Convergence.Axioms
```

## Notes

- The docstrings already describe these as "Axiom 5", "Axiom 6", etc., so the docstrings are consistent with the change
- The placeholder comments explaining why these cannot be proven will be removed (they're part of the proof body)
- All parameters and hypotheses are preserved exactly
- The return type changes from `True` (a trivially provable proposition) to `Prop` (an abstract proposition we axiomatize)
