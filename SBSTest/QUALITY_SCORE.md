# Quality Score Report

**Project:** SBSTest | **Last Evaluated:** 2026-02-04T03:28:15.520507

## Overall Score: 67.12%

| Metric | Name | Weight | Score | Status |
|--------|------|--------|-------|--------|
| t1-cli-execution | CLI Execution | 10% | 0.0 | FAIL |
| t2-ledger-population | Ledger Population | 10% | 48.5 | FAIL |
| t3-dashboard-clarity | Dashboard Clarity | 10% | - | - |
| t4-toggle-discoverability | Toggle Discoverability | 10% | - | - |
| t5-color-match | Status Color Match | 15% | 100.0 | PASS |
| t6-css-coverage | CSS Variable Coverage | 15% | 91.4 | PASS |
| t7-jarring | Jarring-Free Check | 15% | - | - |
| t8-professional | Professional Score | 15% | - | - |

## Findings

### t1-cli-execution
- No evergreen tests found or ran

### t2-ledger-population
- Fields never populated: sync_error
- Population rate 48.4% below threshold 70.0%

### t5-color-match
- All 6 status colors match canonical values

### t6-css-coverage
- Excluded 53 intentional hardcoded colors (syntax: 47, var defs: 6)
- common.css:357: hardcoded rgba(57, 98, 130, 0.08) in background-color
- common.css:358: hardcoded rgba(57, 98, 130, 0.15) in border
- common.css:364: hardcoded rgba(57, 98, 130, 0.14) in background-color
- common.css:365: hardcoded rgba(57, 98, 130, 0.25) in border-color
- common.css:366: hardcoded rgba(0, 0, 0, 0.08) in box-shadow
- common.css:370: hardcoded rgba(57, 98, 130, 0.18) in background-color
- common.css:544: hardcoded rgba(0, 0, 0, 0.15) in box-shadow
- common.css:593: hardcoded rgba(0, 0, 0, 0.2) in box-shadow
- common.css:613: hardcoded rgba(0, 0, 0, 0.4) in background
- common.css:626: hardcoded rgba(0, 0, 0, 0.3) in box-shadow
- ... and 14 more violations

## Score History

| Timestamp | Overall Score |
|-----------|---------------|
| 2026-02-03T17:58:46 | 66.26% |
| 2026-02-03T18:08:39 | 67.39% |
| 2026-02-03T18:52:07 | 67.22% |
| 2026-02-03T18:57:28 | 67.23% |
| 2026-02-03T21:02:48 | 67.20% |
| 2026-02-03T23:27:30 | 67.17% |
| 2026-02-04T00:22:24 | 67.16% |
| 2026-02-04T01:24:10 | 67.14% |
| 2026-02-04T02:50:02 | 67.13% |
| 2026-02-04T03:28:15 | 67.12% |
