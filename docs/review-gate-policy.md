# Review Gate Policy

Status: governance policy. This document defines merge-gate evidence standards.
It does not implement runtime code, change adapter behavior, change verifier
behavior, add AlertForge integration, add benchmarks, or create customer-facing
material.

## Purpose

The review gate protects architecture and contract work from merging based on
ambiguous review-request prose. A PR is not clean merely because someone asked
for a focused review.

## Required Clean Review Evidence

The normal merge gate requires all of the following:

- The PR head SHA being merged is the latest reviewed head.
- An exact `@codex review` trigger exists for that head unless a manual
  exception is explicitly documented.
- Clean evidence comes from `chatgpt-codex-connector[bot]` or from a formal
  Codex review.
- The clean review response appears after the latest head SHA was pushed.
- The clean response says Codex found no major P0/P1 issues, for example:
  `Codex Review: Didn't find any major issues.`
- No newer P0/P1 comments appear after the clean review.
- No unresolved review threads remain.
- The tracked worktree is clean before merge.

Review-request comments such as `Focused Codex review requested` are not clean
review evidence.

## Manual Exceptions

Manual exceptions must be rare and explicit. The exception record must include:

- reason for the exception;
- reviewer identity;
- reviewed head SHA;
- PR scope;
- validation commands and results;
- unresolved risks; and
- confirmation that no newer P0/P1 finding is visible.

If any of those details are missing, do not describe the PR as clean-reviewed.

## Schema And Contract PRs

Schema and contract PRs require practical valid/invalid checks, not just prose.
The checks must include:

- JSON syntax validation;
- JSON Schema metaschema validation where JSON Schema is used;
- accepted valid examples;
- rejected invalid examples; and
- semantic helper validation for constraints JSON Schema cannot express
  portably.

Examples of semantic checks include byte range ordering, line range ordering,
and cross-field consistency such as model-visible content requiring explicit
returned ranges and positive byte counts.

## Historical PR Evidence Notes

For PRs #44 through #47, do not falsely call them Codex-clean if visible bot
evidence is missing. Classify those PRs as manual exception, alternate reviewer
evidence, or evidence-unknown as appropriate.

PR #48 is Codex-clean because an exact `@codex review` trigger and
`chatgpt-codex-connector[bot]` clean response occurred on the latest fixed head
before merge.

## Out-Of-Scope Review Cleanliness

A clean review for docs/contracts does not approve runtime implementation. A
future runtime, AlertForge, benchmark, customer-readiness, signing, legal, or
compliance PR must satisfy its own scoped review gate.
