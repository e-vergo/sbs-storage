# Repository Cleanup Plan for Community Release

## Overview

Prepare the LEAN_mnist repository for public release with mathlib-quality documentation and accurate claims.

**Validated Results:**
- Training works: 95% test accuracy achieved (mnistTrainMedium, 12 min)
- Build succeeds: All files compile with zero errors
- Claims to update: Use "90-95%" range for accuracy (per user preference)

---

## Phase 1: Remove AD-Based Files

Remove files that use SciLean's noncomputable `nabla` operator per user request.

### Files to Delete

| File | Reason |
|------|--------|
| `VerifiedNN/Examples/SimpleExample.lean` | Uses `nabla`, noncomputable main |
| `VerifiedNN/Examples/TrainManual.lean` | Uses `nabla` |
| `VerifiedNN/Testing/GradientCheck.lean` | Uses `nabla` |
| `VerifiedNN/Testing/OptimizerTests.lean` | Uses `nabla` |
| `VerifiedNN/Testing/OptimizerVerification.lean` | Uses `nabla` |
| `VerifiedNN/Testing/_Archived/` | Entire directory (deprecated) |

### Files to Update After Deletion

1. **`lakefile.lean`** - Remove executables:
   - Lines 35-38: `simpleExample`
   - Lines 45-48: `trainManual`
   - Lines 66-69: `gradientCheck`

2. **`VerifiedNN.lean`** - Remove imports:
   - Line 64: `import VerifiedNN.Testing.GradientCheck`
   - Line 66: `import VerifiedNN.Testing.Integration` (broken - file doesn't exist)
   - Line 69: `import VerifiedNN.Examples.SimpleExample`

3. **`VerifiedNN/Testing/RunTests.lean`** - Remove import of GradientCheck if present

---

## Phase 2: Fix Critical Issues

### 2.1 Fix Broken Import

**File:** `VerifiedNN.lean:66`
**Issue:** Imports `VerifiedNN.Testing.Integration` which doesn't exist
**Fix:** Remove the line

### 2.2 Create Missing Loss.lean Reexport

**Create:** `VerifiedNN/Loss.lean`
**Purpose:** Consistency with other modules (Core.lean, Layer.lean, etc. all exist)
**Content:** Re-export Loss submodules (CrossEntropy, Properties, Gradient)

### 2.3 Fix False Claims in Documentation

| Document | Current Claim | Correction |
|----------|---------------|------------|
| README, CLAUDE.md, landing page | "26 gradient theorems" | "12 gradient correctness theorems" |
| README, CLAUDE.md | "59 files" | Update to actual count after cleanup (~64) |
| README, CLAUDE.md, landing page | "93% accuracy" | "90-95% accuracy" |
| Some docs | "0 sorries" | Consistent "4 sorries in TypeSafety.lean" |

**Files to update:**
- `/Users/eric/GitHub/LEAN_mnist/README.md`
- `/Users/eric/GitHub/LEAN_mnist/CLAUDE.md`
- `/Users/eric/GitHub/LEAN_mnist/docs/index.html`
- `/Users/eric/GitHub/LEAN_mnist/VerifiedNN/README.md`

### 2.4 Fix Unused Variable Warning

**File:** `VerifiedNN/Examples/MNISTTrainMedium.lean:162`
**Issue:** Unused variable `numBatches`
**Fix:** Prefix with underscore or remove

---

## Phase 3: Split README

Split the 950-line README.md into focused documents.

### New Structure

1. **README.md** (~200 lines) - Intro + Quick Start
   - Project overview (brief)
   - Key achievements (bullet points)
   - Quick start guide
   - Links to other docs

2. **VERIFICATION.md** (~300 lines) - Proof Details
   - Axiom catalog (currently in README)
   - Sorry documentation
   - Theorem list
   - Verification procedures

3. **CONTRIBUTING.md** (~150 lines) - Development Guide
   - Code style (from CLAUDE.md)
   - Documentation standards
   - Build commands
   - Testing procedures

### Content Migration

| Current README Section | Move To |
|------------------------|---------|
| Lines 1-60 (overview) | README.md |
| Lines 61-135 (quick start) | README.md |
| Lines 319-550 (axiom catalog) | VERIFICATION.md |
| Lines 551-640 (verification procedures) | VERIFICATION.md |
| Lines 684-720 (project structure) | README.md (condensed) |
| Lines 817-900 (execution limitations) | VERIFICATION.md |

---

## Phase 4: Landing Page Fixes

### 4.1 GitHub Username

**Status:** No change needed - `e-vergo` is the correct username.

### 4.2 Fix Broken Documentation Link

**Issue:** Footer links to non-existent `GETTING_STARTED.md`
**Fix:** Update to link to `USAGE.md` instead

### 4.3 Update Statistics

**Changes needed:**
- 93% accuracy -> "90-95%" range (per user preference)
- 26 theorems -> "12 gradient correctness theorems" (per user preference)
- 4 sorries (correct, no change)
- 9 axioms (correct, no change)

---

## Phase 5: Create Subdirectory READMEs

Create mathlib-style READMEs for all 10 VerifiedNN subdirectories.

### Template Structure (~150 lines each)

```markdown
# Module Name

Brief description of the module's purpose.

## Overview

What this module provides and why it exists.

## Main Definitions

- `Definition1`: Description
- `Definition2`: Description

## Main Theorems

- `theorem_name`: Statement and significance

## File Descriptions

| File | Purpose | Status |
|------|---------|--------|
| File1.lean | Description | Verified/In Progress |

## Dependencies

- Imports from: list modules
- Imported by: list modules

## Usage Examples

```lean
-- Example code
```

## Verification Status

- Sorries: count and location
- Axioms: count and justification

## Implementation Notes

Design decisions and rationale.
```

### Directories to Create READMEs

1. `VerifiedNN/Core/README.md` - DataTypes, LinearAlgebra, Activation
2. `VerifiedNN/Data/README.md` - MNIST loading, preprocessing
3. `VerifiedNN/Layer/README.md` - Dense layers, properties
4. `VerifiedNN/Loss/README.md` - Cross-entropy, gradients
5. `VerifiedNN/Network/README.md` - MLP architecture, manual backprop
6. `VerifiedNN/Optimizer/README.md` - SGD, momentum
7. `VerifiedNN/Training/README.md` - Training loop, metrics
8. `VerifiedNN/Testing/README.md` - Test files, smoke tests
9. `VerifiedNN/Verification/README.md` - Proofs, axioms
10. `VerifiedNN/Examples/README.md` - Training executables

---

## Phase 6: Docstring Audit (Lower Priority)

Audit public definitions for mathlib-quality docstrings.

### Priority Files

1. Core module (highest visibility)
2. Network/ManualGradient.lean (key implementation)
3. Verification/*.lean (proof documentation)

### Docstring Requirements

- All public `def`, `theorem`, `structure` have `/-- -/` docstrings
- Module-level docstrings use `/-! -/` format
- Parameter documentation where non-obvious
- Return value documentation

---

## Execution Order

1. **Phase 1**: Remove AD files (cleans repo first)
2. **Phase 2**: Fix critical issues (broken imports, false claims)
3. **Phase 3**: Split README
4. **Phase 4**: Fix landing page
5. **Phase 5**: Create subdirectory READMEs (largest task)
6. **Phase 6**: Docstring audit (optional, time permitting)

## Estimated Scope

| Phase | Files Changed | Effort |
|-------|---------------|--------|
| Phase 1 | ~10 files (6 deleted, 4 updated) | Small |
| Phase 2 | ~5 files | Small |
| Phase 3 | 3 new files, 1 major edit | Medium |
| Phase 4 | 1 file (docs/index.html) | Small |
| Phase 5 | 10 new files | Large |
| Phase 6 | Many files | Large (optional) |

---

## Validation Checklist

After completion:
- [ ] `lake build` succeeds with zero errors
- [ ] No broken imports
- [ ] All executables in lakefile.lean exist
- [ ] README claims match reality
- [ ] Landing page links work
- [ ] Each VerifiedNN subdirectory has README.md
