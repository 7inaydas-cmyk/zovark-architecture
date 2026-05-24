# ADR-0006: Data Flywheel - Opt-In Pooled With Tenant-First Benefits

**Status:** active
**Date:** 2026-05-19
**Owner:** architect
**Source:** rewritten from bootstrap ADR-0006 for the v3.2.5.0 consolidation baseline

## Context

Zovark needs a learning loop without weakening tenant-data authority. INV-001
keeps tenant data isolated, ADR-0038 places tenant data under customer-instance
authority, and ADR-0040 requires research outputs to pass a promotion gate
before they can affect customer runtime. The predecessor ADR-0006 described the
same direction but used an older product frame and did not name the newer
authority and promotion boundaries.

The data-flywheel decision therefore has to separate three things:
customer-owned source data, sanitized learning artifacts that a tenant chooses
to export, and promoted improvements that return only through the governed
update path.

## Decision

Customer raw data stays local by default. A tenant may opt in to produce a
learning pack, but the learning pack is a derived artifact, not a raw replay
record, raw prompt transcript, raw tool-output dump, credential material, or
tenant database export.

Learning packs must be sanitized in the customer instance before export. The
pack contains only the fields allowed by its schema, source linkage, hashes,
and sanitization evidence. The receiving side may verify the schema,
sanitization manifest, and provenance, but it must not depend on reconstructing
the tenant's raw source material.

Two tenant choices are binding:

- **Tenant-isolated learning:** derived material can inform improvements scoped
  to that tenant only.
- **Pooled learning:** derived material can contribute to a shared research
  corpus after sanitization and tenant opt-in, with the tenant receiving access
  to resulting promoted improvements under the same update policy as everyone
  else.

Opting out must not remove baseline product functionality. Opt-out tenants keep
their local runtime behavior and do not contribute learning packs.

Any improvement derived from learning packs remains research output until it is
approved through ADR-0040 and distributed through ADR-0039. This ADR does not
authorize direct runtime mutation, silent model updates, customer-data
exfiltration, or customer-facing benchmark claims.

## Consequences

- The data flywheel is privacy-preserving by construction and aligned with
  tenant-data authority.
- Research work has a real input stream without bypassing the promotion gate.
- Sanitization becomes a continuing obligation for every learning-pack schema
  and exporter.
- Product planning must handle opt-out, tenant-isolated, and pooled tenants in
  every consumer of learning artifacts.

## Alternatives Considered

- **Centralize raw customer records.** Rejected because it violates tenant-data
  authority and makes replay records a data-collection surface.
- **Require every tenant to contribute.** Rejected because contribution is a
  tenant choice, not a condition for baseline functionality.
- **Let learning output update runtime directly.** Rejected because ADR-0040
  requires explicit promotion before customer runtime can change.
