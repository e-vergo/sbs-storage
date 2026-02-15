# Issue #339: Individual Dep Graph Page Visual Fixes

## Context
Individual node pages in the dependency graph have 5 visual bugs: SVG clipping on the right, a spurious border line, contextless above/below content, and legend styling inconsistencies. The root cause of the SVG clipping is architectural — `renderSvgInto()` passes the same DOM element as both viewport and svgContainer to `initPanZoom()`, unlike the full graph page which separates them.

## Alignment Decisions
| Decision | Choice |
|----------|--------|
| Above/below suppression | CSS (display:none) |
| Viewport wrapper | Lean-emitted |
| Legend scope | Both pages, CSS + HTML |
| Viewport height | 90vh |

## Wave 1: Two Parallel Agents (non-overlapping files)

### Agent A — Lean (DepGraph.lean)

**File:** `Side-By-Side-Blueprint/toolchain/Runway/Runway/DepGraph.lean`

**Viewport wrapper (lines 782-783).** Replace the bare subgraph container with a viewport + container structure matching the full graph page (lines 322-327):

```lean
-- BEFORE (lines 782-783):
Html.tag "div" #[("id", "node-subgraph"), ("class", "dg-subgraph-container"),
              ("data-node-id", node.label)] Html.empty

-- AFTER:
Html.tag "div" #[("class", "dep-graph-viewport dg-subgraph-viewport"),
                 ("id", "node-subgraph-viewport"),
                 ("style", "height: 90vh;")] (
  Html.tag "div" #[("id", "node-subgraph"), ("class", "dg-subgraph-container dep-graph-svg"),
                ("data-node-id", node.label)] Html.empty
)
```

Classes explained:
- `dep-graph-viewport` — inherits base viewport CSS (overflow:hidden, cursor:grab, etc.)
- `dg-subgraph-viewport` — allows targeted override (max-height:none)
- `dep-graph-svg` — gives inner div `transform-origin: 0 0` and `will-change: transform`

**Legend HTML:** No Lean changes needed — `graphLegendCompact` structure is clean. Compact sizing will be applied via scoped CSS selectors.

**Commit inside Runway submodule:** `fix: add viewport wrapper for individual node page subgraph (#339)`

### Agent B — CSS + JS (dep_graph.css, verso-code.js)

**File 1:** `Side-By-Side-Blueprint/toolchain/dress-blueprint-action/assets/verso-code.js`

**initPanZoom fix (line 820).** Find the viewport wrapper if present, fall back to container for backward compat:
```js
// BEFORE:
initPanZoom(container, container, toolbarPrefix);

// AFTER:
var viewport = container.closest('.dep-graph-viewport') || container;
initPanZoom(viewport, container, toolbarPrefix);
```

**File 2:** `Side-By-Side-Blueprint/toolchain/dress-blueprint-action/assets/dep_graph.css`

**5 CSS changes:**

1. **Viewport override (after line 95).** Override base `max-height: 600px`:
```css
.dg-subgraph-viewport {
  max-height: none;
  z-index: auto;
}
```

2. **Border fix (lines 1088-1092).** Move border-left from container to viewport wrapper:
```css
/* BEFORE: */
.dg-subgraph-wrapper .dg-subgraph-container {
  border: none; border-radius: 0;
  border-left: 1px solid var(--bp-border);
}

/* AFTER: */
.dg-subgraph-wrapper .dg-subgraph-viewport {
  border-left: 1px solid var(--bp-border);
}
.dg-subgraph-wrapper .dg-subgraph-container {
  border: none; border-radius: 0;
}
```

3. **Above/below suppression (after line 854):**
```css
.dg-node-sbs-section .sbs-above-content,
.dg-node-sbs-section .sbs-above-spacer,
.dg-node-sbs-section .sbs-below-content,
.dg-node-sbs-section .sbs-below-spacer {
  display: none;
}
```

4. **Legend compact sizing via scoped selector (replace dead `.dep-graph-legend-compact` at lines 1044-1062):**
```css
.dg-subgraph-controls .dep-graph-legend {
  width: auto;
  font-size: 0.75rem;
  padding: 0.375rem;
}
.dg-subgraph-controls .dep-graph-legend .legend-title {
  font-size: 0.7rem;
  margin-bottom: 0.375rem;
}
.dg-subgraph-controls .dep-graph-legend .legend-swatch {
  width: 12px; height: 12px;
}
.dg-subgraph-controls .dep-graph-legend .legend-shape {
  width: 12px; height: 10px;
}
```

5. **Legend label consistency (in `.dep-graph-legend` block, after line 446):**
```css
.dep-graph-legend .legend-item span:last-child {
  font-size: 0.8rem;
  white-space: nowrap;
}
```

**Commit inside dress-blueprint-action submodule:** `fix: viewport, border, content suppression, and legend styling (#339)`

## Wave 2: Build + Verify (single agent, after Wave 1)

1. `./dev/build-sbs-test.sh`
2. Navigate to an individual node page, screenshot
3. Verify: no right clipping, no left border artifact, no above/below content, compact legend
4. Check full graph page for regressions (legend, pan/zoom)
5. `pytest sbs/tests/pytest -m evergreen --tb=short`
6. Submodule pointer commits (Runway + dress-blueprint-action -> SBS -> SLS)
