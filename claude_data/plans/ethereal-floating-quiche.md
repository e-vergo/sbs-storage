# Epic #333: SBS Self-Documentation — Blueprint the Toolchain Itself

## Context

The SBS documentation toolchain (LeanArchitect, Dress, Runway) has been built and proven on external projects (SBS-Test, GCR, PNT). The next step is the ultimate dogfood showcase: use the toolchain to document itself. This is being shown to world-class computer scientists, so quality must be exceptional.

Three repos get the full blueprint treatment: `@[blueprint]` annotations on every declaration, comprehensive LaTeX narratives, interactive Verso documents, dependency graphs, dashboards, and deployed GitHub Pages sites.

## Decisions (from alignment)

- **Scope:** All 4 subissues (#334-#337) sequentially
- **Coverage:** 100% — every def, theorem, structure, instance annotated
- **Narrative depth:** Comprehensive 20+ page blueprint.tex per repo
- **Documents:** Blueprint.lean only (no Paper.lean)
- **Drafting:** Autonomous, reviewed during QA convergence
- **LeanArchitect architecture:** Wrapper project at `toolchain/LeanArchitect-Blueprint/` (avoids LeanArchitect -> Dress -> LeanArchitect circular dependency)

## Architecture

| Repo | Strategy | Annotations In | Build Infrastructure In |
|------|----------|---------------|------------------------|
| LeanArchitect | Wrapper project | `forks/LeanArchitect/Architect/*.lean` | `toolchain/LeanArchitect-Blueprint/` |
| Dress | Self-contained | `toolchain/Dress/Dress/*.lean` | `toolchain/Dress/` |
| Runway | Self-contained | `toolchain/Runway/Runway/*.lean` | `toolchain/Runway/` |

**Why wrapper for LeanArchitect:** LeanArchitect defines `@[blueprint]`. Dress depends on LeanArchitect and provides the Lake facets (dressed, blueprint, depGraph). Adding Dress as a LeanArchitect dependency creates a cycle. The wrapper project depends on both, breaking the cycle.

**Why Dress/Runway are self-contained:** Dress already imports LeanArchitect (has access to `@[blueprint]`) and defines its own Lake facets. Runway imports Dress transitively. Both can annotate their own code and build their own blueprints.

## Phase 1: LeanArchitect (#334) — ~98 declarations, 12 modules

### Wave 1.1: Annotations (4 parallel `sbs-developer` agents)

Each agent adds `@[blueprint "la:..." ...]` with LaTeX statements, proof descriptions, `uses` dependencies, and dashboard metadata to every declaration.

| Agent | Files | ~Decls |
|-------|-------|--------|
| A | `Attribute.lean` (core attribute elaboration) | ~9 |
| B | `Basic.lean`, `Content.lean`, `Command.lean` (types + extensions) | ~22 |
| C | `CrossRef.lean`, `Validation.lean`, `Output.lean` (heaviest modules) | ~46 |
| D | `RPC.lean`, `Tactic.lean`, `Load.lean`, `CollectUsed.lean` | ~13 |

**Label convention:** `la:` prefix. E.g., `la:node-status`, `la:elab-blueprint-config`, `la:cross-ref-check`.

**Reference pattern:** Follow `SBS-Test/SBSTest/StatusDemo.lean` exactly. Each annotation includes:
- Unique label with `la:` prefix
- `title` for display name
- `statement` with LaTeX mathematical/technical description
- `proof` describing implementation approach
- `uses` for explicit dependency chains between declarations
- Dashboard metadata where appropriate (`keyDeclaration`, `message`, etc.)

### Wave 1.2: Wrapper Project (1 agent)

Create `Side-By-Side-Blueprint/toolchain/LeanArchitect-Blueprint/`:

```
LeanArchitect-Blueprint/
├── lakefile.toml              # Requires LeanArchitect + Dress + verso
├── LeanArchitectBlueprint.lean # Root: import Architect
├── LeanArchitectBlueprint/
│   └── Blueprint.lean         # Verso doc with :::leanNode hooks
├── GenerateBlueprint.lean     # Verso renderer executable
├── runway.json                # Site config
├── runway/src/
│   └── blueprint.tex          # Placeholder (populated in Wave 1.3)
└── .dress                     # Marker file
```

`lakefile.toml`:
```toml
name = "LeanArchitectBlueprint"
[[require]]
name = "LeanArchitect"
path = "../../forks/LeanArchitect"
[[require]]
name = "Dress"
path = "../Dress"
[[require]]
name = "verso"
git = "https://github.com/e-vergo/verso.git"
rev = "main"
```

### Wave 1.3: Blueprint Narrative (1 agent)

Write `runway/src/blueprint.tex` (~20+ pages):

| Chapter | Content |
|---------|---------|
| 1. Introduction | What LeanArchitect is, role in SBS ecosystem, design philosophy |
| 2. The `@[blueprint]` Attribute | Full syntax reference, 24 options taxonomy, elaboration pipeline |
| 3. Core Types | `Node`, `NodePart`, `NodeStatus` (6-level), `NodeWithPos`, extension state |
| 4. Dependency Inference | `CollectUsed` expression tree walking, statement vs proof deps |
| 5. Statement Validation | LaTeX brace/delimiter checking, cross-reference heuristics |
| 6. Output Generation | LaTeX serialization with `\uses`/`\leanok`, JSON for dashboards |
| 7. Integration Points | RPC endpoint for infoview, proof docstrings, module commands |
| 8. Design Rationale | Attribute-based vs delimiter-based, status hierarchy decisions, minimal deps |

Uses `\inputleannode{la:...}` throughout to embed annotated declarations in the narrative.

### Wave 1.4: Verso Document + Build (1 agent)

- Write `Blueprint.lean` with `#doc (SBSBlueprint)` and `:::leanNode` hooks for key declarations
- Write `GenerateBlueprint.lean` following SBS-Test pattern
- Build: `lake build` in wrapper project
- Verify: dependency graph renders, dashboard populates, all artifacts generate

### QA Gate: LeanArchitect

- `lake build LeanArchitectBlueprint` succeeds
- `lake build LeanArchitectBlueprint:depGraph` generates SVG + JSON
- All 98 declarations appear in dependency graph
- Dashboard shows correct status distribution
- Screenshot capture + visual inspection

## Phase 2: Dress (#335) — ~334 declarations, 39 modules

### Wave 2.1: Annotations (4 parallel agents)

| Agent | Module Group | ~Decls |
|-------|-------------|--------|
| A | Core: `Core`, `Paths`, `Base64`, `Cache`, `Content`, `Load`, `Hook` | ~50 |
| B | Capture + Generate: `ElabRules`, `InfoTree`, `State`, `Config`, `Declaration`, `Latex`, `Module` | ~60 |
| C | Graph: `Types`, `Build`, `Layout`, `Svg`, `Json`, `Subgraph` | ~100 |
| D | Render + Serialize + SVG + misc: `SideBySide`, `Json`, `Html`, `Artifacts`, 6 SVG modules, `Output`, `Highlighting`, `HtmlRender`, `SubVersoExtract` | ~120 |

**Label convention:** `dr:` prefix.

### Wave 2.2: Infrastructure (1 agent)

Add to `toolchain/Dress/`:
- `runway.json`
- `runway/src/blueprint.tex` (chapter structure placeholder)
- `DressBlueprint.lean` (root re-export)
- `DressBlueprint/Blueprint.lean` (Verso doc)
- `GenerateBlueprint.lean`
- Update `lakefile.lean`: add `lean_lib DressBlueprint` + `lean_exe generate-blueprint-verso`

### Wave 2.3: Blueprint Narrative (1 agent)

`runway/src/blueprint.tex` (~25+ pages):
- Ch 1: Introduction — Dress as artifact generator, self-referential meta-documentation
- Ch 2: Two-Phase Architecture — Capture (elaboration-time) vs Serialize (post-compilation)
- Ch 3: Capture Pipeline — ElabRules hooks, SubVerso highlighting, per-decl artifact writing
- Ch 4: Lake Facets — dressed, blueprint, depGraph facet chain, dependency ordering
- Ch 5: Graph Engine — Sugiyama hierarchical layout, edge routing, layer assignment
- Ch 6: SVG Generation — composable combinator library, coordinate systems
- Ch 7: Status Color Model — 6-status system, color source of truth in Lean code
- Ch 8: Serialization — JSON/HTML formats, artifact manifest, base64 encoding
- Ch 9: Rendering — side-by-side display, rainbow brackets, SubVerso integration
- Ch 10: Design Decisions — immediate capture rationale, caching strategy, extension points

### Wave 2.4: Build + Verify (1 agent)

### QA Gate: Dress

## Phase 3: Runway (#336) — ~220-280 declarations, 32 modules

### Wave 3.1: Annotations (4 parallel agents)

| Agent | Module Group | ~Decls |
|-------|-------------|--------|
| A | Core: `Render`, `Theme`, `Traverse`, `Site`, `Config`, `Graph` | ~80 |
| B | Latex: `Parser`, `ToHtml`, `ToLatex`, `Lexer`, `Ast`, `Token` | ~70 |
| C | Content: `DepGraph`, `Templates`, `Macros`, `Doc`, `Genre`, `Paper`, `VersoPaper` | ~80 |
| D | Infrastructure: `Pdf`, `Validate`, `DocGen4`, `AvailableDocuments`, `Assets`, `Dress/Load`, `Html/Render` | ~50 |

**Label convention:** `rw:` prefix. Cross-repo nodes reference Dress types with `dr:` labels.

### Waves 3.2-3.4: Infrastructure, Narrative, Build

Same pattern as Dress. Blueprint.tex (~25+ pages): site generation pipeline, LaTeX parser internals, Verso genre system, theme architecture, cross-repo dependency visualization, configuration system.

### QA Gate: Runway

## Phase 4: CI/CD (#337)

### Wave 4.1: GitHub Actions (1 agent)

Add `.github/workflows/blueprint.yml` to:
- `forks/LeanArchitect/` (configured to build from wrapper project path)
- `toolchain/Dress/`
- `toolchain/Runway/`

Using `e-vergo/dress-blueprint-action@main`.

### Wave 4.2: Deployment

Enable GitHub Pages, verify sites at:
- `e-vergo.github.io/LeanArchitect/`
- `e-vergo.github.io/Dress/`
- `e-vergo.github.io/Runway/`

## Convergence Strategy

After each phase QA gate:
1. Build + screenshot capture
2. Visual inspection: dependency graph, dashboard, blueprint pages
3. Iterate on annotation quality, narrative clarity, visual correctness
4. Move to next phase only when current phase passes

After all 4 phases: full cross-project convergence check.

## Critical Files

**Reference implementation:**
- [StatusDemo.lean](Side-By-Side-Blueprint/toolchain/SBS-Test/SBSTest/StatusDemo.lean) — annotation pattern
- [Blueprint.lean](Side-By-Side-Blueprint/toolchain/SBS-Test/SBSTest/Blueprint.lean) — Verso doc pattern
- [runway.json](Side-By-Side-Blueprint/toolchain/SBS-Test/runway.json) — config pattern
- [blueprint.tex](Side-By-Side-Blueprint/toolchain/SBS-Test/runway/src/blueprint.tex) — TeX pattern
- [lakefile.toml](Side-By-Side-Blueprint/toolchain/SBS-Test/lakefile.toml) — build config pattern

**Target repos:**
- [LeanArchitect/Architect/](Side-By-Side-Blueprint/forks/LeanArchitect/Architect/) — 12 modules to annotate
- [Dress/Dress/](Side-By-Side-Blueprint/toolchain/Dress/Dress/) — 39 modules to annotate
- [Runway/Runway/](Side-By-Side-Blueprint/toolchain/Runway/Runway/) — 32 modules to annotate

## Verification

Per-phase:
1. `lake build` succeeds in project directory
2. `lake build <project>:depGraph` generates valid SVG + JSON
3. All declarations appear in dependency graph (100% coverage check via `computeCoverage`)
4. Dashboard renders with correct status distribution
5. Blueprint pages render with embedded `\inputleannode{}` content
6. Screenshot capture via `sbs capture --interactive`
7. Visual compliance via `sbs compliance`

Final:
8. All three GitHub Pages sites deploy and render correctly
9. Cross-project links work (Runway referencing Dress types)

## Risks

| Risk | Mitigation |
|------|-----------|
| Wrapper project lakefile path resolution | Test early in Wave 1.2 with minimal build |
| Dress self-build facet ordering | Verify dressed facet runs after elaboration completes |
| 100% coverage on Layout.lean (1500 LOC, ~60 decls) | Dedicate full agent to Graph module group |
| LaTeX narrative quality for CS audience | QA convergence cycles with user review |
| Lake dependency version alignment | Pin all to v4.28.0-rc1 / main consistently |
