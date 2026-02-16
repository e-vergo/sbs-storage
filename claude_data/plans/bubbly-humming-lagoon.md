# Fix Dress fromEnvironment: getEntries → getState with Thunk unwrap

## Context

The Dress `ef30c0d` fix for Lean v4.28 changed `Graph/Build.lean:fromEnvironment` from `getState` to `getEntries` to avoid a `Thunk` type error. But `getEntries` only returns entries from the **current module**, not imported modules. When `extract_blueprint graph` runs as an external binary, there are no current-module entries, so it returns 0 nodes. This causes:
- Empty dependency graph (full graph missing, zero nodes/edges)
- All dashboard stats at zero
- Individual chapter subgraphs missing

GCR CI build log confirms: `[timing] fromEnvironment: 0ms (0 nodes)`, `Nodes: 0`.

The other two `getEntries` call sites in Dress (`ElabRules.lean:239`, `Content.lean:44`) are intentionally current-module scoped -- only `Graph/Build.lean:401` is broken.

## Fix

One-line change in `Dress/Graph/Build.lean` line 401:

```lean
-- Current (broken):
let entries := Architect.blueprintExt.getEntries env

-- Fixed:
let entries := (Architect.blueprintExt.getState env).get.toArray.toList
```

- `.get` unwraps the `Thunk` (new in Lean v4.28's `getState` return type)
- `.toArray` converts `NameMap Node` to `Array (Name × Node)` (`.toList` was removed in batteries v4.28 TreeMap migration)
- `.toList` converts to `List` to match the existing `entries.toArray.mapM` on line 402

## Critical file

- `/Users/eric/GitHub/SLS-Strange-Loop-Station/Side-By-Side-Blueprint/toolchain/Dress/Dress/Graph/Build.lean` line 401

## Post-fix steps

1. Check diagnostics with `lean_diagnostic_messages` to verify the fix compiles
2. Commit + push Dress
3. Retrigger CI on GCR (and any other repos with `workflow_dispatch`)
4. Verify `fromEnvironment` reports >0 nodes in the CI log

## Risk

The `Thunk.get` call is the standard unwrap -- no risk. The `.toArray.toList` pattern was validated in the `ef30c0d` commit (it just couldn't reach this code path because `getEntries` returned `[]` first). If `.toArray` on `NameMap` doesn't exist in v4.28, fall back to iterating: `(blueprintExt.getState env).get.fold (init := #[]) fun acc k v => acc.push (k, v)`.
