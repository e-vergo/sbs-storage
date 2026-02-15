# Add Full @[blueprint] Annotations to ChebyshevCircles

## Context

The ChebyshevCircles blueprint shows zero Lean nodes because no declarations have `@[blueprint]` annotations. The content currently lives in two places that will conflict: the Lean source (no annotations) and `content.tex` (full theorem statements + proofs inline). We need to:

1. Move theorem/proof content from TeX into Lean `@[blueprint]` annotations
2. Replace inline TeX theorem environments with `\inputleannode{label}` references
3. Update the paper TeX similarly to avoid duplication
4. Verify with Lean LSP tools throughout

## Architecture: Content Deduplication

**Before (current):** content.tex has inline theorem statements + proofs with `\lean{...}` references:
```tex
\begin{theorem}[Main Theorem]\label{thm:main}
\lean{mainTheorem}
\leanok
For any positive integer $N \geq 1$... [full statement]
\uses{lem:power_sum_invariance, ...}
\end{theorem}
\begin{proof}
\leanok
[full proof text]
\end{proof}
```

**After:** content.tex uses `\inputleannode{label}` to pull from Dress artifacts:
```tex
\inputleannode{thm:main}
```
And the Lean source has:
```lean
/-- The main theorem: rotated roots of unity yield Chebyshev polynomials
up to an additive constant. -/
@[blueprint "thm:main"
  (title := "Main Theorem")
  (keyDeclaration := true)
  (statement := /-- For any positive integer $N \geq 1$... -/)
  (proof := /-- The proof proceeds by showing power sum equality... -/)
  (above := /-- Our main result establishes that this construction yields... -/)
  (below := /-- This theorem reveals several deep connections... -/)
  (uses := [powerSumCos_invariant, multiset_newton_identity, ...])]
theorem mainTheorem : StatementOfTheorem := ...
```

**Prose paragraphs between theorems stay in content.tex** — only theorem environments move to Lean.

## What "Full GCR-Style" Means

Each annotated declaration gets:
1. A Lean **docstring** (`/-- ... -/`) — concise description
2. `@[blueprint "label"` — matches `\label{...}` from content.tex
3. `(title := "...")` — short title
4. `(statement := /-- LaTeX statement -/)` — extracted from content.tex theorem body
5. `(proof := /-- LaTeX proof sketch -/)` — extracted from content.tex proof environment
6. `(above := /-- context -/)` — motivation paragraph (key declarations only)
7. `(below := /-- implications -/)` — consequences paragraph (key declarations only)
8. `(uses := [...])` — matching `\uses{...}` from content.tex
9. `(keyDeclaration := true)` — for main theorem and key definitions

Supporting lemmas get `title` + `statement` minimum. Key theorems get full treatment.

## Tool Usage

Each agent MUST use:
- `lean_hover_info` on declarations to get type signatures for accurate docstrings
- `lean_diagnostic_messages` after edits to verify no errors
- `lean_build` (Wave 2) for full project compilation

## Execution Plan

### Wave 1: Lean Annotations (3 parallel agents)

**Agent 1 — Definitions + Main** (4 Lean files)
- `ChebyshevCircles/Definitions/Core.lean` — enhance 9 bare annotations to full
- `ChebyshevCircles/Definitions/ChebyshevRoots.lean` — enhance 2 bare annotations
- `ChebyshevCircles/MainTheorem.lean` — enhance 1 bare annotation
- `ChebyshevCircles/ProofOfMainTheorem.lean` — enhance 1 bare annotation

Narrative source: content.tex lines 1-136 (Introduction), 138-174 (Preliminaries), 532-716 (Proof chapter)

**Agent 2 — Proofs A** (5 Lean files)
- `Proofs/TrigonometricIdentities.lean` — enhance 4 bare annotations
- `Proofs/RootsOfUnity.lean` — enhance 6 bare annotations
- `Proofs/PolynomialConstruction.lean` — enhance 11 bare annotations
- `Proofs/PowerSums.lean` — enhance 13 bare annotations
- `Proofs/NewtonIdentities.lean` — enhance 10 bare annotations

Narrative source: content.tex lines 176-268 (Roots of unity, Newton), 270-380 (Discrete orthogonality), 382-477 (Power sums)

**Agent 3 — Proofs B** (5 Lean files, from scratch — `import Dress` + full annotations)
- `Proofs/PolynomialProperties.lean` — add 6 full annotations
- `Proofs/ChebyshevRoots.lean` — add 5 full annotations
- `Proofs/ChebyshevOrthogonality.lean` — add 7 full annotations
- `Proofs/PowerSumEquality.lean` — add 3 full annotations
- `Proofs/MainTheoremSupport.lean` — add 5 full annotations

Narrative source: content.tex lines 336-380, 382-477, 479-531, 532-716

### Wave 2: TeX Deduplication (1 agent)

**Agent 4 — Update content.tex + paper TeX**

For `blueprint/src/content.tex`:
- Replace each `\begin{theorem}...\end{theorem}` + `\begin{proof}...\end{proof}` block with `\inputleannode{label}`
- Keep surrounding prose paragraphs, section headings, computational examples
- Keep `\begin{example}` environments (these don't have Lean counterparts)
- Remove `\lean{...}`, `\leanok`, `\uses{...}` commands (now in Lean annotations)

For `paper/chebyshev_circles.tex`:
- Check for any `\lean{...}` or `\inputleannode{...}` references that need updating
- The paper TeX likely uses `\paperstatement{label}`, `\paperfull{label}`, or `\paperproof{label}` — update if needed

### Wave 3: Build + Verify (1 agent)

1. `lake build ChebyshevCircles` — verify annotations compile
2. Check `manifest.json` for `total > 0`
3. Run Runway to regenerate site
4. Verify: chapter pages show Lean content, no duplicate text
5. Verify: dependency graph has nodes and edges
6. Verify: paper page renders correctly
7. Restore `lakefile.toml` to git URLs

## Critical Files

| File | Changes |
|------|---------|
| 14 Lean files in `ChebyshevCircles/` | Full `@[blueprint]` annotations + docstrings |
| `blueprint/src/content.tex` | Replace inline theorems with `\inputleannode{label}` |
| `paper/chebyshev_circles.tex` | Check/update node references |
| `lakefile.toml` | Temporary local paths → restore git URLs |

## Verification

- `lean_diagnostic_messages` on each file after edits (Wave 1)
- No errors from `lake build` (Wave 3)
- `manifest.json` shows 60+ nodes
- Chapter pages show Lean code + status colors (no duplicate text)
- Dependency graph populated
- Paper page renders without missing content
