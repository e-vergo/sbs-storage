# FAQ Page Implementation Plan (Issue #341)

## Context

The FAQ sidebar link currently points to an external URL (`leanprover-community.github.io/blueprint/faq.html`). This task replaces it with an internal FAQ page that algorithmically collects toolchain READMEs and supports user-defined documents, giving SBS users a single navigable reference for all toolchain documentation.

## Decisions

- **Rendering:** Pure Lean — Runway reads README.md files at build time via `IO.FS.readFile`, generates static HTML with raw text in `<pre>` blocks
- **User docs:** Centralized in `dress-blueprint-action/docs/`
- **README scope:** Comprehensive for Dress (6 modules), Runway (3 modules), dress-blueprint-action (assets), LeanArchitect (Architect)
- **Page pattern:** Follows `generateDepGraphPages` — uses `pageShell`, `renderSidebar`, standalone generation function called from both `generateSite` and `generateMultiPageSite`

## Wave 1: FAQ Page Infrastructure

**Single agent — all changes in Runway + dress-blueprint-action**

### New: `toolchain/Runway/Runway/Faq.lean`

```
structure FaqEntry where
  category : String    -- repo name (e.g., "Dress")
  title : String       -- section name (e.g., "Graph")
  content : String     -- raw file content

-- Walk known toolchain directories for README.md files
def collectToolchainDocs (toolchainDir : System.FilePath) : IO (Array FaqEntry)

-- Read user-defined docs from docs/ directory
def collectUserDocs (docsDir : System.FilePath) : IO (Array FaqEntry)

-- Render a single FAQ section (collapsible category with entries)
def renderFaqSection (category : String) (entries : Array FaqEntry) : Html

-- Render the full FAQ page using pageShell
def faqPage (toolchainDocs userDocs : Array FaqEntry)
    (config : Option Config) (sidebar : Html) : Html
```

Collection algorithm:
- Known repos: `["Dress", "Runway", "dress-blueprint-action", "LeanArchitect"]`
- For each: check repo root README.md, then walk immediate subdirectories for README.md
- Category = repo name, title = directory name (or "Overview" for root README)
- Sort entries within each category alphabetically

### Modify: `toolchain/Runway/Runway/Theme.lean`

1. **`isBlueprintPage`** (~line 69): Add `| some "faq" => false`
2. **`renderSidebar`** (~line 111-183):
   - Add FAQ nav item after graphItem (line ~125): `let faqClass := if currentSlug == some "faq" then "sidebar-item active" else "sidebar-item"`
   - Insert into `navItems` array (line 175)
   - Remove `faqUrl` from external links section (line 169)
3. **`generateDepGraphPages`** or new **`generateFaqPage`** (~line 513):
   - New function `generateFaqPage` following same pattern as dep graph generation
   - Reads toolchain docs from paths relative to project root
   - Reads user docs from `assetsDir/../docs/` (co-located with assets in dress-blueprint-action)
4. **`generateSite`** (~line 575): Add `generateFaqPage` call after `generateDepGraphPages`
5. **`generateMultiPageSite`** (~line 792): Add `generateFaqPage` call after `generateDepGraphPages`

### Modify: `toolchain/Runway/Runway/Config.lean`

- Add `docsDir : Option System.FilePath := none` field for user-defined docs path
- Add `toolchainDir : Option System.FilePath := none` for README collection root
- Update `ToJson`/`FromJson` instances

### Modify: `toolchain/Runway/Runway.lean`

- Add `import Runway.Faq`

### New: `toolchain/dress-blueprint-action/assets/faq.css`

- Collapsible category sections (reuse blueprint toggle pattern from sidebar)
- `<pre>` block styling for raw markdown text (monospace, scroll, padding)
- Category headers, entry titles
- Responsive layout using existing CSS variables from `common.css`

### New: `toolchain/dress-blueprint-action/docs/` directory

- `docs/README.md` — explains the docs directory convention

### Modify: `toolchain/Runway/Runway/DepGraph.lean`

- Add `faq.css` to `pageShell` head CSS links (~line 454), or create a separate `faqPageShell` that extends it

## Wave 2: READMEs (4 parallel agents, non-overlapping repos)

### Agent A: Dress READMEs

All in `toolchain/Dress/Dress/`:
- `README.md` — module entry point, phase overview (capture → serialize → generate → graph → render), module map
- `Graph/README.md` — layout algorithm (DAG, Sugiyama-style), SVG rendering, Build pipeline, 59KB Layout.lean overview
- `Render/README.md` — side-by-side HTML/LaTeX rendering, SideBySide.lean
- `Capture/README.md` — compilation artifact capture from Lean elaboration
- `Serialize/README.md` — manifest JSON serialization format
- `Generate/README.md` — artifact generation orchestration
- `Svg/README.md` — SVG utility functions

### Agent B: Runway READMEs

All in `toolchain/Runway/Runway/`:
- `README.md` — module entry point, page types, generation flow, theme system
- `Html/README.md` — HTML page generation, LaTeX AST → HTML conversion
- `Latex/README.md` — LaTeX lexer, parser, AST types
- `Dress/README.md` — Dress artifact loading and consumption

### Agent C: dress-blueprint-action READMEs

- `toolchain/dress-blueprint-action/assets/README.md` — CSS architecture (common.css variables, blueprint.css layout, dep_graph.css graph, paper.css), JS modules (verso-code.js highlighting, plastex.js interactivity), theme system (light/dark via CSS variables)

### Agent D: LeanArchitect README

- `forks/LeanArchitect/Architect/README.md` — `@[blueprint]` attribute definition, 8 metadata fields, 3 status options (notReady/ready/sorry/proven/fullyProven/mathlibReady), data flow into Dress manifest

## Wave 3: User Docs + Integration

### Agent E: User-defined documents

In `toolchain/dress-blueprint-action/docs/`:
- `quickstart.md` — getting started with SBS (install, lakefile setup, first annotation, build, view)
- `user-guide.md` — navigating the blueprint site (dashboard, dep graph, chapters, toggles, search)
- `status-colors.md` — 6-status color model explained for end users (what each status means, visual reference)

### Agent F: Integration test

- Build SBS-Test with `./dev/build-sbs-test.sh`
- Verify `faq.html` exists in output
- Verify sidebar link works
- Verify toolchain READMEs appear grouped by category
- Verify user docs appear in separate section
- Screenshot for visual verification

## Key Files

| File | Action | Purpose |
|------|--------|---------|
| `Runway/Runway/Faq.lean` | CREATE | FAQ collection + rendering |
| `Runway/Runway/Theme.lean` | MODIFY | Sidebar nav, page generation calls |
| `Runway/Runway/Config.lean` | MODIFY | Add docs/toolchain dir config |
| `Runway/Runway.lean` | MODIFY | Import Faq |
| `Runway/Runway/DepGraph.lean` | MODIFY | pageShell CSS (add faq.css) |
| `dress-blueprint-action/assets/faq.css` | CREATE | FAQ page styles |
| `dress-blueprint-action/docs/` | CREATE | User doc directory + content |
| `Dress/Dress/**README.md` | CREATE | 7 module READMEs |
| `Runway/Runway/**README.md` | CREATE | 4 module READMEs |
| `dress-blueprint-action/assets/README.md` | CREATE | Assets architecture doc |
| `LeanArchitect/Architect/README.md` | CREATE | Attribute definition doc |

## Verification

1. `./dev/build-sbs-test.sh` completes without errors
2. `faq.html` present in build output with correct structure
3. Sidebar shows "FAQ" link between "Dependency Graph" and separator
4. Clicking FAQ shows collapsible category sections with raw README text
5. User docs section renders below toolchain docs
6. Existing pages (dashboard, dep_graph, chapters) unaffected
7. `lean_diagnostic_messages` clean on modified Lean files
