# Output Lifecycle Policy

Status: governance policy for generated outputs and fixtures. This document does
not create customer artifacts, runtime code, benchmarks, or outreach material.

## Temporary Output

`.tmp/` examples are ephemeral. They are useful for local validation and should
not be treated as committed product artifacts.

Generated output directories should be gitignored, removed after use, or
promoted through an explicit fixture PR. Do not commit generated outputs by
accident.

## Proof Packages

Generated proof packages are not customer artifacts by default. A proof package
becomes a committed fixture only when a scoped PR says so and the data is
sanitized, deterministic, and reviewable.

Customer-readiness material remains future work. Do not label local generated
packages as customer-ready.

## Sensitive Fixture Data Policy

Committed fixtures must not contain:

- real customer data;
- secrets or tokens;
- raw prompts;
- raw tool arguments;
- raw tool outputs;
- payload bodies;
- chat messages;
- analyst notes;
- hidden reasoning;
- chain-of-thought;
- host-local absolute paths; or
- nondeterministic timestamps.

Fixtures should use deterministic IDs, deterministic timestamps, sanitized host
names, and evidence-backed source refs.

## Deterministic Compare Guidance

When comparing generated packages:

- generate into a clean ignored output directory;
- normalize or avoid local path fields;
- avoid wall-clock-generated values;
- compare stable JSON serialization where possible;
- verify package output with offline Replay; and
- run leak checks for unsafe prompt, tool, payload, message, note, and reasoning
  strings.

## Cleanup Guidance

Before merging a PR, confirm:

- tracked files are clean except for intentional changes;
- `.vscode/`, `uv.lock`, and local archives remain uncommitted unless explicitly
  scoped;
- generated `.tmp/` outputs are not staged;
- proof packages under `tests/fixtures` are intentional fixtures; and
- no benchmark, customer-readiness, or outreach artifacts were created by
  validation commands.
