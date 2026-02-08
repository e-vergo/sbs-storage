# Quality Score Report

**Project:** SBSTest | **Last Evaluated:** 2026-02-08T12:46:51.571987

## Overall Score: 67.25%

| Metric | Name | Weight | Score | Status |
|--------|------|--------|-------|--------|
| t1-cli-execution | CLI Execution | 10% | 0.0 | FAIL |
| t2-ledger-population | Ledger Population | 10% | 48.9 | FAIL |
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
- Population rate 48.9% below threshold 70.0%

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
- common.css:555: hardcoded rgba(0, 0, 0, 0.15) in box-shadow
- common.css:604: hardcoded rgba(0, 0, 0, 0.2) in box-shadow
- common.css:624: hardcoded rgba(0, 0, 0, 0.4) in background
- common.css:637: hardcoded rgba(0, 0, 0, 0.3) in box-shadow
- ... and 14 more violations

## Score History

| Timestamp | Overall Score |
|-----------|---------------|
| 2026-02-08T12:25:13 | 67.23% |
| 2026-02-08T12:26:44 | 67.24% |
| 2026-02-08T12:36:44 | 67.24% |
| 2026-02-08T12:38:09 | 67.24% |
| 2026-02-08T12:38:49 | 67.24% |
| 2026-02-08T12:39:33 | 67.24% |
| 2026-02-08T12:40:50 | 67.24% |
| 2026-02-08T12:42:15 | 67.25% |
| 2026-02-08T12:45:36 | 67.25% |
| 2026-02-08T12:46:51 | 67.25% |
