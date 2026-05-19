# Repository Reviewer Guidance

Status: reviewer guidance for this architecture/reference repository. This file
does not define runtime behavior or product readiness.

## Review Priority

Review P0/P1 only unless the PR explicitly asks for a broader pass.

Treat overclaims as serious issues. In this repository, a statement can be
unsafe even when the code or document is syntactically correct.

## P0/P1 Issues To Flag

Flag any production SOC readiness, autonomous response, legal admissibility,
compliance certification, tamper-proof evidence, cryptographic signing, SLSA,
in-toto, production-grade guarantee, benchmark, or customer-readiness claim
unless it is explicitly implemented, tested, and in scope for the PR.

Flag any live EDR, SIEM, LLM, DB, Vault, control-plane, network, or
customer-data integration introduced without explicit scope approval.

Flag any change that breaks offline Replay or causes Replay to call live
systems.

Flag any change that mutates Proof Package V1 instead of using explicit
versioned V2 or additive contracts.

Flag any artifact leaking raw prompts, raw tool arguments, raw tool outputs,
payload bodies, messages, analyst notes, hidden reasoning, or chain-of-thought.

Flag any AlertForge integration before a committed input contract/schema and
unsafe-field rejection rules exist.

Flag generated proof packages or fixtures containing secrets, tokens, real
customer data, host-local absolute paths, or nondeterministic timestamps.

Flag recovered `ADR-0044` through `ADR-0051` material treated as binding current
implementation law before reconciliation.

Flag Context Compaction Memory runtime, storage, or retrieval implementation
added while the PR claims docs/contracts only.

Flag JSON Schema contracts presented as runtime-enforced without validation
fixtures and enforcement code.

Flag model-visible data contracts that do not bind visibility to exact ranges
and byte counts.

Flag JSON Schema limitations where semantic helper validation is required but
missing.

## Scope Discipline

This repository is currently an architecture/reference/proof repository. Do not
let review language imply that the final runtime product, AlertForge
integration, benchmark suite, customer-readiness workflow, or outreach process
already exists.
