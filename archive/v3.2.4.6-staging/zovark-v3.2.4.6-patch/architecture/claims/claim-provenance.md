# Claim Provenance

Every quantified product, architecture, security, schedule, support, capacity, reliability, latency, throughput, false-positive, retention, RPO/RTO, cost, or patch-response claim must carry one provenance tag.

Allowed tags:

- `[hypothesis:evidence-milestone]` for internal claims that still need evidence.
- `[measured:artifact-id,YYYY-MM-DD]` for claims backed by an artifact present in this repository.
- `[vendor-cited:citation-id]` for claims backed by a real vendor citation file, URL, or reference.
- `[policy-commitment:owner,review-cadence]` for commitments owned by a role and reviewed on a fixed cadence.

Rules:

- Customer-facing documents must not contain `[hypothesis:*]`.
- Measured claims must point to an artifact that exists in this tree or in the post-apply baseline tree.
- Vendor-cited claims must point to a real citation.
- Policy commitments must name an owner and review cadence.
- If the enforcement artifact does not exist, describe the claim as a planned deliverable and name the milestone.

No claim-provenance checker exists in this patch tree. `scripts/check_claim_provenance.py` is an M0 deliverable before customer-facing architecture review.
