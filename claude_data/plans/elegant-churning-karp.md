# Fix Landing Page SVG and Update Dates

## Issue 1: SVG Chart Overlap

**Problem:** The theorem category boxes extend to y=475 in a 480-height viewBox, leaving only 5px margin. A rect is overlapping the x-axis area.

**Fix in `/Users/eric/GitHub/LEAN_mnist/docs/index.html`:**

1. Line 142: Change viewBox from `0 0 400 480` to `0 0 400 520`
2. Verify all rect/text elements have proper spacing from bottom edge

## Issue 2: Outdated Dates (16 files)

All dates currently showing 2025 need to be updated to **January 2026**.

### Files to Update:

| File | Line | Current | Update To |
|------|------|---------|-----------|
| `VerifiedNN/Examples/README.md` | 269 | November 2025 | January 2026 |
| `VerifiedNN/Verification/README.md` | 224 | November 2025 | January 2026 |
| `VerifiedNN/Optimizer/README.md` | 244 | 2025-01-05 | 2026-01-06 |
| `VerifiedNN/Loss/README.md` | 154 | 2025-01-05 | 2026-01-06 |
| `VerifiedNN/Network/README.md` | 220 | 2025-01-05 | 2026-01-06 |
| `VerifiedNN/README.md` | 1077 | January 2025 | January 2026 |
| `docs/DEPLOYMENT_CHECKLIST.md` | 367 | November 21, 2025 | January 2026 |
| `docs/assets/README.md` | 5 | November 21, 2025 | January 2026 |
| `docs/README.md` | 317 | November 21, 2025 | January 2026 |
| `docs/content.md` | 234 | November 21, 2025 | January 2026 |
| `docs/index.html` | 542 | January 2025 | January 2026 |
| `documentation/USAGE.md` | 1114 | November 21, 2025 | January 2026 |
| `documentation/ARCHITECTURE.md` | 3 | November 21, 2025 | January 2026 |
| `documentation/VERIFICATION.md` | 377 | January 2025 | January 2026 |
| `CLAUDE.md` | 896 | January 2025 | January 2026 |
| `README.md` | 210 | January 2025 | January 2026 |

## Execution Plan

**Parallel Agent 1:** Fix SVG in `docs/index.html`
- Increase viewBox height
- Verify chart spacing

**Parallel Agent 2:** Update dates in VerifiedNN/ READMEs (6 files)

**Parallel Agent 3:** Update dates in docs/, documentation/, and root files (10 files)

## Commit
Single commit: "Fix SVG chart overlap and update all dates to January 2026"
