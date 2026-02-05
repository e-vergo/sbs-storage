# Quality Score Report

**Project:** SBSTest | **Last Evaluated:** 2026-02-05T17:06:39.702143

## Overall Score: 67.20%

| Metric | Name | Weight | Score | Status |
|--------|------|--------|-------|--------|
| t1-cli-execution | CLI Execution | 10% | 0.0 | FAIL |
| t2-ledger-population | Ledger Population | 10% | 48.6 | FAIL |
| t3-dashboard-clarity | Dashboard Clarity | 10% | - | - |
| t4-toggle-discoverability | Toggle Discoverability | 10% | - | - |
| t5-color-match | Status Color Match | 15% | 100.0 | PASS |
| t6-css-coverage | CSS Variable Coverage | 15% | 91.6 | PASS |
| t7-jarring | Jarring-Free Check | 15% | - | - |
| t8-professional | Professional Score | 15% | - | - |

## Findings

### t1-cli-execution
- No evergreen tests found or ran

### t2-ledger-population
- Fields never populated: sync_error
- Population rate 48.6% below threshold 70.0%

### t5-color-match
- All 6 status colors match canonical values

### t6-css-coverage
- Excluded 53 intentional hardcoded colors (syntax: 47, var defs: 6)
- common.css:349: hardcoded rgba(57, 98, 130, 0.08) in background-color
- common.css:350: hardcoded rgba(57, 98, 130, 0.15) in border
- common.css:356: hardcoded rgba(57, 98, 130, 0.14) in background-color
- common.css:357: hardcoded rgba(57, 98, 130, 0.25) in border-color
- common.css:358: hardcoded rgba(0, 0, 0, 0.08) in box-shadow
- common.css:362: hardcoded rgba(57, 98, 130, 0.18) in background-color
- common.css:550: hardcoded rgba(0, 0, 0, 0.15) in box-shadow
- common.css:599: hardcoded rgba(0, 0, 0, 0.2) in box-shadow
- common.css:619: hardcoded rgba(0, 0, 0, 0.4) in background
- common.css:632: hardcoded rgba(0, 0, 0, 0.3) in box-shadow
- ... and 14 more violations

## Score History

| Timestamp | Overall Score |
|-----------|---------------|
| 2026-02-05T16:58:35 | 67.18% |
| 2026-02-05T16:59:16 | 67.18% |
| 2026-02-05T16:59:52 | 67.18% |
| 2026-02-05T17:00:07 | 67.19% |
| 2026-02-05T17:00:56 | 67.19% |
| 2026-02-05T17:02:17 | 67.19% |
| 2026-02-05T17:03:10 | 67.19% |
| 2026-02-05T17:05:11 | 67.19% |
| 2026-02-05T17:05:36 | 67.20% |
| 2026-02-05T17:06:39 | 67.20% |
