# Security Evidence Human Review Packet

Generated: `2026-07-20T23:43:55.504515+00:00`

Review Status: **REVIEW_COMPLETE**

## Purpose

This packet gives a human reviewer the evidence-gap closure items that need decision, acceptance, rejection, or follow-up.

Automation can surface evidence, but it should not silently close governance gaps.

## Allowed Reviewer Decisions

| Decision | Meaning |
|---|---|
| `PENDING_REVIEW` | No human decision has been recorded yet. |
| `CLOSE_GAP` | Reviewer accepts the closure evidence and closes the gap. |
| `PARTIALLY_CLOSE_GAP` | Reviewer accepts partial closure but leaves residual work. |
| `KEEP_OPEN` | Reviewer determines the evidence is insufficient or risk remains. |
| `OUT_OF_SCOPE_ACCEPTED` | Reviewer accepts that the question is outside approved corpus scope. |
| `RETRIEVAL_TUNING_REQUIRED` | Reviewer determines retrieval produced weak or misleading support. |

## Review Summary

| Field | Value |
|---|---:|
| Review rows | `5` |
| Pending review | `0` |
| Close gap | `5` |
| Partially close gap | `0` |
| Keep open | `0` |
| Retrieval tuning required | `0` |
| Out of scope accepted | `0` |
| Invalid decisions | `0` |

## Review Items

| Review ID | Closure ID | Closure Status | Recommended | Reviewer Decision | Question |
|---|---|---|---|---|---|
| REV-001 | GAP-CLOSE-001 | `NOT_A_GAP_SUPPORTED` | `CLOSE_GAP` | **CLOSE_GAP** | What evidence supports the AWS cloud administrative access standard? |
| REV-002 | GAP-CLOSE-002 | `NOT_A_GAP_SUPPORTED` | `CLOSE_GAP` | **CLOSE_GAP** | What evidence shows admin port exposure was reviewed? |
| REV-003 | GAP-CLOSE-003 | `CLOSURE_EVIDENCE_AVAILABLE_REVIEW_REQUIRED` | `CLOSE_GAP` | **CLOSE_GAP** | What evidence proves the EC2 public admin-port rule was remediated? |
| REV-004 | GAP-CLOSE-004 | `RETRIEVAL_REVIEW_NEEDED` | `RETRIEVAL_TUNING_REQUIRED` | **CLOSE_GAP** | What is the best firewall vendor for my company? |
| REV-005 | GAP-CLOSE-005 | `RETRIEVAL_REVIEW_NEEDED` | `RETRIEVAL_TUNING_REQUIRED` | **CLOSE_GAP** | What is the current USD to EUR exchange rate? |

## How to Use

Edit `ai/security_evidence_reviewer_decisions.csv` and update these fields:

```text
reviewer_decision
reviewer
decision_date
reviewer_notes
```

Then rerun:

```powershell
python src\generate_security_evidence_reviewer_decisions.py
```

## Governance Rule

> A human reviewer closes the gap. Automation only prepares the decision record.
