# Design-Partner Validation Workflow

This workflow validates the product wedge with a real customer. It is not a benchmark and must not be used for quantified accuracy or latency claims without separate measured artifacts.

1. Customer provides representative sample data under an agreed data-handling boundary.
2. System creates a recorded investigation object.
3. Customer reviews raw evidence used by the investigation.
4. Customer reviews the reconstructed timeline.
5. Customer reviews grouped campaign or incident.
6. Customer reviews evidence-backed findings.
7. Customer reviews verdict or conclusion.
8. Customer reviews proposed external action or handoff, if applicable.
9. Customer reviews rollback/reversal plan, if applicable.
10. Customer replays the investigation using recorded outputs only.
11. Customer scores usefulness.

## Scorecard

| Question | Score |
| --- | --- |
| Timeline accuracy | 1-5 |
| Evidence completeness | 1-5 |
| Grouping accuracy | 1-5 |
| Verdict trustworthiness | 1-5 |
| Action/handoff usefulness | 1-5 |
| Replay usefulness | 1-5 |
| Would use in incident review | yes/no |
| Would pilot | yes/no |
| Would pay | yes/no |

## Acceptance Boundary

This workflow can support MVP fit decisions. It cannot support public performance, reliability, false-positive, or accuracy claims unless the repository also contains the measurement corpus, method, and report.
