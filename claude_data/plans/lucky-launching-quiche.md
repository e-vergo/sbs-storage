# Plan: Remove Zebra Styling from Dashboard

## Goal

Remove all alternating row backgrounds (zebra striping) from the dashboard page while preserving zebra styling on blueprint chapter pages.

**Purpose:** Dry run to validate the /task workflow, scoring system, and visual testing.

---

## Analysis

### Current Zebra Styling Locations

| File | Lines | Selector | Target |
|------|-------|----------|--------|
| `common.css` | 187-209 | `.dashboard-list > li:nth-child(odd/even)` | Dashboard messages |
| `common.css` | 187-209 | `.notes-list > li:nth-child(odd/even)` | Project notes |
| `blueprint.css` | 723-732 | `.key-declaration-item:nth-child(odd/even)` | Key declarations |

All selectors are dashboard-specific - no risk to blueprint pages.

### Files to Modify

```
toolchain/dress-blueprint-action/assets/common.css
toolchain/dress-blueprint-action/assets/blueprint.css
```

---

## Wave 1: CSS Changes

**Agent: Remove zebra styling rules**

### 1A: common.css

Remove lines 187-209 (entire zebra striping section for dashboard lists).

Keep the section header comment but replace content with uniform background:
```css
/* ============================================
   Dashboard List Styling
   Uniform background for clean appearance
   ============================================ */

.dashboard-list > li,
.notes-list > li {
  padding: 0.5rem 0.75rem;
  margin: 0;
  border-radius: 4px;
  background-color: var(--sbs-bg-surface);
}
```

### 1B: blueprint.css

Remove lines 723-732 (zebra striping for key declarations).

Replace with uniform styling:
```css
/* Key declarations styling */
.key-declaration-item {
  background-color: var(--sbs-bg-surface);
  border-radius: 4px;
}
```

---

## Wave 2: Build and Capture

**Agent: Rebuild and capture screenshots**

```bash
cd /Users/eric/GitHub/Side-By-Side-Blueprint/toolchain/SBS-Test
python3 ../../dev/scripts/build.py --capture
```

Wait for build to complete, verify new screenshots captured.

---

## Wave 3: Visual Validation

**Agent: Validate no zebra styling on dashboard**

1. Run visual compliance check:
```bash
cd /Users/eric/GitHub/Side-By-Side-Blueprint/dev/scripts
python3 -m sbs compliance --project SBSTest
```

2. Manually inspect dashboard screenshot:
   - Path: `dev/storage/SBSTest/latest/dashboard.png`
   - Verify: No alternating row backgrounds visible
   - Verify: Lists have uniform background color

3. Compare before/after:
   - Before: `dev/storage/SBSTest/previous/dashboard.png` (if exists)
   - After: `dev/storage/SBSTest/latest/dashboard.png`

4. Record pass/fail in quality ledger

---

## Validation Rubric

| Metric | Type | Pass Criteria |
|--------|------|---------------|
| No zebra on dashboard lists | Visual | Dashboard lists have uniform background |
| No zebra on key declarations | Visual | Key theorem items have uniform background |
| Blueprint pages unchanged | Visual | Chapter pages still have expected styling |
| Build succeeds | Deterministic | `build.py` exits 0 |

---

## Critical Files

| File | Action |
|------|--------|
| `toolchain/dress-blueprint-action/assets/common.css` | Remove zebra rules (lines 187-209) |
| `toolchain/dress-blueprint-action/assets/blueprint.css` | Remove zebra rules (lines 723-732) |

---

## Success Criteria

1. ✅ Dashboard screenshot shows uniform backgrounds (no alternating colors)
2. ✅ Build completes successfully
3. ✅ No visual regressions on other pages
4. ✅ Quality score recorded in ledger

---

## Verification

After completion:

1. **Visual check:** Open `http://localhost:8000` and inspect dashboard
2. **Screenshot comparison:** View before/after in `dev/storage/SBSTest/`
3. **Automated validation:** `sbs compliance --project SBSTest`
4. **Quality ledger:** Verify entry in `dev/storage/SBSTest/quality_ledger.json`
