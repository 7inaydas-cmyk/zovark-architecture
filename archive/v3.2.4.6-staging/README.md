# Archived: zovark-v3.2.4.6 Engineering-Ready Staging

## Status

Reference-only. Not authoritative. Not validated by current scripts.

## Origin

This directory was previously located at the repo root as
`zovark-v3.2.4.6-engineering-ready/`. It contained pre-promotion
staging material from the v3.2.4.6 patch series, intended to become
authoritative architecture content.

## Disposition

All authoritative content from this subtree has been promoted to
current paths under `architecture/` as part of the v3.2.5.0
consolidation:

- ADRs 0038-0043 → `architecture/adr/` (consolidation commit 5)
- INV-001..032 → `architecture/invariants.md` (consolidation commit 1)
- Schemas → `architecture/blueprint/schemas/` (consolidation commit 1)

Files remaining in this archive directory are duplicates,
superseded variants, redundant patch material, or reference scripts.
Per the consolidation census, zero files in this subtree were
unique-and-promotable beyond what's already in the authoritative
paths above.

## Do not

- Do not import or copy content from this directory into authoritative
  paths.
- Do not validate content here against current scripts.
- Do not edit files here as if they were authoritative.
- Do not reference files in this directory from authoritative
  architecture documentation.

## See also

- `architecture/source-of-truth.md` — authoritative architecture
  inventory.
- The consolidation census at `/tmp/zovark-census.md` (local artifact)
  enumerated the per-file classification that led to this archive
  decision.
