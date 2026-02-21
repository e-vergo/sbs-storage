# Plan: Use Original Dress dep-graph.json (#358 refinement)

## Context

The client-side subgraph renderer works but uses a re-serialized JSON (`depGraph.toJsonString` at `Main.lean:526`) that strips node positions, edge Bezier points, and adjacency. This forced us to write `computeSimpleLayout` and `buildAdjacencyFromEdges` as JS fallbacks — producing approximate layouts instead of the exact Dress-computed coordinates.

The original `dep-graph.json` from Dress already has everything: `x`, `y`, `width`, `height` on nodes, `points` on edges, full `adjacency` map. A `loadDepGraphJson` function already exists at `Main.lean:288` but is unused. The fix is to use it instead of re-serializing.

## Changes (2 files)

### 1. `Runway/Main.lean` — Use original JSON instead of re-serialized

**Line 526**, change:
```lean
let depGraphJson := some depGraph.toJsonString
```
to:
```lean
let depGraphJson ← loadDepGraphJson dressedDir
```

`loadDepGraphJson` (line 288) reads `.lake/build/dressed/dep-graph.json` verbatim. The `depGraphJson` field flows through to `Theme.lean` which writes it to `dep_graph/dep-graph.json` in the site output, and also to chapter pages as `data-graph` attributes.

### 2. `verso-code.js` — Remove fallback layout code

With the original JSON providing all coordinates and adjacency, delete:
- `buildAdjacencyFromEdges` function (~lines 725-739)
- `computeSimpleLayout` function (~lines 741-839)
- The fallback logic in `loadGraphData` that calls these (~lines 868-875)

Keep everything else (BFS, rendering, arrowhead config, pan-zoom, etc.) unchanged.

## Verification

1. `lake build runway` in Runway directory (not needed — Main.lean change only affects runtime)
2. Actually: **does need rebuild** since Main.lean changed → `lake build runway`
3. `runway build` from SBS-Test
4. Verify `dep_graph/dep-graph.json` in output has `x`, `y`, `points`, `adjacency`
5. Serve on localhost, check subgraphs render with exact Dress layout
6. Confirm arrowhead positioning and dark mode colors still work
