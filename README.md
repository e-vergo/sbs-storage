# Side-by-Side Blueprint: Archive & Tooling Hub

> **This is the central reference for all monorepo tooling.**
> All repository READMEs link here for CLI commands, validation, and development workflows.

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `sbs capture` | Capture screenshots of all pages |
| `sbs capture --interactive` | Include hover/click states |
| `sbs compliance` | Run visual compliance validation |
| `sbs rubric list` | List all quality rubrics |
| `sbs rubric show <id>` | Display a rubric |
| `sbs rubric evaluate <id>` | Evaluate against a rubric |
| `sbs archive list` | List archive entries |
| `sbs archive show <id>` | Show entry details |
| `sbs archive upload` | Extract ~/.claude data and archive |
| `sbs archive charts` | Generate visualizations |
| `sbs archive sync` | Sync to iCloud |

**Run from:** `/Users/eric/GitHub/Side-By-Side-Blueprint/dev/scripts`

---

## Rubric System

Custom quality rubrics enable structured improvement workflows.

### Commands

```bash
# Create a rubric from JSON
sbs rubric create --from-json path/to/rubric.json

# Create an empty rubric by name
sbs rubric create --name "my-rubric"

# List all rubrics
sbs rubric list

# Display a rubric (human-readable)
sbs rubric show my-rubric --format markdown

# Display as JSON
sbs rubric show my-rubric --format json

# Evaluate a project against a rubric
sbs rubric evaluate my-rubric --project SBSTest

# Delete a rubric
sbs rubric delete my-rubric --force
```

### Rubric Structure

A rubric contains:
- **Categories**: User-defined groupings (e.g., "Dashboard Clarity", "CSS Quality")
- **Metrics**: Measurable items with thresholds and weights
- **Scoring**: Weighted average of metric scores

### Storage

```
dev/storage/rubrics/
├── index.json              # Registry of all rubrics
├── {rubric-id}.json        # Rubric definition
├── {rubric-id}.md          # Human-readable (auto-generated)
└── {rubric-id}_eval_*.json # Evaluation results
```

### Creating Rubrics

Rubrics are typically created during `/execute --grab-bag` sessions:

1. **Brainstorm** improvements with user
2. **Align** on measurable metrics
3. **Create** rubric with thresholds and weights
4. **Execute** tasks with rubric-based validation
5. **Finalize** with evaluation summary

See `.claude/skills/execute/SKILL.md` for the full grab-bag workflow.

---

## Archive System

Central archive for build data, screenshots, and metrics.

### Directory Structure

```
dev/storage/
├── unified_ledger.json     # Build metrics and timing (single source of truth)
├── lifetime_stats.json     # Cross-run aggregates
├── archive_index.json      # Entry index with tags/notes
├── compliance_ledger.json  # Compliance tracking
├── rubrics/                # Quality rubrics
│   ├── index.json
│   ├── {id}.json
│   └── {id}.md
├── charts/                 # Generated visualizations
│   ├── loc_trends.png
│   ├── timing_trends.png
│   └── activity_heatmap.png
├── chat_summaries/         # Session summaries
│   └── {entry_id}.md
└── {project}/              # Per-project screenshots
    ├── latest/
    │   ├── capture.json
    │   └── *.png
    └── archive/{timestamp}/
```

### Archive Entries

Each build creates an `ArchiveEntry`:

| Field | Description |
|-------|-------------|
| `entry_id` | Unique ID (unix timestamp) |
| `created_at` | ISO timestamp |
| `project` | Project name |
| `build_run_id` | Links to unified ledger |
| `rubric_id` | Links to quality rubric (if evaluated) |
| `rubric_evaluation` | Evaluation results snapshot |
| `notes` | User notes |
| `tags` | User-defined tags |
| `screenshots` | List of captured screenshots |
| `repo_commits` | Git commits at build time (all repos) |
| `synced_to_icloud` | Sync status |

### Commands

```bash
# List all entries
sbs archive list

# List entries for a project
sbs archive list --project SBSTest

# List entries with a specific tag
sbs archive list --tag release

# Show entry details
sbs archive show <entry_id>

# Add tags to an entry
sbs archive tag <entry_id> release v1.0

# Add note to an entry
sbs archive note <entry_id> "First stable release"

# Generate charts from build data
sbs archive charts

# Sync archive to iCloud
sbs archive sync

# Migrate historical captures
sbs archive retroactive --dry-run
sbs archive retroactive
```

### iCloud Sync

Archive data syncs to iCloud on every build:

```
~/Library/Mobile Documents/com~apple~CloudDocs/SBS_archive/
```

Sync is non-blocking - failures are logged but don't break builds.

---

## Archive Upload System

The archive upload system extracts Claude Code interaction data and maintains a complete record of development sessions.

### Single Command

```bash
sbs archive upload
```

This command:
1. Extracts relevant data from `~/.claude`
2. Creates an archive entry with session data
3. Applies auto-tagging rules
4. Commits and pushes all repos (porcelain guarantee)
5. Syncs to iCloud

### Options

```bash
sbs archive upload --dry-run          # Show what would be done
sbs archive upload --project SBSTest  # Associate with project
sbs archive upload --trigger manual   # Set trigger type (build/manual/skill)
```

### Data Extracted from ~/.claude

| Source | Content | Storage |
|--------|---------|---------|
| `projects/*SBS*/` | Sessions, tool calls | `claude_data/sessions/` |
| `plans/*.md` | Plan files | `claude_data/plans/` |
| Tool results | Aggregated statistics | `claude_data/tool_calls/` |

### Auto-Tagging

Tags are applied automatically via:
1. **Declarative rules** in `tagging/rules.yaml`
2. **Python hooks** in `tagging/hooks/`

#### Rules Format

```yaml
rules:
  - name: successful-build
    condition:
      field: build_success
      equals: true
    tags: ["successful-build"]

  - name: toolchain-change
    condition:
      field: files_modified
      matches_any: ["*/Dress/*.lean", "*/Runway/*.lean"]
    tags: ["toolchain-change"]
```

#### Available Operators

| Operator | Description |
|----------|-------------|
| `equals` | Exact match |
| `not_equals` | Not equal |
| `greater_than` | Numeric comparison |
| `less_than` | Numeric comparison |
| `contains` | String/list contains |
| `matches_any` | Glob pattern match |
| `is_empty` | Check if empty |

#### Writing Hooks

Hooks receive `(entry, sessions)` and return a list of tags:

```python
# tagging/hooks/my_hook.py
def analyze(entry, sessions):
    tags = []
    if some_condition(sessions):
        tags.append("my-tag")
    return tags
```

### Build Integration

Archive upload runs automatically at the end of every build:

```bash
./dev/build-sbs-test.sh  # Triggers archive upload with build context
```

Build context passed to tagging:
- `build_success`: Whether build succeeded
- `build_duration_seconds`: Total build time
- `repos_changed`: List of repos with new commits

### Porcelain Guarantee

After upload, all repos are in clean state:
- Main repo committed and pushed
- All submodules committed and pushed
- No uncommitted changes anywhere

### Storage Structure

```
dev/storage/
├── claude_data/           # Extracted ~/.claude data
│   ├── sessions/          # Parsed session JSON
│   │   ├── {session_id}.json
│   │   └── index.json
│   ├── plans/             # Copied plan files
│   ├── tool_calls/
│   │   └── summary.json
│   └── extraction_state.json
└── tagging/
    ├── rules.yaml         # Declarative rules
    └── hooks/             # Python hooks
        ├── __init__.py
        ├── cli_arg_misfires.py
        └── session_quality.py
```

---

## Compliance System

Visual compliance validation using AI vision analysis.

### Workflow

```bash
# 1. Build project (from monorepo root)
./dev/build-sbs-test.sh

# Or from project directory
cd /Users/eric/GitHub/Side-By-Side-Blueprint/toolchain/SBS-Test
python ../../dev/scripts/build.py

# 2. Capture screenshots
cd /Users/eric/GitHub/Side-By-Side-Blueprint/dev/scripts
sbs capture --project SBSTest --interactive

# 3. Run compliance
sbs compliance --project SBSTest
```

### Captured Pages

| Page | Description |
|------|-------------|
| `dashboard` | Main homepage with stats, key theorems, messages |
| `dep_graph` | Dependency graph with pan/zoom and modals |
| `chapter` | First detected chapter page with side-by-side displays |
| `paper_tex` | Paper from TeX source |
| `pdf_tex` | PDF viewer from TeX source |
| `paper_verso` | Paper from Verso source |
| `pdf_verso` | PDF viewer from Verso source |
| `blueprint_verso` | Blueprint from Verso source |

Pages returning HTTP 404 are skipped without error.

### Interactive States

With `--interactive`, additional screenshots are captured:

- `*_theme_toggle.png` - Dark mode variant
- `*_proof_toggle.png` - Proof expanded state
- `*_hover_token.png` - Token hover popup
- `dep_graph_zoom_*.png` - Zoom in/out/fit states
- `dep_graph_node_click_*.png` - Node modal views

### Documentation

See `scripts/VISUAL_COMPLIANCE.md` for detailed compliance criteria and validation workflow.

---

## Visualizations

Charts generated from `unified_ledger.json`:

| Chart | Description |
|-------|-------------|
| `loc_trends.png` | Lines of code by language over last 20 builds |
| `timing_trends.png` | Build phase durations (stacked area) |
| `activity_heatmap.png` | Files changed per repo per build |

Regenerate manually: `sbs archive charts`

---

## Build Integration

The archive system integrates with `build.py`:

1. Build completes
2. Metrics saved to `unified_ledger.json`
3. Archive entry created with `build_run_id`
4. Charts regenerated
5. Entry synced to iCloud
6. Entry saved to `archive_index.json`

---

## Validators

Validators provide automated quality checks.

### Available Validators

| Validator | Category | Purpose |
|-----------|----------|---------|
| `visual-compliance` | visual | AI vision validation of screenshots |
| `timing` | timing | Build phase timing metrics |
| `git-metrics` | git | Commit/diff tracking |
| `code-stats` | code | LOC and file counts |
| `ledger-health` | code | Ledger field population |
| `rubric` | code | Custom rubric evaluation |
| `color-match` | design | Status color validation |
| `variable-coverage` | design | CSS variable coverage |
| `dashboard-clarity` | design | Dashboard communication check |
| `toggle-discoverability` | design | Proof toggle visibility |
| `jarring-check` | design | Visual jarring detection |
| `professional-score` | design | Professional appearance rating |

### Usage

```python
from sbs.validators import discover_validators, registry, ValidationContext

discover_validators()
validator = registry.get('visual-compliance')
result = validator.validate(context)
```

### Creating Custom Validators

See `scripts/sbs/validators/base.py` for the `BaseValidator` class and `@register_validator` decorator.

---

## Quality Scoring

The 8-dimensional quality test suite (T1-T8) provides comprehensive quality metrics:

| Test | Dimensions | Weight |
|------|------------|--------|
| T1: CLI Execution | Functional, Deterministic, Binary | 10% |
| T2: Ledger Population | Functional, Deterministic, Gradient | 10% |
| T3: Dashboard Clarity | Functional, Heuristic, Binary | 10% |
| T4: Toggle Discoverability | Functional, Heuristic, Gradient | 10% |
| T5: Status Color Match | Aesthetic, Deterministic, Binary | 15% |
| T6: CSS Variable Coverage | Aesthetic, Deterministic, Gradient | 15% |
| T7: Jarring-Free Check | Aesthetic, Heuristic, Binary | 15% |
| T8: Professional Score | Aesthetic, Heuristic, Gradient | 15% |

**Current score:** 91.77/100

See `scripts/sbs/tests/SCORING_RUBRIC.md` for detailed methodology.

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| [`dev/scripts/VISUAL_COMPLIANCE.md`](../scripts/VISUAL_COMPLIANCE.md) | Visual compliance workflow and criteria |
| [`dev/scripts/sbs/tests/SCORING_RUBRIC.md`](../scripts/sbs/tests/SCORING_RUBRIC.md) | Quality scoring methodology |
| [`.claude/skills/execute/SKILL.md`](../../.claude/skills/execute/SKILL.md) | Execute skill with grab-bag mode |
| [`.claude/agents/sbs-developer.md`](../../.claude/agents/sbs-developer.md) | Development agent guide |
| [`dev/markdowns/README.md`](../markdowns/README.md) | Project overview |
| [`dev/markdowns/ARCHITECTURE.md`](../markdowns/ARCHITECTURE.md) | Architecture documentation |
| [`dev/markdowns/GOALS.md`](../markdowns/GOALS.md) | Project goals and vision |
