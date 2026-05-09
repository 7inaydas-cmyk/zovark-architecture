# V3 Fixture Capture Report

Status: docs-only fixture capture report.

This report captures representative V3 fixture evidence from the older
`Zovark_final` runtime before designing the Capability Identity Contract,
Investigation Trace V1, or a V3-to-proof-package adapter. It is report-only:
no fixture files are added because the current repo has no clear policy for
committing V3 runtime fixture files, and several required cases depend on DB,
LLM, Docker, Temporal, or local runtime services.

## Evidence Baseline

| Source | Ref | Role |
|---|---|---|
| `zovark-architecture` | `7f83b430d7d8e17ecb4697b1794dfeca4d43eccc` | Current repo after PR #27 merge. |
| `Zovark_final` | `0290d6b879b5afc4565e9a5e7756f7364d120e85` | Older product/runtime repo default branch inspected for fixture evidence. |
| `docs/v3-ground-truth-check.md` | current repo | Establishes V3 tools mode as default and V2 sandbox/codegen as legacy/fallback. |
| `docs/v3-asset-inventory.md` | current repo | Lists V3 assets and scale limitations. |
| `docs/v3-to-v4-domain-map.md` | current repo | Maps V3 runtime evidence to v4.1 domains and proof/replay boundaries. |
| `docs/adr-index-and-architecture-constraints.md` | current repo | Requires fixture capture before CIC, Trace, and adapter work. |

Fixture classification:

- `captured from static tests`: field shape is visible in committed tests or
  code, but no new runtime fixture file is committed here.
- `not reproduced`: a case requires local services or credentials not used in
  this PR.
- `lab only`: fixture evidence comes from local tests, generated corpora, or
  benchmark reports.
- `unknown`: evidence was not found in inspected repos.

## Summary

| Required case | Capture status | Evidence quality | Reason |
|---|---|---|---|
| V3 saved-plan deterministic path | Captured from static tests | lab only | `worker/tools/tests/test_runner.py` and `test_path_d.py` show plan, input alert, tool execution, tool outputs, findings, IOCs, risk, and verdict. |
| V3 LLM-selected tool path | Not reproduced | code evidence only | `worker/stages/analyze.py` implements Path C tool selection and prompt/version logging, but reproducing it requires an LLM endpoint and runtime settings. |
| V3 tool-runner error with Path D fallback | Captured from static tests | lab only / mocked | `worker/tools/tests/test_path_d.py` patches V3 failure and V2 fallback output. |
| Explicit `ZOVARK_EXECUTION_MODE=sandbox` V2 run | Captured from static tests | lab only / mocked | `worker/tools/tests/test_path_d.py` verifies explicit sandbox mode bypasses V3 and calls `_execute_v2_sandbox`. |
| Governance observe/assist/autonomous outcomes | Partially captured from code/tests | lab only / code evidence | `worker/stages/govern.py` implements all three modes; tests cover assist/benign, while observe/autonomous are code-evidence only here. |
| Institutional knowledge lookup | Captured from static tests | lab only | `worker/tools/tests/test_enrichment.py` and `worker/stages/context_loader.py` show fields and DB loader behavior. |
| Correlation history lookup | Captured from static tests | lab only | `worker/tools/tests/test_runner.py`, `test_redteam_v3.py`, and `worker/tools/enrichment.py` show correlation result shape. |

No case in this report is real-user or SOC-reviewed evidence.

## Fixture Case 1: V3 Saved-Plan Deterministic Path

| Field | Captured / observed value shape |
|---|---|
| Input alert | Synthetic SIEM event dict with fields such as `title`, `source_ip`, `username`, `rule_name`, and `raw_log`. |
| Ingest metadata | Not captured in static tool-runner tests; workflow expects `task_id`, `tenant_id`, `task_type`, `trace_id`, dedup fields, and skill fields from `IngestOutput`. |
| Dedup/batching decision | Not captured. Dedup exists in `api/alert_dedup.go` and `worker/stages/ingest.py`, but not in the saved-plan unit fixture. |
| Plan/template selected | Built-in plan from `worker/tools/investigation_plans.json`; examples include `brute_force`, `phishing_investigation`, and `kerberoasting`. |
| Tool calls | Plan steps such as `detect_kerberoasting`, `extract_ipv4`, `score_brute_force`, `correlate_with_history`, and `map_mitre`. |
| Tool outputs | `worker/tools/runner.py` returns `findings`, `iocs`, `risk_score`, `verdict`, `tools_executed`, `tool_names`, `tool_results`, and `errors`. |
| Model invocations | None for saved-plan Path A in the observed tests. |
| `prompt_hash` / `prompt_version` | Not present for saved-plan Path A. |
| `generated_code` | Not present for V3 tools mode. |
| AST validation / sandbox result | Not used. |
| Findings | Produced by detection/scoring tools and aggregated by the runner. |
| Verdict | Derived by `worker/tools/runner.py` through `verdict.derive_verdict(..., execution_mode="tools")`. |
| Governance decision | Not part of tool-runner fixture; applied later by `worker/stages/govern.py`. |
| Stored output fields | `worker/stages/store.py` can persist `execution_mode`, `path_d_fallback`, `path_d_reason`, `autonomy_level`, and `tools_executed`. |

Evidence paths:

- `Zovark_final@0290d6b:worker/tools/tests/test_runner.py`
- `Zovark_final@0290d6b:worker/tools/tests/test_path_d.py`
- `Zovark_final@0290d6b:worker/tools/runner.py`
- `Zovark_final@0290d6b:worker/tools/investigation_plans.json`
- `Zovark_final@0290d6b:worker/stages/execute.py`

Suggested safe reproduction, if the old repo test dependencies are installed:

```bash
cd /tmp/zovark_final_groundtruth
PYTHONPATH=worker pytest worker/tools/tests/test_runner.py::TestBasicPlanExecution::test_detection_tool -q
PYTHONPATH=worker pytest worker/tools/tests/test_path_d.py::TestNormalV3Execution::test_successful_v3_with_detection -q
```

This PR did not run those old-repo tests or commit their outputs.

## Fixture Case 2: V3 LLM-Selected Tool Path

| Field | Captured / observed value shape |
|---|---|
| Input alert | `IngestOutput.siem_event` passed to `worker/stages/analyze.py`. |
| Ingest metadata | `task_id`, `tenant_id`, `task_type`, `skill_id`, `skill_methodology`, `skill_template`, `trace_id`. |
| Dedup/batching decision | Not captured. |
| Plan/template selected | No saved plan; Path C calls LLM to select tools and returns `AnalyzeOutput(plan=..., source="llm_tool_call", path_taken="C", execution_mode="tools")`. |
| Tool calls | LLM response is parsed by `_parse_tool_plan()`, validated against `TOOL_CATALOG`, deduplicated, and capped. |
| Tool outputs | Not captured because the LLM selection path was not reproduced. |
| Model invocations | `worker/stages/llm_gateway.py` returns `content`, `tokens_in`, `tokens_out`, `latency_ms`, `model`, and `prompt_version`. |
| `prompt_hash` / `prompt_version` | `prompt_hash` is computed and stored in `llm_audit_log`; `prompt_version` is returned and stored in `llm_audit_log`. |
| `generated_code` | Not used in V3 LLM tool-selection path. |
| AST validation / sandbox result | Not used unless Path D fallback later triggers V2 sandbox. |
| Findings / verdict | Not captured at this stage; later produced by tool execution and assess. |
| Governance decision | Not captured. |
| Stored output fields | Workflow passes `tokens_in`, `tokens_out`, `path_taken`, `execution_mode`, and `plan_executed` to store. |

Evidence paths:

- `Zovark_final@0290d6b:worker/stages/analyze.py`
- `Zovark_final@0290d6b:worker/stages/llm_gateway.py`
- `Zovark_final@0290d6b:migrations/046_llm_audit_log.sql`
- `Zovark_final@0290d6b:migrations/050_model_performance_tracking.sql`

Blocked capture reason:

- Reproduction requires configured LLM endpoint/settings and possibly DB-backed
  tenant/task context. This PR intentionally does not call live LLMs, network,
  DB, or external services.

## Fixture Case 3: V3 Tool-Runner Error With Path D Fallback

| Field | Captured / observed value shape |
|---|---|
| Input alert | Synthetic dict with `raw_log` and `execution_mode="tools"`. |
| Ingest metadata | Not captured in Path D unit tests. |
| Dedup/batching decision | Not captured. |
| Plan/template selected | Broken or empty plan in tests; e.g. `[{\"tool\": \"broken_tool\", \"args\": {}}]`. |
| Tool calls | V3 `_execute_v3_tools` is patched to fail in Path D tests. |
| Tool outputs | V2 fallback output is patched as an `ExecuteOutput` dict. |
| Model invocations | None captured in Path D unit tests. |
| `generated_code` | Required by real `_execute_v2_sandbox`; mocked tests do not capture real generated code. |
| AST validation / sandbox result | Real path would call `_ast_check()` and `_run_in_sandbox()`; unit tests mock `_execute_v2_sandbox`. |
| Findings | Mocked V2 output preserves findings such as `{\"title\": \"Attack detected\"}`. |
| Verdict | Not directly captured in execute-stage fallback; later assess derives verdict. |
| Governance decision | Not captured. |
| Stored output fields | `execution_mode=\"sandbox_fallback\"`, `path_d_fallback=True`, and `path_d_reason=<V3 error>` are captured in code/test expectations. |

Evidence paths:

- `Zovark_final@0290d6b:worker/tools/tests/test_path_d.py`
- `Zovark_final@0290d6b:worker/stages/execute.py`
- `Zovark_final@0290d6b:worker/stages/__init__.py`

Suggested safe reproduction:

```bash
cd /tmp/zovark_final_groundtruth
PYTHONPATH=worker pytest worker/tools/tests/test_path_d.py::TestV3FailureTriggersPathD -q
```

This PR did not run that old-repo test or commit its mocked output.

## Fixture Case 4: Explicit `ZOVARK_EXECUTION_MODE=sandbox` V2 Run

| Field | Captured / observed value shape |
|---|---|
| Input alert | Synthetic dict with `execution_mode="sandbox"`, `code`, and `siem_event` in test. |
| Ingest metadata | Not captured. |
| Dedup/batching decision | Not captured. |
| Plan/template selected | Not relevant for explicit sandbox mode. |
| Tool calls | None. |
| Tool outputs | None. |
| Model invocations | Analyze-stage code generation may have happened upstream, but explicit sandbox test mocks the execute stage only. |
| `generated_code` | Real sandbox path requires `code`; workflow stores `generated_code` from analyze output. |
| AST validation / sandbox result | Real path uses `_ast_check()`, sandbox policy, Docker `--network=none`, seccomp profile, timeout, and resource limits. Test verifies routing to `_execute_v2_sandbox`. |
| Findings / verdict | Sandbox output can include findings, IOCs, risk score, and recommendations. Test fixture only verifies execution mode. |
| Governance decision | Not captured. |
| Stored output fields | Store can persist `generated_code`, `path_taken`, `execution_mode`, and output payload. |

Evidence paths:

- `Zovark_final@0290d6b:worker/tools/tests/test_path_d.py`
- `Zovark_final@0290d6b:worker/stages/execute.py`
- `Zovark_final@0290d6b:tests/sandbox/*`
- `Zovark_final@0290d6b:sandbox/seccomp_profile.json`

Suggested safe reproduction:

```bash
cd /tmp/zovark_final_groundtruth
PYTHONPATH=worker pytest worker/tools/tests/test_path_d.py::TestGlobalSandboxMode::test_sandbox_mode_no_path_d -q
```

This PR did not run Docker sandbox execution or commit sandbox outputs.

## Fixture Case 5: Governance Observe / Assist / Autonomous Outcomes

| Field | Captured / observed value shape |
|---|---|
| Input alert | Governance stage consumes assessed investigation dict plus `tenant_id`, `task_type`, and `verdict`. |
| Ingest metadata | `tenant_id` and `task_type` are used to query `governance_config`. |
| Dedup/batching decision | Not applicable. |
| Plan/template selected | Not applicable. |
| Tool calls / outputs | Not applicable. |
| Model invocations | None in governance stage. |
| Findings / verdict | `verdict` controls `needs_human_review` depending on autonomy level. |
| Governance decision | Code implements `observe`, `assist`, and `autonomous`; test captures `assist` with benign verdict producing no review. |
| Stored output fields | `needs_human_review`, `review_reason`, and `autonomy_level`. |

Observed behavior from `worker/stages/govern.py`:

- `observe`: all investigations require analyst review.
- `assist`: non-benign verdicts require analyst review; benign does not.
- `autonomous`: inconclusive/error/manual-review style verdicts require analyst review; other verdicts do not.
- Unknown autonomy defaults to review.

Evidence paths:

- `Zovark_final@0290d6b:worker/stages/govern.py`
- `Zovark_final@0290d6b:worker/tests/test_ticket4_temporal_activity_env.py`
- `Zovark_final@0290d6b:migrations/062_v3_tool_calling.sql`
- `Zovark_final@0290d6b:api/governance_handlers.go`

Capture limitation:

- Observe and autonomous are code-evidence only in this report. A full fixture
  set should run all three modes against the same assessed payload after DB
  setup or deterministic test patching.

## Fixture Case 6: Institutional Knowledge Lookup

| Field | Captured / observed value shape |
|---|---|
| Input alert | `siem_event` fields such as `source_ip`, `username`, `hostname`, and `dest_ip`. |
| Ingest metadata | `tenant_id` is needed for DB-backed lookup. |
| Dedup/batching decision | Not applicable. |
| Plan/template selected | Plans can include `lookup_institutional_knowledge` with `knowledge_base=\"$institutional_knowledge\"`. |
| Tool calls | `lookup_institutional_knowledge(entities, knowledge_base)`. |
| Tool outputs | `known_entities`, `baselines`, `analyst_notes`, and `has_context`. |
| Model invocations | None in the tool. |
| Findings / verdict | Tool output can influence plan output but does not by itself define proof findings. |
| Governance decision | Not part of the tool fixture. |
| Stored output fields | Stored indirectly via tool results if included in output payload. |

Evidence paths:

- `Zovark_final@0290d6b:worker/tools/enrichment.py`
- `Zovark_final@0290d6b:worker/tools/tests/test_enrichment.py`
- `Zovark_final@0290d6b:worker/stages/context_loader.py`
- `Zovark_final@0290d6b:worker/tools/investigation_plans.json`
- `Zovark_final@0290d6b:migrations/062_v3_tool_calling.sql`

Suggested safe reproduction:

```bash
cd /tmp/zovark_final_groundtruth
PYTHONPATH=worker pytest worker/tools/tests/test_enrichment.py::TestLookupInstitutionalKnowledge -q
```

This PR did not run that old-repo test or commit its output.

## Fixture Case 7: Correlation History Lookup

| Field | Captured / observed value shape |
|---|---|
| Input alert | IOC values or fields such as `source_ip`, `dest_ip`, `username`, and `hostname`. |
| Ingest metadata | `tenant_id` is needed for DB-backed context loading. |
| Dedup/batching decision | Not applicable. |
| Plan/template selected | Many built-in plans end with `correlate_with_history`. |
| Tool calls | `correlate_with_history(ioc_values, lookback_hours, history_context)`. |
| Tool outputs | `related_investigations`, `kill_chain_stage`, `escalation_recommended`, and `correlation_count`. |
| Model invocations | None in the tool. |
| Findings / verdict | Correlation can affect plan branching and escalation but is not current proof verdict logic. |
| Governance decision | Not part of the tool fixture. |
| Stored output fields | Stored indirectly via `tool_results` and output payload if preserved. |

Evidence paths:

- `Zovark_final@0290d6b:worker/tools/enrichment.py`
- `Zovark_final@0290d6b:worker/tools/tests/test_runner.py`
- `Zovark_final@0290d6b:worker/tools/tests/test_redteam_v3.py`
- `Zovark_final@0290d6b:worker/stages/context_loader.py`
- `Zovark_final@0290d6b:worker/tools/investigation_plans.json`

Suggested safe reproduction:

```bash
cd /tmp/zovark_final_groundtruth
PYTHONPATH=worker pytest worker/tools/tests/test_runner.py::TestConditionalBranching::test_boolean_condition -q
```

This PR did not run that old-repo test or commit its output.

## Fields That Actually Exist

The inspected runtime code exposes these fields or field groups:

- `IngestOutput`: `task_id`, `tenant_id`, `task_type`, `siem_event`, `prompt`,
  `is_duplicate`, `duplicate_of`, `dedup_reason`, `pii_masked`,
  `pii_entity_map_key`, `skill_id`, `skill_template`, `skill_params`,
  `skill_methodology`, `trace_id`.
- `AnalyzeOutput`: `code`, `source`, `path_taken`, `skill_id`,
  `preflight_passed`, `preflight_fixes`, `tokens_in`, `tokens_out`,
  `generation_ms`, `plan`, `execution_mode`.
- `ExecuteOutput`: `stdout`, `stderr`, `exit_code`, `status`, `iocs`,
  `findings`, `risk_score`, `recommendations`, `execution_ms`, `retries_used`,
  `execution_mode`, `path_d_fallback`, `path_d_reason`.
- Tool runner result: `findings`, `iocs`, `risk_score`, `verdict`,
  `tools_executed`, `tool_names`, `tool_results`, `errors`.
- `AssessOutput`: `verdict`, `risk_score`, `severity`, `confidence`,
  `false_positive_confidence`, `entities`, `edges`, `blast_radius`,
  `recommendations`, `memory_summary`.
- Assess-stage extras: `mitre_attack`, `investigation_metadata`,
  `plain_english_summary`, optional `mitre_attack_validated`,
  `compliance_mapping`.
- Governance extras: `needs_human_review`, `review_reason`, `autonomy_level`.
- Store output/payload: `generated_code`, `path_taken`, `execution_mode`,
  `path_d_fallback`, `path_d_reason`, `tools_executed`, `model_used`,
  `plain_english_summary`, `mitre_attack`, and task status fields.
- LLM audit fields: `stage`, `task_type`, `model_name`, `tokens_in`,
  `tokens_out`, `latency_ms`, `prompt_hash`, `prompt_version`, `status`,
  `error_message`.

## Fields Missing Or Not Captured

| Field / concept | Status |
|---|---|
| Durable per-tool call record table | Not found. Tool calls are represented in `plan_executed`, `tool_names`, `tool_results`, and output payloads. |
| Full runtime fixture output for Path C | Not captured. Requires LLM endpoint/settings and runtime context. |
| Full runtime fixture output for real Path D fallback | Not captured. Static tests mock fallback and do not run Docker. |
| Full runtime fixture output for explicit sandbox execution | Not captured. Static tests mock route behavior; Docker sandbox was not run. |
| All three governance modes over one shared payload | Not captured. Assist benign test exists; observe/autonomous are code-evidence here. |
| DB-backed dedup/batching decision | Not captured. Code exists, but this report did not run API/DB/Redis. |
| DB-backed institutional knowledge fixture | Not captured. Static unit tests show tool shape; DB loader code is inspected only. |
| DB-backed correlation history fixture | Not captured. Static unit tests show tool shape; DB loader code is inspected only. |
| Real customer data | Not found and not used. |
| SOC-reviewed fixtures | Not found. |

## Repo-Grounded Versus Inferred

| Category | Status |
|---|---|
| Repo-grounded | Stage dataclasses, V3 analysis path, V3 execute path, Path D fallback behavior, governance behavior, tool runner output shape, LLM audit fields, institutional knowledge tool shape, correlation tool shape, and store payload fields are grounded in inspected code/tests/migrations. |
| Repo-grounded but not reproduced here | Test commands and runtime code paths are grounded in `Zovark_final`, but this PR did not execute old-repo tests or services. |
| Inferred | Future CIC and Investigation Trace requirements are derived from observed fields and current ADR constraints; they are not schema decisions. |
| Unknown / not found | Production customer fixtures, SOC-reviewed fixtures, durable per-tool call records, full Path C output, full real Path D output, and full explicit sandbox output. |

## Capability Identity Contract Requirements

Future CIC work should represent at least:

- alert identity: source system, tenant, task, trace, normalized SIEM event,
  dedup hash, duplicate status, and ingest method;
- plan identity: source (`db_saved_plan`, `builtin_plan`, `llm_tool_call`),
  plan key, ordered steps, conditions, aliases, and source ref;
- tool identity: tool name, category, args schema, implementation ref/hash,
  version/ref, timeout policy, and error behavior;
- model invocation identity: model, provider/endpoint class, role, stage,
  prompt hash, prompt version, tokens, latency, status, and response hash if
  later captured;
- execution mode identity: `tools`, `sandbox`, `sandbox_fallback`, or `failed`;
- fallback identity: V3 failure reason, V2 sandbox result, AST decision,
  seccomp/policy ref, and generated-code hash;
- governance identity: autonomy level, policy source, review decision, and
  review reason;
- storage identity: task row, investigation row, audit event, and migration/schema
  ref where runtime DB state matters.

## Investigation Trace V1 Requirements

Future Investigation Trace V1 should represent:

- stage sequence: ingest, analyze, execute, assess, govern, store;
- recorded tool plan and each tool call with args, outputs, errors, and order;
- recorded model calls for LLM tool selection and assess-stage summaries;
- candidate findings proposed by tools or models;
- deterministic acceptance or rejection of candidate findings;
- proof-facing findings and verdict derivation boundary;
- fallback path with explicit mode transition from V3 tools to V2 sandbox;
- institutional knowledge and correlation context as recorded inputs, not live
  replay calls;
- governance decision as policy evaluation, not proof-layer authorization.

Replay must remain recorded-output replay and must not call live models, tools,
DB, SIEM, EDR, network services, or the V2 sandbox.

## Proof-Package Schema Impact

A proof-package schema bump is not required for this report. A future adapter
could initially map V3 runtime output into the existing nine-file proof package
as normalized evidence and findings.

A schema bump is likely needed if the product requires first-class export of:

- model invocation records;
- tool invocation records;
- candidate/accepted/rejected findings;
- fallback provenance;
- plan/tool implementation identities;
- DB-backed context provenance;
- runtime governance records separate from proof handoff approval.

That decision belongs in a later package-contract or Investigation Trace PR, not
in fixture capture.

## Reproduction Plan For Later Fixture Capture

To convert this report into committed fixture files later, use sanitized local
inputs only and record the old repo ref, environment, and command output.

Suggested sequence:

1. Run V3 saved-plan tool-runner tests against `Zovark_final@0290d6b`.
2. Run mocked Path D fallback tests to capture expected fallback shape.
3. Run explicit sandbox routing tests without Docker output first.
4. If Docker sandbox fixtures are needed, run them only in a controlled local
   lab with synthetic generated code and no secrets.
5. If Path C fixtures are needed, use a local mock LLM server and record
   `prompt_hash`, `prompt_version`, tokens, selected plan, and parsed plan.
6. For governance, patch `_get_governance_config` or seed a local DB with
   observe/assist/autonomous rows and run one shared assessed payload.
7. For institutional knowledge and correlation, prefer direct tool tests first;
   DB-backed loader fixtures require local DB setup and sanitized rows.

## Explicit Non-Actions

This PR does not:

- add fixture files;
- run live EDR, SIEM, network, DB, dispatcher, Vault runtime, Temporal, Docker,
  or LLM services;
- change runtime product code;
- change tests;
- change proof-package schema;
- define Capability Identity Contract;
- define Investigation Trace;
- implement a V3-to-proof adapter;
- change Replay V2 behavior;
- add manifest, provenance, signing, or transparency-log work;
- freeze final architecture.
