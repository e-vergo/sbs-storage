# SBS Test Catalog

> Auto-generated on 2026-02-02 04:16:16
> Run `sbs test-catalog` to regenerate

```

  SBS Test Catalog
  ==================================================

  MCP TOOLS
  --------------------------------------------------

  Orchestration
  Session state and context

    [+] sbs_oracle_query             RO
    [+] sbs_archive_state            RO
    [+] sbs_epoch_summary            RO
    [+] sbs_context                  RO

  Testing
  Validation and quality checks

    [+] sbs_run_tests                RO
    [+] sbs_validate_project         RO

  Build
  Project compilation

    [+] sbs_build_project            RW
    [+] sbs_serve_project            RW

  Investigation
  Screenshots and history

    [+] sbs_last_screenshot          RO
    [+] sbs_visual_history           RO
    [+] sbs_search_entries           RO

  PYTEST TESTS
  --------------------------------------------------

  Total: 283 tests

    [*] evergreen     283  (100.0%)  Stable, always run

  By file:

    [*] oracle/test_compiler.py                   11 tests
    [*] oracle/test_extractors.py                 23 tests
    [*] readme/test_check.py                      19 tests
    [*] test_cli.py                               14 tests
    [*] test_ledger_health.py                     24 tests
    [*] validators/test_color_match.py            30 tests
    [*] validators/test_dashboard_clarity.py      31 tests
    [*] validators/test_jarring_check.py          27 tests
    [*] validators/test_professional_score.py     34 tests
    [*] validators/test_toggle_discoverability.py  34 tests
    [*] validators/test_variable_coverage.py      36 tests

  CLI COMMANDS
  --------------------------------------------------

  Visual Testing

    [+] capture              Capture screenshots of generated site
    [+] compare              Compare latest screenshots to previous capture
    [+] history              List capture history for a project
    [+] compliance           Visual compliance validation loop

  Validation

    [+] validate             Run validation checks on generated site
    [+] validate-all         Run compliance + quality score evaluation
    [+] inspect              Show build state, artifact locations, manifest contents

  Repository

    [+] status               Show git status across all repos
    [+] diff                 Show changes across all repos
    [+] sync                 Ensure all repos are synced (commit + push)
    [+] versions             Show dependency versions across repos

  Archive

    [+] archive list         List archive entries
    [+] archive tag          Add tags to an archive entry
    [+] archive note         Add or update note on an archive entry
    [+] archive show         Show details of an archive entry
    [+] archive charts       Generate all charts from unified ledger
    [+] archive sync         Sync archive to iCloud
    [+] archive upload       Extract Claude data and upload to archive

  Utilities

    [+] oracle compile       Compile Oracle from sources
    [+] readme-check         Check which READMEs may need updating
    [+] test-catalog         List all testable components

  ==================================================
  11 MCP tools | 283 tests | 21 CLI commands

```
