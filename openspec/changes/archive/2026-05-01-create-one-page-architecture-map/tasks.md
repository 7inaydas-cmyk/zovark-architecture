## 1. Write the one-pager

- [ ] 1.1 Create `architecture/one-page-architecture.md` with the seven sections: product wedge, first MVP build slice, core architecture objects (referencing canonical capability names), runtime path for first slice, trust boundaries, deferred architecture, build rule.
- [ ] 1.2 Verify the file fits the page-fit budget (≤ 100 lines including blanks/headings).
- [ ] 1.3 Verify the canonical wedge statement and core flow appear verbatim.
- [ ] 1.4 Verify the seven-step MVP slice matches the rc3 scorecard's "Bridge to product implementation".
- [ ] 1.5 Verify the deferred scope includes M2 DR sketch, M3 vault IPC schemas, and post-apply baseline-ADR cross-link verification.

## 2. Write the Mermaid diagram

- [ ] 2.1 Create `architecture/one-page-architecture.mmd` with an MVP Slice subgraph (7 nodes wired in flow order) and a Deferred subgraph (out-of-scope nodes, no edges to MVP).
- [ ] 2.2 Verify Mermaid syntax is valid.

## 3. Capture the spec

- [ ] 3.1 Run `openspec validate create-one-page-architecture-map`.
- [ ] 3.2 Run `openspec archive create-one-page-architecture-map --yes`.

## 4. Commit on docs branch

- [ ] 4.1 Stage `architecture/one-page-architecture.md`, `architecture/one-page-architecture.mmd`, the change archive, and the new spec.
- [ ] 4.2 Commit: "Add one-page architecture map".
- [ ] 4.3 Push the branch to origin.

## 5. Merge to main

- [ ] 5.1 Switch to main; merge `docs/one-page-architecture` (fast-forward expected).
- [ ] 5.2 Push main.

## 6. Stage the next branch

- [ ] 6.1 From main, create `mvp/slice-001-investigation-tape`. Do not start implementation; the branch is staged for the user to begin from.
