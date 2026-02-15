# SLS Infrastructure Crush Session

## Context

The L0/L1/L2 introspection cascade (Feb 15) revealed that 16 of 17 introspection-generated issues were closed without code fixes. This crush session addresses the highest-impact SLS infrastructure issues: 3 code fixes + 4 behavioral documentation fixes.

## Issues

| # | Title | Type | Wave |
|---|-------|------|------|
| #344 | Recursive `sls_task` reentry corrupts global_state | Code fix | 1 |
| #285 | Oracle-first protocol systematically violated | Behavioral | 1 |
| #343 | Orchestrator role confusion (skill state management) | Behavioral | 2 |
| #346 | Orchestrator loses handoff fidelity | Behavioral | 2 |
| #287 | Tagger session-level granularity | Code fix | 3 |
| #347 | Cross-task signal tag leakage | Code fix | 3 |
| #289 | update-and-archive deprecation ambiguity | Close as not-a-bug | 4 |

## Pre-Execution

1. Reopen closed-but-unresolved issues: #344, #285, #287, #347, #343, #346
2. Close #289 with explanation (all documentation treats `sls_update_and_archive` as active; the improvement capture was premature)

## Wave 1: Reentry Guard + Oracle Enforcement (2 agents, parallel)

**Agent 1A — #344: Skill Reentry Guard** (`skill_tools.py`)

File: `dev/mcp/sls-mcp/src/sls_mcp/skill_tools.py`

The bug: `if current_skill and current_skill != "task":` allows reentry when `current_skill == "task"`. Same bug in 3 other skills.

Fix all 4 start-phase guards to `if current_skill:` (block start when ANY skill is active):
- Line 944 (`sls_task`)
- Line 1430 (`sls_qa`)
- Line 1856 (`sls_introspect`)
- Line 2395 (`sls_converge`)

Reference: `sls_update_and_archive` (line 2908) already uses the correct pattern.

Also update the error messages to be informative: `f"Cannot start {skill}: skill '{current_skill}' is already active (use sls_skill_status to check)"`.

**Agent 1B — #285: Oracle-First Enforcement** (`CLAUDE.md`)

Replace the "Oracle-First Approach" section (lines ~790-798). Current weak language ("should be the go-to") becomes mandatory language matching `sbs-developer.md`:

> **Oracle-first is mandatory.** Before searching for file locations, architecture, or codebase relationships, call `ask_oracle`. Sessions that use Glob/Grep before `ask_oracle` for orientation questions are tagged `oracle-first:missed`.

Keep the existing bullet list and configurable arguments table unchanged.

## Wave 2: Skill State + Handoff Protocol (1 agent)

**Agent 2A — #343 + #346: CLAUDE.md Behavioral Updates**

Single agent handles both since they target the same file.

**#343 fix:** Insert "Skill State Management" subsection after the Orchestration Model table (after line ~29):
- MCP workflow tools manage state transitions internally
- Orchestrator invokes workflow tools with `phase` arg, does NOT call `sls_skill_start`/`sls_skill_transition` directly
- Agents are unaware of skill state; they execute and report

**#346 fix:** Expand "Spawning Protocol" (lines ~300-306) to add "Agent Output Handoff Protocol":
- Three fidelity levels: pass-through, summarize, escalate
- Orchestrator must not silently swallow agent failures
- When spawning a downstream agent that needs prior agent's findings, pass raw output or agent ID for resumption — not a hand-summarized version

## Wave 3: Tagger Session Scoping (1 agent)

**Agent 3A — #287 + #347: Session Boundary Filtering**

Files:
- `dev/scripts/sls/archive/upload.py` — Add session filtering before tagger invocation
- `dev/scripts/sls/archive/tagger.py` — Understand flow (may need minor changes)

**Design:** Filter sessions at the caller site (`upload.py`) before passing to `tagger.evaluate()`. No hook signature changes needed.

Before `tagger.evaluate(entry, context, sessions)` is called (~line 578), add:
```python
skill_sessions = _filter_sessions_to_skill_boundary(sessions, entry)
auto_tags = tagger.evaluate(entry, context, skill_sessions)
```

The filter function uses `entry.global_state` to determine the current skill and its start time, then filters `SessionData` objects to only include tool calls after the skill boundary.

**Note:** This is a ~30-line change, not a 3-line fix. Medium effort but architecturally clean — hooks remain unchanged.

## Wave 4: Verification + Close-Out (1 agent)

**Agent 4A:**
1. Run `pytest sbs/tests/pytest -m evergreen --tb=short`
2. Grep `skill_tools.py` for `current_skill != "` — only `update-and-archive` comparison should remain
3. Grep `CLAUDE.md` for: "mandatory" near "oracle", "Skill State Management", "Handoff Protocol"
4. Comment on each issue with the commit SHA
5. Close #289 as not-a-bug

## Verification Summary

| Fix | How to Verify |
|-----|--------------|
| #344 reentry guard | Grep for old pattern; only u&a comparison remains |
| #285 oracle-first | CLAUDE.md contains "mandatory" near oracle section |
| #343 skill state | CLAUDE.md contains "Skill State Management" heading |
| #346 handoff | CLAUDE.md contains "Handoff Protocol" heading |
| #287/#347 tagger | Evergreen tests pass; manual entry inspection |

## Total: 5 agents across 4 sequential waves
