# Plan: Complete TypeSafety Dimension Proofs

## Task Summary
Convert 4 trivial `True := trivial` lemmas/theorems into actual dimension proofs using `DataArrayN.h_size`.

## Understanding the Data Structures

From SciLean's `DataArray.lean` (lines 183-185):
```lean
structure DataArrayN (α : Type*) [pd : PlainDataType α] (ι : Type*) {n : outParam ℕ} [Size' ι n] : Type where
  data : DataArray α
  h_size : n = data.size
```

Key insight: `h_size : n = data.size` proves the type-level dimension equals runtime size.

For vectors (`Float^[n]` = `DataArrayN Float (Idx n)`): `h_size : n = data.size`
For 2D arrays (`Float^[m, n]` = `DataArrayN Float (Idx m × Idx n)`): `h_size : m * n = data.size`

## Changes Required

### 1. Line 93: `type_guarantees_dimension`
**Current:**
```lean
lemma type_guarantees_dimension {n : Nat} (_ : Float^[n]) : True := trivial
```
**Change to:**
```lean
lemma type_guarantees_dimension {n : Nat} (x : Float^[n]) : x.data.size = n := x.h_size.symm
```
Bind the parameter to `x`, return the proof that `data.size = n` (using `symm` since `h_size` is `n = data.size`).

### 2. Line 106: `vector_type_correct`
**Current:**
```lean
theorem vector_type_correct {n : Nat} (_ : Vector n) : True := trivial
```
**Change to:**
```lean
theorem vector_type_correct {n : Nat} (x : Vector n) : x.data.size = n := x.h_size.symm
```
Same logic - `Vector n` is just an abbrev for `Float^[n]`.

### 3. Line 115: `matrix_type_correct`
**Current:**
```lean
theorem matrix_type_correct {m n : Nat} (_ : Matrix m n) : True := trivial
```
**Change to:**
```lean
theorem matrix_type_correct {m n : Nat} (x : Matrix m n) : x.data.size = m * n := x.h_size.symm
```
For 2D arrays, `h_size : m * n = data.size`, so `h_size.symm : data.size = m * n`.

### 4. Line 123: `batch_type_correct`
**Current:**
```lean
theorem batch_type_correct {b n : Nat} (_ : Batch b n) : True := trivial
```
**Change to:**
```lean
theorem batch_type_correct {b n : Nat} (x : Batch b n) : x.data.size = b * n := x.h_size.symm
```
`Batch b n` is also `Float^[b, n]`, so same as matrix.

## Verification Approach
After making changes, run:
```bash
lake build VerifiedNN.Verification.TypeSafety
```

## Implementation Ready
All changes are straightforward applications of `h_size.symm`. No complex proof tactics needed.
