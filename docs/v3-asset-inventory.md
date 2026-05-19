# V3 Asset Inventory

Status: docs-only inventory.

This document inventories the older `Zovark_final` runtime assets that may feed
future V3 absorption work. It does not import code, change proof-package
schemas, capture fixtures, define the Capability Identity Contract, implement
Investigation Trace, or freeze a final architecture.

## Evidence Baseline

| Source | Ref | Role |
|---|---|---|
| `zovark-architecture` | `9e6337eb3c7caf2cedd1387384dd35f562be0d8c` | Current proof/replay repo after ADR index merge. |
| `Zovark_final` | `0290d6b879b5afc4565e9a5e7756f7364d120e85` | Older product/runtime repo default branch inspected for this inventory. |
| `docs/v3-ground-truth-check.md` | current repo | Ground-truth report for V3 versus V2 runtime truth. |
| `docs/adr-index-and-architecture-constraints.md` | current repo | Governing constraints and unresolved decision records. |
| `zovark/slice001/cli.py`, `tests/test_cli_verify.py` | current repo | Customer-readable verification summary behavior from PR #24. |

Validation labels used below:

- `real users`: production or design-partner use found in repo evidence.
- `SOC reviewed`: explicit SOC or practitioner review found in repo evidence.
- `synthetic only`: generated corpora or simulations only.
- `lab only`: local lab environments such as Juice Shop or SIEM lab.
- `benchmark only`: benchmark report exists but no customer validation found.
- `speculative`: design or roadmap idea without implementation evidence.
- `unknown`: evidence not found in inspected repos.

No asset below has repo evidence of real-user or SOC-reviewed validation.

## Scale And Throughput Truth

The strongest V3 benchmark artifact found is
`Zovark_final@0290d6b:docs/V3_BENCHMARK_REPORT.md`.

| Question | Evidence-backed answer |
|---|---|
| Current measured V3 submission throughput | About `1.6 alerts/s` in the V3 benchmark report. |
| Current measured V3 completion throughput | Not found as a full-corpus completed-throughput number. The report snapshot completed `164` Path A alerts and had `416` pending alerts. |
| Saved-plan hit rate | `164/164` completed alerts were Path A saved-plan executions in the snapshot. This is benchmark-subset evidence, not full production mix. |
| Novel-path rate | Novel-path completion rate is unknown. The report says `35` novel alerts were still awaiting LLM tool selection on an RTX 3050. |
| Path C / LLM bottleneck | Present. The benchmark says Path C novel alerts were pending because the RTX 3050 processes one LLM call at a time. |
| Path D fallback frequency | `0%` in the completed V3 benchmark snapshot. This is lab/benchmark evidence only. |
| v4.1 target gap | The current V3 evidence does not support the v4.1 target of `10K alerts/sec` ingest and about `100 investigation-worthy events/sec`. |
| Early-customer scale story | Evidence supports a low-volume, saved-plan-heavy design-partner story only. Novel-path and full-funnel throughput remain unproven. |

The v4.1 scale target remains aspirational relative to measured V3 evidence.
The V3 API has deduplication, batching, and backpressure code, but the inspected
benchmark does not prove enterprise-scale ingest or completion throughput.

## Asset Inventory

| Asset area | Path / commit evidence | Active/default/legacy/fallback status | Current implementation status | Maps to v4.1 domain | Maps to proof/replay contract? | Maps to Capability Identity Contract? | Validation status | Throughput or benchmark evidence | Keep / rewrite / defer / archive | Reason |
|---|---|---|---|---|---|---|---|---|---|---|
| Ingestion, dedup, batching | `Zovark_final@0290d6b:api/siem_ingest.go`, `api/alert_dedup.go`, `api/batch_buffer.go`, `api/backpressure.go`, `worker/stages/ingest.py`, `worker/redpanda_consumer.py` | Active runtime assets in older repo | SIEM ingestion, dedup hashes, Redis backpressure, batching, and worker ingest stage exist | Ingestion, Funnel, State | Future adapter input only; current Slice proof package still starts from static JSON | Candidate source identities for alert, dedup, batch, and tenant boundaries | synthetic only / benchmark only | Submission about `1.6 alerts/s` in V3 benchmark; no proven v4.1 target support | keep with rewrite | Useful runtime foundation, but scale and proof mapping are unproven. |
| SIEM alert handling | `Zovark_final@0290d6b:api/siem_ingest.go`, `api/siem.go`, `api/siem_pushback.go`, `docs/SIEM_INTEGRATION.md`, `scripts/pov/import_alerts.py` | Active or lab/runtime assets | Splunk HEC and Elastic-style SIEM ingestion/pushback code exists | Ingestion, Action, Integrations | No direct current proof contract; future evidence source | Candidate source-system and alert-shape identities | lab only / unknown | No SIEM customer throughput found | keep with rewrite | Important for live ingestion later, but must not bypass static proof semantics. |
| Tool library | `Zovark_final@0290d6b:worker/tools/catalog.py`, `extraction.py`, `analysis.py`, `parsing.py`, `scoring.py`, `detection.py`, `enrichment.py` | Active/default in V3 tools mode | Current default branch has `39` catalog entries; `v3.0.0` had `34` | Harness, Fact lane, Threat lane, Threat Intelligence, deterministic synthesis | Future tool outputs must become recorded evidence/trace inputs before proof synthesis | Yes, primary candidate: tool name, category, schema, implementation hash, version/ref | benchmark only | V3 benchmark completed Path A tool runs; no customer validation found | keep | Core V3 asset, but must be identity-bound before proof integration. |
| Tool runner | `Zovark_final@0290d6b:worker/tools/runner.py`, `worker/tools/tests/test_runner.py` | Active/default in V3 tools mode | In-process deterministic plan runner with timeout/error isolation and dependency-aware parallel batches | Harness, deterministic synthesis | Future trace should record plan steps, tool args, outputs, errors, and order | Yes, candidate executor identity and plan-step identity | benchmark only | V3 benchmark Path A completed through tools mode; no standalone runner throughput found | keep | This is the safest bridge from V3 runtime to replayable trace, if outputs are recorded. |
| Templates and saved plans | `Zovark_final@0290d6b:worker/tools/investigation_plans.json`, `worker/stages/analyze.py`, `migrations/062_v3_tool_calling.sql`, DB `agent_skills.investigation_plan` | Active/default for known alert types | Built-in plan JSON and DB-backed saved plans exist; current default has `25` plan keys | Harness, Learning, deterministic synthesis | Future adapter can map plan outputs to findings only after deterministic accept/reject rules | Yes, plan identity is required | benchmark only | Completed V3 benchmark subset was `164/164` Path A saved-plan executions | keep | Fast saved-plan path is real, but plan identity and versioning need a contract. |
| LLM tool selection | `Zovark_final@0290d6b:worker/stages/analyze.py`, `worker/tools/tool_subsets.py`, `worker/stages/llm_gateway.py`, `worker/llm_logger.py`, `migrations/046_llm_audit_log.sql` | Active fallback in V3 tools mode when no saved plan exists | LLM selects tools, not Python code, for no-plan cases; prompt hash/version support exists | Inference Gateway, Harness, Threat lane | Must map through future recorded model invocation records; current Slice replay cannot call live LLMs | Yes, model invocation and selected-plan identity needed | benchmark only | V3 benchmark says `35` novel alerts were awaiting LLM tool selection; completion rate unknown | defer | Needed for investigation body, but replay-safe recorded-output semantics must come first. |
| Final LLM / novel path | `Zovark_final@0290d6b:worker/stages/analyze.py`, `worker/stages/assess.py`, `worker/stages/llm_gateway.py` | Active for novel/no-plan and some assess paths | LLM use remains outside V2 code generation: tool selection and assessment/summary paths exist | Inference Gateway, Harness, deterministic synthesis | Current proof package has no live LLM path; future outputs must be recorded and accepted/rejected deterministically | Yes, model call, prompt, response, and acceptance identity needed | benchmark only | Novel-path completion not found; benchmark identifies RTX 3050 LLM queue bottleneck | defer | High product value but high replay risk without Investigation Trace. |
| AST and sandbox security | `Zovark_final@0290d6b:worker/stages/execute.py`, `sandbox/ast_prefilter.py`, `sandbox/seccomp_profile.json`, `tests/sandbox/*`, `config/seccomp-inference.json` | Legacy/fallback | V2 generated-code path and sandbox isolation remain present | Runtime safety, Action/State support | Only relevant when a fixture used V2 sandbox or Path D fallback | Yes for legacy/fallback execution identity | lab only | V2-era docs claim slower Path C; no current production validation found | defer / archive selectively | Keep for forensic fixture interpretation, but not as default V3 proof path. |
| V2 sandbox fallback / Path D | `Zovark_final@0290d6b:worker/stages/execute.py`, `worker/tools/tests/test_path_d.py`, `CLAUDE.md` | Fallback | Path D can fall back from failed V3 tool runner to V2 sandbox; explicit `ZOVARK_EXECUTION_MODE=sandbox` also exists | Harness, runtime safety | Future proof adapter must mark fallback provenance explicitly | Yes, fallback mode and generated-code hash identities needed | benchmark only | V3 benchmark reports `0%` Path D fallback in completed subset | keep as fallback | Important for compatibility and error recovery, but must not be treated as normal V3. |
| Template promotion flywheel | `Zovark_final@0290d6b:worker/stages/template_promoter.py`, `api/promotion_handlers.go`, `migrations/055_template_promotion.sql`, `migrations/059_template_promotion_quorum.sql`, `scripts/extract_template_from_investigation.py` | Mixed active/legacy | Promotion logic and DB columns for generated code/template promotion exist | Learning, Research Pipeline, Harness | No direct current proof mapping; promotion candidates should not mutate proof rules automatically | Yes later for skill/template identity and promotion provenance | unknown / lab only | No reliable throughput or customer validation found | defer | Needs ADR-0040-style candidate promotion discipline before absorption. |
| Governance | `Zovark_final@0290d6b:worker/stages/govern.py`, `api/governance_handlers.go`, `migrations/062_v3_tool_calling.sql` | Active V3 stage | Observe/assist/autonomous governance config exists; no LLM in govern stage | Action, Policy, State | Current proof handoff remains approval-required; V3 governance cannot replace vault authorization | Candidate policy/decision identity later | unknown / benchmark only | No real-user governance outcome evidence found | keep with rewrite | Useful policy asset, but must be reconciled with approval-required proof and future Vault runtime. |
| Telemetry and observability | `Zovark_final@0290d6b:worker/tracing.py`, `worker/events.py`, `api/otel.go`, `config/signoz/*`, `dashboard/src/telemetry.ts`, `config/signoz/dashboards/*.json` | Implemented runtime/lab assets | OpenTelemetry/Signoz and dashboard event streams exist | Observability, State | Current proof/replay verifier uses no telemetry or network | Possible telemetry identity later, not current CIC core | lab only / unknown | No production telemetry validation found | defer | Must respect ADR-0041 telemetry boundary before reuse. |
| SIEM lab | `Zovark_final@0290d6b:docker-compose.yml` SIEM/benchmark profiles, `scripts/pov/*`, `docs/JUICE_SHOP_BENCHMARK.md`, `scripts/benchmark/*` when present | Lab only | Juice Shop, SIEM lab, generated corpora, and demo scripts exist | Ingestion, Benchmarking, Harness | Useful fixture sources only; not proof contract source of truth | Candidate fixture provenance later | lab only / synthetic only | Juice Shop and V3 benchmark docs present; customer validation not found | keep as fixture source | Useful for PR #28 fixtures, but not buyer-proof evidence. |
| Deployment assets | `Zovark_final@0290d6b:docker-compose*.yml`, `deploy/docs/*`, `scripts/deploy.sh`, `scripts/k8s_*`, `scripts/test-airgap.sh`, `config/postgresql.conf`, `config/pg_hba.conf` | Runtime/platform assets | Multiple compose profiles and deployment guides exist | Deployment profiles, State, Control Plane | No current Slice proof mapping | Not CIC except runtime environment identity later | unknown / lab only | No deployment-scale proof found | defer | Useful later, but runtime rollout is explicitly after proof and trace semantics. |
| DPO experiments | `Zovark_final@0290d6b:scripts/dpo_train.py`, `dpo/*` if present in other refs, `docs/MODEL_TIER_STRATEGY.md` | Research/experiment | DPO and model-tier artifacts are present or referenced; current implementation status is incomplete from inspected default tree | Learning, Inference Gateway | No current proof mapping | Possible future model identity, not current | speculative / unknown | No verified performance evidence found | archive / defer | Do not import into proof path without model governance and trace. |
| AutoResearch | `Zovark_final@0290d6b:autoresearch/*`, including `tool_selection_prompt/*`, `redteam_nightly/*`, template/evaluation scripts | Research/lab | Prompt optimization, red-team vectors, and evaluation scripts exist | Learning, Research Pipeline, Threat Intelligence | Candidate outputs only; no direct proof mapping | Possible candidate capability source later | lab only / synthetic only | Local evaluation artifacts found; customer validation not found | defer | Fits ADR-0040 candidate-promotion model, not runtime authority. |
| Dashboard, API, runtime services | `Zovark_final@0290d6b:api/*`, `dashboard/*`, `worker/stages/*`, `worker/temporal_client.py`, `worker/activities.py` | Active older runtime assets | Go API, React dashboard, Temporal worker stages, integrations, approvals, shadow/response handlers exist | Harness, Action, State, Observability, Runtime platform | No direct current proof mapping; future adapter may consume runtime records | CIC may need task, workflow, action, and integration identities | lab only / unknown | No real-user runtime scale evidence found | defer / rewrite selectively | Large product body exists, but proof/replay semantics must govern absorption. |

## Not Found Or Unknown

| Item | Result |
|---|---|
| Real customer validation | Not found in inspected repo evidence. |
| SOC-reviewed validation | Not found in inspected repo evidence. |
| Production completion throughput | Not found. |
| Full-corpus V3 completion rate | Not found; V3 benchmark snapshot was incomplete. |
| Exact Fast Mode / Reasoning Mode runtime names | Not found as current `Zovark_final` runtime terms. |
| RamaLama references in `Zovark_final` | Not found in the original ground-truth report. Later v3.2.4.4 amendment names RamaLama as the local-SLM runtime and classifies legacy `Zovark_swami` local-inference work as salvage material, not implemented runtime. |
| Current proof-package schema mapping for V3 tool output | Not implemented. |
| Separate durable `tool_call_records` table | Not found in inspected migrations. Tool data appears in task outputs and plan fields. |

## Scale Risk

The current V3 assets do not prove the v4.1 target. The measured evidence shows:

- saved-plan Path A can be fast in a lab benchmark;
- no-plan/novel Path C depends on LLM tool selection and was pending in the V3 benchmark snapshot;
- submitted alerts and completed investigations are not the same throughput measure;
- API backpressure code exists, but no end-to-end enterprise ingest proof was found;
- Path D fallback was not observed in the completed snapshot, so fallback cost and frequency remain unknown.

The early-customer story should be constrained to low-volume or saved-plan-heavy
design partners until Track C produces measured completion throughput and
funnel-mix evidence.

## PR #27 Boundary

This inventory is an input to later work. It does not:

- choose final architecture;
- define Capability Identity Contract;
- define Investigation Trace;
- capture fixtures;
- build a V3-to-proof adapter;
- alter Slice proof-package files;
- change Replay V2 behavior;
- add live EDR, live LLM runtime, network calls, DB runtime, Vault runtime,
  dispatcher, Sentry, signing, or transparency-log work.
