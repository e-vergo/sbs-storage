# Plan: Merged Lemma 147+148 Formalization

## Summary
Prove `h_crit` in `Criterion.mk'` directly without the false polynomial intermediary, following Tao's suggestion. Mark `prod_epsilon_ge` as false with documentation.

## Scope (per user direction)
- **Focus**: Only `h_crit` proof (line 975)
- **Assume**: `exists_p_primes`, `exists_q_primes`, `inv_cube_log_sqrt_le` are correct (keep sorry)
- **Cleanup**: Mark `prod_epsilon_ge` as false, don't remove other lemmas

## Target
File: `/Users/eric/GitHub/PrimeNumberTheoremAnd/PrimeNumberTheoremAnd/Lcm.lean`
Location: Line 975 in `Criterion.mk'`

```lean
h_crit : ∏ i, (1 + (1 : ℝ) / q i) ≤
    (∏ i, (1 + (1 : ℝ) / (p i * (p i + 1)))) * (1 + (3 : ℝ) / (8 * n)) *
      (1 - 4 * (∏ i, (p i : ℝ)) / ∏ i, (q i : ℝ))
```

## Implementation Strategy

### Step 1: Establish local bounds
Follow pattern from `h_ord_2` proof (lines 961-973):
```lean
h_crit := by
  -- Extract bounds from exists_p_primes and exists_q_primes specs
  have hp_bound : ∀ i, (p i : ℝ) ≤ √n * (1 + 1 / (log √n) ^ 3) ^ ((i : ℕ) + 1) := ...
  have hq_bound : ∀ i, n * (1 + 1 / (log √n) ^ 3) ^ (3 - (i : ℕ)) ≤ (q i : ℝ) := ...
  have hdelta_bound : 1 / (log √n) ^ 3 ≤ 0.000675 := inv_cube_log_sqrt_le n hn
```

### Step 2: Bound LHS from above
Use q-bounds to show:
```lean
∏ i, (1 + 1/q i) ≤ ∏ i, (1 + (1 + δ)^(i+1) / n)  -- where δ = 1/log³√n
```

### Step 3: Bound RHS factors from below
- p-product: Use p-bounds to get lower bound on `∏(1 + 1/(p_i(p_i+1)))`
- pq-ratio: Bound `1 - 4∏p/∏q` from below using both bounds

### Step 4: Combine and verify
- Substitute δ ≤ 0.000675
- Expand products with `Fin.prod_univ_three`
- Apply `nlinarith` with all hypotheses

### Step 5: Mark prod_epsilon_ge as false
Add comment at line 903:
```lean
/-- WARNING: This theorem is FALSE. Counterexample at ε = 1/89693².
    See Zulip thread discussion by Pietro Monticone.
    The constant 3.37 is too aggressive. -/
theorem prod_epsilon_ge ... := by sorry -- FALSE, do not prove
```

## Key Tactics (from h_ord_2 pattern)
- `positivity` - establish 0 < n, 0 < √n, 0 < log √n, etc.
- `convert ... using 2` - extract bounds from choose_spec
- `nlinarith [...]` - main numerical verification
- `exact_mod_cast` - final ℕ/ℝ conversion
- `grind` - handle log positivity

## Fallback Options
1. **Increase heartbeats**: `set_option maxHeartbeats 800000`
2. **Use polyrith**: If nlinarith insufficient (requires internet)
3. **Manual decomposition**: Break into smaller intermediate lemmas

## Verification
```bash
lake build PrimeNumberTheoremAnd.Lcm
```
Success = `L_not_HA_of_ge` compiles with only expected sorries (exists_p_primes, exists_q_primes, inv_cube_log_sqrt_le)
