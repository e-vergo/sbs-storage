# OSreconstruction Sorry Clearing Plan

## Context

The OSreconstruction project (OS reconstruction theorem for QFT formalization) has 47 `sorry` statements across 10 files. You've been invited to collaborate on the Formal QFT Zulip channel, and clearing sorries demonstrates SBS toolchain value while contributing directly to the project. This plan maximizes sorry count cleared via parallel agent waves, prioritized by feasibility.

## Inventory Summary

| File | Sorries | Closeable Estimate |
|------|---------|-------------------|
| ModularAutomorphism.lean | 15 | 6-8 |
| KMS.lean | 11 | 1-2 |
| ModularTheory.lean | 9 | 2-4 |
| StoneTheorem.lean | 4 | 0-1 |
| Spectral.lean | 2 | 1-2 |
| Predual.lean | 2 | 0 |
| Basic.lean | 2 | 0-1 |
| WightmanAxioms.lean | 2 | 0 |
| Reconstruction.lean | 4 | 0 |
| SpectralStieltjes.lean | 1 | 0-1 |
| **Total** | **47** | **10-19** |

## Wave Structure

### Wave 1: Algebraic Identities (4 agents, target: 6-8 sorries)

Agents triage their own sorry sites inline (lean_goal first, then attempt proof).

These use only already-proven infrastructure (`unitaryGroup_*`, `ContinuousLinearMap` API, adjoint lemmas). No deep theory.

**Agent 1A: ModularAutomorphism.lean — `preserves_mul` (L99) + `preserves_adjoint` (L109)**
- `preserves_mul`: U(ab)U* = (UaU*)(UbU*). Insert U(-t)U(t)=1 in the middle via `unitaryGroup_neg_comp`.
- `preserves_adjoint`: U(a*)U* = (UaU*)*. Use `adjoint_comp` + `unitaryGroup_inv`.

**Agent 1B: ModularAutomorphism.lean — `cocycle_unitary` (L230) + `chain_rule` (L266)**
- `cocycle_unitary`: (U1(t)U2(-t))* (U1(t)U2(-t)) = 1. Adjoint distributes, then U1(-t)U1(t)=1 cancels middle.
- `chain_rule`: Same middle-cancellation pattern with three unitary groups.

**Agent 1C: KMS.lean — `strip_boundary` (L66)**
- Frontier of open strip {0 < Im(z) < β} = two boundary lines. Pure topology: frontier = closure \ interior, the strip is open so interior = strip, closure = closed strip.

**Agent 1D: ModularAutomorphism.lean — `sigma_weak_continuous` (L174) + `strong_continuous` (L182)**
- Both follow from `unitaryGroup_continuous` (proven) + continuity of inner product and ContinuousLinearMap application. Composition of continuous functions.

### Wave 2: Medium Infrastructure (4 agents, target: 4-6 sorries)

**Agent 2A: ModularTheory.lean — `Ω_in_domain` (L135) + `Ω_in_modular_domain` (L142)**
- Cyclic vector is in the domain of the modular operator. Conceptually: S₀(1·Ω) = Ω so Ω ∈ dom(S̄) ∩ dom(Δ). May be blocked by how `domain` is defined — triage will reveal.

**Agent 2B: SpectralStieltjes.lean — `complexMeasure_eq_inner` (L644)**
- Polarization identity: complex measure equals ⟨x, P(E)y⟩. Expand both sides, apply the 4-term polarization identity for inner products.

**Agent 2C: Spectral.lean — `power_zero` (L2654)**
- T^0 = 1 for positive self-adjoint T. For positive T, spectrum ⊆ [0,∞), so P((-∞,0]) = 0, and ∫ 1 dP = P(ℝ) = 1. Infrastructure (`power_add`, spectral theorem) already proven.

**Agent 2D: Basic.lean — `separating_iff_cyclic_commutant` reverse direction (L165)**
- Ω cyclic for M' ⟹ Ω separating for M. If aΩ = 0 and a ∈ M, then ⟨aΩ, bΩ⟩ = 0 for all b ∈ M', and M'Ω dense ⟹ a = 0. The forward direction (L159) is harder.

### Wave 3: Dependent Results (4 agents, target: 3-5 sorries)

**Agent 3A: Spectral.lean — `power_imaginary_unitary` (L2771)**
- T^{it} is unitary. Uses `power_zero` (Wave 2C) + `power_add` + `functionalCalculus_star`. Proof outline already in file.

**Agent 3B: ModularAutomorphism.lean — `state_invariant` (L190)**
- ⟨Ω, σ_t(a)Ω⟩ = ⟨Ω, aΩ⟩. Requires Δ^{it}Ω = Ω (from Ω being fixed point). Depends on Wave 2A.

**Agent 3C: KMS.lean — `kms_is_equilibrium` (L132)**
- KMS states are σ-invariant. Set b=1 in KMS condition, get F(t) = F(t+iβ), bounded analytic on strip ⟹ constant.

**Agent 3D: StoneTheorem.lean — `timeEvolution_generator` (L589)**
- Generator of exp(-itH) is H. Limit definition + sign convention. Medium difficulty.

### Wave 4: Speculative Hard (2-3 agents, target: 0-3 sorries)

Only attempt if Waves 1-3 go well. These are deep theorems where success is unlikely but worth trying.

- `tomita_fundamental` (ModularTheory.lean L284): JMJ = M'. Central theorem.
- `preserves_algebra` (ModularAutomorphism.lean L88): σ_t(a) ∈ M. Depends on Tomita.
- `fixes_cyclic_vector` (ModularTheory.lean L161): ΔΩ = Ω. Statement may be ill-posed.

### Skip List (not attempted)

- Kaplansky density, standard form uniqueness, positive cone self-duality
- Connes approximate innerness, modular inner characterization
- Stone's theorem chain (generator_densely_defined, generator_selfadjoint, Stone)
- All KMS theory except strip_boundary and kms_is_equilibrium
- All Wightman/Reconstruction theorems
- sigmaWeak_convergence_iff

## Execution

- Each wave uses up to 4 `sbs-developer` agents (block-wait, no background)
- Wave N+1 starts only after Wave N completes
- Agents use lean_goal, lean_multi_attempt, lean_hover_info, lean_leansearch, lean_loogle
- Partial progress preserved — agents never revert a partially-proven theorem
- After each wave: `lake build` to verify no regressions

## Verification

After all waves complete:
1. `lake build` from OSreconstruction root — confirm build succeeds with fewer sorry warnings
2. Count remaining sorries via build output
3. Report delta: sorries cleared, sorries remaining, any new issues introduced

## Expected Outcome

**Realistic target: 10-19 sorries cleared** (from 47 down to 28-37). The algebraic identities in ModularAutomorphism.lean are high-confidence. Medium-difficulty spectral calculus and topology results are probable. Deep Tomita-Takesaki and KMS theory results are stretch goals.
