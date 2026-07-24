# Security Evidence Status Dashboard

Generated: `2026-07-24T20:54:44.086034+00:00`

Overall Status: **REVIEW_REQUIRED_EVALUATION_FAILURES**

## Purpose

This dashboard summarizes the current posture of the local security evidence system.

It consolidates corpus coverage, answer evaluation, evidence gaps, closure review, reviewer decisions, adjudicated status, and remediation evidence.

## Executive Rollup

| Area | Current Value |
|---|---:|
| Corpus documents indexed | `57` |
| Evaluation cases | `5` |
| Evaluation failures | `2` |
| Pending reviewer decisions | `0` |
| Final closed gaps | `5` |
| Final open gaps | `0` |
| Pending human review | `0` |
| Retrieval tuning required | `0` |
| AWS admin-port remediation | `PUBLIC_ADMIN_EXPOSURE_CLEARED_PENDING_REVIEW` |

## Next Actions

- Review failed evaluation cases and tune retrieval, answer thresholds, or test expectations.

## Artifact Health

| Artifact | Status |
|---|---|
| `ai/security_evidence_corpus_manifest.csv` | Present |
| `ai/security_evidence_eval_results.csv` | Present |
| `ai/security_evidence_gap_register.csv` | Present |
| `ai/security_evidence_gap_closure_register.csv` | Present |
| `ai/security_evidence_reviewer_decisions.csv` | Present |
| `ai/security_evidence_adjudicated_gap_status.csv` | Present |
| `security/aws_admin_port_remediation_register.csv` | Present |

## Final Gap Status Counts

| Final Status | Count |
|---|---:|
| `CLOSED` | `5` |

## Reviewer Decision Counts

| Reviewer Decision | Count |
|---|---:|
| `CLOSE_GAP` | `5` |

## Control Interpretation

| Control Question | Current Interpretation |
|---|---|
| Is there an approved corpus? | Corpus count shows whether local source material exists for bounded retrieval. |
| Are answer guardrails tested? | Evaluation failure count shows whether the no-source/no-confident-answer rule is holding. |
| Are gaps managed? | Gap, closure, reviewer, and adjudication counts show lifecycle state. |
| Is closure human-reviewed? | Pending and completed reviewer decisions show whether humans accepted closure. |
| Is remediation evidenced? | Admin-port remediation status shows whether the detected issue has post-fix evidence. |

## One-Sentence Takeaway

> A security evidence system needs a dashboard that shows not only what it knows, but what still needs review, closure, or correction.
