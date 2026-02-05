# SBS Rewrite Wave 1-2 Execution Plan

## Overview

Execute issues #225-229 (Waves 1-2 of #224) via sequential agent orchestration, then validate with a testing agent.

## Execution Model

**Orchestrator** (top-level chat): Spawns one `sbs-developer` agent per issue, waits for completion, then spawns next.

**Each agent**: Implements its issue, may spawn parallel subagents for non-overlapping work.

**Final agent**: Runs comprehensive testing to validate build time improvements.

---

## Agent 1: Manifest Hash Cache (#225)

**Scope**: `dev/scripts/sbs/build/caching.py` + `orchestrator.py`

**Implementation**:
1. Add `get_manifest_hash(manifest_path)` → SHA256 of manifest.json content
2. Add `get_graph_cache_path(cache_dir, manifest_hash)` → `.graph_cache/{hash}.json`
3. In `orchestrator.py`:
   - Before `generate_dep_graph()`: check cache hit
   - If hit: copy cached files, skip generation
   - If miss: run normally, save to cache

**Cache Location**: `.lake/build/dressed/.graph_cache/{manifest_hash}.{json,svg}`

**Files Modified**:
- `dev/scripts/sbs/build/caching.py` (add functions)
- `dev/scripts/sbs/build/orchestrator.py` (integrate cache check)

---

## Agent 2: Asset Pipeline Optimization (#226)

**Scope**: `dev/scripts/sbs/build/caching.py` + `orchestrator.py`

**Implementation**:
1. Add `get_asset_hashes(assets_dir)` → dict of filename → SHA256
2. Add `load_asset_hash_cache(cache_path)` / `save_asset_hash_cache()`
3. In asset copy phase:
   - Compare current hashes vs cached
   - Skip unchanged files
   - Update cache after copy

**Cache Location**: `{cache_dir}/{project}/asset_hashes.json`

**Files Modified**:
- `dev/scripts/sbs/build/caching.py` (add asset hash functions)
- `dev/scripts/sbs/build/orchestrator.py` (integrate into asset copy)

---

## Agent 3: Unified Configuration (#227)

**Scope**: `toolchain/Runway/Runway/Config.lean` + `dev/scripts/sbs/build/config.py`

**Implementation**:
1. Extend `Config` struct with optional fields:
   ```lean
   workflow : Option String := none  -- "lean-first" | "paper-first" | "hybrid"
   statementSource : Option String := none  -- "delimiters" | "attribute" | "both"
   validation : Option ValidationConfig := none
   ```
2. Add `ValidationConfig` structure:
   ```lean
   structure ValidationConfig where
     statementMatch : Bool := true
     dependencyCheck : Bool := true
     paperCompleteness : Bool := true
   ```
3. Update FromJson/ToJson instances
4. Python config.py: Parse and expose new fields

**Files Modified**:
- `toolchain/Runway/Runway/Config.lean` (extend schema)
- `dev/scripts/sbs/build/config.py` (parse new fields)

---

## Agent 4: Per-Declaration Content Cache (#228)

**Scope**: `toolchain/Dress/` (Lean) + `dev/scripts/sbs/build/caching.py` (Python)

**This is the most complex task - agent may spawn subagents for Lean vs Python work.**

**Implementation**:

**Lean side** (`toolchain/Dress/Dress/Cache.lean` - new file):
1. `computeDeclarationHash(name, node, subversoVersion)` → content hash
2. `getCachePath(hash)` → cache directory path
3. `checkCache(hash)` → returns cached artifacts if valid
4. `writeToCache(hash, artifacts)` → persist artifacts

**Lean side** (`Dress/Generate/Declaration.lean` - modify):
1. Before generation: compute hash, check cache
2. If hit: copy from cache, skip generation
3. If miss: generate normally, save to cache

**Cache structure**:
```
.lake/build/dressed/.decl_cache/
├── index.json              # label -> hash mapping
└── {content_hash}/
    ├── decl.json
    ├── decl.tex
    ├── decl.html
    └── decl.hovers.json
```

**Files Modified**:
- `toolchain/Dress/Dress/Cache.lean` (new)
- `toolchain/Dress/Dress/Generate/Declaration.lean` (integrate cache)
- `toolchain/Dress/Dress.lean` (import Cache)

---

## Agent 5: JSON Schema Stabilization (#229)

**Scope**: `dev/schemas/` (new directory)

**Implementation**:
1. Create JSON Schema files based on exploration findings:
   - `manifest.schema.json` - stats, nodes, messages, projectNotes, keyDeclarations, checks
   - `dep-graph.schema.json` - width, height, nodes[], edges[]
   - `declaration.schema.json` - name, label, highlighting
   - `hovers.schema.json` - hovers map

2. Add optional schema validation to build.py:
   ```python
   def validate_artifact(artifact_path, schema_name):
       # Optional: validate JSON against schema
   ```

3. Document schemas in `dev/schemas/README.md`

**Files Created**:
- `dev/schemas/manifest.schema.json`
- `dev/schemas/dep-graph.schema.json`
- `dev/schemas/declaration.schema.json`
- `dev/schemas/hovers.schema.json`
- `dev/schemas/README.md`

---

## Agent 6: Validation & Testing

**Scope**: Validate all changes work together

**Testing Protocol**:
1. Run evergreen tests: `pytest sbs/tests/pytest -m evergreen`
2. Build SBS-Test: `./dev/build-sbs-test.sh`
3. Measure build times:
   - Full build (clean)
   - Incremental build (no changes)
   - CSS-only change
   - Graph-only change (should be near-instant with cache hit)
4. Validate site generation works
5. Run `sbs compliance --project SBSTest`

**Success Criteria**:
| Scenario | Before | Target |
|----------|--------|--------|
| Full rebuild | 5-7s | 3-4s |
| Incremental (no changes) | 3-4s | 0.5-1s |
| CSS-only | 1-2s | 0.3s |
| Graph cache hit | 2-3s | 0.1s |

---

## Execution Order

```
Orchestrator
    │
    ├── Agent 1: #225 Manifest Hash Cache
    │   └── (single agent, Python only)
    │
    ├── Agent 2: #226 Asset Pipeline
    │   └── (single agent, Python only)
    │
    ├── Agent 3: #227 Unified Config
    │   └── (may spawn: Lean subagent + Python subagent)
    │
    ├── Agent 4: #228 Per-Declaration Cache
    │   └── (will spawn: Lean subagent + Python subagent)
    │
    ├── Agent 5: #229 JSON Schemas
    │   └── (single agent, schema files only)
    │
    └── Agent 6: Testing & Validation
        └── (single agent, runs tests + benchmarks)
```

---

## Critical Files Summary

**Python Build Layer** (`dev/scripts/sbs/build/`):
- `caching.py` - Core caching logic (Agents 1, 2)
- `orchestrator.py` - Build flow (Agents 1, 2)
- `config.py` - Configuration parsing (Agent 3)

**Lean Layer**:
- `toolchain/Runway/Runway/Config.lean` - Config schema (Agent 3)
- `toolchain/Dress/Dress/Cache.lean` - New cache module (Agent 4)
- `toolchain/Dress/Dress/Generate/Declaration.lean` - Declaration gen (Agent 4)

**New Files**:
- `dev/schemas/*.schema.json` - JSON schemas (Agent 5)

---

## Verification

After all agents complete:
1. All pytest tests pass
2. SBS-Test builds successfully
3. Build times meet targets
4. Compliance check passes
5. No regressions in visual output
