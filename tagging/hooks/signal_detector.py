"""Signal detector hook -- identifies anomalies and red flags in sessions.

Produces tags in the ``signal:`` namespace:
- bash-error-rate-high: Elevated Bash error rate
- cli-misfire: CLI argument/option errors detected
- max-tokens-hit: Model hit max token limit
- user-correction: Entry notes suggest a correction/redo
- retry-loop: Same tool+file repeated 3+ times in sequence
- high-churn: Extremely long session suggesting churn
- context-compaction: Session continuation detected
- sync-error: Archive sync failed
- stale-metrics: Quality scores contain stale data
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sbs.archive.entry import ArchiveEntry
    from sbs.archive.session_data import SessionData


# Patterns that indicate non-actionable errors (carried over from cli_arg_misfires.py)
NON_ERROR_PATTERNS = [
    "user doesn't want",
    "sibling tool call errored",
    "nothing to commit",
    "already up to date",
    "already exists",
    "ignored by one of your .gitignore",
]

# CLI misfire indicators
CLI_MISFIRE_PATTERNS = [
    "unknown option",
    "invalid argument",
    "unrecognized",
    "no such",
]

# User correction keywords (checked against entry.notes)
CORRECTION_KEYWORDS = [
    "correction",
    "redo",
    "retry",
    "revert",
    "wrong",
    "mistake",
    "back to",
    "restart",
    "pivot",
    "scratch that",
]

# Context compaction indicators (checked against first_prompt)
COMPACTION_KEYWORDS = [
    "continue",
    "context",
    "pick up",
    "resume",
    "where we left",
]


def detect_signals(entry: "ArchiveEntry", sessions: list["SessionData"]) -> list[str]:
    """Detect anomalies and red flags, returning signal: tags."""
    if not sessions:
        return []

    tags: list[str] = []

    # ------------------------------------------------------------------
    # signal:bash-error-rate-high
    # ------------------------------------------------------------------
    bash_errors = 0
    bash_calls = 0
    has_cli_misfire = False

    for session in sessions:
        for tc in session.tool_calls:
            if tc.tool_name == "Bash":
                bash_calls += 1
                if tc.error:
                    error_lower = str(tc.error).lower()
                    if not any(p in error_lower for p in NON_ERROR_PATTERNS):
                        bash_errors += 1

                    # Check for CLI misfire patterns
                    if any(p in error_lower for p in CLI_MISFIRE_PATTERNS):
                        has_cli_misfire = True

    if bash_calls > 10 and bash_errors / bash_calls > 0.1:
        tags.append("signal:bash-error-rate-high")

    # ------------------------------------------------------------------
    # signal:cli-misfire
    # ------------------------------------------------------------------
    if has_cli_misfire:
        tags.append("signal:cli-misfire")

    # ------------------------------------------------------------------
    # signal:max-tokens-hit
    # ------------------------------------------------------------------
    for session in sessions:
        if "max_tokens" in session.stop_reasons:
            tags.append("signal:max-tokens-hit")
            break

    # ------------------------------------------------------------------
    # signal:user-correction
    # ------------------------------------------------------------------
    if entry.notes:
        notes_lower = entry.notes.lower()
        if any(kw in notes_lower for kw in CORRECTION_KEYWORDS):
            tags.append("signal:user-correction")

    # ------------------------------------------------------------------
    # signal:retry-loop
    # Detect same tool+file combination repeated 3+ times in sequence
    # ------------------------------------------------------------------
    for session in sessions:
        calls = session.tool_calls
        if len(calls) < 3:
            continue

        streak = 1
        for i in range(1, len(calls)):
            prev = calls[i - 1]
            curr = calls[i]

            # Build a signature from tool name + primary file argument
            prev_sig = _tool_file_sig(prev)
            curr_sig = _tool_file_sig(curr)

            if prev_sig and curr_sig and prev_sig == curr_sig:
                streak += 1
                if streak >= 3:
                    tags.append("signal:retry-loop")
                    break
            else:
                streak = 1

        if "signal:retry-loop" in tags:
            break

    # ------------------------------------------------------------------
    # signal:high-churn
    # Proxy: total message count > 500
    # ------------------------------------------------------------------
    total_msgs = sum(s.message_count for s in sessions)
    if total_msgs > 500:
        tags.append("signal:high-churn")

    # ------------------------------------------------------------------
    # signal:context-compaction
    # ------------------------------------------------------------------
    for session in sessions:
        if session.session_summary is not None:
            tags.append("signal:context-compaction")
            break
        if session.first_prompt:
            prompt_lower = session.first_prompt.lower()
            if any(kw in prompt_lower for kw in COMPACTION_KEYWORDS):
                tags.append("signal:context-compaction")
                break

    # ------------------------------------------------------------------
    # signal:sync-error
    # ------------------------------------------------------------------
    if entry.sync_error is not None:
        tags.append("signal:sync-error")

    # ------------------------------------------------------------------
    # signal:stale-metrics
    # ------------------------------------------------------------------
    if entry.quality_scores and isinstance(entry.quality_scores.get("scores"), dict):
        for _metric_id, score_data in entry.quality_scores["scores"].items():
            if isinstance(score_data, dict) and score_data.get("stale"):
                tags.append("signal:stale-metrics")
                break

    return tags


def _tool_file_sig(tc) -> str | None:
    """Extract a tool+file signature for retry-loop detection.

    Returns a string like "Edit:/path/to/file.py" or None if no file arg
    is present.
    """
    if not tc.input_full:
        # Fall back to input_summary if available
        if tc.input_summary and tc.tool_name in ("Edit", "Read", "Write"):
            return f"{tc.tool_name}:{tc.input_summary[:200]}"
        return None

    # Common file path parameter names
    for key in ("file_path", "path", "notebook_path"):
        val = tc.input_full.get(key)
        if val:
            return f"{tc.tool_name}:{val}"

    # Bash: use command as signature (first 200 chars)
    if tc.tool_name == "Bash":
        cmd = tc.input_full.get("command", "")
        return f"Bash:{cmd[:200]}" if cmd else None

    return None
