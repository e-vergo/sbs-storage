# Plan: FLT Pipeline Test (Issue #354)

## Context

The Dress CLI `quickstart` and `auto-tag` subcommands were validated on TDCSG (335 nodes, 788 edges, zero errors). FLT (Fermat's Last Theorem) is a substantially larger project (~175 source files, ~2,046 declarations, mathlib dependency) that serves as a real-world stress test.

**Goal:** Run the full quickstart -> build -> auto-tag -> graph -> serve pipeline on FLT and verify it produces a working SBS site.

**User decisions:**
- Fork FLT to `e-vergo/FLT`, add as submodule
- Nuke `.lake/`, fresh dependency resolution
- Register FLT in `sls_tools.py`

---

## Phase 0: Porcelain + Fork Setup

**Agent 1** (sbs-developer): Commit stale submodule pointers + fork FLT

1. In SBS repo, commit stale submodule pointers for GCR, OSforGFF, SBS-Test
2. Fork `ImperialCollegeLondon/FLT` to `e-vergo/FLT` via `gh repo fork`
3. Remove the existing `showcase/FLT/` directory
4. Add `e-vergo/FLT` as a git submodule at `showcase/FLT`
5. Update FLT's git remote to point to the fork
6. Commit FLT submodule addition in SBS
7. Update SLS pointer to SBS, commit in SLS

**Agent 2** (sbs-developer, parallel): Register FLT in `sls_tools.py`

Add FLT to all 13 project maps in `sls_tools.py` (same pattern as TDCSG registration):
- `project_paths` maps (5 locations): `"FLT": SBS_ROOT / "showcase" / "FLT"`
- `project_map` normalization dicts (5 locations): `"flt": "FLT"`
- Error message strings (3 locations): add `FLT` to the valid project lists

**Files modified:**
- `Side-By-Side-Blueprint/.gitmodules`
- `dev/mcp/sls-mcp/src/sls_mcp/sls_tools.py`

---

## Phase 1: Dependency Injection + Quickstart

**Agent** (sbs-developer): Add Dress dependency and run quickstart

1. Delete `showcase/FLT/.lake/` entirely (fresh start)
2. Add Dress dependency to `FLT/lakefile.toml`:
   ```toml
   [[require]]
   name = "Dress"
   git = "https://github.com/e-vergo/Dress.git"
   rev = "main"
   ```
3. Run `lake update` in FLT to resolve all dependencies (test Dress + mathlib coexistence)
4. Run `lake exe cache get` to download pre-built mathlib oleans
5. Run `lake exe extract_blueprint quickstart --dry-run` to preview what would be created
6. Run `lake exe extract_blueprint quickstart` (no dry-run) to scaffold:
   - `runway.json` (with auto-detected GitHub URL, assetsDir from `findAssetsDir`)
   - `runway/src/blueprint.tex` (with auto-generated chapters from `scanChapters` -- expect ~18 chapters)
   - `import Dress` injected into ~170 source files
   - `.github/workflows/blueprint.yml` -- **will be skipped** (file exists). Manually create `sbs-blueprint.yml` as alternative.
7. Verify scaffolded files look correct

**Risk mitigation:** If `lake update` fails on dependency resolution, diagnose the conflict (likely batteries version). May need to pin Dress to a specific rev or adjust LeanArchitect's batteries requirement.

**Files modified:**
- `showcase/FLT/lakefile.toml`
- `showcase/FLT/lake-manifest.json` (auto-generated)
- `showcase/FLT/runway.json` (created)
- `showcase/FLT/runway/src/blueprint.tex` (created)
- `showcase/FLT/.github/workflows/sbs-blueprint.yml` (created manually since `blueprint.yml` exists)
- `showcase/FLT/FLT/**/*.lean` (~170 files get `import Dress`)

---

## Phase 2: Build

**Agent** (sbs-developer): Build FLT with Dress

1. Run `lake build` in FLT directory
   - This compiles FLT + Dress, producing `.olean` files and dressed artifacts
   - Expected to take 10-30 minutes depending on cache hit rate
   - Mathlib should come from cache (`lake exe cache get` in Phase 1)
   - FLT source files need compilation with `import Dress`
2. Verify build succeeds (zero errors)
3. Check `.lake/build/dressed/` directory exists with artifacts

**Risk:** Build may fail if `import Dress` causes conflicts with existing imports or if Dress's elaboration-time code interacts badly with mathlib's type universe. If build fails, diagnose per-file and potentially skip problematic files.

---

## Phase 3: Auto-Tag + Rebuild

**Agent** (sbs-developer): Run auto-tag and rebuild

1. Run `lake exe extract_blueprint auto-tag --dry-run FLT` to preview (~2,000 insertions expected)
2. Run `lake exe extract_blueprint auto-tag FLT` (real run)
3. Verify `@[blueprint]` attributes added to declarations
4. Run `lake build` again to compile with `@[blueprint]` attributes (generates dressed artifacts)
5. Check for any `@[blueprint]` parser conflicts (the three bug fixes from TDCSG session should handle them)

**Key metrics to capture:**
- Number of `@[blueprint]` attributes added
- Number of files modified
- Number of instances skipped
- Number of existing attribute blocks injected into (vs new lines)
- Build success (zero errors after auto-tag)

---

## Phase 4: Graph + Serve

**Agent** (sbs-developer): Generate graph and serve site

1. Run `lake exe extract_blueprint graph FLT` to generate `dep-graph.svg` and `dep-graph.json`
2. Run Runway site generation (via `sls_build_project` or manual Runway invocation)
3. Serve on localhost via `sls_serve_project FLT` (or manual `python3 -m http.server`)
4. Report node count, edge count, chapter count

**Key metrics:**
- Total nodes in dependency graph
- Total edges
- Number of chapters generated
- Site renders correctly

---

## Phase 5: Commit + Report

1. Commit all FLT changes inside the submodule (Dress dep, quickstart scaffold, auto-tag attributes)
2. Push FLT submodule to `e-vergo/FLT`
3. Update SBS pointer, commit + push SBS
4. Update SLS pointer, commit
5. Report results: comparison table with TDCSG baseline

| Metric | TDCSG | FLT |
|--------|-------|-----|
| Source files | ~50 | ~175 |
| Declarations tagged | 335 | ~2,000 |
| Chapters | 3 | ~18 |
| Graph nodes | 335 | TBD |
| Graph edges | 788 | TBD |
| Build errors | 0 | TBD |

---

## Critical Files

| File | Role |
|------|------|
| `showcase/FLT/lakefile.toml` | Add Dress dependency |
| `toolchain/Dress/Dress/Quickstart.lean` | Quickstart logic (being tested) |
| `toolchain/Dress/Dress/AutoTag.lean` | Auto-tag logic (stress test at 2K+ scale) |
| `toolchain/Dress/Main.lean` | CLI entry point |
| `dev/mcp/sls-mcp/src/sls_mcp/sls_tools.py` | FLT registration |

All SBS paths relative to `Side-By-Side-Blueprint/`.

---

## Verification

1. `lake update` succeeds (Dress + mathlib coexist)
2. Quickstart scaffolds correct files (runway.json, blueprint.tex with ~18 chapters, ~170 imports injected)
3. `lake build` succeeds (zero errors)
4. Auto-tag adds ~2,000 `@[blueprint]` attributes
5. Rebuild after auto-tag succeeds (zero errors)
6. Graph generates with expected node/edge count
7. Site serves and renders correctly at localhost
