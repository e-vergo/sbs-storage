# GitHub Issues Integration Plan

## Summary

Integrate GitHub Issues with the archive system via:
1. New MCP tools wrapping `gh` CLI
2. `/log` skill for quick issue capture
3. Archive schema extension for `issue_refs`
4. `/task` modifications to consume/close issues

---

## Design Decisions (from Alignment)

| Aspect | Decision |
|--------|----------|
| Skill name | `/log` |
| UX | Smart hybrid (parse input, ask for gaps) |
| Labels | `bug`, `feature`, `idea` (minimal) |
| Priority | None |
| Archive link | `issue_refs` field (archive → issue, one-way) |
| `/task` input | Explicit `#N` or offer list |
| `/task` close | Prompt during finalization |
| MCP approach | Tools wrap `gh` CLI internally |

---

## Implementation Waves

### Wave 1: MCP Tools (sbs-lsp-mcp)

**Files to modify:**
- [sbs_models.py](forks/sbs-lsp-mcp/src/sbs_lsp_mcp/sbs_models.py) - Add issue models
- [sbs_tools.py](forks/sbs-lsp-mcp/src/sbs_lsp_mcp/sbs_tools.py) - Add 4 tools

**New tools:**

| Tool | gh Command | Returns |
|------|------------|---------|
| `sbs_issue_create` | `gh issue create` | Issue number, URL, title |
| `sbs_issue_list` | `gh issue list` | List of open issues with metadata |
| `sbs_issue_get` | `gh issue view` | Full issue details |
| `sbs_issue_close` | `gh issue close` | Success/failure |

**Models to add:**
```python
class GitHubIssue(BaseModel):
    number: int
    title: str
    state: str  # "open" | "closed"
    labels: list[str]
    url: str
    body: Optional[str] = None
    created_at: Optional[str] = None

class IssueCreateResult(BaseModel):
    success: bool
    number: Optional[int] = None
    url: Optional[str] = None
    error: Optional[str] = None

class IssueListResult(BaseModel):
    issues: list[GitHubIssue]
    total: int

class IssueCloseResult(BaseModel):
    success: bool
    error: Optional[str] = None
```

**Tool implementation pattern:**
```python
@mcp.tool("sbs_issue_create", annotations=ToolAnnotations(...))
def sbs_issue_create(
    ctx: Context,
    title: Annotated[str, Field(description="Issue title")],
    body: Annotated[Optional[str], Field(description="Issue body")] = None,
    label: Annotated[Optional[str], Field(description="Label: bug, feature, idea")] = None,
) -> IssueCreateResult:
    cmd = ["gh", "issue", "create", "--repo", "anthropics/Side-By-Side-Blueprint",
           "--title", title]
    if body:
        cmd.extend(["--body", body])
    if label:
        cmd.extend(["--label", label])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    # Parse output, return structured result
```

---

### Wave 2: Archive Schema Extension

**Files to modify:**
- [entry.py](dev/scripts/sbs/archive/entry.py) - Add `issue_refs` field
- [rules.yaml](dev/storage/tagging/rules.yaml) - Add tagging rule

**Schema change:**
```python
@dataclass
class ArchiveEntry:
    # ... existing fields ...
    issue_refs: list[str] = field(default_factory=list)  # e.g., ["42", "57"]
```

**Tagging rule:**
```yaml
  - name: has-github-issues
    condition:
      field: issue_refs
      is_empty: false
    tags: ["has-github-issue"]
```

---

### Wave 3: /log Skill

**Files to create:**
- [.claude/skills/log/SKILL.md](.claude/skills/log/SKILL.md)

**Skill structure:**
```yaml
---
name: log
description: Quick capture of issues and ideas to GitHub
version: 1.0.0
---

# /log - Issue Capture Skill

## Invocation
- `/log` - Interactive mode (asks for details)
- `/log fix the graph layout bug` - Infers type, creates issue
- `/log --idea --label=enhancement "tooltip feature"` - Direct creation

## Workflow
1. Parse input for title, type, description
2. Infer missing fields (type from keywords: "bug", "fix" → bug)
3. Ask user to confirm/fill gaps via AskUserQuestion
4. Call sbs_issue_create MCP tool
5. Archive with issue_refs populated
6. Report issue number and URL

## Archive Protocol
- Single archive upload with trigger="skill"
- Sets issue_refs to [<new_issue_number>]
- No global_state (atomic operation, not multi-phase)
```

---

### Wave 4: /task Integration

**Files to modify:**
- [.claude/skills/task/SKILL.md](.claude/skills/task/SKILL.md)

**Changes:**

1. **Invocation accepts issue number:**
   ```
   /task #42      → Loads issue #42 as task spec
   /task          → Lists open issues, lets user pick or describe freeform
   ```

2. **Alignment phase modification:**
   - If issue number given: call `sbs_issue_get`, use issue body as task context
   - If no issue: call `sbs_issue_list`, present options + freeform option

3. **Archive entries during execution:**
   - All archive uploads include `issue_refs` with linked issue numbers

4. **Finalization modification:**
   - After gate validation, before documentation cleanup:
   - "Close issue #42? [Yes/No]"
   - If yes: call `sbs_issue_close`

---

### Wave 5: Testing & Validation

**Manual testing:**
1. MCP tools: Use Claude Code to call each tool directly
2. `/log` skill: Test interactive and one-shot modes
3. `/task` integration: Test with and without issue number

**Automated tests:**
- Add tests to `dev/scripts/sbs/tests/pytest/` for archive schema (verify `issue_refs` serialization)
- Test tagging rule applies correctly

---

## Critical Files

| File | Purpose |
|------|---------|
| `forks/sbs-lsp-mcp/src/sbs_lsp_mcp/sbs_models.py` | Issue Pydantic models |
| `forks/sbs-lsp-mcp/src/sbs_lsp_mcp/sbs_tools.py` | Issue MCP tools |
| `dev/scripts/sbs/archive/entry.py` | Archive schema |
| `dev/storage/tagging/rules.yaml` | Auto-tagging rules |
| `.claude/skills/log/SKILL.md` | New skill |
| `.claude/skills/task/SKILL.md` | Modified skill |

---

## Verification

1. **MCP tools work:**
   ```
   # In Claude Code session
   Call sbs_issue_list → should return open issues
   Call sbs_issue_create with test title → should create issue
   Call sbs_issue_get with number → should return details
   Call sbs_issue_close with number → should close it
   ```

2. **Archive integration:**
   ```bash
   # After creating an issue via /log
   python3 -m sbs archive upload --trigger skill
   # Check archive_index.json for issue_refs field
   ```

3. **Skill functionality:**
   ```
   /log fix the graph layout bug
   # Should create issue, report number, archive with issue_refs

   /task #<number>
   # Should load issue as context
   ```

---

## Gates

```yaml
gates:
  tests: all_pass
  quality:
    T1: >= 0.8  # CLI execution
    T2: >= 0.8  # Ledger population
  regression: >= 0
```

---

## Execution Order

1. Wave 1 (MCP) - Foundation
2. Wave 2 (Archive) - Data model
3. Wave 3 (/log) - Capture path
4. Wave 4 (/task) - Consumption path
5. Wave 5 (Testing) - Validation

Each wave should be validated before proceeding to the next.
