"""Session profiler hook -- analyzes session data across 5 dimensions.

Produces tags in these namespaces:
- session:  behavioral profile (exploration-heavy, edit-heavy, etc.)
- token:    token usage patterns
- thinking: reasoning trace characteristics
- tool:     tool usage patterns and dominant tools
- model:    model version information
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sbs.archive.entry import ArchiveEntry
    from sbs.archive.session_data import SessionData


def profile_session(entry: "ArchiveEntry", sessions: list["SessionData"]) -> list[str]:
    """Analyze sessions and return dimension tags."""
    if not sessions:
        return []

    tags: list[str] = []

    # ------------------------------------------------------------------
    # Aggregate counts across all sessions
    # ------------------------------------------------------------------
    total_reads = 0
    total_edits = 0
    total_writes = 0
    total_tool_calls = 0
    total_msgs = 0
    total_user_msgs = 0
    bash_calls = 0
    mcp_calls = 0
    glob_calls = 0
    grep_calls = 0
    task_calls = 0
    tool_counter: Counter[str] = Counter()
    tool_failures = 0
    has_slow_op = False
    unique_tools: set[str] = set()

    # Token aggregates
    total_input = 0
    total_output = 0
    cache_read = 0

    # Thinking aggregates
    thinking_count = 0
    thinking_lengths: list[int] = []

    # Model versions
    model_versions: set[str] = set()

    for session in sessions:
        total_reads += len(session.files_read)
        total_edits += len(session.files_edited)
        total_writes += len(session.files_written)
        total_msgs += session.message_count
        total_user_msgs += session.user_messages

        for tc in session.tool_calls:
            total_tool_calls += 1
            tool_counter[tc.tool_name] += 1
            unique_tools.add(tc.tool_name)

            if tc.tool_name == "Bash":
                bash_calls += 1
            elif tc.tool_name.startswith("mcp__") or tc.tool_name.startswith("sbs_"):
                mcp_calls += 1
            elif tc.tool_name == "Glob":
                glob_calls += 1
            elif tc.tool_name == "Grep":
                grep_calls += 1
            elif tc.tool_name == "Task":
                task_calls += 1

            if not tc.success:
                tool_failures += 1

            if tc.duration_ms is not None and tc.duration_ms > 5000:
                has_slow_op = True

        # Token data from session
        if session.message_usage:
            total_input += session.message_usage.input_tokens
            total_output += session.message_usage.output_tokens
            cache_read += session.message_usage.cache_read_input_tokens

        # Thinking blocks
        for tb in session.thinking_blocks:
            thinking_count += 1
            thinking_lengths.append(len(tb.content))

        # Model versions
        for mv in session.model_versions:
            model_versions.add(mv)

    total_file_ops = total_reads + total_edits + total_writes
    unique_tools_count = len(unique_tools)

    # Fallback: use entry.claude_data for token data if sessions lack it
    if total_input == 0 and total_output == 0:
        claude_data = entry.claude_data or entry.load_claude_data()
        if claude_data:
            total_input = claude_data.get("total_input_tokens", 0)
            total_output = claude_data.get("total_output_tokens", 0)
            cache_read = claude_data.get("cache_read_tokens", 0)
            if not model_versions:
                for mv in claude_data.get("model_versions_used", []):
                    model_versions.add(mv)
            if thinking_count == 0:
                thinking_count = claude_data.get("thinking_block_count", 0)

    # ------------------------------------------------------------------
    # session: tags
    # ------------------------------------------------------------------
    # Session-type tags: mutually exclusive (emit only the dominant one)
    if total_file_ops > 0:
        session_type_candidates: list[tuple[float, str]] = [
            (total_reads / total_file_ops, "session:exploration-heavy"),
            (total_edits / total_file_ops, "session:edit-heavy"),
            (total_writes / total_file_ops, "session:creation-heavy"),
        ]
        best_ratio, best_tag = max(session_type_candidates, key=lambda x: x[0])
        if best_ratio > 0.4:
            tags.append(best_tag)

    # Tool-dominance tags: mutually exclusive (emit only the dominant one)
    if total_tool_calls > 0:
        tool_dom_candidates: list[tuple[float, str]] = [
            (bash_calls / total_tool_calls, "session:bash-heavy"),
            (mcp_calls / total_tool_calls, "session:mcp-heavy"),
            ((glob_calls + grep_calls) / total_tool_calls, "session:search-heavy"),
            (task_calls / total_tool_calls, "session:delegation-heavy"),
        ]
        best_ratio, best_tag = max(tool_dom_candidates, key=lambda x: x[0])
        if best_ratio > 0.3:
            tags.append(best_tag)

    if total_msgs > 0:
        user_ratio = total_user_msgs / max(total_msgs, 1)
        if 0.3 <= user_ratio <= 0.7:
            tags.append("session:interactive")

    if total_user_msgs <= 2:
        tags.append("session:one-shot")

    if len(sessions) > 1:
        tags.append("session:multi-session")

    if total_msgs > 200:
        tags.append("session:long")

    if total_msgs < 20:
        tags.append("session:short")

    if unique_tools_count > 15:
        tags.append("session:tool-diverse")

    if unique_tools_count < 5:
        tags.append("session:tool-narrow")

    # ------------------------------------------------------------------
    # token: tags
    # ------------------------------------------------------------------
    if total_input > 100_000:
        tags.append("token:input-heavy")

    if total_output > 100_000:
        tags.append("token:output-heavy")

    total_tokens = total_input + total_output

    if cache_read > 0 and (cache_read / (cache_read + total_input)) > 0.2:
        tags.append("token:cache-efficient")

    if cache_read == 0 and total_input > 10_000:
        tags.append("token:cache-unused")

    if total_tokens > 200_000:
        tags.append("token:total-heavy")

    if total_tokens < 20_000:
        tags.append("token:total-light")

    if total_tool_calls > 0 and total_tokens / total_tool_calls < 500:
        tags.append("token:efficient")

    # ------------------------------------------------------------------
    # thinking: tags
    # ------------------------------------------------------------------
    if thinking_count > 10:
        tags.append("thinking:heavy")

    if thinking_count == 0:
        tags.append("thinking:none")

    if thinking_lengths and max(thinking_lengths) > 2000:
        tags.append("thinking:extended")

    if thinking_lengths and (sum(thinking_lengths) / len(thinking_lengths)) > 1000:
        tags.append("thinking:deep")

    # ------------------------------------------------------------------
    # tool: tags
    # ------------------------------------------------------------------
    if tool_counter:
        top_tool = tool_counter.most_common(1)[0][0]
        tool_dominant_map = {
            "Read": "tool:read-dominant",
            "Edit": "tool:edit-dominant",
            "Bash": "tool:bash-dominant",
            "Task": "tool:task-dominant",
        }
        if top_tool in tool_dominant_map:
            tags.append(tool_dominant_map[top_tool])

    if total_tool_calls > 0 and tool_failures / total_tool_calls > 0.15:
        tags.append("tool:failure-rate-high")

    if total_tool_calls > 0 and tool_failures == 0:
        tags.append("tool:failure-rate-zero")

    if has_slow_op:
        tags.append("tool:slow-operations")

    # ------------------------------------------------------------------
    # model: tags
    # ------------------------------------------------------------------
    for mv in model_versions:
        mv_lower = mv.lower()
        if "opus" in mv_lower:
            tags.append("model:opus")
        if "sonnet" in mv_lower:
            tags.append("model:sonnet")
        if "haiku" in mv_lower:
            tags.append("model:haiku")

    if len(model_versions) > 1:
        tags.append("model:multi-model")
    elif len(model_versions) == 1:
        tags.append("model:single-model")

    # Deduplicate (model tags could fire multiple times from different versions)
    seen: set[str] = set()
    unique: list[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            unique.append(t)

    return unique
