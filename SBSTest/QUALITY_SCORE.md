# Quality Score Report

**Project:** SBSTest | **Last Evaluated:** 2026-02-03T18:08:39.015476

## Overall Score: 67.39%

| Metric | Name | Weight | Score | Status |
|--------|------|--------|-------|--------|
| t1-cli-execution | CLI Execution | 10% | 0.0 | FAIL |
| t2-ledger-population | Ledger Population | 10% | 49.1 | FAIL |
| t3-dashboard-clarity | Dashboard Clarity | 10% | - | - |
| t4-toggle-discoverability | Toggle Discoverability | 10% | - | - |
| t5-color-match | Status Color Match | 15% | 100.0 | PASS |
| t6-css-coverage | CSS Variable Coverage | 15% | 91.9 | FAIL |
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
- common.css:345: hardcoded rgba(57, 98, 130, 0.08) in background-color
- common.css:346: hardcoded rgba(57, 98, 130, 0.15) in border
- common.css:352: hardcoded rgba(57, 98, 130, 0.14) in background-color
- common.css:353: hardcoded rgba(57, 98, 130, 0.25) in border-color
- common.css:354: hardcoded rgba(0, 0, 0, 0.08) in box-shadow
- common.css:358: hardcoded rgba(57, 98, 130, 0.18) in background-color
- common.css:526: hardcoded rgba(0, 0, 0, 0.15) in box-shadow
- common.css:575: hardcoded rgba(0, 0, 0, 0.2) in box-shadow
- common.css:595: hardcoded rgba(0, 0, 0, 0.4) in background
- common.css:608: hardcoded rgba(0, 0, 0, 0.3) in box-shadow
- ... and 14 more violations

## Score History

| Timestamp | Overall Score |
|-----------|---------------|
| 2026-02-03T04:43:56 | 66.95% |
| 2026-02-03T17:58:46 | 66.26% |
| 2026-02-03T18:08:39 | 67.39% |
