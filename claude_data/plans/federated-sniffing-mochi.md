# Issue #359: Push & CI Deployment Plan

## Context

Waves 1-3 are implemented and validated locally. All Lean code changes compile and the environment-based discovery feature works (tested on SBS-Test with untagged declarations: 23 nodes with correct auto-inferred edges).

**Problem:** During local development, we switched Dress → LeanArchitect and SBS-Test → Dress from git deps to path deps. These path deps break CI because `dress-blueprint-action` uses federated checkout (clones each toolchain repo independently). We need to restore git deps and push in dependency order.

**Additional work:** OSreconstruction needs a CI workflow file, runway.json, and git dep for Dress (not path dep).

## Push Sequence

Strict dependency order: LeanArchitect → Dress → {SBS-Test, PNT, OSreconstruction} → SBS monorepo

### Step 1: Push LeanArchitect

Repo: `e-vergo/LeanArchitect` (on `main`)

- Commit all changes (CollectUsed, Basic, Attribute, Output, RPC, ArchitectTest)
- Push to origin main

### Step 2: Restore Dress git dep + push

Repo: `e-vergo/Dress` (on `main`)

- Revert `lakefile.lean` line 20 from path back to git:
  ```lean
  require LeanArchitect from git
    "https://github.com/e-vergo/LeanArchitect.git" @ "main"
  ```
- Clean `.lake/packages/LeanArchitect` (stale path dep artifacts)
- Run `lake update LeanArchitect` → updates `lake-manifest.json` from path to git dep with new commit hash
- Rebuild Dress to verify (176 jobs, should reuse most cached oleans)
- Commit all changes (Build.lean, deleted AutoTag, Main, Quickstart, Output, Latex, lakefile, manifest)
- Push to origin main

### Step 3a: Restore SBS-Test git dep + push

Repo: `e-vergo/SBS-Test` (on `main`)

- Revert `lakefile.toml` from `path = "../Dress"` back to:
  ```toml
  git = "https://github.com/e-vergo/Dress.git"
  rev = "main"
  ```
- Clean `.lake/packages/Dress` (stale path dep artifacts)
- Run `lake update Dress` → manifest picks up new Dress commit
- Rebuild SBS-Test + verify graph (21 nodes, 21 edges)
- Commit and push to origin main

### Step 3b: Push PNT

Repo: `e-vergo/PrimeNumberTheoremAnd` (on `main`)

- Commit the 2 files with `uses` removals
- Push to origin main

### Step 3c: Set up OSreconstruction + push

Repo: `e-vergo/OSreconstruction` (on `clear-sorries-wave1-wave2`)

**lakefile.toml** — change Dress from path to git dep:
```toml
[[require]]
name = "Dress"
git = "https://github.com/e-vergo/Dress.git"
rev = "main"
```

**lean-toolchain** — align with Dress:
```
leanprover/lean4:v4.28.0-rc1
```

**runway.json** — create minimal config:
```json
{
  "title": "OS Reconstruction",
  "projectName": "OSReconstruction",
  "githubUrl": "https://github.com/e-vergo/OSreconstruction",
  "baseUrl": "/OSreconstruction/",
  "docgen4Url": null,
  "runwayDir": "runway",
  "assetsDir": "../dress-blueprint-action/assets"
}
```

**.github/workflows/full-blueprint-build-and-deploy.yml** — copy from SBS-Test (identical):
```yaml
name: Full Blueprint Build and Deploy
on:
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages-${{ github.ref }}
  cancel-in-progress: true
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: e-vergo/dress-blueprint-action@main
  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
        id: deployment
```

- Run `lake update` to generate `lake-manifest.json`
- Do NOT build locally (mathlib takes hours) — CI handles it
- Commit and push to origin `clear-sorries-wave1-wave2`

### Step 4: Update SBS monorepo pointers

Repo: `e-vergo/Side-By-Side-Blueprint` (on `main`)

- `git add` all modified submodule pointers (LeanArchitect, Dress, SBS-Test, PNT, OSreconstruction)
- Commit: "feat: environment-based declaration discovery (#359)"
- Push to origin main

### Step 5: Update SLS pointer

- `git add Side-By-Side-Blueprint`
- Commit SLS
- Push via `sbs archive upload` or subprocess

## CI Expectations

**SBS-Test CI:** Should pass — fully validated locally. Graph: 21 nodes, 21 edges.

**OSreconstruction CI:** May fail on first run for reasons unrelated to our changes:
- mathlib build from source (~2-4 hours on CI runner)
- OSreconstruction source code has never been compiled by us
- GaussianField (`rev = "main"`) compatibility unknown

The `dress-blueprint-action` handles everything: it extracts versions from `lake-manifest.json`, clones toolchain repos (LeanArchitect, Dress, Runway, SubVerso) independently, builds in dependency order, generates graph + site. No import of Dress needed in source files.

**deploy job gating**: `if: github.ref == 'refs/heads/main'` — since OSreconstruction pushes to `clear-sorries-wave1-wave2`, deploy won't run until merged to main. But the build job runs on any branch via `workflow_dispatch`.

## Key Files Modified

| Step | File | Change |
|------|------|--------|
| 2 | `toolchain/Dress/lakefile.lean` | Restore git dep for LeanArchitect |
| 2 | `toolchain/Dress/lake-manifest.json` | Auto-updated by `lake update` |
| 3a | `toolchain/SBS-Test/lakefile.toml` | Restore git dep for Dress |
| 3a | `toolchain/SBS-Test/lake-manifest.json` | Auto-updated by `lake update` |
| 3c | `showcase/OSreconstruction/lakefile.toml` | Dress git dep (replace path) |
| 3c | `showcase/OSreconstruction/lean-toolchain` | v4.28.0-rc1 |
| 3c | `showcase/OSreconstruction/runway.json` | NEW — site config |
| 3c | `showcase/OSreconstruction/.github/workflows/...` | NEW — CI workflow |
| 3c | `showcase/OSreconstruction/lake-manifest.json` | Auto-generated by `lake update` |

## Verification

1. After step 2: `lake build Dress` succeeds with git dep
2. After step 3a: `lake build SBSTest` + `extract_blueprint graph` → 21 nodes
3. After step 3c: `lake update` resolves in OSreconstruction (no build needed locally)
4. After step 4: Trigger SBS-Test CI via workflow_dispatch → verify graph renders
5. After step 3c push + user enables Pages: Trigger OSreconstruction CI → verify build + graph

## Risks

- **OSreconstruction CI build time**: Mathlib from source = 2-4 hours on GitHub runner. First run will be slow; subsequent runs use action's cache.
- **OSreconstruction compilation**: Source code untested. If it fails to compile, that's a pre-existing issue unrelated to our changes.
- **`lake update` in Dress/SBS-Test**: May pull newer versions of transitive deps (verso, subverso). Should be fine since they're pinned by rev in manifests.
