# Source of Truth

This patch tree is an overlay package. Files present here are authoritative for the patch bundle. Files not present here remain post-apply baseline dependencies and must be verified in the full v3.2.3.5 baseline repository.

## Conflict Resolution

1. `VERSION_METADATA.json` is authoritative for counts and post-apply structural expectations.
2. `PATCH-MANIFEST.json` is authoritative for patch contents, file hashes, and `apply_mode`.
3. `architecture/adr/*.md` is authoritative for ADR decisions present in this patch tree.
4. `architecture/adr-index.md` is authoritative for patch-shipped ADR inventory and implementation-status notes.
5. `invariants.md` is authoritative for invariant statements and milestone status.
6. `architecture/blueprint/schemas/*.schema.json` is authoritative for wire and storage shape.
7. Executable scripts under `scripts/` are authoritative for enforcement that exists in this patch tree.
8. `ops/compliance/*` records generated evidence for patch-tree gates only.
9. Customer-facing claims must be backed by existing artifacts or by `[policy-commitment:<owner>,<review-cadence>]` tags.

If a document names a script, test, schema, runbook, benchmark, report, ledger, or CI workflow that does not exist in this tree, the document must label it as a milestone deliverable rather than current enforcement.

## Hash Domains

`REPORT_HASH` and `TREE_HASH` are different evidence domains and must not be compared or substituted.

- `REPORT_HASH` means `sha256(ops/compliance/bootstrap-acceptance-report.stable.json)` for a baseline repository after its bootstrap acceptance run.
- `TREE_HASH` means the patch-package hash chain recorded in `PATCH-MANIFEST.json` and verified by `scripts/check_patch_self_test.py`.

Schema `x-zovark-compatibility` fields are compatibility floors, not patch-package counters. Do not bump them for a documentation-only patch unless the schema compatibility contract changes.
