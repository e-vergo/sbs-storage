# Quality Score Report

**Project:** SBSTest | **Last Evaluated:** 2026-02-08T15:20:09.761308

## Overall Score: 67.29%

| Metric | Name | Weight | Score | Status |
|--------|------|--------|-------|--------|
| t1-cli-execution | CLI Execution | 10% | 0.0 | FAIL |
| t2-ledger-population | Ledger Population | 10% | 49.1 | FAIL |
| t3-dashboard-clarity | Dashboard Clarity | 10% | - | - |
| t4-toggle-discoverability | Toggle Discoverability | 10% | - | - |
| t5-color-match | Status Color Match | 15% | 100.0 | PASS |
| t6-css-coverage | CSS Variable Coverage | 15% | 91.5 | PASS |
| t7-jarring | Jarring-Free Check | 15% | - | - |
| t8-professional | Professional Score | 15% | - | - |

## Findings

### t1-cli-execution
- No evergreen tests found or ran

### t2-ledger-population
- Fields never populated: sync_error
- Population rate 49.1% below threshold 70.0%

### t5-color-match
- All 6 status colors match canonical values

### t6-css-coverage
- Excluded 53 intentional hardcoded colors (syntax: 47, var defs: 6)
- common.css:368: hardcoded rgba(57, 98, 130, 0.08) in background-color
- common.css:369: hardcoded rgba(57, 98, 130, 0.15) in border
- common.css:375: hardcoded rgba(57, 98, 130, 0.14) in background-color
- common.css:376: hardcoded rgba(57, 98, 130, 0.25) in border-color
- common.css:377: hardcoded rgba(0, 0, 0, 0.08) in box-shadow
- common.css:381: hardcoded rgba(57, 98, 130, 0.18) in background-color
- common.css:551: hardcoded rgba(0, 0, 0, 0.15) in box-shadow
- common.css:600: hardcoded rgba(0, 0, 0, 0.2) in box-shadow
- common.css:620: hardcoded rgba(0, 0, 0, 0.4) in background
- common.css:633: hardcoded rgba(0, 0, 0, 0.3) in box-shadow
- ... and 14 more violations

## Score History

| Timestamp | Overall Score |
|-----------|---------------|
| 2026-02-08T14:08:08 | 67.28% |
| 2026-02-08T14:39:31 | 67.28% |
| 2026-02-08T14:49:39 | 67.28% |
| 2026-02-08T14:51:57 | 67.28% |
| 2026-02-08T14:54:34 | 67.28% |
| 2026-02-08T14:55:41 | 67.28% |
| 2026-02-08T15:05:56 | 67.28% |
| 2026-02-08T15:06:59 | 67.29% |
| 2026-02-08T15:19:01 | 67.29% |
| 2026-02-08T15:20:09 | 67.29% |
