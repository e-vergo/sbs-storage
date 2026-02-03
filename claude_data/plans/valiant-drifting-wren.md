# Sidebar Overhaul - Issue #104

## Scope
Remove standalone chapter panel, inline chapters under "Blueprint" toggle in sidebar, reduce width, bump font size. Touches 2 submodule repos: `dress-blueprint-action` (CSS/JS) and `Runway` (Lean template).

---

## Wave 1: Template Changes (Runway/Theme.lean)

**File:** `toolchain/Runway/Runway/Theme.lean`

### 1a. Remove `renderChapterPanel` (lines 84-101)
Delete entirely -- no longer needed.

### 1b. Modify `renderSidebar` (lines 103-200)
Replace the TeX Blueprint `mkDocItem` call (line 156) with a new inline toggle structure:

```html
<li class="sidebar-blueprint-group">
  <span class="sidebar-item sidebar-blueprint-toggle">
    <span class="sidebar-chevron">&#x25B8;</span> Blueprint
  </span>
  <ul class="sidebar-chapter-list">
    <li><a href="ch1.html" class="sidebar-chapter-item active">Ch 1: Title</a></li>
    ...
  </ul>
</li>
```

New Lean helper `renderBlueprintToggle` takes `chapters`, `currentSlug`, `toRoot`, `available`. When `available == false`, renders disabled span (no toggle, no chapters).

### 1c. Modify `primaryTemplateWithSidebar` (lines 298-380)
- Remove `showChapterPanel` / `chapterPanel` computation (lines 310-313)
- Remove conditional `wrapperClass` (line 328) -- always `"wrapper"`
- Remove `chapterPanel` from template output (line 368)

### 1d. Add `data-blueprint-page` attribute to `<body>`
Use existing `isBlueprintPage` to set `data-blueprint-page="true"` on body tag. Gives JS the signal to auto-expand chapters.

---

## Wave 2: CSS Changes (dress-blueprint-action)

### blueprint.css

**2a. Reduce sidebar width** (line 175): `25ch` -> `17.5ch`

**2b. Bump font-size** (line 178): `0.875rem` -> `0.9375rem`

**2c. Remove `.wrapper.with-chapter-panel` styles** (lines 1389-1401)

### common.css

**2d. Remove chapter panel section** (lines 1041-1135) -- entire "Section 11"

**2e. Remove chapter panel CSS variables** (light ~line 114, dark ~line 321)

**2f. Add inline chapter styles** (in section 10):
- `.sidebar-blueprint-group` -- flex column container
- `.sidebar-blueprint-toggle` -- clickable, cursor pointer
- `.sidebar-chevron` -- rotate 90deg when `.expanded`
- `.sidebar-chapter-list` -- `max-height: 0` -> `max-height: 50vh` transition
- `.sidebar-chapter-item` -- indented, smaller font, active highlight

---

## Wave 3: JavaScript (plastex.js)

**3a. Remove** `$("nav.chapter-panel").toggle()` from mobile toggle (line 61)

**3b. Add chapter toggle:**
```js
(function() {
  var $group = $('.sidebar-blueprint-group');
  if (!$group.length) return;
  var $toggle = $group.find('.sidebar-blueprint-toggle');
  if (document.body.hasAttribute('data-blueprint-page')) {
    $group.addClass('expanded');
  }
  $toggle.on('click', function() {
    $group.toggleClass('expanded');
  });
})();
```

---

## Execution

Single `sbs-developer` agent, sequential waves (tight coupling between template and CSS/JS). Commit order: dress-blueprint-action first, Runway second, parent repo pointer update last.

---

## Gates

```yaml
gates:
  tests: all_pass
  test_tier: evergreen
  quality:
    T5: ">= 0.8"
    T6: ">= 0.9"
  regression: ">= 0"
validators:
  - visual: [dashboard, chapter, dep_graph]
  - timing: true
```

## Validation Steps

1. Build SBS-Test: `python ../../dev/scripts/build.py`
2. Capture: `python3 -m sbs capture --project SBSTest --interactive`
3. Visual check: no chapter panel column, narrower sidebar, chapters inline under Blueprint
4. Tests: `pytest sbs/tests/pytest -m evergreen --tb=short`
5. Build GCR to confirm multi-project (has real chapters)
