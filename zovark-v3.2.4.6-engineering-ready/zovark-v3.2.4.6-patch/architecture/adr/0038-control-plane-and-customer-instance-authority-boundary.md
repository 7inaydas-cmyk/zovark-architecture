# ADR-0038 — Control Plane and Customer-Instance Authority Boundary

**Status:** Proposed (becomes Accepted on M1-ARCH-001 merge).
**Date:** 30 April 2026.
**Established by:** architecture extension.
**Amends:** ADR-0011 (lifts air-gap from "later topology" to "primary deployment mode for control-plane subsystem").
**Related:** ADR-0001 §11 (zvadmin disambiguation), ADR-0003, ADR-0008, ADR-0019, ADR-0022, ADR-0039, ADR-0040, ADR-0041.

## Review metadata

- **Scope:** M1 architecture; M2 control-plane data-classification enforcement; M10 air-gap operational proof.
- **Affected invariants:** INV-001, INV-003, INV-029, INV-032.
- **Implementation status:** Document-only in this patch except for schema-presence checks. Runtime control-plane data-classification enforcement is an M2 deliverable. Air-gap operational proof is an M10 deliverable.
- **Enforcement mechanism:** Current: `scripts/check_control_plane_schemas_present.py` verifies required control-plane schemas are present. Planned M2: `check_control_plane_data_classification.py` scans control-plane code paths and storage schemas for ADR-0041 forbidden fields.
- **Supersession/amendment links:** Amends ADR-0011. Not superseded.
- **Claim provenance:** No measured runtime claims. Operational topology is a design decision, not evidence.

## Context

Zovark customer instances need fleet visibility and managed updates without violating tenant data authority. Regulated customers require air-gap operation. SaaS customers benefit from automatic update delivery. The architecture must support all three topologies (SaaS-connected, hybrid, air-gap) from a single design.

## Decision

Zovark will operate a Control Plane subsystem that:

- Maintains a **pseudonymized** instance registry. Each customer instance has a cryptographic pseudonym; mapping pseudonym → customer identity requires elevated role + audit log entry.
- Stores registry data with **per-row encryption keys** (no single-key compromise discloses everything).
- Distributes signed update bundles under customer policy control.
- **Never holds**: customer evidence, raw alerts, investigation records, vault material, EDR credentials, audit log entries, replay records (per ADR-0041 forbidden list).
- Operates in three modes (SaaS-connected, hybrid, air-gap) from a single API surface, with offline-package equivalents for every API.
- Authenticates customer instances using per-instance certificates issued at deployment; certificate issuance and rotation procedures are M2 deliverables.
- Has its own future disaster-recovery plan: registry data replication, RPO/RTO, same-region HA, cross-region DR, and restore drills are M3 deliverables. Loss of the Control Plane DB must not affect customer instance data authority.

## Disambiguation from zvadmin

Per `zovark.md §11`, **zvadmin** is the customer-side operator console for managing their own Zovark instance (creating tenants, configuring policies, viewing their own data). It is part of the Customer Instance subsystem and is customer-authenticated. The **Control Plane** is the Zovark-side fleet management subsystem. They are different. They run on different infrastructure. They have different authentication models. They have different data classifications.

## Customer instance authority

The Customer Instance is and remains tenant-data authoritative. The Control Plane recommends; the Customer Instance decides.

## Healer and Mesh placement

ADR-0019 (Mesh agent pool) and ADR-0022 (Healer service) are components of the Customer Instance subsystem. They run entirely within the customer environment. Mesh investigation summaries and Healer findings are **never** sent to the Control Plane (no telemetry-allowlist field exists for them; adding any would require ADR-0041 amendment).

## Consequences

- Adds a control-plane subsystem requiring its own deployment, operational SLOs, disaster recovery, and security review.
- Creates a new attack surface (control plane DB) that must be threat-modeled separately.
- Enables fleet-wide visibility, version compatibility checks, and managed update flows.
- Forces explicit air-gap support in the API design from day one.
- Per-row encryption + pseudonymization adds operational complexity in elevated-role lookups.

## Alternatives considered

- *No control plane*: rejected; foregoing fleet visibility and managed updates concedes a major buyer requirement.
- *Centralized SaaS-only model*: rejected; incompatible with regulated and air-gap customers.
- *Customer-self-managed updates only*: rejected; foregoes supply-chain integrity benefits.
- *Combine zvadmin and Control Plane into a single subsystem*: rejected; mixes customer-authenticated and Zovark-authenticated trust boundaries.
