# Task #81: Enrich GitHub Issue Label Taxonomy

## Summary

Define a hierarchical, colon-delimited label taxonomy (11 dimensions, ~125 labels) for GitHub issues. Update `sbs_issue_create` MCP tool, `/log` skill, and `/self-improve` skill to use it. Create CLI tooling to sync labels to GitHub. Defer retroactive application.

---

## Waves

### Wave 1: Taxonomy Definition + CLI Sync (Foundation)

**Files:**
- `dev/storage/labels/taxonomy.yaml` (CREATE) -- Full taxonomy, 11 dimensions, colors, descriptions
- `dev/scripts/sbs/labels/__init__.py` (CREATE) -- Taxonomy loader, validation, lookup
- `dev/scripts/sbs/labels/sync.py` (CREATE) -- `gh label create/edit` sync (idempotent)
- `dev/scripts/sbs/cli.py` (MODIFY) -- Add `sbs labels sync` and `sbs labels list`
- `dev/scripts/sbs/tests/pytest/test_taxonomy.py` (CREATE) -- Validation tests

**Color scheme by dimension:**
| Dimension | Color | Hex |
|-----------|-------|-----|
| origin | Gray | #9E9E9E |
| type:bug | Red | #d73a4a |
| type:feature | Cyan | #0E8A16 |
| type:idea | Purple | #d876e3 |
| type:behavior | Yellow | #fbca04 |
| type:housekeeping | Warm Gray | #CFD8DC |
| type:investigation | Dark Green | #0e8a16 |
| area:sbs | Blue | #1565C0 |
| area:devtools | Teal | #00695C |
| area:lean | Amber | #E65100 |
| loop | Indigo | #283593 |
| impact | Green | #1B5E20 |
| scope | Brown | #795548 |
| pillar | Deep Purple | #311B92 |
| project | Pink | #880E4F |
| friction | Orange | #BF360C |

### Wave 2: MCP Tool Migration

**Files:**
- `forks/sbs-lsp-mcp/src/sbs_lsp_mcp/sbs_tools.py` (MODIFY) -- `sbs_issue_create`: add `labels: List[str]` param, keep `label`/`area` for backward compat. `sbs_issue_summary`: group by all dimensions.
- `forks/sbs-lsp-mcp/src/sbs_lsp_mcp/sbs_models.py` (MODIFY) -- Update result models

**Backward compat logic:**
```python
resolved_labels = ["ai-authored"]
if labels:
    resolved_labels.extend(labels)
else:
    if label: resolved_labels.append(label)
    if area: resolved_labels.append(f"area:{area}")
```

### Wave 3: `/log` Skill Enrichment

**Files:**
- `.claude/skills/log/SKILL.md` (MODIFY) -- Expanded keyword tables, multi-dimension inference

**Inference tiers:**
- **Always infer:** origin (always `origin:agent`), type (18 subtypes), area (42 areas)
- **Conditionally infer:** impact, scope, friction (only when keywords strongly signal)
- **Never prompt for:** loop, pillar, project

### Wave 4: `/self-improve` Skill + GitHub Sync

**Files:**
- `.claude/skills/self-improve/SKILL.md` (MODIFY) -- Logging phase uses enriched labels
- Run `sbs labels sync` to create all labels on GitHub

**Self-improve label mapping:**
- Always: `origin:self-improve`
- Map pillar to `pillar:*` label
- Infer `friction:*` from finding content
- Include `impact:*` from finding impact

### Wave 5: Documentation (handled by /update-and-archive)

No manual wave needed -- `/update-and-archive` at task end will refresh CLAUDE.md, oracle, and READMEs.

---

## Gates

```yaml
gates:
  tests: all_pass
  test_tier: evergreen
```

---

## Verification

1. `sbs labels list` renders full taxonomy tree
2. `sbs labels sync --dry-run` reports ~125 labels to create
3. `sbs_issue_create(title="test", labels=["bug:visual", "area:sbs:graph", "friction:slow-feedback"])` creates issue with all labels
4. `/log graph nodes overlap` infers `bug:visual` + `area:sbs:graph` + `origin:agent`
5. Evergreen tests pass
6. `sbs labels sync` creates all labels on GitHub
