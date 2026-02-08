# SBS Test Catalog

> Auto-generated on 2026-02-07 22:45:42
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

  Total: 887 tests

    [*] evergreen     719  ( 81.1%)  Stable, always run
    [~] dev            71  (  8.0%)  In development
    [-] unmarked       97  ( 10.9%)  Needs tier marker

  By file:

    [-] interactions/test_sidebar.py               6 tests
    [*] mvp/test_authoring_modes.py               15 tests
    [*] mvp/test_cicd.py                          16 tests
    [*] mvp/test_cross_page_consistency.py        20 tests
    [*] mvp/test_dashboard.py                     13 tests
    [*] mvp/test_dashboard_accuracy.py            16 tests
    [*] mvp/test_dependency_graph.py              20 tests
    [*] mvp/test_graph_navigation.py              18 tests
    [*] mvp/test_inspect_project.py               14 tests
    [*] mvp/test_paper_generation.py              12 tests
    [*] mvp/test_paper_quality.py                 14 tests
    [*] mvp/test_sbs_content.py                   18 tests
    [*] mvp/test_showcase.py                      27 tests
    [*] mvp/test_side_by_side.py                  15 tests
    [*] mvp/test_status_indicators.py             12 tests
    [*] mvp/test_taste.py                         25 tests
    [*] mvp/test_theme_and_dark_mode.py           16 tests
    [*] mvp/test_visual_quality.py                31 tests
    [*] oracle/test_compiler.py                   11 tests
    [*] oracle/test_extractors.py                 23 tests
    [-] oracle/test_oracle_filters.py              7 tests
    [*] readme/test_check.py                      19 tests
    [*] test_archive_invariants.py                34 tests
    [*] test_cli.py                               14 tests
    [*] test_compliance_mapping.py                19 tests
    [*] test_gates.py                             38 tests
    [~] test_incremental_artifacts.py              5 tests
    [*] test_ledger_health.py                     24 tests
    [~] test_self_improve.py                      66 tests
    [-] test_tagger_v2.py                         31 tests
    [-] test_taxonomy.py                          53 tests
    [*] test_timing_optimization.py               20 tests
    [*] validators/test_cli_execution.py           6 tests
    [*] validators/test_color_match.py            31 tests
    [*] validators/test_dashboard_clarity.py      31 tests
    [*] validators/test_jarring_check.py          27 tests
    [*] validators/test_professional_score.py     34 tests
    [*] validators/test_runner.py                  7 tests
    [*] validators/test_sbs_alignment.py           8 tests
    [*] validators/test_toggle_discoverability.py  34 tests
    [*] validators/test_variable_coverage.py      37 tests

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
  11 MCP tools | 887 tests | 21 CLI commands

```
