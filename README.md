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
| `sbs archive list` | List archive entries |
| `sbs archive show <id>` | Show entry details |
| `sbs archive upload` | Extract ~/.claude data and archive |
| `sbs archive charts` | Generate visualizations |
| `sbs archive sync` | Sync to iCloud |
| `sbs oracle compile` | Compile Oracle knowledge base from READMEs |
| `sbs readme-check` | Check which READMEs need updating |
| `sbs validate-all` | Run compliance + quality score status |
| `sbs test-catalog` | List all testable components with metadata |
| `sbs labels sync` | Sync label taxonomy to GitHub |
| `sbs labels list` | List all labels from taxonomy |
| `sbs labels validate <label>...` | Validate label names against taxonomy |

**Run from:** `/Users/eric/GitHub/Side-By-Side-Blueprint/dev/scripts`

---

## Archive System

Central archive for build data, screenshots, metrics, workflow state, and PR tracking.

**Naming:** The local directory is `dev/storage/` but conceptually referred to as "the archive" throughout the codebase. The iCloud backup location is `~/Library/Mobile Documents/com~apple~CloudDocs/SBS_archive/`.

### Directory Structure

```
dev/storage/  (local archive)
+-- unified_ledger.json     # Build metrics and timing (single source of truth)
+-- archive_index.json      # Entry index with tags/notes/state machine
+-- compliance_ledger.json  # Compliance tracking
+-- baselines.json          # Visual baseline hashes for comparison
+-- charts/                 # Generated visualizations
|   +-- loc_trends.png
|   +-- timing_trends.png
|   +-- activity_heatmap.png
|   +-- archive_timing_trends.png
+-- chat_summaries/         # Session summaries
|   +-- {entry_id}.md
+-- claude_data/            # Extracted ~/.claude data
|   +-- sessions/           # Parsed session JSON
|   +-- plans/              # Copied plan files
|   +-- tool_calls/
|   +-- extraction_state.json
+-- tagging/
|   +-- rules.yaml          # Declarative rules
|   +-- hooks/              # Python hooks
+-- {project}/              # Per-project screenshots
    +-- latest/
    |   +-- capture.json
    |   +-- *.png
    +-- archive/{timestamp}/
```

### Archive Entries

Each build creates an `ArchiveEntry`:

| Field | Description |
|-------|-------------|
| `entry_id` | Unique ID (unix timestamp) |
| `created_at` | ISO timestamp |
| `project` | Project name |
| `trigger` | "build", "skill", or "manual" |
| `build_run_id` | Links to unified ledger |
| `global_state` | Current workflow state (skill + substate) |
| `state_transition` | Phase boundary marker ("phase_start", "phase_end", or null) |
| `epoch_summary` | Aggregated data when epoch closes |
| `notes` | User notes |
| `tags` | User-defined tags |
| `screenshots` | List of captured screenshots |
| `added_at` | UTC ISO timestamp when entry was archived |
| `repo_commits` | Git commits at build time (all repos) |
| `issue_refs` | GitHub issue numbers linked to this entry |
| `pr_refs` | GitHub PR numbers linked to this entry |
| `synced_to_icloud` | Sync status |

### State Machine Fields

The archive tracks workflow state for orchestration:

**`global_state`** in ArchiveIndex:
```python
{
    "skill": "task",           # Current skill name or null
    "substate": "execution"    # Current phase within skill
}
```

**`state_transition`** in entries:
- `"phase_start"` - Beginning of a new phase
- `"phase_end"` - Completion of a phase
- `null` - Regular entry (not a boundary)

**Skill substates:**
- `/task`: alignment -> planning -> execution -> finalization
- `/update-and-archive`: readme-wave -> oracle-regen -> porcelain -> archive-upload

### Epoch Semantics

An **epoch** is a logical unit of work bounded by `/update-and-archive` invocations:

1. Epoch N starts (previous `/update-and-archive` completed)
2. Build entries, manual entries, skill-triggered entries accumulate
3. `/update-and-archive` invoked
4. Final entry includes `epoch_summary` with aggregated data
5. Epoch N closes, Epoch N+1 begins

**Epoch summary structure:**
```python
{
    "epoch_number": 42,
    "duration_hours": 3.5,
    "entry_count": 12,
    "builds": {"total": 4, "successful": 3, "failed": 1},
    "quality_delta": {"start": 89.5, "end": 91.77, "change": 2.27},
    "repos_changed": ["Dress", "Runway"],
    "tags_applied": ["visual-improvement", "successful-build"]
}
```

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

The entire archive syncs to iCloud on every build for complete backup:

```
~/Library/Mobile Documents/com~apple~CloudDocs/SBS_archive/
```

**What Gets Backed Up:**
| Content | Description |
|---------|-------------|
| `archive_index.json` | Main entry index |
| `unified_ledger.json` | Build metrics |
| `compliance_ledger.json` | Compliance data |
| `baselines.json` | Visual baseline hashes |
| `migrations.json` | File migration tracking |
| `claude_data/` | Sessions, plans, tool calls (full rich data) |
| `tagging/` | Rules and hooks |
| `charts/` | Generated visualizations |
| `entries/` | Individual entry metadata + screenshots |
| `{project}/` | Project screenshots (SBSTest, GCR, PNT) |

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
4. Runs deterministic validators when `--validate` is passed, or auto-runs when build trigger has empty quality scores
5. Commits and pushes all repos (porcelain guarantee)
6. Syncs to iCloud

### Options

```bash
sbs archive upload --dry-run          # Show what would be done
sbs archive upload --project SBSTest  # Associate with project
sbs archive upload --trigger manual   # Set trigger type (build/manual/skill)
sbs archive upload --issue-refs 42,43 # Link GitHub issues to entry
sbs archive upload --pr-number 123    # Link GitHub PR to entry
sbs archive upload --validate         # Run validators and attach quality scores
```

### Data Extracted from ~/.claude

| Source | Content | Storage |
|--------|---------|---------|
| `projects/*SBS*/` | Sessions, tool calls | `claude_data/sessions/` |
| `plans/*.md` | Plan files | `claude_data/plans/` |
| Tool results | Aggregated statistics | `claude_data/tool_calls/` |

### Rich Data Extraction

The extractor captures comprehensive data from Claude Code JSONL files:

| Data | Source | Purpose |
|------|--------|---------|
| Thinking blocks | `message.content[].thinking` | Reasoning traces for prompting analysis |
| Token usage | `message.usage.*` | Cost analysis, cache efficiency |
| Model version | `message.model`, thinking signature | Version tracking |
| Message threading | `parentUuid` chains | Conversation reconstruction |
| Stop reasons | `message.stop_reason` | Completion analysis |
| Session metadata | `sessions-index.json` | Slug, first prompt, summary |
| Full tool inputs | `tool_use.input` | Pattern analysis (not truncated) |
| Tool results | `tool_result.content` | Success/failure tracking |

**Per-Session Data:**
- `thinking_blocks`: List of reasoning traces with signatures
- `message_usage`: Aggregated token counts (input, output, cache)
- `model_versions`: Models used during session
- `parent_uuid_chain`: Message threading for reconstruction
- `stop_reasons`: How each response completed

**Per-Snapshot Aggregates:**
- `total_input_tokens`, `total_output_tokens`: Cost tracking
- `cache_read_tokens`, `cache_creation_tokens`: Cache efficiency
- `thinking_block_count`: Total reasoning traces
- `model_versions_used`: All models across sessions
- `unique_tools_used`: Distinct tools invoked

### Auto-Tagging

Tags are applied automatically via:
1. **Declarative rules** in `tagging/rules.yaml`
2. **Python hooks** in `tagging/hooks/`

#### Agent-State Tag Taxonomy (v2.0)

Tags use a **colon-delimited hierarchical format** (`dimension:value`) across 17 dimensions with ~138 total tags. The archive tags are part of the unified taxonomy at `taxonomy.yaml` (entries with `contexts: [archive]` or `contexts: [both]`).

| Dimension | Example Tags | Purpose |
|-----------|-------------|---------|
| `phase` | `phase:alignment`, `phase:execution`, `phase:idle` | Skill lifecycle phase |
| `transition` | `transition:phase-start`, `transition:epoch-close` | State machine transition type |
| `skill` | `skill:task`, `skill:update-and-archive` | Active skill |
| `trigger` | `trigger:build`, `trigger:skill`, `trigger:manual` | What created the entry |
| `session` | `session:edit-heavy`, `session:long`, `session:tool-diverse` | Behavioral profile of session |
| `outcome` | `outcome:gate-pass`, `outcome:pr-merged`, `outcome:quality-improved` | Observable results |
| `signal` | `signal:backward-transition`, `signal:retry-loop`, `signal:high-churn` | Anomaly/attention signals |
| `scope` | `scope:cross-repo`, `scope:lean`, `scope:narrow` | Breadth and type of changes |
| `repo` | `repo:dress`, `repo:runway`, `repo:dev-scripts` | Which repositories were touched |
| `epoch` | `epoch:opening`, `epoch:closing`, `epoch:long` | Epoch position and character |
| `linkage` | `linkage:has-issue`, `linkage:has-pr`, `linkage:issue-driven` | GitHub artifact linkage |
| `token` | `token:input-heavy`, `token:cache-efficient`, `token:total-light` | Token usage profile |
| `thinking` | `thinking:heavy`, `thinking:extended`, `thinking:deep` | Extended thinking usage |
| `tool` | `tool:read-dominant`, `tool:bash-dominant`, `tool:failure-rate-high` | Tool usage patterns |
| `quality` | `quality:high`, `quality:all-pass`, `quality:t5-fail` | Quality score state |
| `model` | `model:opus`, `model:multi-model` | Model usage |

#### Rules (v2.0)

50 declarative rules in `tagging/rules.yaml` map entry fields to taxonomy tags:

```yaml
rules:
  - name: phase-alignment
    condition:
      field: substate
      equals: "alignment"
    tags: ["phase:alignment"]

  - name: scope-cross-repo
    condition:
      field: repos_changed_count
      greater_than: 2
    tags: ["scope:cross-repo"]
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

#### Tagging Hooks

Three hooks provide session-level behavioral analysis beyond declarative rules:

| Hook | Tags Produced | Purpose |
|------|---------------|---------|
| `session_profiler.py` | ~30 (`session:*`, `token:*`, `thinking:*`, `tool:*`, `model:*`) | Profiles session behavior from tool call stats and token usage |
| `signal_detector.py` | ~10 (`signal:*`) | Detects anomalies: high error rates, retry loops, context compaction |
| `outcome_tagger.py` | ~8 (`outcome:*`) | Tags observable outcomes: PR/issue events, quality changes |

Hooks receive `(entry, sessions)` and return a list of tags:

```python
# tagging/hooks/my_hook.py
def analyze(entry, sessions):
    tags = []
    if some_condition(sessions):
        tags.append("dimension:value")
    return tags
```

#### Key Files

| File | Purpose |
|------|---------|
| `taxonomy.yaml` | Unified taxonomy (27 dimensions, 243 entries; archive tags filtered by `contexts`) |
| `tagging/rules.yaml` | 50 declarative rules mapping fields to tags |
| `tagging/hooks/session_profiler.py` | Session behavioral profiling hook |
| `tagging/hooks/signal_detector.py` | Anomaly detection hook |
| `tagging/hooks/outcome_tagger.py` | Outcome classification hook |

### Build Integration

Archive upload runs automatically at the end of every build:

```bash
./dev/build-sbs-test.sh  # Triggers archive upload with build context
```

Build context passed to tagging includes state machine fields (`skill`, `substate`, `state_transition`), token usage aggregates, quality scores, and repo change data. The `build_tagging_context()` function assembles all fields consumed by rules and hooks.

### Porcelain Guarantee

After upload, all repos are in clean state:
- Main repo committed and pushed
- All submodules committed and pushed
- No uncommitted changes anywhere

### Archive Upload Timing

Each `sbs archive upload` now instruments every step and records timings in the `archive_timings` field of the archive entry. Phases tracked:
- `extraction` -- Claude data extraction from ~/.claude
- `quality_scores` -- Quality ledger loading and optional validation
- `repo_commits` -- Git SHA collection across all repos
- `tagging` -- Auto-tagging engine evaluation
- `gate_validation` -- Finalization gate checks (when applicable)
- `index_save` -- Archive index serialization
- `icloud_sync_launch` -- Async iCloud sync launch
- `porcelain` -- Git commit and parallel push

### Async iCloud Sync

iCloud sync now runs in a background daemon thread. The archive upload returns immediately after launching the sync -- it does not block on iCloud file copies. This reduces archive upload wall-clock time by 30-60 seconds.

### Parallel Git Pushes

Git pushes during `ensure_porcelain()` now run in parallel (up to 4 concurrent pushes). Commits are still sequential (required for submodule pointer correctness). Main repo is always pushed last.

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

Charts generated from archive data:

| Chart | Source | Description |
|-------|--------|-------------|
| `loc_trends.png` | `unified_ledger.json` | Lines of code by language over last 20 builds |
| `timing_trends.png` | `unified_ledger.json` | Build phase durations (stacked area) |
| `activity_heatmap.png` | `unified_ledger.json` | Files changed per repo per build |
| `archive_timing_trends.png` | `archive_index.json` | Archive upload phase timings (stacked bar) |

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

### Build Flags

| Flag | Description |
|------|-------------|
| `--dry-run` | Show what would be done without executing |
| `--skip-cache` | Bypass toolchain build cache |
| `--verbose` | Enable debug output |
| `--capture` | Capture screenshots after build |
| `--force-lake` | Force Lake builds even if Lean sources unchanged |

**Lean Source Skip:** By default, the build script detects whether `.lean` files have changed since the last successful build. If unchanged, Lake build phases (toolchain, project, blueprint, mathlib cache, manifests) are skipped entirely. Use `--force-lake` to override this and force a full rebuild.

---

## Validators

Validators provide automated quality checks.

### Available Validators

| Validator | Category | Purpose |
|-----------|----------|---------|
| `cli-execution` | code | Evergreen pytest suite pass/fail (T1) |
| `visual-compliance` | visual | AI vision validation of screenshots |
| `timing` | timing | Build phase timing metrics |
| `git-metrics` | git | Commit/diff tracking |
| `code-stats` | code | LOC and file counts |
| `ledger-health` | code | Ledger field population |
| `color-match` | design | Status color validation |
| `variable-coverage` | design | CSS variable coverage |
| `dashboard-clarity` | design | Dashboard communication check |
| `toggle-discoverability` | design | Proof toggle visibility |
| `jarring-check` | design | Visual jarring detection |
| `professional-score` | design | Professional appearance rating |

### Validator Runner

The runner (`sbs/tests/validators/runner.py`) is the central orchestration layer for running validators:

- Maps validator names (registry keys) to metric IDs (ledger keys)
- Builds `ValidationContext` with project paths, git commits, screenshot directories
- Runs validators, extracts scores, and persists results to the quality score ledger
- Automatically skips heuristic validators when no screenshots are available

```python
from sbs.tests.validators.runner import run_validators

# Run all deterministic validators for SBSTest
result = run_validators(project="SBSTest", skip_heuristic=True)

# Run specific metrics
result = run_validators(
    project="SBSTest",
    metric_ids=["t1-cli-execution", "t5-color-match"],
)

# Check results
print(result.overall_passed)   # True if all ran validators passed
print(result.ledger_updated)   # True if ledger was written
print(result.skipped)          # Metric IDs that were skipped
print(result.errors)           # Error messages from failed validators
```

### Individual Validator Usage

```python
from sbs.validators import discover_validators, registry, ValidationContext

discover_validators()
validator = registry.get('visual-compliance')
result = validator.validate(context)
```

### Creating Custom Validators

See `scripts/sbs/tests/validators/base.py` for the `BaseValidator` class and `@register_validator` decorator.

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

### Commands

```bash
# Unified validation: compliance + quality scores
sbs validate-all --project SBSTest
```

### Quality Score Ledger

Scores are persisted in `{project}/quality_ledger.json` with:
- Per-metric scores and pass/fail status
- Repo commits at evaluation time
- Staleness detection (auto-invalidates on repo changes)
- Score history (last 20 snapshots)

Human-readable report generated at `{project}/QUALITY_SCORE.md`.

### Implementation

Located in `scripts/sbs/tests/scoring/`:

| File | Purpose |
|------|---------|
| `ledger.py` | `QualityScoreLedger`, `MetricScore`, persistence |
| `reset.py` | Repo-change detection, metric invalidation |

See `scripts/sbs/tests/SCORING_RUBRIC.md` for detailed methodology.

---

## Oracle System

The Oracle provides instant codebase Q&A for Claude agents without searching.

### Compiling the Oracle

```bash
sbs oracle compile
```

This regenerates `dev/storage/oracle/knowledge_base.md` from all repository READMEs:
- Main monorepo README
- Per-repository READMEs (Dress, Runway, SubVerso, Verso, LeanArchitect, etc.)
- Extracts key concepts, file locations, patterns, and gotchas

### What the Oracle Knows

- **Concept Index**: Concept -> file location mapping
- **File Purpose Map**: One-liner summaries per file
- **How-To Patterns**: Add CLI command, add validator, add hook, etc.
- **Gotchas**: Status color source of truth, manual ToExpr, etc.
- **Cross-Repo Impact**: What to check when changing X

### Usage by Agents

The `sbs-oracle` agent uses the compiled knowledge base to answer questions without searching:

```
Task(subagent_type="sbs-oracle", prompt="Where is graph layout implemented?")
```

### Auto-Regeneration

The Oracle is auto-regenerated during `/update-and-archive` skill execution.

---

## Capability Context Tools

MCP context-fetcher tools that assemble context for agent capabilities:

| Tool | Agent | Purpose |
|------|-------|---------|
| `sbs_task()` | `sbs-task` | Fetch archive state, issues, recent entries, quality scores for task execution |
| `sbs_end_epoch()` | `sbs-end-epoch` | Fetch retrospective data, session stats, README staleness for epoch close |
| `sbs_introspect()` | `sbs-end-epoch` | Fetch entries since last improvement, session stats for introspection |
| `sbs_qa()` | `sbs-qa` | Fetch project info, server state, prior QA ledger for visual QA |
| `sbs_converge()` | `sbs-converge` | Fetch prior convergence data, adaptation notes for QA convergence loop |
| `sbs_log()` | (none -- atomic) | Direct issue creation, no agent needed |

These tools read from the archive and return structured context blobs for agent injection at zero orchestrator token cost. State is tracked by archive entries written via `sbs archive upload` CLI.

---

## README Staleness Detection

Identifies which READMEs may need updating based on git state.

### Commands

```bash
# Human-readable report
sbs readme-check

# JSON output for programmatic use
sbs readme-check --json
```

### What It Checks

For each repository (main + 10 submodules):
- **Uncommitted changes**: Files modified but not committed
- **Unpushed commits**: Commits not pushed to remote
- **Changed files list**: Specific files that changed

### Example Output

```
README Staleness Report
=======================

Main (Side-By-Side-Blueprint):
  Status: has changes
  Uncommitted: 3 files
  Changed files:
    - CLAUDE.md
    - dev/scripts/sbs/cli.py

Dress:
  Status: clean

Runway:
  Status: has changes
  Unpushed: 2 commits
```

### Integration with /update-and-archive

The skill runs `sbs readme-check --json` to determine which repos have changes. Agents only update READMEs for repos with actual code changes, avoiding unnecessary documentation churn.

---

## Test Organization System

Tests are organized into three tiers using pytest markers:

| Tier | Marker | Purpose |
|------|--------|---------|
| **Evergreen** | `@pytest.mark.evergreen` | Production tests that always run |
| **Dev** | `@pytest.mark.dev` | Development/WIP tests, toggle-able |
| **Temporary** | `@pytest.mark.temporary` | Tests to be discarded after use |

### Commands

```bash
# List all testable components
sbs test-catalog

# JSON output for programmatic use
sbs test-catalog --json

# Filter by tier
sbs test-catalog --tier evergreen

# Run specific tier via MCP tool
sbs_run_tests(tier="evergreen")
```

### What test-catalog Shows

- **MCP Tools (11)**: SBS tools with category and read-only status
- **Pytest Tests**: All tests with tier markers
- **CLI Commands**: All sbs subcommands with availability

---

## GitHub Label Taxonomy

An 11-dimension, ~105 label taxonomy for structured issue classification.

### Taxonomy Definition

The canonical taxonomy lives at `dev/storage/taxonomy.yaml` (unified v3.0). Issue labels are entries with `contexts: [issues]` or `contexts: [both]`. It defines labels across these dimensions:

| Dimension | Example Labels | Purpose |
|-----------|---------------|---------|
| `origin` | `origin:user`, `origin:agent`, `origin:self-improve` | Who initiated the issue |
| `type` | `bug:visual`, `feature:new`, `idea:design`, `housekeeping:docs` | What kind of work |
| `area_sbs` | `area:sbs:graph`, `area:sbs:dashboard`, `area:sbs:css` | Which part of the generated product |
| `area_devtools` | `area:devtools:archive`, `area:devtools:mcp`, `area:devtools:validators` | Which part of the dev toolchain |
| `area_lean` | `area:lean:dress`, `area:lean:runway`, `area:lean:verso` | Which Lean repo or framework component |
| `loop` | `loop:work`, `loop:archive`, `loop:analyze`, `loop:improve` | Where in the self-improvement cycle |
| `impact` | `impact:visual`, `impact:functional`, `impact:dx` | What does this affect |
| `scope` | `scope:single-repo`, `scope:cross-repo`, `scope:architectural` | How big is the change |
| `pillar` | `pillar:user-effectiveness`, `pillar:claude-execution` | Self-improvement analysis pillar |
| `project` | `project:sbs-test`, `project:gcr`, `project:pnt` | Which showcase project surfaces this |
| `friction` | `friction:context-loss`, `friction:tooling-gap`, `friction:slow-feedback` | What pain point is addressed |

Plus standalone labels like `ai-authored`.

### Label CLI

```bash
# Sync all labels to GitHub (creates/updates/preserves)
sbs labels sync

# Dry-run sync (show what would change)
sbs labels sync --dry-run

# List all taxonomy labels
sbs labels list

# Validate label names
sbs labels validate "bug:visual" "area:sbs:graph"
```

### Python API

```python
from sbs.labels import load_taxonomy, get_all_labels, validate_labels, get_label_color

# Get all ~105 label names
all_labels = get_all_labels()

# Validate a set of labels
valid, invalid = validate_labels(["bug:visual", "not-a-label"])

# Get color for a label
color = get_label_color("bug:visual")  # "#d73a4a"
```

### MCP Integration

The `sbs_issue_create` MCP tool accepts a `labels` parameter for applying taxonomy labels when creating issues. The `sbs_issue_summary` tool groups issues by taxonomy dimension for structured reporting.

### Key Files

| File | Purpose |
|------|---------|
| `dev/storage/taxonomy.yaml` | Unified taxonomy (issues + archive, v3.0) |
| `dev/scripts/sbs/labels/__init__.py` | Taxonomy loader, validator, color lookup |
| `dev/scripts/sbs/labels/sync.py` | GitHub label sync (create/update, never delete) |
| `dev/scripts/sbs/tests/pytest/test_taxonomy.py` | Taxonomy tests (evergreen tier) |

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| [`dev/scripts/VISUAL_COMPLIANCE.md`](../scripts/VISUAL_COMPLIANCE.md) | Visual compliance workflow and criteria |
| [`dev/scripts/sbs/tests/SCORING_RUBRIC.md`](../scripts/sbs/tests/SCORING_RUBRIC.md) | Quality scoring methodology |
| [`.claude/skills/task/SKILL.md`](../../.claude/skills/task/SKILL.md) | Task skill workflow |
| [`.claude/skills/log/SKILL.md`](../../.claude/skills/log/SKILL.md) | Quick issue logging skill |
| [`.claude/agents/sbs-developer.md`](../../.claude/agents/sbs-developer.md) | Development agent guide |
| [`.claude/agents/sbs-oracle.md`](../../.claude/agents/sbs-oracle.md) | Oracle agent guide |
| [`dev/markdowns/living/README.md`](../markdowns/living/README.md) | Project overview |
| [`dev/markdowns/permanent/ARCHITECTURE.md`](../markdowns/permanent/ARCHITECTURE.md) | Architecture documentation |
| [`dev/markdowns/permanent/GOALS.md`](../markdowns/permanent/GOALS.md) | Project goals and vision |
| [`dev/markdowns/permanent/Archive_Orchestration_and_Agent_Harmony.md`](../markdowns/permanent/Archive_Orchestration_and_Agent_Harmony.md) | Archive roles and state machine |
| [`TEST_CATALOG.md`](TEST_CATALOG.md) | Auto-generated catalog of testable components |
