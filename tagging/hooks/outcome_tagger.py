"""Outcome tagger hook -- cross-references entry fields with session data.

Produces tags in the ``outcome:`` namespace for cases that require
combining entry-level metadata with session-level tool call analysis.

Declarative rules already handle:
- outcome:build-success / outcome:build-fail
- outcome:gate-pass / outcome:gate-fail

This hook adds:
- outcome:clean-execution -- zero tool failures, no signal-worthy anomalies
- outcome:had-retries -- same file edited 3+ times across sessions
- outcome:task-completed -- terminal state transition for a task
- outcome:task-incomplete -- mid-task entry (no terminal transition)
- outcome:pr-created -- PR references present
- outcome:quality-improved / quality-regressed / quality-stable
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sbs.archive.entry import ArchiveEntry
    from sbs.archive.session_data import SessionData

# Reuse signal detector constants to check "would any signal fire"
from .signal_detector import (
    NON_ERROR_PATTERNS,
    CLI_MISFIRE_PATTERNS,
    CORRECTION_KEYWORDS,
)


def tag_outcomes(entry: "ArchiveEntry", sessions: list["SessionData"]) -> list[str]:
    """Tag outcomes by cross-referencing entry and session data."""
    if not sessions:
        return []

    tags: list[str] = []

    # ------------------------------------------------------------------
    # Precompute: tool failures and signal indicators
    # ------------------------------------------------------------------
    total_failures = 0
    bash_errors = 0
    bash_calls = 0
    has_cli_misfire = False
    has_max_tokens = False
    has_high_churn = False
    total_msgs = 0

    for session in sessions:
        total_msgs += session.message_count
        if "max_tokens" in session.stop_reasons:
            has_max_tokens = True

        for tc in session.tool_calls:
            if not tc.success:
                total_failures += 1
            if tc.tool_name == "Bash" and tc.error:
                bash_calls += 1
                error_lower = str(tc.error).lower()
                if not any(p in error_lower for p in NON_ERROR_PATTERNS):
                    bash_errors += 1
                if any(p in error_lower for p in CLI_MISFIRE_PATTERNS):
                    has_cli_misfire = True

    if total_msgs > 500:
        has_high_churn = True

    has_user_correction = False
    if entry.notes:
        notes_lower = entry.notes.lower()
        has_user_correction = any(kw in notes_lower for kw in CORRECTION_KEYWORDS)

    has_sync_error = entry.sync_error is not None

    # ------------------------------------------------------------------
    # outcome:clean-execution
    # Zero tool failures AND no signal-worthy anomalies
    # ------------------------------------------------------------------
    signals_would_fire = (
        has_cli_misfire
        or has_max_tokens
        or has_user_correction
        or has_high_churn
        or has_sync_error
        or (bash_calls > 10 and bash_errors / bash_calls > 0.1)
    )

    if total_failures == 0 and not signals_would_fire:
        tags.append("outcome:clean-execution")

    # ------------------------------------------------------------------
    # outcome:had-retries
    # Same file edited 3+ times across all sessions
    # ------------------------------------------------------------------
    file_edit_counts: Counter[str] = Counter()
    for session in sessions:
        for f in session.files_edited:
            file_edit_counts[f] += 1

    if file_edit_counts and file_edit_counts.most_common(1)[0][1] >= 3:
        tags.append("outcome:had-retries")

    # ------------------------------------------------------------------
    # outcome:task-completed / outcome:task-incomplete
    # ------------------------------------------------------------------
    is_task = (
        entry.global_state
        and entry.global_state.get("skill") == "task"
    )

    if entry.state_transition in ("phase_end", "handoff"):
        tags.append("outcome:task-completed")
    elif is_task and entry.state_transition is None:
        tags.append("outcome:task-incomplete")

    # ------------------------------------------------------------------
    # outcome:pr-created
    # ------------------------------------------------------------------
    if entry.pr_refs:
        tags.append("outcome:pr-created")

    # ------------------------------------------------------------------
    # outcome:quality-improved / quality-regressed / quality-stable
    # ------------------------------------------------------------------
    if entry.quality_delta and isinstance(entry.quality_delta, dict):
        overall_delta = entry.quality_delta.get("overall", 0)
        if isinstance(overall_delta, (int, float)):
            if overall_delta > 0.05:
                tags.append("outcome:quality-improved")
            elif overall_delta < -0.05:
                tags.append("outcome:quality-regressed")
            else:
                tags.append("outcome:quality-stable")

    return tags
