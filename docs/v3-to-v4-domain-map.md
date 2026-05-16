# V3 To v4.1 Domain Map

Status: docs-only mapping.

This document maps the inspected `Zovark_final` V3 runtime assets to the broader
v4.1 architecture domains and the current proof/replay contract. It does not
resolve architecture conflicts, define a final Capability Identity Contract,
change schemas, capture fixtures, or implement an adapter.

## Mapping Principles

- Repo evidence wins over stale handover assumptions.
- V3 tools mode is the active/default path in the inspected older runtime.
- V2 code generation and Docker sandbox remain legacy/fallback paths.
- The current proof/replay repo remains the Slice 001 and Replay V2 baseline.
- Any V3 model or tool output must be recorded before it can participate in
  deterministic proof or replay.
- Product-mode labels such as Fast Mode and Reasoning Mode are future design
  language unless a later spec maps them to concrete runtime behavior.

## Domain Map

| v4.1 domain / component | V3 evidence in `Zovark_final@0290d6b` | Current status | Proof/replay relationship | Capability Identity implication | Gap / risk | Next PR input |
|---|---|---|---|---|---|---|
| Ingestion | `api/siem_ingest.go`, `worker/stages/ingest.py`, `worker/redpanda_consumer.py` | Implemented older runtime | Future input to evidence ledger; current proof uses static JSON | Need alert source, tenant, ingest batch, and normalization identities | Live ingest scale and customer validation unknown | PR #28 fixture capture; PR #31 adapter |
| Funnel | `api/alert_dedup.go`, `api/batch_buffer.go`, `api/backpressure.go`, `migrations/064_dedup_count.sql`, `migrations/032_stampede_protection.sql` | Implemented older runtime | Current verifier does not use runtime funnel state | Need dedup hash, batch, queue, and retry identities if included in proof | v4.1 target not proven; backpressure code is not throughput proof | PR #27 scale note; PR #29 synthesis |
| Threat Intelligence | `worker/tools/enrichment.py`, `worker/integrations/abuseipdb.py`, `virustotal.py`, `migrations/038_kev_processing.sql` | Mixed local tools and external integrations | Local enrichment can become recorded evidence; live external lookup is later runtime | Need source and lookup-result identities; external calls need recorded output | Live intel/network calls are out of current proof scope | PR #30 trace spec before runtime |
| Harness | `worker/stages/investigation_workflow.py`, `worker/stages/analyze.py`, `execute.py`, `assess.py`, `govern.py`, `store.py` | Implemented, but historical wire name `InvestigationWorkflowV2` remains | Future harness output must adapt into tape/evidence/findings/verdict | Need workflow, stage, plan, tool, fallback, and governance identities | Name can mislead; mixed V2/V3 code paths require explicit mode capture | PR #29 CIC; PR #31 adapter |
| Fact lane | Extraction/parsing/enrichment tools in `worker/tools/*` | Implemented as tool categories, not named lane | Tool outputs can support evidence-backed findings after trace design | Need tool-output schema and evidence-ref identity | No current proof trace for tool I/O | PR #30 Investigation Trace |
| Threat lane | Detection/scoring/MITRE-related tools in `worker/tools/detection.py`, `scoring.py`, `enrichment.py` | Implemented as tool categories, not named lane | Outputs can propose findings; deterministic synthesis must accept/reject | Need candidate finding and accepted/rejected finding identities | Existing V3 verdicts are not the same as Slice proof verdict contract | PR #30 and PR #31 |
| Deterministic Synthesis Engine | `worker/stages/assess.py`, scoring/detection tools, current proof `zovark/slice001/findings.py` and `verdict.py` | Present in both repos but with different semantics | Current proof layer is authoritative for package verdict derivation | Need mapping from V3 outcomes to proof findings/verdict | Risk of trusting V3 summaries instead of re-deriving proof artifacts | PR #31 adapter |
| Inference Gateway | `worker/stages/llm_gateway.py`, `worker/llm_client.py`, `worker/model_router.py`, `worker/llm_logger.py`, `migrations/046_llm_audit_log.sql` | Partial/active for tool selection and assessment LLM calls | Live inference cannot run during replay; outputs must be recorded | Need model, prompt, response, hash, provider, and policy identities | Local-vs-cloud config conflict remains unresolved | PR #30 trace; later Gateway MVP |
| Temporal workflow history | `worker/stages/investigation_workflow.py`, `worker/activities.py`, `worker/temporal_client.py`, `api/temporal.go` | Implemented runtime | Current proof package does not depend on Temporal | Need workflow/run/stage identity if fixture comes from Temporal | Runtime history is not exported as current proof evidence | PR #28 fixtures may capture minimal runtime metadata |
| Recorded model/tool invocations | `llm_audit_log`, `prompt_hash`, `prompt_version`, `tool_results`, `tools_executed`, `plan_executed` | Hooks exist, no current proof trace | Must become recorded-output replay substrate before live model/tool replay | Central CIC requirement | No separate durable `tool_call_records` table found | PR #30 Investigation Trace |
| Cloud egress policy | `.env.example`, `docker-compose.yml`, `CLAUDE.md`, `worker/settings.py` | Conflicting evidence: local-inference docs vs OpenAI-compatible defaults | Current proof/replay has no network calls | Need egress policy and provider identity before runtime import | Deployment truth conflict; cannot claim air-gapped default without resolving config | PR #29 conflict resolution |
| Action domain | `api/approval_handlers.go`, `api/response_handlers.go`, `api/shadow.go`, `api/vault.go`, `worker/stages/govern.py` | Implemented broader runtime assets | Current proof handoff remains approval-required and pending | Need action, policy, approval, authorization, and rollback identities | V3 governance cannot substitute for Vault authorization | Later runtime after CIC/trace |
| State domain | Postgres migrations, Redis/Valkey use, ClickHouse telemetry, `migrations/072_schema_migrations_ledger.sql` | Implemented older runtime | Current proof package is file-based; no DB dependency | Need DB schema/ref identity only for runtime fixture provenance | Migration ledger integrity risk; live DB outside current proof scope | PR #28 fixture metadata; PR #29 |
| Replay domain | Current repo `package_verifier.py`, `replay.py`, `cli.py`; older repo audit/log assets | Current proof repo is authoritative | Offline verifier already validates existing package directory | Need future adapter to produce packages verifier can validate | Do not change nine-file contract without separate package-contract PR | PR #32 end-to-end proof gate |
| Audit chain | Current repo `audit.py`; older repo `migrations/067_audit_platform_governance_events.sql`, `046_llm_audit_log.sql` | Current proof audit is deterministic; older runtime has logs | Runtime logs are not the current audit-chain-entry contract | Need mapping from runtime events to proof audit entry or trace | Risk of conflating operational audit logs with proof audit chain | PR #31 adapter |
| Evidence chain | Current repo evidence ledger; older runtime IOCs/evidence refs in outputs and migrations such as `053_ioc_evidence_refs.sql` | Partial in older runtime; complete for Slice proof | V3 fixture evidence must be normalized into proof raw evidence | Need evidence source, hash, ref, and transformation identities | Upstream completeness cannot be claimed | PR #28 fixtures; PR #31 adapter |
| Signed manifest | Not found as current V3 runtime package feature | Not implemented | Current proof package has no manifest/provenance/signing | Future package-contract identity only | Do not imply cryptographic signing today | Future package-contract PR, not PR #27 |
| Evidentiary package | Current repo nine-file package; older runtime reports/docs | Implemented only in current proof repo | Current verifier validates package consistency, not legal completeness | Need package identity later if manifest/provenance added | Avoid legal-admissibility claims | Later package-contract PR |
| Deployment profiles | `docker-compose*.yml`, `deploy/docs/*`, `scripts/deploy.sh`, `scripts/test-airgap.sh` | Implemented platform assets | No current proof dependency | Need deployment/environment identity for measured runtime fixtures | Profiles conflict with proof-local constraints; no production validation found | Later runtime work |
| RamaLama/local inference | Recovered local-inference material includes llama-server-style work; v3.2.4.4 amendment names RamaLama as the local-SLM runtime | Architecture naming decision only; no runtime implementation | Current proof verifier uses no live model runtime and replay never re-inferences | Future local model provider identity is required before integration | Legacy local-inference assets require retraining/rework under bounded-envelope semantics | Later Inference Gateway |
| WASM content safety | Not found in inspected V3 runtime evidence | Not implemented | No proof relationship today | Unknown | Do not add until separately justified | Later platform work, if any |
| Contract registry | Current repo OpenSpec specs and validators; older repo migrations/specs | Partial | Current specs govern proof/replay | CIC should align with specs and ADR hierarchy | No runtime contract registry found | PR #29 |
| Semantic invariants | Current repo tests/validators; older repo tool and sandbox tests | Partial | Current proof invariants remain authoritative | CIC and Trace must preserve fail-closed semantics | Old runtime tests were not rerun in this PR | PR #29 and PR #30 |
| Replay V2 package verifier | Current repo `zovark/slice001/package_verifier.py`, CLI verify tests | Implemented | Verifies exported package offline | Adapter output must satisfy verifier | None for PR #27 | PR #32 |
| AI Investigation Trace V1 | Hooks only; not implemented | Future work | Required before live/recorded model/tool output enters proof layer | Central identity object set still undefined | Do not import V3 model/tool output without trace | PR #30 |
| Fast Mode | Not found as current V3 runtime term | Product-mode language only | Could map later to saved-plan path after trace semantics exist | Needs explicit design decision | Do not claim it exists today | After PR #30 |
| Reasoning Mode | Not found as current V3 runtime term | Product-mode language only | Could map later to LLM-selected/deeper investigation after trace semantics exist | Needs explicit design decision | Do not claim it exists today | After PR #30 |

## Scale Mapping

| Scale dimension | V3 evidence | v4.1 target relationship | Risk |
|---|---|---|---|
| Ingest submission | V3 benchmark reports about `1.6 alerts/s` submitted | Far below the v4.1 target of `10K alerts/sec` ingest | Current evidence does not prove enterprise ingest. |
| Completion throughput | Full-corpus completion throughput not found; snapshot completed `164` Path A alerts and had `416` pending | Cannot compare fairly to about `100 investigation-worthy events/sec` without full completion measurement | Completion bottleneck remains unknown. |
| Saved-plan fast path | Path A completed subset used saved plans and tools mode; Path A under `<100ms` in benchmark | Promising for known alert types | Depends on saved-plan hit rate in real customer mix. |
| Novel/no-plan path | `35` novel alerts pending LLM tool selection on RTX 3050 | Does not support high-volume novel investigations today | LLM queue is the visible bottleneck. |
| Path D fallback | `0%` in completed benchmark subset | No evidence of fallback cost at scale | Fallback behavior still needs fixture capture. |
| Early-customer fit | Low-volume, saved-plan-heavy environments only | Not an enterprise-scale claim | Customer discovery and Track C measurement needed. |

## Mapping Into Upcoming Work

| Upcoming PR | Inputs from this map | Boundary |
|---|---|---|
| PR #28 V3 fixture capture | Capture representative saved-plan, LLM tool-selection, fallback, governance, and runtime metadata cases | No schema changes and no adapter implementation. |
| PR #29 Capability Identity Contract and final synthesis | Define identities for tools, plans, model calls, fallback modes, workflow stages, evidence, governance, and package outputs | Must resolve or explicitly defer cloud/local inference and scale conflicts. |
| PR #30 Investigation Trace V1 | Specify recorded model/tool invocation records, candidate findings, accepted/rejected findings, and deterministic synthesis boundaries | No unrecorded live model/tool replay. |
| PR #31 V3 fixture to proof-package adapter | Convert captured V3 fixture shapes into current proof package semantics | Existing verifier must remain the proof gate. |
| PR #32 V3 package verification gate | Verify generated V3 proof package with Replay V2 verifier | Fail closed on mismatch or tampering. |

## Explicit Non-Decisions

This map does not decide:

- final architecture;
- Capability Identity Contract fields;
- Investigation Trace schema;
- manifest/provenance package contract;
- signing, transparency logs, or key management;
- live EDR or SIEM connector rollout;
- cloud model egress policy;
- RamaLama local-SLM runtime implementation;
- Vault runtime authorization;
- action execution;
- dashboard/runtime deployment;
- customer buyer-pain roadmap commitments.

These decisions require later scoped PRs and, where necessary, ADR or OpenSpec
changes.
