# Plan: Update Blueprint for General CRT and Merge to Main

## Overview

The general Crystallographic Restriction Theorem (CRT) implementation in `General/` is complete (0 sorries, ~4200 lines across 7 files). This plan covers:
1. Updating the blueprint to document the general approach
2. Adding new declarations to `lean_decls`
3. Merging `feature/general-crt` into `main`

---

## Current State

### Blueprint
- **File**: `blueprint/src/chapter/crystallographic.tex` (124 lines)
- **Current content**: Trace-based 2D proof only (Section 1), Point groups (Section 2-3)
- **Proofs status**: All marked `\notready` (informal proofs present, not linked to Lean)

### General CRT Implementation (Complete)
| File | Lines | Key Content |
|------|-------|-------------|
| `MainTheorem.lean` | 1818 | `crystallographic_restriction` main theorem |
| `CompanionMatrix.lean` | 920 | Companion matrix theory, `companion_charpoly` |
| `TwoDimensional.lean` | 455 | `crystallographic_restriction_2D`, `integerMatrixOrders_two` |
| `Psi.lean` | 246 | `psi` function definition and properties |
| `IntegerMatrixOrder.lean` | 297 | `integerMatrixOrders` definition |
| `Eigenvalues.lean` | 225 | `minpoly_dvd_X_pow_sub_one` |
| `RotationMatrices.lean` | 201 | Explicit 2x2 matrices for orders 1,2,3,4,6 |

### Git State
- Branch: `feature/general-crt` (9 commits ahead of `main`)
- Working tree: Clean
- Fast-forward merge possible

---

## Task 1: Update Blueprint (`crystallographic.tex`)

### Approach
Keep existing trace-based section as motivation, add new section documenting the general theory.

### New Content to Add

After Section 1 (The Trace Argument), add:

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\section{General Crystallographic Restriction}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\begin{definition}[Integer matrix orders]
    \label{def:integer_matrix_orders}
    \lean{WallpaperGroups.Crystallographic.General.integerMatrixOrders}
    \leanok
    For $N \in \N$, define $\text{integerMatrixOrders}(N) \subseteq \N$ as the set
    of positive integers $m$ such that there exists an $N \times N$ integer matrix
    $A$ with $A^m = I$ and $\text{ord}(A) = m$.
\end{definition}

\begin{definition}[The $\psi$ function]
    \label{def:psi}
    \lean{WallpaperGroups.Crystallographic.General.psi}
    \leanok
    For $m \in \N^+$, define
    \[
        \psi(m) = \sum_{p^k \| m} \psi_{\text{pp}}(p, k)
    \]
    where $\psi_{\text{pp}}(p, k) = (p-1) \cdot p^{k-1}$ if $p$ is odd,
    and $\psi_{\text{pp}}(2, k) = \max(0, 2^{k-1} - 1)$.
\end{definition}

\begin{theorem}[General crystallographic restriction]
    \label{thm:general_crystallographic_restriction}
    \lean{WallpaperGroups.Crystallographic.General.crystallographic_restriction}
    \uses{def:integer_matrix_orders, def:psi}
    \leanok
    For all $N, m \in \N$ with $m > 0$:
    \[
        m \in \text{integerMatrixOrders}(N) \iff \psi(m) \leq N.
    \]
\end{theorem}

\begin{proof}
    \leanok
    The forward direction uses eigenvalue analysis: if $A^m = I$ with integer
    entries, eigenvalues are $m$-th roots of unity. The minimal polynomial
    divides $\prod_{d \mid m} \Phi_d(X)$, constraining the degree.

    The backward direction constructs matrices via companion matrices of
    cyclotomic polynomials and block diagonal combinations.
\end{proof}

\begin{theorem}[Two-dimensional specialization]
    \label{thm:2d_crystallographic}
    \lean{WallpaperGroups.Crystallographic.General.crystallographic_restriction_2D}
    \uses{thm:general_crystallographic_restriction}
    \leanok
    $\text{integerMatrixOrders}(2) = \{1, 2, 3, 4, 6\}$.
\end{theorem}

\begin{proof}
    \leanok
    Compute $\psi(m)$ for small $m$: $\psi(1) = \psi(2) = 0$, $\psi(3) = \psi(4) = \psi(6) = 2$,
    and $\psi(m) > 2$ for $m \geq 7$. The achievability of $\{3, 4, 6\}$ follows from
    explicit matrix constructions.
\end{proof}
```

### Updates to Existing Content

1. **Line 49**: Update `\lean{...}` reference to clarify this is the trace-based 2D version
2. **Line 83**: Add `\uses{thm:2d_crystallographic}` to corollary

---

## Task 2: Update `lean_decls`

Add these declarations to `blueprint/lean_decls`:

```
WallpaperGroups.Crystallographic.General.integerMatrixOrders
WallpaperGroups.Crystallographic.General.psi
WallpaperGroups.Crystallographic.General.psiPrimePow
WallpaperGroups.Crystallographic.General.crystallographic_restriction
WallpaperGroups.Crystallographic.General.crystallographic_restriction_2D
WallpaperGroups.Crystallographic.General.integerMatrixOrders_two
WallpaperGroups.Crystallographic.General.companion
WallpaperGroups.Crystallographic.General.companion_charpoly
WallpaperGroups.Crystallographic.General.companion_cyclotomic_orderOf
WallpaperGroups.Crystallographic.General.mem_integerMatrixOrders_totient
WallpaperGroups.Crystallographic.General.psi_le_of_mem_integerMatrixOrders
WallpaperGroups.Crystallographic.General.mem_integerMatrixOrders_of_psi_le
```

---

## Task 3: Merge to Main (Squash)

```bash
git checkout main
git merge --squash feature/general-crt
git commit -m "Add general n-dimensional crystallographic restriction theorem

- Prove m in integerMatrixOrders(N) iff psi(m) <= N for all dimensions
- Specialize to 2D: integerMatrixOrders(2) = {1,2,3,4,6}
- Add companion matrix infrastructure (companion_charpoly)
- Add psi function and properties
- Add explicit rotation matrices for orders 1,2,3,4,6"
git push origin main
```

---

## Execution Steps

1. **Edit `blueprint/src/chapter/crystallographic.tex`**
   - Add new section after "The Trace Argument"
   - ~60 lines of new LaTeX

2. **Edit `blueprint/lean_decls`**
   - Add ~12 new declaration names

3. **Rebuild blueprint**
   ```bash
   leanblueprint web
   ```

4. **Verify**
   - Run `leanblueprint checkdecls`
   - Check dependency graph in `blueprint/web/dep_graph_document.html`

5. **Merge to main (squash)**
   ```bash
   git checkout main
   git merge --squash feature/general-crt
   git commit -m "Add general n-dimensional crystallographic restriction theorem..."
   git push origin main
   ```

6. **Deploy**
   ```bash
   ./deploy.sh --build
   ```

---

## Files to Modify

| File | Action |
|------|--------|
| `blueprint/src/chapter/crystallographic.tex` | Add ~60 lines (new section) |
| `blueprint/lean_decls` | Add ~12 declarations |
| Git: merge `feature/general-crt` -> `main` | |

---

## Verification

- [ ] `leanblueprint checkdecls` passes
- [ ] `leanblueprint web` builds without errors
- [ ] Dependency graph shows new theorems
- [ ] `lake build` passes on main after merge
- [ ] Site deployed successfully
