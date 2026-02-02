# Task 4: Archive Audit & Claude Data Extraction Overhaul

## Summary

Two objectives to establish a rock-solid foundation for downstream tooling:

1. **Archive Audit** - Comprehensive validation that iCloud backup, metadata capture, and screenshot storage are working correctly
2. **Claude Data Overhaul** - Expand extraction to capture ALL rich data from JSONL files (thinking blocks, token usage, message threading, etc.)

**Meta-goal:** Build a dataset rich enough to support prompting analysis, session reconstruction, cost optimization, meta-learning, and future "strange loops."

---

## Current State Analysis

### What's Being Captured Now
- Session metadata: timestamps, message counts, tool calls (truncated)
- File operations: reads, writes, edits
- Plan files (copied wholesale)
- Tool call summaries (aggregated counts)

### What's Available but NOT Captured
| Data | Source | Value |
|------|--------|-------|
| Thinking blocks | `message.content[].thinking` | Reasoning traces for prompting analysis |
| Token usage | `message.usage.*` | Cost analysis, cache efficiency |
| Model version | `message.model`, thinking signature | Version tracking |
| Message threading | `parentUuid` chains | Conversation reconstruction |
| Stop reasons | `message.stop_reason` | Completion analysis |
| Session summary | `sessions-index.json` | Human-readable session purpose |
| First prompt | `sessions-index.json` | Initial intent/goal |
| Full tool inputs | Currently truncated to 200 chars | Pattern analysis |
| Tool results | `tool_result` content | Success/failure analysis |

### Archive System Status
- iCloud sync: **Working** (81 entries in `SBS_archive/entries/`)
- Screenshot storage: Needs validation
- Metadata: Needs completeness check
- Auto-tagging: Working (16 rules + 2 hooks)

---

## Design Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Store full tool inputs? | Yes, with separate `input_full` field | Keep truncated for quick scans, full for analysis |
| Extract thinking blocks? | Yes, with `thinking_blocks` list | Critical for prompting analysis |
| Store token usage? | Yes, per-message and aggregated | Enables cost optimization |
| Message threading? | Yes, `parent_uuid` field | Session reconstruction |
| Backwards compatibility? | Maintain existing fields | Don't break existing consumers |

---

## Execution Waves

### Wave 1: Audit (Single Agent)

**Objective:** Validate the archive system is production-ready.

**Checks:**
1. **iCloud Backup Validation**
   - Verify `SBS_archive/` directory exists and is writable
   - Check entry count matches local archive
   - Verify screenshot files exist for recent entries
   - Validate `archive_index.json` integrity

2. **Metadata Completeness**
   - Load recent entries, verify all expected fields populated
   - Check `global_state` transitions are valid
   - Verify `repo_commits` captured for build-triggered entries
   - Validate auto-tags applied correctly

3. **Screenshot Storage**
   - Verify `latest/` screenshots exist for each project
   - Check `archive/` has timestamped backups
   - Validate `capture.json` metadata files
   - Test screenshot file accessibility

4. **Report Generation**
   - Create audit report with pass/fail status
   - Identify any gaps or inconsistencies
   - Recommend fixes if issues found

**Validation:** Audit report shows all green or issues documented.

### Wave 2: Data Model Extension (Single Agent)

**Objective:** Extend `SessionData` and `ToolCall` to capture rich data.

**Changes to `session_data.py`:**

```python
@dataclass
class ToolCall:
    # Existing fields...
    tool_name: str
    timestamp: str
    duration_ms: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    input_summary: Optional[str] = None

    # NEW fields
    input_full: Optional[dict] = None      # Complete input (not truncated)
    result_content: Optional[str] = None   # Tool result content
    result_type: Optional[str] = None      # "text", "image", "error"
    tool_use_id: Optional[str] = None      # For linking to results

@dataclass
class ThinkingBlock:
    """Claude's reasoning trace."""
    content: str
    signature: Optional[str] = None        # Model version signature
    timestamp: Optional[str] = None

@dataclass
class MessageUsage:
    """Token usage for a message."""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0

@dataclass
class SessionData:
    # Existing fields...

    # NEW fields
    slug: Optional[str] = None             # Human-readable session name
    first_prompt: Optional[str] = None     # Initial user intent
    session_summary: Optional[str] = None  # From index
    model_versions: list[str] = field(default_factory=list)
    thinking_blocks: list[ThinkingBlock] = field(default_factory=list)
    message_usage: Optional[MessageUsage] = None  # Aggregated
    parent_uuid_chain: list[str] = field(default_factory=list)  # For reconstruction
    stop_reasons: list[str] = field(default_factory=list)
```

**Validation:** New dataclasses serialize/deserialize correctly.

### Wave 3: Extractor Enhancement (Single Agent)

**Objective:** Update `extractor.py` to capture all rich data.

**Changes:**

1. **Extract session index metadata:**
   - `first_prompt` from `firstPrompt`
   - `session_summary` from `summary`
   - `slug` from slug field

2. **Parse thinking blocks:**
   - Detect `type: "thinking"` in message content
   - Extract `thinking` text and `signature`
   - Aggregate model versions from signatures

3. **Capture token usage:**
   - Parse `message.usage` for each assistant message
   - Aggregate totals across session

4. **Track message threading:**
   - Capture `parentUuid` for conversation flow
   - Build chain for session reconstruction

5. **Enhanced tool call extraction:**
   - Store full input (new field)
   - Link tool_use to tool_result by ID
   - Capture actual success/error from result

6. **Stop reason tracking:**
   - Capture `stop_reason` and `stop_sequence`

**Validation:** Extract a session and verify all new fields populated.

### Wave 4: Storage & Snapshot Update (Single Agent)

**Objective:** Update `ClaudeDataSnapshot` and storage to include new data.

**Changes to `session_data.py`:**

```python
@dataclass
class ClaudeDataSnapshot:
    # Existing fields...
    session_ids: list[str]
    plan_files: list[str]
    tool_call_count: int
    message_count: int
    files_modified: list[str]
    extraction_timestamp: str

    # NEW fields
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    thinking_block_count: int = 0
    model_versions_used: list[str] = field(default_factory=list)
    unique_tools_used: list[str] = field(default_factory=list)
```

**Validation:** Archive upload includes new snapshot fields.

### Wave 5: Integration Testing (Orchestrator)

**Objective:** End-to-end validation of the enhanced system.

**Tests:**
1. Run `sbs archive upload` and verify new fields in entry
2. Check iCloud sync includes enhanced data
3. Verify session JSON files have all new fields
4. Run existing tests to ensure no regression
5. Validate tagging hooks still work with enhanced data

---

## Gates

```yaml
gates:
  tests: all_pass
  quality:
    T1: >= 1.0    # CLI commands work
    T2: >= 0.9    # Ledger population
  regression: >= 0
```

---

## Key Files

**Modified Files:**
- `dev/scripts/sbs/archive/session_data.py` - Add new dataclasses and fields
- `dev/scripts/sbs/archive/extractor.py` - Enhanced extraction logic
- `dev/scripts/sbs/archive/upload.py` - Use enhanced snapshot

**Reference Files:**
- `dev/scripts/sbs/archive/icloud_sync.py` - Understand sync flow
- `dev/scripts/sbs/archive/entry.py` - ArchiveEntry structure
- `~/.claude/projects/*/*.jsonl` - Source JSONL format

**Test Files:**
- `dev/scripts/sbs/tests/pytest/test_extractor.py` - New tests for enhanced extraction

---

## Verification

| Wave | Check | Method |
|------|-------|--------|
| 1 | iCloud backup working | Audit script checks |
| 1 | Metadata complete | Audit script checks |
| 1 | Screenshots stored | Audit script checks |
| 2 | Data model valid | Unit tests for new dataclasses |
| 3 | Extraction captures all | Parse test session, verify fields |
| 4 | Snapshot includes new data | Check archive entry after upload |
| 5 | No regression | `sbs_run_tests()` - all pass |
| 5 | iCloud sync works | Verify new data in iCloud |

---

## Success Criteria

1. Audit report shows archive system is production-ready
2. All JSONL data captured: thinking blocks, token usage, threading, full inputs
3. Backwards compatible - existing fields unchanged
4. All 340+ tests pass
5. Enhanced data visible in iCloud sync
6. Foundation ready for downstream tooling (prompting analysis, cost optimization, etc.)

---

## Data Flow After Enhancement

```
~/.claude/projects/{project}/
├── sessions-index.json          → slug, first_prompt, session_summary
└── {sessionId}.jsonl
    ├── message entries
    │   ├── thinking blocks      → ThinkingBlock list, model_versions
    │   ├── tool_use blocks      → ToolCall with input_full, tool_use_id
    │   ├── tool_result blocks   → ToolCall.result_content, result_type, success
    │   └── usage stats          → MessageUsage, token aggregation
    ├── parentUuid               → parent_uuid_chain
    └── stop_reason              → stop_reasons list

↓ (enhanced extraction)

SessionData
├── All existing fields preserved
├── thinking_blocks: [ThinkingBlock, ...]
├── model_versions: ["claude-opus-4-5-...", ...]
├── message_usage: MessageUsage(input=X, output=Y, cache=Z)
├── parent_uuid_chain: ["uuid1", "uuid2", ...]
└── stop_reasons: ["end_turn", ...]

↓ (upload)

ArchiveEntry.claude_data
├── All existing fields preserved
├── total_input_tokens, total_output_tokens
├── cache_read_tokens, cache_creation_tokens
├── thinking_block_count
└── model_versions_used
```
