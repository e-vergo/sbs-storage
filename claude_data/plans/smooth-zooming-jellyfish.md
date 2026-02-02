# Task 1: Agent Documentation and Workflow Updates

## Summary

Three related documentation changes:
1. Absorb TAXONOMY.md into ARCHITECTURE.md (then delete)
2. Update multi-agent policy in CLAUDE.md and sbs-developer.md
3. Refresh SBS MCP tool references across agent/skill docs

---

## Wave 1: TAXONOMY.md Absorption

**Files:**
- `dev/markdowns/permanent/ARCHITECTURE.md` - Add "Document Taxonomy" section before Related Documents
- `CLAUDE.md` - Remove TAXONOMY.md from Reference Documents table
- `dev/markdowns/permanent/TAXONOMY.md` - Delete

**Content to merge:**
- Categories: Permanent, Living, Generated (with characteristics and examples)
- Semantic Meaning of Changes table
- Decision Guide flowchart

---

## Wave 2: Multi-Agent Policy

**New policy:**
> Only one agent with edit permissions at a time. Multiple read-only agents (search, exploration) may run in parallel.

**Files:**
- `CLAUDE.md` - Replace "sequentially, never in parallel" constraint in Orchestration Model with:
  ```
  **Agent Parallelism:**
  - **Edit agents:** Only ONE at a time (architectural invariant)
  - **Read-only agents:** May run in parallel for search/exploration
  - **Rule:** If agents might touch same files, run sequentially
  ```

- `.claude/agents/sbs-developer.md` - Add section after Repository Architecture:
  ```
  ## Agent Parallelism

  This agent has full edit permissions. Only one sbs-developer runs at a time.
  Multiple Explore agents can run in parallel alongside.
  ```

---

## Wave 3: SBS MCP Tool References

**Tools to reference:** `sbs_oracle_query`, `sbs_archive_state`, `sbs_context`, `sbs_epoch_summary`, `sbs_run_tests`, `sbs_validate_project`, `sbs_build_project`, `sbs_serve_project`, `sbs_last_screenshot`, `sbs_visual_history`, `sbs_search_entries`

**Files:**

1. **sbs-developer.md** - Add SBS Tools section after existing MCP section:
   - Orchestration tools: `sbs_archive_state`, `sbs_context`, `sbs_epoch_summary`
   - Testing tools: `sbs_run_tests`, `sbs_validate_project`
   - Build tools: `sbs_build_project`, `sbs_serve_project`
   - Visual tools: `sbs_last_screenshot`, `sbs_visual_history`

2. **task/SKILL.md** - Add explicit tool references:
   - `sbs_run_tests` in Metric Gates section
   - `sbs_context` for agent spawn (optional note)

3. **update-and-archive/SKILL.md** - Add tool references:
   - `sbs_search_entries` for entry lookup
   - `sbs_epoch_summary` for epoch data in Part 4

4. **ARCHITECTURE.md** - Add brief MCP section in Tooling area referencing sbs-lsp-mcp

5. **Archive_Orchestration_and_Agent_Harmony.md** - Verify MCP Fork Philosophy section is current (likely no changes needed)

---

## Execution

Single `sbs-developer` agent executes all waves sequentially (documentation-only).

---

## Gates

```yaml
gates:
  tests: all_pass
  regression: >= 0
```

---

## Verification

1. Confirm TAXONOMY.md deleted
2. Confirm no broken cross-references in modified files
3. Run `sbs readme-check --json` to verify clean state
