# Subgraph Generation Performance Optimization

## Context

Graph generation for OSforGFF (752 nodes) takes far too long because Phase 2 runs full Sugiyama layout independently for each unique subgraph. The main graph layout already has all node positions, edge bezier paths, and dimensions — subgraphs should extract from that, not recompute from scratch.

**Current bottleneck:** Phase 2 calls `Graph.Layout.layout sg cfg` per unique subgraph. Sugiyama includes: layer assignment, crossing reduction (4 barycenter iterations), coordinate refinement (12+ iterations), and edge routing (visibility graph + Dijkstra for small graphs, bezier for large). For hundreds of unique subgraphs, this is O(hundreds * Sugiyama).

**Target:** Phase 2 becomes O(n) filtering + arithmetic per subgraph. Total graph generation for OSforGFF should complete in seconds, not hours.

---

## Implementation

### 1. Add `LayoutGraph.extractSubgraph` to Layout.lean

**File:** `Side-By-Side-Blueprint/toolchain/Dress/Dress/Graph/Layout.lean` (after `LayoutGraph` definition, ~line 80)

```lean
/-- Extract a subgraph from a laid-out graph by filtering to the given node IDs.
    Re-centers coordinates so the subgraph content starts at (padding, padding).
    This avoids re-running Sugiyama layout — positions are inherited from the
    main graph. -/
def LayoutGraph.extractSubgraph (lg : LayoutGraph) (nodeIds : Std.HashSet String)
    (config : LayoutConfig := {}) : LayoutGraph := Id.run do
  let subNodes := lg.nodes.filter (fun ln => nodeIds.contains ln.node.id)
  let subEdges := lg.edges.filter (fun le => nodeIds.contains le.from_ && nodeIds.contains le.to)
  if subNodes.isEmpty then
    return { nodes := #[], edges := #[], width := 0, height := 0 }
  -- Compute bounding box of filtered nodes
  let mut minX := subNodes[0]!.x
  let mut minY := subNodes[0]!.y
  let mut maxX := subNodes[0]!.x + subNodes[0]!.width
  let mut maxY := subNodes[0]!.y + subNodes[0]!.height
  for n in subNodes do
    if n.x < minX then minX := n.x
    if n.y < minY then minY := n.y
    if n.x + n.width > maxX then maxX := n.x + n.width
    if n.y + n.height > maxY then maxY := n.y + n.height
  -- Re-center: shift so content starts at (padding, padding)
  let offsetX := minX - config.padding
  let offsetY := minY - config.padding
  let shiftedNodes := subNodes.map fun n =>
    { n with x := n.x - offsetX, y := n.y - offsetY }
  let shiftedEdges := subEdges.map fun e =>
    { e with points := e.points.map fun (px, py) => (px - offsetX, py - offsetY) }
  let width := maxX - minX + 2 * config.padding
  let height := maxY - minY + 2 * config.padding
  { nodes := shiftedNodes, edges := shiftedEdges, width, height, minX := 0, minY := 0 }
```

### 2. Modify Phase 1 in Main.lean — collect node ID sets, not Graphs

**File:** `Side-By-Side-Blueprint/toolchain/Dress/Main.lean` (lines 240-267)

Change the data collected in Phase 1:
- `uniqueSubgraphs : Std.HashMap UInt64 Graph.Graph` → `uniqueSubgraphs : Std.HashMap UInt64 (Std.HashSet String)`
- Instead of storing the full `Graph`, store just the `HashSet` of node IDs
- The BFS extraction (`extractSubgraphsIncremental`) still runs to determine which nodes belong to each subgraph, but we only keep the ID sets

```lean
-- Phase 1: Collect all work items via BFS + hashing (fast, single-threaded)
let mut workItems : Array (System.FilePath × String × UInt64) := #[]
let mut uniqueNodeSets : Std.HashMap UInt64 (Std.HashSet String) := {}
for node in reducedGraph.nodes do
  let sanitizedId := Paths.sanitizeLabel node.id
  let nodeDir := subgraphsDir / sanitizedId
  for direction in Graph.SubgraphDirection.all do
    let dirKey := direction.toString
    let maxDepth := ...  -- same as before
    let subgraphs := Graph.extractSubgraphsIncremental reducedGraph adj node.id maxDepth direction
    for (depth, subgraph) in subgraphs do
      if !subgraph.nodes.isEmpty then
        let sortedIds := subgraph.nodes.map (·.id) |>.qsort (· < ·)
        let nodeHash := hash sortedIds
        let filename := s!"{dirKey}-{depth}.svg"
        workItems := workItems.push (nodeDir, filename, nodeHash)
        if !uniqueNodeSets.contains nodeHash then
          let idSet := subgraph.nodes.foldl (init := ({} : Std.HashSet String)) fun acc n => acc.insert n.id
          uniqueNodeSets := uniqueNodeSets.insert nodeHash idSet
```

### 3. Modify Phase 2 in Main.lean — extract from main layout instead of recomputing

**File:** `Side-By-Side-Blueprint/toolchain/Dress/Main.lean` (lines 269-283)

Replace the parallel `Graph.Layout.layout` calls with `LayoutGraph.extractSubgraph`:

```lean
-- Phase 2: Extract subgraph layouts from main graph (no Sugiyama recomputation)
let p2Start ← IO.monoNanosNow
IO.eprintln s!"  Phase 2: Extracting {uniqueNodeSets.size} subgraph layouts from main graph..."
let mut layoutCache : Std.HashMap UInt64 Graph.Layout.LayoutGraph := {}
for (nodeHash, nodeIds) in uniqueNodeSets do
  let subLayout := layoutGraph.extractSubgraph nodeIds layoutConfig
  layoutCache := layoutCache.insert nodeHash subLayout
let p2End ← IO.monoNanosNow
IO.eprintln s!"  Phase 2: All extractions complete ({(p2End - p2Start) / 1000000}ms)"
```

Phase 2 becomes single-threaded since each extraction is O(|V| + |E|) filtering — no need for dedicated threads. The entire phase should complete in milliseconds.

### 4. Add cross-run hash-based caching

**File:** `Side-By-Side-Blueprint/toolchain/Dress/Main.lean`

Add caching that skips unchanged subgraphs between runs:

**Before subgraph generation (after main graph outputs):**
```lean
-- Load previous cache manifest if it exists
let cacheManifestPath := subgraphsDir / "cache-manifest.json"
let previousHashes : Std.HashMap String UInt64 := loadCacheManifest cacheManifestPath
```

**In Phase 3, skip writing if hash matches:**
```lean
for (nodeDir, filename, nodeHash) in workItems do
  let path := nodeDir / filename
  let pathStr := path.toString
  -- Skip if hash matches previous run
  if previousHashes.get? pathStr == some nodeHash then
    skippedCount := skippedCount + 1
    continue
  -- Otherwise render and write
  ...
```

**After Phase 3:**
```lean
-- Write updated cache manifest
let mut newHashes : Std.HashMap String UInt64 := {}
for (nodeDir, filename, nodeHash) in workItems do
  newHashes := newHashes.insert (nodeDir / filename).toString nodeHash
writeCacheManifest cacheManifestPath newHashes
```

**Also: Don't clean the subgraphs directory.** Remove the lines 221-236 that delete all existing subgraph files. Instead, let cached files persist. Only delete files whose node no longer exists (stale cleanup based on which sanitizedIds are in the current graph).

Helper functions needed (add to Main.lean or a new `Cache.lean`):
- `loadCacheManifest : System.FilePath → IO (Std.HashMap String UInt64)` — parse JSON
- `writeCacheManifest : System.FilePath → Std.HashMap String UInt64 → IO Unit` — write JSON

---

## Files Modified

| File | Change |
|------|--------|
| `Dress/Dress/Graph/Layout.lean` | Add `LayoutGraph.extractSubgraph` (~25 lines) |
| `Dress/Main.lean` | Rewrite Phase 1 (collect ID sets), Phase 2 (extract from main layout), add cache manifest logic, telemetry |

## Execution Order

### Wave 0: Baseline Benchmarks (before any changes)

Timing telemetry already exists in Main.lean (`IO.monoNanosNow`). Capture baseline numbers on current code:

1. **SBS-Test** (25 nodes): `lake exe extract_blueprint graph SBSTest` — record Phase 1/2/3 times and total
2. **GCR** (128 nodes): `lake exe extract_blueprint graph GCR.Basic GCR.Goldbach ...` — record same

These baselines establish the "before" for comparison.

### Wave 1: Implement optimization (steps 1-3 above)

1. Add `LayoutGraph.extractSubgraph` to Layout.lean
2. Modify Phase 1 + Phase 2 in Main.lean
3. `lake build` Dress

### Wave 2: After-benchmarks on SBS-Test and GCR

1. **SBS-Test**: Run again, compare Phase 2 time against baseline
2. **GCR**: Run again, compare Phase 2 time against baseline
3. Verify SVG output is correct (spot-check a few subgraph SVGs)
4. Verify total subgraph count matches baseline

### Wave 3: Cross-run caching (step 4 above)

1. Add cache manifest logic to Main.lean
2. Remove directory cleaning, add stale file cleanup
3. `lake build` Dress

### Wave 4: Cache verification on SBS-Test and GCR

1. Run SBS-Test twice — second run should show skipped files
2. Run GCR twice — second run should show skipped files
3. Record telemetry for cached vs uncached runs

### Wave 5: OSforGFF

1. Copy updated binary to OSforGFF's `.lake/packages/Dress/`
2. Run `lake exe extract_blueprint graph` with all 46 modules
3. Record full telemetry — this is the real payoff

## Telemetry Output Format

The existing `[timing]` lines cover the main graph phases. Add to subgraph phases:

```
[timing] Phase 1 (BFS + hash): Xms (N work items, M unique)
[timing] Phase 2 (subgraph extraction): Xms
[timing] Phase 3 (render + write): Xms (N written, M cached-skipped)
[timing] Total subgraph generation: Xms
```

## Performance Expectations

| Phase | Before | After |
|-------|--------|-------|
| Phase 1 (BFS + hash) | ~same | ~same (stores `HashSet` instead of `Graph`) |
| Phase 2 (layout) | Full Sugiyama per unique subgraph | O(V+E) filtering per subgraph |
| Phase 3 (render + write) | ~same (first run) | Skip cached files (subsequent runs) |

## Verification Criteria

- Phase 2 time drops by >10x on SBS-Test/GCR
- SVG file count matches before/after
- Cache manifest correctly skips unchanged subgraphs on re-run
- OSforGFF completes in seconds, not hours
