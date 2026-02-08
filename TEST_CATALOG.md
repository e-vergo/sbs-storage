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

## Testing Conventions

### Threshold-Based Assertions

For visual and layout tests, prefer threshold assertions over exact-value assertions:

**When to use thresholds:**
- CSS spacing values: `assert padding >= parse_rem("1rem")` instead of `assert padding == "1.5rem"`
- Coverage metrics: `assert coverage >= 0.90` instead of `assert coverage == 0.95`
- Timing measurements: `assert duration < 200` (ms) instead of `assert duration == 150`

**When to use exact values:**
- Hex color codes (T5 status colors must match exactly)
- Boolean states (element exists or doesn't)
- Enum values (status must be one of 6 defined values)

**Pattern examples from existing tests:**
- `test_sbs_alignment.py`: Uses `>= 1rem` threshold for padding checks
- `test_color_match.py`: Uses exact hex comparison for status colors
- `test_variable_coverage.py`: Uses `>= 0.90` threshold for CSS variable coverage

**Rationale:** Exact pixel assertions create false failures when CSS is adjusted. Threshold assertions catch real regressions (value dropped to 0) while tolerating intentional adjustments (1.5rem -> 2rem).

## Artifact Encoding Paths (Dress)

All output paths must apply the same sanitization. See #273 for background.

### Per-Declaration Artifacts (Generate/Declaration.lean)

These are written during elaboration when `BLUEPRINT_DRESS=1`. Each `@[blueprint]` declaration
gets a subdirectory under `.lake/build/dressed/{Module/Path}/{sanitized-label}/`.

| Path | Output File | Sanitization | Test Coverage |
|------|-------------|-------------|---------------|
| HTML direct | `decl.html` | `stripDelimiterBlocks` on rendered HTML | `test_delimiter_sanitization.py` |
| Hover JSON direct | `decl.hovers.json` | `stripDelimiterBlocks` on hover JSON | `test_delimiter_sanitization.py` |
| Metadata JSON | `decl.json` | None (JSON-escaped name/label only) | None |
| Manifest entry | `manifest.entry` | None (JSON-escaped label/path only) | None |

### TeX Artifacts (Generate/Latex.lean)

These embed syntax-highlighted HTML inside LaTeX macros via base64 encoding.
The `decl.tex` file contains all of these as LaTeX commands.

| Path | LaTeX Macro | Sanitization | Test Coverage |
|------|------------|-------------|---------------|
| Signature HTML | `\leansignaturesourcehtml{base64}` | `stripDelimiterBlocks` then `Base64.encodeString` | `test_delimiter_sanitization.py` |
| Proof body HTML | `\leanproofsourcehtml{base64}` | `stripDelimiterBlocks` then `Base64.encodeString` | `test_delimiter_sanitization.py` |
| Hover JSON | `\leanhoverdata{base64}` | `stripDelimiterBlocks` then `Base64.encodeString` | `test_delimiter_sanitization.py` |
| Above/below narrative | `\leanabove{base64}`, `\leanbelow{base64}` | `Base64.encodeString` only (raw LaTeX, no delimiter concern) | None |

### Legacy Output Path (Output.lean)

The `toLatex` method on `NodeWithPos` emits additional macros for backward compatibility
with leanblueprint. This path does NOT apply `stripDelimiterBlocks`.

| Path | LaTeX Macro | Sanitization | Test Coverage |
|------|------------|-------------|---------------|
| Full source HTML | `\leansourcehtml{base64}` | `Base64.encodeString` only | None |
| Signature HTML | `\leansignaturesourcehtml{base64}` | `Base64.encodeString` only | None |
| Proof body HTML | `\leanproofsourcehtml{base64}` | `Base64.encodeString` only | None |
| Full source JSON | `\leansource{base64}` | `Base64.encodeString` only | None |
| Signature JSON | `\leansignaturesource{base64}` | `Base64.encodeString` only | None |
| Proof body JSON | `\leanproofsource{base64}` | `Base64.encodeString` only | None |

**Note:** The `Output.lean` legacy path does not strip delimiter blocks. This is a known
gap -- the `toLatex` method renders HTML via `HtmlRender.renderHighlightedToHtml` without
`stripDelimiterBlocks`. Since this path is used for the `:blueprint` Lake facet (plasTeX
consumption), delimiter leakage here would appear as raw `/-%%...%%-/` text in the
leanblueprint-style output. See #273.

### Serialize Paths (Serialize/*.lean)

Module-level serialization for the hook mechanism. These write per-module aggregate files,
not per-declaration artifacts.

| Path | Output File | Sanitization | Test Coverage |
|------|-------------|-------------|---------------|
| Module JSON | `module.json` | None (SubVerso Module format) | None |
| HTML map JSON | `module.html.json` | None (raw HTML from `renderHighlightedToHtml`) | None |
| Dressed artifacts | `module.dressed.json` | None (includes `htmlBase64` and `jsonBase64`) | None |

**Note:** The Serialize paths store raw highlighting data and pre-rendered HTML without
delimiter stripping. These are intermediate files consumed by `Output.lean`'s `toLatex`
method, which inherits the same gap.

### Sanitization Function

`stripDelimiterBlocks` (defined in `Generate/Latex.lean`) removes `/-%%...%%-/` block
delimiters that embed TeX content in Lean comments. These leak through SubVerso's
highlighting pipeline because SubVerso preserves comment text. The function:

1. Splits on `/-%%` opening markers
2. For each segment, finds the matching `%%-/` closing marker
3. Removes content between delimiters, preserving text outside
4. Handles unclosed delimiters gracefully (restores the opener)

## Fan-Out Synchronization Points

Architecture has identified fan-out points where changes must be applied to ALL parallel paths:

### @[blueprint] Declaration Fan-Out

When a new field is added to `Architect.Node` or the rendering of a declaration changes,
these parallel output paths must all be updated:

| Path | File | Consumer |
|------|------|----------|
| HTML artifact | `Generate/Declaration.lean` -> `decl.html` | Runway blueprint pages |
| TeX artifact | `Generate/Latex.lean` -> `decl.tex` | plasTeX / leanblueprint |
| Hover JSON | `Generate/Declaration.lean` -> `decl.hovers.json` | JavaScript tooltip engine |
| Legacy TeX | `Output.lean` -> `\leansourcehtml`, `\leansignaturesourcehtml`, etc. | `:blueprint` Lake facet |
| Metadata JSON | `Generate/Declaration.lean` -> `decl.json` | Debugging / tooling |

### Runway Rendering Fan-Out

The side-by-side display is rendered in two contexts that must stay synchronized:

| Context | File | Entry Point |
|---------|------|-------------|
| Blueprint chapter pages | `Runway/Render.lean` | `renderNode` -> `Dress.Render.renderSideBySide` |
| Paper pages | `Runway/Paper.lean` | `PaperNodeInfoExt.toSbsData` -> `Dress.Render.renderSideBySide` |
| Dependency graph modals | `Runway/Render.lean` | `renderNodeModal` -> `renderNode` |

These three consumers all route through `Dress.Render.renderSideBySide` (in
`Dress/Render/SideBySide.lean`), which is the consolidation point. Changes to
`SbsData` fields propagate automatically. However, the *construction* of `SbsData`
differs between `Render.lean` (from `NodeInfo`) and `Paper.lean` (from `PaperNodeInfoExt`),
so new fields must be mapped in both places.

### Metric: Synchronization Completeness

For each fan-out point, track:
- **Paths enumerated:** Number of parallel paths (from architecture docs)
- **Paths updated:** Number modified in a given change (from git diffs)
- **Ratio:** Updated / Enumerated

A ratio < 1.0 signals a synchronization hazard. This can be checked during build
validation or as a pre-commit hook.

**Implementation approach:** A lightweight script could parse git diffs for changes
to fan-out files and warn when only a subset of a fan-out group is modified. For
example, if `Generate/Declaration.lean` is modified but `Output.lean` is not, emit
a warning for the `@[blueprint] Declaration Fan-Out` group.
