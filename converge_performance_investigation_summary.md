# Converge Performance Investigation Summary

**Issue:** #191
**PR:** #193
**Date:** 2026-02-04

---

## Executive Summary

Investigation identified **5 concrete optimization opportunities** that can reduce CSS-only converge iterations from ~210s to ~30-45s (**5-7x speedup**) while fixing critical reliability issues.

**Key findings:**
- 60% build failure rate due to `clean_artifacts` bug (#186)
- Archive extraction (3.8s) runs on every upload - processes all session JSONL files
- CSS-only changes trigger full Lake build unnecessarily (58-100s wasted)
- 3 archive timing categories never persisted (measurement blind spot)
- QA evaluation phase uninstrumented (unknown cost)

---

## Baseline Metrics

### Current Converge Iteration Time
- **Full build:** 193s (SBSTest), 253s (GCR)
- **Incremental build:** 48-93s (SBSTest), 48-64s (GCR)
- **CSS-only (theoretical):** 20-30s

### Time Breakdown
- **Build phases:** 73-75% of total time
  - `update_manifests`: 82-91s (Lake dependency resolution)
  - `build_project`: 58-100s (Lean compilation)
  - `generate_verso`: 11-64s (bimodal, cache issues)
- **Archive upload:** 3.8-4.7s (94.5% is extraction)
- **Validators:** 0.15s (negligible)
- **Pytest:** 4.07s (796 tests, 5ms/test)

### Bottlenecks Ranked
1. Build failure rate: 60% (wastes 50-90s per failed attempt)
2. CSS-only triggering full build: 58-100s wasted
3. Archive extraction overhead: 3.8s per upload (not incremental)
4. TodoWrite planning overhead: 11 hours across sessions (674 calls @ 58s avg)
5. API latency tail: p90 at 37s vs p50 at 3.4s (10x variance)

---

## Optimization Proposals

### Reliability Cluster (Implement First)

**P4: Fix clean_artifacts/build_toolchain misalignment**
- **Impact:** Eliminates 60% build failure rate
- **Complexity:** Low (~10 lines)
- **Closes:** #186
- **Ready-to-spawn issue:** ✓

**P3: Pre-flight build validation**
- **Impact:** Prevents 50-90s waste on remaining failures
- **Complexity:** Low (~30 lines)
- **Ready-to-spawn issue:** ✓

### Measurement Cluster (Implement Second)

**P2: Persist missing archive timing categories**
- **Impact:** Closes porcelain/iCloud measurement blind spot
- **Complexity:** Low (~5 lines)
- **Ready-to-spawn issue:** ✓

**P5: Instrument QA evaluation phase**
- **Impact:** Reveals true QA cost (currently unknown)
- **Complexity:** Low (~100 lines analysis code)
- **Ready-to-spawn issue:** ✓

### Performance Cluster (Implement Last)

**P1: CSS-only fast rebuild path**
- **Impact:** 60-135s saved per CSS-only iteration (3-5x speedup)
- **Complexity:** Medium (~150 lines)
- **Ready-to-spawn issue:** ✓

---

## Recommended Implementation Order

1. **P4 + P3 together** (reliability cluster) - ~40 lines total, closes #186
2. **P2 + P5 together** (measurement cluster) - ~105 lines total
3. **P1 standalone** (performance cluster) - ~150 lines, highest impact

**Expected total impact:**
- Build failure rate: 60% → <10%
- CSS-only iteration: ~210s → ~30-45s (5-7x speedup)
- Measurement blind spots: 3 → 0
- Per 3-iteration converge run: 8.7-17.1 min → 2.5-5 min

---

## Deliverables

✓ **Baseline metrics:** Current iteration time breakdown quantified
✓ **Top 5 opportunities:** Ranked by impact vs effort
✓ **Concrete proposals:** Ready-to-spawn GitHub issues for each
✓ **Prioritization framework:** Implementation order with dependencies

### Output Files
- `archive_timing_analysis.json` - 169 entries analyzed
- `build_timing_analysis.json` - 20 builds analyzed
- `session_timing_analysis.json` - 32 converge sessions analyzed
- `validator_git_timing_analysis.json` - Timing from validators, pytest, git ops
- `optimization_opportunities.md` - 10 opportunities identified, top 5 selected
- `optimization_proposals.md` - Full proposals with implementation details (555 lines)

---

## Next Steps

1. **Immediate:** Spawn P4 + P3 as single task to fix build reliability
2. **Short-term:** Spawn P2 + P5 as single task to close measurement gaps
3. **Medium-term:** Spawn P1 to implement CSS fast rebuild path
4. **Validation:** After P4 deployed, run 10 SBSTest builds and confirm >90% success rate

---

## Archive Stats

- **Agents spawned:** 7 total (4 Wave 1 parallel, 1 Wave 2, 1 Wave 3, 1 finalization)
- **Data analyzed:** 169 archive entries, 20 builds, 32 sessions
- **Investigation duration:** ~15 minutes wall-clock time
- **Proposals ready:** 5 concrete issues ready to spawn
