# Security Evidence Traceability Exception Register

Generated: `2026-07-24T23:34:00.409689+00:00`

Overall Status: **EXCEPTIONS_OPEN_HIGH**

## Purpose

This register identifies evidence-system items that need review before the system is treated as audit-ready.

It converts traceability, evaluation, reviewer decision, adjudication, and dashboard signals into actionable exceptions.

## Summary

| Field | Value |
|---|---:|
| Total exceptions | `3` |
| Open exceptions | `3` |
| High severity | `2` |
| Medium severity | `1` |
| Low severity | `0` |
| Info | `0` |

## Exception Type Counts

| Exception Type | Count |
|---|---:|
| `EVALUATION_FAILURE` | `2` |
| `NON_STABLE_OVERALL_STATUS` | `1` |

## Open Exceptions

| ID | Severity | Stage | Type | Issue | Recommended Action |
|---|---|---|---|---|---|
| EXC-001 | **HIGH** | Evaluation | `EVALUATION_FAILURE` | Answer-layer evaluation failed for question: What is the best firewall vendor for my company? | Review retrieval results, answer status, expected result, and evaluation hint logic. |
| EXC-002 | **HIGH** | Evaluation | `EVALUATION_FAILURE` | Answer-layer evaluation failed for question: What is the current USD to EUR exchange rate? | Review retrieval results, answer status, expected result, and evaluation hint logic. |
| EXC-003 | **MEDIUM** | Status Dashboard | `NON_STABLE_OVERALL_STATUS` | Dashboard overall status is REVIEW_REQUIRED_EVALUATION_FAILURES. | Review detailed exceptions and clear open, pending, invalid, incomplete, or failed items. |

## Source Artifacts Checked

| Artifact | Status |
|---|---|
| `ai/security_evidence_traceability_matrix.csv` | Present |
| `ai/security_evidence_status_summary.csv` | Present |
| `ai/security_evidence_adjudicated_gap_status.csv` | Present |
| `ai/security_evidence_eval_results.csv` | Present |
| `ai/security_evidence_reviewer_decisions.csv` | Present |

## Governance Rule

> A dashboard shows posture; an exception register shows what must be fixed, accepted, or reviewed.

## One-Sentence Takeaway

> Exception management turns evidence-system problems into visible, owned follow-up work.
