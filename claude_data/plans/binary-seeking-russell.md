# Plan: Reorganize Theorem Categories in Documentation

## Summary

Reorganize gradient correctness theorems into meaningful categories across READMEs and landing page. Update SVG to show theorem category blocks. Move theorem descriptions to be prominent on landing page.

---

## Proposed Theorem Categories

### Category 1: Main Results (3 theorems)
Core contributions proving backpropagation formulas:
- `network_gradient_correct` - End-to-end network differentiability
- `dense_layer_gradient_formula` - Backprop formula: `fderiv = diag(σ'(z)) · W`
- `softmax_cross_entropy_gradient_formula` - Loss gradient: `∇L = softmax(z) - onehot(y)` (partial)

### Category 2: Building Block Theorems (9 theorems)
Proven correctness for individual operations:

**Activation Functions (2):**
- `relu_gradient_almost_everywhere`
- `sigmoid_gradient_correct`

**Linear Algebra (4):**
- `matvec_gradient_wrt_vector`
- `matvec_gradient_wrt_matrix`
- `vadd_gradient_correct`
- `smul_gradient_correct`

**Composition (3):**
- `chain_rule_preserves_correctness`
- `layer_composition_gradient_correct`
- `cross_entropy_softmax_gradient_correct`

### Category 3: Numerical Validation (1 theorem)
- `gradient_matches_finite_difference` - Validates analytical gradients match finite differences

---

## Files to Update

### 1. docs/index.html

**SVG Update (lines 164-206):**
Replace current "What This Project Verifies" section with theorem category blocks:
```
┌─────────────────────────────────────────────┐
│           Theorem Categories (13 total)     │
├─────────────────┬─────────────┬─────────────┤
│  Main Results   │  Building   │ Validation  │
│      (3)        │  Blocks (9) │    (1)      │
│ network_grad... │ relu, smul  │ finite_diff │
│ dense_formula   │ matvec, ... │             │
│ softmax_formula │ chain_rule  │             │
└─────────────────┴─────────────┴─────────────┘
```

**Note:** Current badges show "14 theorems" but actual count is 13 (3+9+1). Update badge to 13.

**Add Theorem Descriptions Section:**
After the hero section (after line 210), add a new section with detailed theorem descriptions similar to what's currently in the "Proof Strategy Deep-Dive" but focused on the theorem categories.

### 2. VerifiedNN/Verification/README.md

**Update Main Theorems table (lines 22-36):**
Split into three subsections:
1. "Main Results (3)" - network_gradient_correct, dense_layer_gradient_formula, softmax_cross_entropy_gradient_formula
2. "Building Block Theorems (9)" - activation, linear algebra, and composition theorems
3. "Numerical Validation (1)" - gradient_matches_finite_difference

### 3. documentation/VERIFICATION.md

Already has good categorization. Minor updates:
- Move `gradient_matches_finite_difference` description to clarify it's validation, not a main result
- Ensure counts are consistent (currently shows 11 "additional" which should be 9 building blocks + 1 validation + cross_entropy)

---

## Execution Order

1. Update VerifiedNN/Verification/README.md with new theorem categories
2. Update docs/index.html:
   - Redesign inline SVG with theorem category blocks
   - Add theorem descriptions section after hero
3. Update documentation/VERIFICATION.md for consistency
4. Verify all theorem counts match across files
5. Commit changes

---

## SVG Design Details

New SVG layout (approximate, will refine):
- Width: 400px, Height: expanded to ~550px
- Top: Float MLP | Real MLP (keep existing)
- Middle: Float/Real Gap (keep existing)
- Bottom: Three-column theorem categories grid
  - Column 1: Main Results (green border, 3 theorems listed by name)
  - Column 2: Building Blocks (blue border, 9 theorems with subcategories: Activation, Linear Algebra, Composition)
  - Column 3: Validation (gray border, 1 theorem)

## Theorem Descriptions Section

Add new section after hero (before Training Results) with:
- Header: "Verified Theorems"
- Three subsections matching the categories
- For each theorem: name, one-line description, status (proven/partial)
- Similar format to current "Proof Strategy Deep-Dive" but organized by category
