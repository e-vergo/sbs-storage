"""
Detect CLI tool argument misfires.

This hook analyzes tool calls for patterns indicating incorrect CLI usage:
- Repeated Bash calls with similar commands but varying args
- Error outputs containing "unknown option" or "invalid argument"
- High retry count on same tool

This is a stub - full implementation is future work.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sbs.archive.entry import ArchiveEntry
    from sbs.archive.session_data import SessionData


# Patterns that indicate non-actionable errors (user rejections, expected states)
NON_ERROR_PATTERNS = [
    "user doesn't want",
    "sibling tool call errored",
    "nothing to commit",
    "already up to date",
    "already exists",
    "ignored by one of your .gitignore",
]


def detect_misfires(entry: "ArchiveEntry", sessions: list["SessionData"]) -> list[str]:
    """
    Analyze sessions for CLI argument misfire patterns.

    Returns tags like:
    - "cli-misfire-detected" - When misfire pattern found
    - "bash-retry-pattern" - When repeated Bash calls suggest issues

    This is a stub implementation. Full analysis is future work.
    """
    tags = []

    # Count total Bash calls and errors
    bash_errors = 0
    bash_calls = 0

    for session in sessions:
        for tc in session.tool_calls:
            if tc.tool_name == "Bash":
                bash_calls += 1
                if tc.error:
                    # Filter non-actionable errors
                    error_text = str(tc.error).lower()
                    if not any(p in error_text for p in NON_ERROR_PATTERNS):
                        bash_errors += 1

    # Simple heuristic: if >10% of Bash calls have errors, flag it
    if bash_calls > 10 and bash_errors / bash_calls > 0.1:
        tags.append("bash-error-rate-high")

    return tags
