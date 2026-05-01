## Why

`architecture-rc3` is tagged. The architecture is finalized for build planning. Before the first product code lands, an engineer should be able to read a single page that answers:

1. What is Zovark?
2. What is the first MVP build slice?
3. What are the core architecture objects?
4. How does data flow through the system?
5. What is explicitly deferred?
6. What trust boundaries apply to the first slice?
7. What does the first build need to prove?

The 8 governing specs and 5 architecture object documents under `architecture/objects/` answer these questions thoroughly but not concisely. A one-pager derived from them gives builders an at-a-glance map without re-reading the corpus. This change creates that map.

## What Changes

- Add `architecture/one-page-architecture.md` — a one-printed-page derived map of the rc3-frozen architecture: wedge, first MVP slice, core objects (with canonical field names from the specs), runtime path, trust boundaries, deferred scope, build rule.
- Add `architecture/one-page-architecture.mmd` — a Mermaid flowchart of the same map. MVP slice and Deferred scope are explicit subgraphs.
- Add a small governing capability `build-planning-artifacts` codifying the rules the one-pager must follow (one page, canonical wedge, deferred scope explicit, MVP slice explicit, no new architecture).
- **Out of scope:** changing any ADR, modifying any other OpenSpec spec, introducing new product scope, or adding new architecture decisions. The one-pager is purely derived.

## Capabilities

### New Capabilities

- `build-planning-artifacts`: Governs the one-page architecture map and any future build-planning-derived artifacts. Defines what they must contain, what they must NOT introduce, and how updates are gated.

### Modified Capabilities

(none)

## Impact

- **Documents added:** `architecture/one-page-architecture.md`, `architecture/one-page-architecture.mmd`, `openspec/specs/build-planning-artifacts/spec.md` (after archive).
- **Documents touched:** none.
- **Code:** none.
- **Linked items:** unblocks build planning. The first MVP slice (`mvp/slice-001-investigation-tape`) is the natural next branch.
