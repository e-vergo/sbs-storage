# Plan: Eliminate Axioms in OSreconstruction

## Context

GitHub issue [xiyin137/OSreconstruction#6](https://github.com/xiyin137/OSreconstruction/issues/6) tracks 15 axiom declarations that should be theorems. The repo already contains proven infrastructure that makes several of these axioms immediately replaceable — the work was done but never wired up. This plan connects that infrastructure and fills accessible sorry gaps to maximize axiom/sorry elimination in one session.

## Scope

| Item | Type | Difficulty | Est. Lines |
|------|------|-----------|------------|
| 1. Replace `edge_of_the_wedge` axiom | Axiom → Theorem | Trivial | ~10 |
| 2. Derive `boundary_value_zero` | Axiom → Theorem | Moderate | ~80-120 |
| 3. Fill `joined_one_all` sorry | Sorry → Proof | Moderate | ~60-80 |
| 4. Fill `RestrictedLorentzGroup.isPathConnected` sorry | Sorry → Proof | Moderate | ~40-60 |

**Net result:** 2 axioms eliminated (15 → 13), 2 sorry's filled, unblocking future BHW axiom elimination.

---

## Wave 1: Replace `edge_of_the_wedge` axiom

**File:** `OSReconstruction/Wightman/Reconstruction/AnalyticContinuation.lean`
**Issue ref:** #20

The theorem `SCV.edge_of_the_wedge_theorem` in `SCV/TubeDomainExtension.lean:2832` is fully proven with zero sorry's. The signatures are identical (confirmed via `AxiomBridge.lean:211-225`). `SCV.TubeDomain` and the local `TubeDomain` (line 445) are definitionally equal. `SCV.realEmbed x` = `fun i => (x i : ℂ)` by rfl.

**Steps:**
1. Add `import OSReconstruction.SCV.TubeDomainExtension` to AnalyticContinuation.lean
2. Delete local `TubeDomain` definition (lines 444-446) — redundant with `SCV.TubeDomain`
3. Add `open SCV` or qualify references
4. Change `axiom edge_of_the_wedge` to `theorem edge_of_the_wedge` with body:
   ```lean
   theorem edge_of_the_wedge ... :=
     SCV.edge_of_the_wedge_theorem C hC hconv h0 hcone hCne
       f_plus f_minus hf_plus hf_minus E hE bv hbv_cont
       hf_plus_bv hf_minus_bv
   ```
5. Fix any downstream references that used the local `TubeDomain` (check for namespace issues — file uses no namespace, just `open Complex`)

**Risk:** Import may pull in heavy transitive deps and slow compilation. No circular import risk (verified).

---

## Wave 2: Derive `boundary_value_zero` from existing axioms

**File:** `OSReconstruction/SCV/TubeDistributions.lean`
**Issue ref:** #9

The axiom's own docstring says it combines `continuous_boundary_tube` + `boundary_value_recovery` + the fundamental lemma of distributions. Mathlib has the fundamental lemma:

- `ae_eq_zero_of_integral_contDiff_smul_eq_zero` — if locally integrable f integrates to 0 against all C^infty_c functions, f = 0 a.e.
- `SchwartzMap.denseRange_toLpCLM` — Schwartz functions are dense in Lp

**Proof sketch:**
1. From `continuous_boundary_tube`: F extends continuously to boundary, giving `G : (Fin m → ℝ) → ℂ` continuous
2. From `boundary_value_recovery` with T = 0: `∫ G(x) * f(x) dx = 0` for all Schwartz f
3. Schwartz ⊇ C_c^infty, so the integral vanishes against smooth compactly supported functions too
4. Apply `ae_eq_zero_of_integral_contDiff_smul_eq_zero`: G = 0 a.e.
5. G continuous + G = 0 a.e. → G = 0 pointwise

**Steps:**
1. Change `axiom boundary_value_zero` to `theorem boundary_value_zero`
2. Proof body uses `continuous_boundary_tube`, `boundary_value_recovery`, and the Mathlib fundamental lemma
3. May need `import Mathlib.Analysis.Distribution.AEEqOfIntegralContDiff` (check if already transitively available)
4. The downstream `distributional_uniqueness_tube` theorem (line 168) already uses `boundary_value_zero` — it continues to work since it doesn't care if it's an axiom or theorem

**Risk:** The bridge between Schwartz functions (`SchwartzMap (Fin m → ℝ) ℂ`) and `ContDiff ℝ ⊤` + `HasCompactSupport` may require non-trivial glue. The Mathlib lemma works with `ℝ`-valued test functions; our axiom uses `ℂ`-valued Schwartz functions. May need to decompose into real/imaginary parts or use a ℂ-valued variant.

---

## Wave 3: Fill `joined_one_all` (ComplexLorentzGroup path-connectedness)

**File:** `OSReconstruction/ComplexLieGroups/Complexification.lean:522`

The infrastructure is already built:
- `expLieAlg` — maps Lie algebra elements to group elements
- `joined_one_expLieAlg` — proves `Joined one (expLieAlg X hX)` via path `t ↦ exp(tX)`
- `joined_one_mul` — if a,b joined to identity, so is a*b
- `ofEuclidean` — Wick rotation embedding SO(d+1;ℝ) → SO⁺(1,d;ℂ)

**Proof strategy:** Decompose arbitrary Λ ∈ SO⁺(1,d;ℂ) into product of exponentials. Every element of SO(n;ℂ) is a product of complex Givens rotations exp(θ E_{ij}), where E_{ij} are Lie algebra generators. Each exponential is joined to identity via `joined_one_expLieAlg`, and the product via `joined_one_mul`.

**Steps:**
1. Show that Lie algebra generators (antisymmetric matrices) span the tangent space
2. Decompose Λ into product of exp(X_i) using existing `expLieAlg`
3. Chain `joined_one_mul` over the product
4. Alternative approach: use `ofEuclidean` to embed path-connected SO(d+1;ℝ), then extend via the complex exponential map

**Risk:** The decomposition of arbitrary Λ into exponentials may be technically involved. May need Schur decomposition or direct Givens rotation construction. If the full decomposition is too hard, could instead use the exponential surjectivity results for connected Lie groups.

---

## Wave 4: Fill `RestrictedLorentzGroup.isPathConnected`

**File:** `OSReconstruction/ComplexLieGroups/LorentzLieGroup.lean:272`

**Proof strategy:** SO⁺(1,d) is the identity component of O(1,d). Standard approach:
1. Every Λ ∈ SO⁺(1,d) can be written as exp(X) for some X in the Lie algebra so(1,d) (for the identity component, this follows from general Lie theory)
2. The path t ↦ exp(tX) connects identity to Λ
3. Alternatively: use polar decomposition Λ = R·B where R is a spatial rotation and B is a boost, then connect each to identity via standard parameterizations

**Steps:**
1. Leverage existing `TopologicalGroup` instance
2. Show exp maps from Lie algebra to identity component
3. Construct explicit continuous path
4. If matrix exponential approach is hard, can use the fact that SO⁺(1,d) is generated by boosts (which are exp of boost generators) and rotations (which are exp of rotation generators)

**Risk:** May need Lie algebra exponential surjectivity which isn't in Mathlib. Could use a more elementary argument (continuous deformation via parameter t, using det and Λ₀₀ continuity to stay in the identity component).

---

## Verification

After each wave, run:
```bash
cd /Users/eric/GitHub/SLS-Strange-Loop-Station/Side-By-Side-Blueprint/showcase/OSreconstruction
lake build
```

For targeted checking, use the `lean_diagnostic_messages` MCP tool on modified files.

Post-completion:
- Verify axiom count dropped: `grep -r "^axiom " OSReconstruction/ | wc -l` should show 13 (down from 15)
- Verify sorry count in ComplexLieGroups: `grep -r "sorry" OSReconstruction/ComplexLieGroups/ | grep -v "\.md" | wc -l` should decrease by 2

---

## Execution Order & Dependencies

```
Wave 1 (edge_of_the_wedge)     Wave 3 (joined_one_all)
         |                               |
         v                               v
Wave 2 (boundary_value_zero)    Wave 4 (isPathConnected)
```

Waves 1-2 and Waves 3-4 are independent tracks. Within each track, sequencing matters (Wave 1 before 2 due to possible import changes; Wave 3 before 4 since the complex case may inform the real case approach).

Agents: 2 parallel `sbs-developer` agents (one per track), or sequential if file overlap is a concern.
