# V3 Ground-Truth Check

## Summary verdict

**Verdict: C. Both exist; V3 deterministic tool-calling is the active default and V2 LLM-code-generation/sandbox remains feature-flagged legacy/fallback.**

The older runtime repo `Zovark_final` contains real V3 tool-calling code, not just documentation:

- `worker/tools/catalog.py`
- `worker/tools/investigation_plans.json`
- `worker/tools/runner.py`
- `worker/stages/analyze.py` V3 branch
- `worker/stages/execute.py` V3 branch
- `worker/stages/govern.py`
- `migrations/062_v3_tool_calling.sql`
- V3-specific tests under `worker/tools/tests/`

At tag `v3.0.0`, the repository matches the historical claim closely: **34 tools and 24 saved investigation plans**. At the current default branch, the implementation has drifted to **39 catalog tools and 25 plan keys** on `origin/audit/execution-fixes`; `origin/master` has 39 tools and 24 plans.

The conflicting V2-style architecture document is real but stale. `docs/ARCHITECTURE.md`, `docs/pipeline_stages.md`, and `docs/pipeline_map.md` describe the older Path A/B/C code-generation and Docker-sandbox pipeline. The active runtime code and V3 migration docs show that V3 tools mode is the default through `ZOVARK_EXECUTION_MODE=tools`, while `ZOVARK_EXECUTION_MODE=sandbox` keeps the V2 path available.

No exact product terms **"Fast Mode"** or **"Reasoning Mode"** were found as V3 mode names in reachable repo history. There are **FAST/CODE/reasoning model-tier references**, but those are model-routing concepts, not the named product modes.

## Branch/ref inventory

### Current proof/replay repo

Repo: `https://github.com/7inaydas-cmyk/zovark-architecture`

Local branch for this report:

| Field | Value |
| --- | --- |
| Branch | `docs/v3-ground-truth-check` |
| HEAD | `1be589b60476ac62ca58ccfca36d2ec016f9f693` |
| Tracked worktree before this report | Clean |
| Existing untracked local-only files | `.vscode/`, `uv.lock`, `zovark-yc-demo.zip` |
| Intended change from this task | `docs/v3-ground-truth-check.md` only |

### Older product/runtime repo

Repo: `https://github.com/7inaydas-cmyk/Zovark_final`

Cloned for inspection at `/tmp/zovark_final_groundtruth`.

Remote default branch:

| Field | Value |
| --- | --- |
| Remote HEAD | `origin/audit/execution-fixes` |
| Local checked branch | `audit/execution-fixes` |

Branches:

| Branch/ref | Latest commit | Commit date | Subject | Interpretation |
| --- | --- | --- | --- | --- |
| `origin/audit/execution-fixes` | `0290d6b879b5afc4565e9a5e7756f7364d120e85` | 2026-04-15 | `chore(migration): archive migrate-to-zovak-final-repo` | Default branch. Contains V3 tools default plus execution audit cleanup. |
| `origin/master` | `94980c418858cac6810166667bb3f8f141d347c7` | 2026-04-12 | `fix(worker): _return_connection self-recursion on pool failure` | Mainline branch before archive/default-branch switch. Also contains V3 tools default. |

Tags:

| Tag | Commit | Subject | V3 relevance |
| --- | --- | --- | --- |
| `v3.0.0` | `8473eb8edfe20c0616c5ec63bd1a3b70c87b0aca` | `feat: Zovark v3.0.0 - deterministic tool-calling architecture` | First explicit deterministic tool-calling V3 tag. |
| `v3.2.1` | `d800cd03db3bde0543468f7dec5317c1ac4a3774` | `merge: v3.1-hardening -> master (v3.2.1)` | Later V3 hardening/validation tag. |
| `v1.8.1` and earlier | older commits | V2-era releases | Code-generation/sandbox era. |

Branch names suggesting `v3`, `v3.1`, or `v3.2` were **not present as remote branches** in the clone. The V3 lineage is represented by tags and commit messages, especially `v3.0.0`, `v3.2.1`, and commits such as:

- `35b3622 feat: Zovark v3 - deterministic tool-calling architecture (Phases 1-3)`
- `642072a feat: v3 red team, governance API, docs, CLAUDE.md update (Phases 5-6)`
- `ab9e034 feat: Path D - per-investigation fallback from v3 tool runner to v2 sandbox`
- `298aae4 fix: v3 plumbing - correlation context, institutional knowledge, store fields`
- `b729f35 v3.2.1: Gemma 4 swap, MITRE fix, parallel execution, engineering framework`
- `b6e49b0 audit: apply all 24 confirmed findings from execution audit`

The only branch name suggesting audit/execution hardening is `audit/execution-fixes`, which is the remote default branch.

Reflog/stash check:

- Reflog only shows the fresh clone entries for `0290d6b`.
- No stashes were present.
- No deleted branch evidence was available from the local clone.

## Architecture doc findings

| Path | Branch/ref | Claimed date/version | Pipeline described | V2/V3 label | Current/stale assessment |
| --- | --- | --- | --- | --- | --- |
| `CLAUDE.md` | `origin/audit/execution-fixes`, `origin/master`, `v3.2.1` | v3.2.1, 2026-04-04 | V3 six-stage deterministic tools + governance; V2 sandbox behind feature flag | V3/v3.2.1 | Mostly current for runtime direction. Count claims drift from code. |
| `docs/V3_MIGRATION_REPORT.md` | `origin/audit/execution-fixes`, `origin/master`, `v3.2.1` | V3 migration | Replaces Docker sandbox code execution with deterministic tool-calling; saved plans or LLM tool selection | V3 | Authoritative for V3 design intent. Exact 34-tool count is true at `v3.0.0`, stale for current branch. |
| `docs/ARCHITECTURE.md` | `origin/audit/execution-fixes`, `origin/master`, `v3.2.1` | v1.8.1, 2026-03-29 | Template fast-fill, template+LLM parameter extraction, full LLM Python code generation, AST prefilter, Docker sandbox, template promotion | V2 | Stale relative to current default runtime. Still useful for V2 legacy path. |
| `docs/pipeline_stages.md` | current/default and V3 refs | no V3 date in header | Five-stage V2 pipeline with ANALYZE code generation and EXECUTE Docker sandbox | V2 | Stale for active V3 default path. |
| `docs/pipeline_map.md` | current/default and V3 refs | no V3 date in header | Activity map with code generation, follow-up code generation, preflight validation, Docker dry-run | V2 | Stale for active V3 default path. |
| `docs/ARCHITECTURE_SNAPSHOT.md` | inspected refs | not found | N/A | N/A | Not present in inspected current refs. |
| `docs/ZOVARK_IMPLEMENTATION_AUDIT.md` | current/default | v1.7.0, 2026-03-28 | Code-generation/sandbox implementation inventory | V2-era | Historical audit, not current V3 truth. |
| `openspec/changes/archive/2026-04-15-stabilize-runtime-hygiene/proposal.md` | `origin/audit/execution-fixes` | 2026-04-15 archive | Says `InvestigationWorkflowV2` is the V3 tool-calling path and the name is misleading | V3 clarification | Current/useful for resolving workflow-name confusion. |

Key excerpts/facts:

- `CLAUDE.md` says the pipeline is **"V3 6-stage - deterministic tools + governance layer (v2 sandbox behind feature flag)"** and lists feature flag **`ZOVARK_EXECUTION_MODE=tools` (v3, default) or `sandbox` (v2 legacy)**.
- `docs/V3_MIGRATION_REPORT.md` says V3 **"replaces the Docker sandbox code execution pipeline with a deterministic tool-calling architecture"** and compares V2 code generation against V3 tool-calling.
- `docs/ARCHITECTURE.md` still says Zovark **"generates Python investigation code using locally-hosted LLMs"** and executes it in Docker sandbox. That describes V2.

## Deterministic tool-calling evidence

### Code artifacts

| Evidence | Location | Current default branch status |
| --- | --- | --- |
| Tool catalog | `worker/tools/catalog.py` | Present. Maps tool names to deterministic Python functions. |
| Saved plans | `worker/tools/investigation_plans.json` | Present. JSON plans for attack/task types. |
| Tool runner | `worker/tools/runner.py` | Present. Executes plan steps in-process with timeout/error isolation and optional parallel batching. |
| Tool subset/pruned catalog | `worker/tools/tool_subsets.py` | Present. Reduces catalog for LLM tool selection. |
| V3 analyze path | `worker/stages/analyze.py` | Present. `EXECUTION_MODE = os.getenv("ZOVARK_EXECUTION_MODE", "tools")`; in tools mode loads saved plan or asks LLM to select tools. |
| V3 execute path | `worker/stages/execute.py` | Present. `_execute_v3_tools()` calls `execute_plan()` in-process. |
| Governance | `worker/stages/govern.py` | Present. No-LLM governance stage using `governance_config`. |
| Workflow path | `worker/stages/investigation_workflow.py` | Present. Six stages: ingest, analyze, execute, assess, govern, store. Wire name remains `InvestigationWorkflowV2`. |
| Tool tests | `worker/tools/tests/*` | Present. Includes runner, schemas, red-team, extraction, parsing, detection, scoring, enrichment, Path D tests. |

### Tool/plan counts by ref

| Ref | Tool catalog count | Plan count | Notes |
| --- | ---: | ---: | --- |
| `v3.0.0` | 34 | 24 | Matches the historic "34 tools, 24 plans" claim. |
| `v3.2.1` | 39 | 24 | Detection tools expanded after v3.0.0. |
| `origin/master` | 39 | 24 | Same tool count as `v3.2.1`. |
| `origin/audit/execution-fixes` | 39 | 25 | Adds `probe_noop` plan key. |

Current default branch category count:

| Category | Count |
| --- | ---: |
| extraction | 8 |
| analysis | 4 |
| parsing | 5 |
| scoring | 6 |
| detection | 12 |
| enrichment | 4 |
| total | 39 |

The catalog comment says "Detection (11 tools)", but the dictionary contains 12 detection entries. `CLAUDE.md` says 40 tools / 24 plans. `docs/V3_MIGRATION_REPORT.md` says 34 tools / 24 plans. The exact historical V3 claim is true at `v3.0.0`, but not on the current default branch.

### Active/default status

V3 tool-calling is active by default:

- `.env.example`: `ZOVARK_EXECUTION_MODE=tools`
- `docker-compose.yml`: `ZOVARK_EXECUTION_MODE=${ZOVARK_EXECUTION_MODE:-tools}`
- `worker/settings.py`: `execution_mode: str = "tools"`
- `worker/stages/analyze.py`: `EXECUTION_MODE = os.getenv("ZOVARK_EXECUTION_MODE", "tools")`
- `worker/stages/execute.py`: `EXECUTION_MODE = os.environ.get("ZOVARK_EXECUTION_MODE", "tools")`

When `execution_mode == "tools"`:

1. `analyze_alert()` calls `_analyze_v3_tools()`.
2. `_analyze_v3_tools()` tries DB-stored `agent_skills.investigation_plan`.
3. If absent, it tries built-in `worker/tools/investigation_plans.json`.
4. If still absent and not in templates-only mode, it calls the LLM for **tool selection**, not Python code generation.
5. `execute_investigation()` calls `_execute_v3_tools()` and runs the selected/saved plan via `tools.runner.execute_plan()`.

Answer to deterministic tool-calling questions:

| Question | Answer |
| --- | --- |
| Do 34 tools exist as code? | Yes at `v3.0.0`. Current default has 39 catalog entries. |
| Do 24 plans exist as JSON/data? | Yes at `v3.0.0`, `v3.2.1`, and `origin/master`. Current default has 25 plan keys due `probe_noop`. |
| Does a tool runner exist? | Yes: `worker/tools/runner.py`. |
| Is it active by default? | Yes: `ZOVARK_EXECUTION_MODE=tools` default. |
| Is it behind a feature flag? | Tools mode is the default. V2 sandbox is behind `ZOVARK_EXECUTION_MODE=sandbox`; Path D can fall back per investigation. |
| Are tests present? | Yes, especially `worker/tools/tests/*`, `worker/tests/test_ticket4_temporal_activity_env.py`, `worker/tools/tests/test_path_d.py`, and `worker/tests/test_benchmark.py`. This archaeology pass did not rerun the old repo test suite. |

## LLM code-generation/sandbox evidence

The V2 code-generation/sandbox path still exists in code and docs.

### Code artifacts

| Evidence | Location | Status |
| --- | --- | --- |
| Path A/B/C code-generation implementation | `worker/stages/analyze.py` | Present. Top docstring still describes Stage 2 as code generation. |
| Template parameter extraction | `worker/stages/analyze.py` | Present in V2 branch. |
| Full LLM code generation | `worker/stages/analyze.py` | Present in V2 branch. |
| Generated Python code field | `worker/stages/investigation_workflow.py`, `worker/stages/store.py`, migrations | Present. Stored as `generated_code`. |
| AST prefilter | `worker/stages/execute.py`, `sandbox/ast_prefilter.py`, `worker/tests/test_ast_prefilter.py` | Present. |
| Docker sandbox execution | `worker/stages/execute.py` `_run_in_sandbox()` and `_execute_v2_sandbox()` | Present. |
| Seccomp sandbox profile | `sandbox/seccomp_profile.json`, compose mounts | Present. |
| Template promotion flywheel | `worker/stages/template_promoter.py`, `api/promotion_handlers.go`, `migrations/055_template_promotion.sql`, `migrations/059_template_promotion_quorum.sql` | Present. |
| Code cache | `worker/stages/code_cache.py` | Present. |

### Active/default status

The V2 path is **not the current default**. It runs when:

- `ZOVARK_EXECUTION_MODE=sandbox`, or
- V3 tools mode fails and Path D fallback attempts the V2 sandbox for that investigation, or
- code-based execution flows reach the V2 fallthrough.

`worker/stages/execute.py` explicitly documents:

- `tools -> v3 in-process tool runner (default)`
- `sandbox -> v2 Docker sandbox (global feature flag)`
- `Path D -> per-investigation fallback from v3 to v2 on failure`

Answer to LLM-code-generation/sandbox questions:

| Question | Answer |
| --- | --- |
| Does this path exist? | Yes. |
| Is it active? | Not by default. It is selectable via `ZOVARK_EXECUTION_MODE=sandbox` and reachable as Path D fallback. |
| Is it legacy/feature-flagged? | Yes. Current docs/code call it V2 legacy behind feature flag. |
| Is it the path described by current `docs/ARCHITECTURE.md`? | Yes. That document describes the V2 path and is stale relative to default runtime. |
| Are tests present? | Yes. Examples include AST prefilter tests, pipeline V2 tests, template/code-generation tests, and sandbox-related tests. This pass did not rerun them. |

## Runtime/default pipeline evidence

### Default execution mode

The path that would run from the current default branch is V3 tools mode unless environment variables override it:

- `docker-compose.yml`: `ZOVARK_EXECUTION_MODE=${ZOVARK_EXECUTION_MODE:-tools}`
- `.env.example`: `ZOVARK_EXECUTION_MODE=tools`
- `worker/settings.py`: `execution_mode: str = "tools"`
- `worker/stages/analyze.py`: defaults to `tools`
- `worker/stages/execute.py`: defaults to `tools`

### Registered workflow

The Temporal workflow name remains:

- `InvestigationWorkflowV2`

That name is historical. `worker/stages/investigation_workflow.py` states that the wire name is preserved for backward compatibility and that the class is the current investigation pipeline. The archived OpenSpec proposal also says `InvestigationWorkflowV2` is now the V3 tool-calling path and that the name is misleading.

### Actual default flow

On the default branch, a normal deployment would run:

1. `INGEST`: dedup, PII masking, skill retrieval.
2. `ANALYZE`: V3 saved-plan lookup or LLM tool selection.
3. `EXECUTE`: V3 in-process tool runner.
4. `ASSESS`: verdict/summary/false-positive analysis. LLM use may still occur here.
5. `GOVERN`: autonomy/human-review policy.
6. `STORE`: DB writes including execution mode and plan/code metadata.

Important nuance: **V3 does not mean "no LLM anywhere."** It means the default execution no longer depends on LLM-generated Python code. LLMs still appear in:

- Path C tool selection when no saved plan exists.
- Assess-stage summary/entity/false-positive reasoning paths.
- Other platform modules such as reporting, Sigma generation, SRE, and entity graph logic.

### Runtime/config conflict

`CLAUDE.md` describes local llama-server endpoints as the LLM host. Current `docker-compose.yml` on `origin/audit/execution-fixes` sets OpenAI-compatible endpoint defaults:

- `ZOVARK_LLM_PROVIDER=${ZOVARK_LLM_PROVIDER:-openai}`
- `ZOVARK_LLM_ENDPOINT=${ZOVARK_LLM_ENDPOINT:-https://api.openai.com/v1/chat/completions}`

This appears to be later audit/runtime-hygiene drift from the earlier air-gapped/local-inference docs. It does not change the V3-vs-V2 conclusion, but it is a deployment-truth conflict to track separately.

## Database/schema evidence

The database supports both V3 tool plans and V2 code-generation records.

### V3/tool-plan support

`migrations/062_v3_tool_calling.sql` adds:

- `agent_skills.investigation_plan JSONB`
- `agent_skills.execution_mode VARCHAR(20) DEFAULT 'sandbox'`
- `governance_config`
- `institutional_knowledge`
- analyst feedback columns for investigation notes, environment baseline, and missing context

Runtime code uses these:

- `worker/stages/analyze.py` reads `agent_skills.investigation_plan`.
- `worker/stages/govern.py` reads `governance_config`.
- `worker/stages/context_loader.py` reads `institutional_knowledge`.
- `worker/stages/store.py` stores `execution_mode` and `plan_executed`.

### V2/code-generation support

Older migrations and code still support generated-code records:

- `migrations/002_schema_drift_fixes.sql`: `generated_code`, `execution_mode`
- `migrations/045_investigation_memory.sql`: `code_template`
- `migrations/055_template_promotion.sql`: `agent_tasks.generated_code`, `agent_skills.auto_promoted`
- `migrations/059_template_promotion_quorum.sql`: `template_promotion_approvals`
- `worker/stages/store.py`: persists `generated_code`
- `api/promotion_handlers.go`: reads `generated_code` for template promotion

### LLM audit/prompt tracking

LLM audit support exists:

- `migrations/046_llm_audit_log.sql`: `llm_audit_log` with `prompt_hash`
- `migrations/050_model_performance_tracking.sql`: adds `prompt_version`
- `worker/stages/llm_gateway.py`: computes `prompt_hash` and `prompt_version`
- `worker/llm_logger.py`: logs model calls

### Tool-call record support

There is no separate durable table named `tool_call_records` in the inspected migrations. Tool execution data appears to be carried as:

- `plan_executed`
- `execution_mode`
- `tool_results`
- `tools_executed`
- `tool_names`
- investigation/task output payloads

Answer to DB questions:

| Question | Answer |
| --- | --- |
| Does the DB support tool plans? | Yes: `agent_skills.investigation_plan`, `execution_mode`, governance, institutional knowledge. |
| Does it support code-generation records? | Yes: `generated_code`, `code_template`, template promotion, LLM audit logs. |
| Does it support both? | Yes. The schema is mixed V2/V3. |

## Benchmark evidence

| Claim/source | Branch/ref | Harness/artifact | Synthetic/lab/real | Reproducibility status | Customer validation status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 515-alert V3 corpus | `docs/V3_BENCHMARK_REPORT.md`, current default | `scripts/benchmark/corpus_515.json`, `tests/benchmark/run_benchmark.py` | Generated/lab corpus | Corpus and runner present | No customer validation found | Report claims 164 completed Path A alerts, 100% detection, 0% FP, 416 pending. This is a snapshot, not full 515 completed. |
| 34 tools / 24 plans | `v3.0.0`, `docs/V3_MIGRATION_REPORT.md` | `worker/tools/catalog.py`, `investigation_plans.json` | Code inventory | Recomputed from tag | N/A | True at `v3.0.0`. Current default is 39/25. |
| 40 tools / 24 plans | `CLAUDE.md` current/default | Documentation claim | Code inventory claim | Does not match current catalog count | N/A | Code count is 39 tools on current default. |
| 1000-alert corpus | `docs/ARCHITECTURE.md`, `scripts/benchmark/corpus_1000.json` | `scripts/benchmark/run_1000_benchmark.py` | Generated/lab corpus | Corpus/runner present | No customer validation found | `docs/ARCHITECTURE.md` claims 983/1000 completed and 38h on RTX 3050; this doc is V2-era/stale. |
| Juice Shop 99/100 | `docs/README.md` says 99/100; `docs/JUICE_SHOP_BENCHMARK.md` gives details | `scripts/benchmark/run_juice_benchmark.py`, `juice_shop_corpus.json` | Real traffic against local OWASP Juice Shop lab | Corpus/runner present | No customer validation found | Detailed report says 69/100 completed, 63/63 completed attacks detected, benign completion/FP issues. It labels pipeline as V2. |
| 15/15 pipeline regression | `docs/ZOVARK_IMPLEMENTATION_AUDIT.md` | historical tests | V2 regression/lab | Historical doc | No customer validation found | V2-era pipeline validation. |
| 10/10 MITRE or template coverage claims | `docs/CHANGELOG.md`, older docs | sprint/docs claims | Lab/dev | Not independently rerun here | No customer validation found | Treat as historical claims until revalidated. |
| 100 Attack Simulation | `docs/SIMULATION_REPORT_100_ATTACKS.md` | generated 100 attacks | Synthetic/lab | Report present | No customer validation found | Contradicts high accuracy claims: detection rate 26%, 74 missed attacks. |
| Path A latency | `docs/V3_MIGRATION_REPORT.md`, `docs/V3_BENCHMARK_REPORT.md` | benchmark/report docs | Lab | Reports present | No customer validation found | V3 migration says ~5ms plan load/tool calls; V3 benchmark says Path A <100ms. |
| Path C latency | `docs/V3_MIGRATION_REPORT.md`, `docs/V3_BENCHMARK_REPORT.md` | benchmark/report docs | Lab | Partial | No customer validation found | V3 migration says ~30s; V3 benchmark snapshot had novel Path C alerts still pending. |
| Single-GPU bottleneck | `docs/V3_BENCHMARK_REPORT.md`, `docs/ARCHITECTURE.md` | RTX 3050 notes | Lab/deployment constraint | Observed in reports | No customer validation found | V3 515 snapshot says RTX 3050 processes one LLM call at a time; V2 architecture says Path C 120-280s. |
| Ingest/submission throughput | `docs/V3_BENCHMARK_REPORT.md` | benchmark runner | Lab | Report present | No customer validation found | Submission throughput ~1.6 alerts/s, not end-to-end completion throughput. |

Benchmark conclusion: the repo contains useful lab evidence, but claims are inconsistent across time. For V3 specifically, the strongest direct evidence is the V3 benchmark snapshot: completed Path A saved-plan cases were fast and accurate, but the full corpus was not complete in that snapshot.

## Conflicts and stale docs

### Current source conflicts

1. **V3 doc vs V2 architecture doc**
   - `docs/V3_MIGRATION_REPORT.md` says V3 replaces Docker sandbox code execution with deterministic tool-calling.
   - `docs/ARCHITECTURE.md` still says the platform generates Python investigation code and executes it in Docker.
   - Code defaults confirm the V3 migration doc, not the stale architecture doc.

2. **Workflow name conflict**
   - Runtime workflow wire name remains `InvestigationWorkflowV2`.
   - Current code comments and OpenSpec archive say this name is historical and now points to the current V3-capable workflow.

3. **Tool/plan count drift**
   - `v3.0.0`: 34 tools / 24 plans.
   - `v3.2.1`: 39 tools / 24 plans.
   - `origin/audit/execution-fixes`: 39 tools / 25 plans.
   - `CLAUDE.md`: 40 tools / 24 plans.

4. **Air-gap/local inference vs OpenAI defaults**
   - Older docs emphasize local llama-server/air-gap.
   - Current default branch `docker-compose.yml` uses OpenAI-compatible endpoint defaults unless overridden.
   - This is a runtime configuration truth conflict separate from the V3/V2 pipeline question.

5. **Benchmark claims conflict**
   - Some docs claim 100% detection / 0% FP.
   - `docs/SIMULATION_REPORT_100_ATTACKS.md` reports 26% detection.
   - Juice Shop details are narrower than the headline: 69/100 completed and 63/63 completed attacks detected, with benign issues.

### Search results for disputed terms

| Term/concept | Found? | Interpretation |
| --- | --- | --- |
| `Fast Mode` exact | No | Not a repo-grounded V3 product mode name. |
| `Reasoning Mode` exact | No | Not a repo-grounded V3 product mode name. |
| Fast/reasoning model tiers | Yes | Model-routing language exists, not product modes. |
| `recorded_io` | No | Not present in `Zovark_final`. |
| `model_contribution` | No | Not present in `Zovark_final`. |
| `model_versions_pin` | No | Not present in `Zovark_final`. |
| `RamaLama` | No | Not present in `Zovark_final`. |
| `tool catalog` / `tool call` | Yes | Core V3 evidence. |
| `inference gateway` | Weak/partial | Found mainly as LiteLLM/LLM gateway references, not a full v4.1-style Inference Gateway domain. |
| `prompt_hash` / `prompt_version` | Yes | LLM audit/versioning exists. |
| `hypothesis` / `hypotheses` | Incidental | Mostly property-testing/model-tokenizer/marketing context, not a structured investigation hypothesis trace. |

## Implications for next PRs

### V3 asset inventory

The V3 inventory should treat these as real assets:

- 39 current tool catalog entries on default branch.
- 25 current plan keys on default branch.
- 24 plan keys on `origin/master`/`v3.2.1`.
- 34-tool/24-plan baseline at `v3.0.0`.
- `worker/tools/runner.py`.
- V3 tests under `worker/tools/tests/`.
- V3 governance config and institutional knowledge migrations.
- V2 sandbox/codegen/template-promotion assets as legacy/fallback assets, not current default assets.

The inventory should not repeat the old "34 tools / 24 plans" claim without pinning it to `v3.0.0`.

### Capability Identity Contract

The Capability Identity Contract should account for both sides of the mixed runtime:

- Tool identity: tool name, category, args schema, code version/hash.
- Plan identity: plan key, ordered steps, conditions, source (`db_saved_plan`, `builtin_plan`, or `llm_tool_call`).
- Execution mode: `tools`, `sandbox`, `sandbox_fallback`, `failed`.
- Fallback provenance: if Path D occurs, the proof layer must know that the result came from V2 sandbox fallback.
- Template/codegen identity for legacy records: template skill, generated code hash, prompt hash/version, model metadata.

### Investigation Trace V1

Investigation Trace V1 should be grounded in the actual V3 implementation terms:

- `plan_executed`
- `tool_names`
- `tool_results`
- `tools_executed`
- `errors`
- `execution_mode`
- `path_taken`
- `source` (`saved_plan`, `llm_tool_call`, `template`, `llm`, etc.)
- `prompt_hash` / `prompt_version` for LLM tool selection and assess-stage LLM calls

It should not claim that "Fast Mode" or "Reasoning Mode" already exist as named product modes in `Zovark_final`. If those names are used later, they should be explicitly mapped onto existing mechanics:

- likely "fast" = saved-plan/tool Path A.
- likely "reasoning" = LLM-selected tool plan and/or deeper multi-step investigation.

That mapping would be a product/design decision, not repo ground truth.

### V3 fixture capture

Fixture capture should include at least these cases:

1. V3 saved-plan Path A, no analysis LLM.
2. V3 LLM tool-selection Path C.
3. V3 tool-runner error with Path D fallback to V2 sandbox.
4. Explicit `ZOVARK_EXECUTION_MODE=sandbox` V2 run.
5. Governance observe/assist/autonomous outcomes.
6. Tool result with institutional knowledge lookup.
7. Tool result with correlation history.

The 515-alert benchmark snapshot is not enough by itself because it captured only 164 completed Path A cases at report time.

### V3-to-proof-package adapter

The adapter should consume the V3 runtime shape, not stale V2 docs:

- Prefer `plan_executed`, `tool_results`, `tool_names`, `execution_mode`, `path_taken`, and `source`.
- Preserve `generated_code` only when the run used V2 sandbox or Path D fallback.
- Preserve LLM audit references for tool selection and assess-stage LLM work.
- Treat V2 code-generation artifacts as legacy/fallback evidence, not as the normal V3 path.

The proof package should be explicit when a result came from:

- saved deterministic plan,
- LLM-selected tool plan,
- deterministic tool runner,
- V2 sandbox fallback,
- or explicit V2 sandbox mode.

### Ingest/funnel throughput risk

The throughput risk is not simply ingest submission rate.

Known facts:

- V3 benchmark report says submission throughput was about 1.6 alerts/s.
- The same report says only 164 of 580 submitted alerts were completed at the snapshot.
- It also says 416 were pending, including 35 novel alerts awaiting LLM tool selection on an RTX 3050.
- Path A saved plans are fast (`<100ms` in the V3 benchmark; `~5ms` in the migration report).
- Path C tool selection remains GPU/LLM-bound.

So the risk is the funnel mix:

- If most alerts hit saved plans, V3 tools mode is fast.
- If many alerts miss saved plans, Path C LLM tool selection becomes the bottleneck.
- If tool execution fails and Path D fallback triggers, V2 sandbox behavior and latency return.

## Final ground-truth statement

V3 in `Zovark_final` is **not** the V2 full-LLM Python code-generation pipeline described by `docs/ARCHITECTURE.md`.

V3 is a deterministic tool-calling architecture where:

- known alert types use saved deterministic plans,
- unknown/no-plan alerts can use LLM tool selection,
- tools execute in-process through an allowlisted catalog,
- governance runs after assessment,
- V2 Docker sandbox/code generation remains available as legacy/fallback,
- and the runtime default is `ZOVARK_EXECUTION_MODE=tools`.

The repo's stale docs and benchmark headlines should be corrected before absorbing V3 into the current proof/replay architecture, but the code-level V3 asset is real and usable as the basis for future Capability Identity, Investigation Trace, fixture capture, and V3-to-proof-package adapter work.
