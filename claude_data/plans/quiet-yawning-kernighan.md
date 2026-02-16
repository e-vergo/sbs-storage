# Plan: Register Dress + Runway as Buildable SBS Projects

## Context

Dress and Runway already have complete self-documentation infrastructure (311 and 304 `@[blueprint]` annotations, `blueprint.tex`, `runway.json`, Verso docs). What's missing is registration in the SLS build tools so `sls_build_project`, `sls_validate_project`, etc. recognize them.

## Changes

### File 1: `dev/mcp/sls-mcp/src/sls_mcp/sls_tools.py`

**10 project maps/descriptions need Dress + Runway entries.** All follow the same pattern:

Add to each `project_paths`/`project_map` dict:
```python
"Dress": SBS_ROOT / "toolchain" / "Dress",
"dress": SBS_ROOT / "toolchain" / "Dress",
"Runway": SBS_ROOT / "toolchain" / "Runway",
"runway": SBS_ROOT / "toolchain" / "Runway",
```

And update each Field description to include "Dress, Runway" in the list.

Affected functions (line numbers from exploration):
1. `sls_validate_project` -- L609 (description), L633-646 (project_map)
2. `sls_build_project` -- L736 (description), L752-758 (docstring), L761-777 (project_paths), L785 (error msg)
3. `sls_generate_graph` -- L885 (description), L904-920 (project_paths), L928 (error msg)
4. `sls_serve_project` -- L1051 (description), L1071-1087 (site_paths), L1096 (error msg), L1100-1116 (project_map)
5. `sls_last_screenshot` -- L1314 (description), L1337-1350 (project_map)
6. `sls_visual_history` -- L1411 (description), L1429-1442 (project_map)
7. `sls_search_entries` -- L1497 (description), L1524-1537 (project_map)
8. `sls_inspect_project` -- L1636 (description), L1660-1673 (project_map)

**Fix `sls_build_project` invocation (pre-existing bug):**
- L804: `cmd = ["python", str(scripts_dir / "build.py")]` -- `build.py` doesn't exist
- Change to: `cmd = ["lake", "build"]` (which is what actually works)
- This fixes all projects, not just Dress/Runway

### File 2: `dev/scripts/sls/cli.py`

**L460:** Add "Dress" and "Runway" to `choices=["SBSTest", "GCR", "PNT"]`

## Execution

**Wave 1:** Single `sbs-developer` agent -- all changes are in 2 files, mechanical but extensive.

**Wave 2:** Verify by building Dress via `lake build` in the project directory (already confirmed working from #342 build). Then test `sls_build_project("Dress")` and `sls_generate_graph("Dress")`.

## Verification

1. `sls_build_project("Dress")` returns success
2. `sls_generate_graph("Dress")` generates graph with ~311 nodes
3. `sls_build_project("Runway")` returns success (after Dress is pushed to git)
4. MCP server restarts cleanly with new tool descriptions
