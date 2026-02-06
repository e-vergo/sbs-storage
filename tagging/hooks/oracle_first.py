"""Oracle-first compliance hook -- detects sessions that bypass ask_oracle.

Produces tags:
- oracle-first:missed   -- Glob/Grep used for location queries without
                           preceding ask_oracle calls (search-before-oracle pattern)
- oracle-first:compliant -- ask_oracle was used and preceded search tool calls

The oracle-first mandate (CLAUDE.md) requires using ask_oracle as the
default starting point before Glob/Grep for orientation questions. This
hook instruments that mandate by checking tool call ordering.

All tags are session-scoped (constant across all entries in the same session).
"""

from __future__ import annotations

TAG_SCOPE = "session"

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sbs.archive.entry import ArchiveEntry
    from sbs.archive.session_data import SessionData


def check_oracle_first(
    entry: "ArchiveEntry", sessions: list["SessionData"]
) -> list[str]:
    """Check oracle-first compliance across sessions.

    Logic:
    - If no Glob/Grep calls exist, no compliance issue (not applicable).
    - If Glob/Grep calls exist but zero ask_oracle calls, tag as missed.
    - If ask_oracle calls exist AND the first ask_oracle call precedes the
      first Glob/Grep call, tag as compliant.
    - If ask_oracle calls exist but the first one is AFTER the first
      Glob/Grep call, tag as missed (search-before-oracle pattern).
    """
    if not sessions:
        return []

    # Collect timestamps of relevant tool calls across all sessions
    oracle_timestamps: list[str] = []
    search_timestamps: list[str] = []

    for session in sessions:
        for tc in session.tool_calls:
            if tc.tool_name == "ask_oracle":
                oracle_timestamps.append(tc.timestamp)
            elif tc.tool_name in ("Glob", "Grep"):
                search_timestamps.append(tc.timestamp)

    # No search tools used -- oracle-first is not applicable
    if not search_timestamps:
        return []

    # Search tools used but no oracle calls at all -- definite miss
    if not oracle_timestamps:
        return ["oracle-first:missed"]

    # Check temporal ordering: did the first oracle call precede the
    # first search call? Timestamps are ISO strings, so lexicographic
    # comparison works correctly.
    first_oracle = min(oracle_timestamps)
    first_search = min(search_timestamps)

    if first_oracle <= first_search:
        return ["oracle-first:compliant"]
    else:
        return ["oracle-first:missed"]
