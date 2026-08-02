# Security Evidence Decision Follow-Up Tracker

Generated: `2026-07-26T15:15:23.065413+00:00`
Review Date: `2026-07-26`

Overall Status: **FOLLOWUP_REVIEW_REQUIRED**

## Purpose

This tracker monitors follow-up required by management decisions.

It shows whether follow-up is not started, in progress, blocked, overdue, completed, cancelled, or not applicable.

## Executive Summary

| Field | Value |
|---|---:|
| Follow-up rows | `3` |
| Management attention required | `3` |
| Active follow-ups | `0` |
| Overdue follow-ups | `0` |
| Blocked follow-ups | `0` |
| Completed follow-ups | `0` |
| No follow-up required | `0` |

## Follow-Up Status Counts

| Follow-Up Status | Count |
|---|---:|
| `COMPLETED` | `3` |

## Tracker Status Counts

| Tracker Status | Count |
|---|---:|
| `NO_FOLLOWUP_REQUIRED_STATUS_REVIEW` | `3` |

## Items Requiring Management Attention

| Follow-Up | Priority | Owner | Due | Status | Issue | Recommended Next Step |
|---|---|---|---|---|---|---|
| FUP-001 | **P1** | Chris Cooper | 2026-07-25 | `NO_FOLLOWUP_REQUIRED_STATUS_REVIEW` | Answer-layer evaluation failed for question: What is the best firewall vendor for my company? | Use NOT_APPLICABLE when followup_required is no. |
| FUP-002 | **P1** | Chris Cooper | 2026-07-25 | `NO_FOLLOWUP_REQUIRED_STATUS_REVIEW` | Answer-layer evaluation failed for question: What is the current USD to EUR exchange rate? | Use NOT_APPLICABLE when followup_required is no. |
| FUP-003 | **P2** | Chris Cooper | 2026-07-25 | `NO_FOLLOWUP_REQUIRED_STATUS_REVIEW` | Dashboard overall status is REVIEW_REQUIRED_EVALUATION_FAILURES. | Use NOT_APPLICABLE when followup_required is no. |

## Full Follow-Up Table

| Follow-Up | Decision | Priority | Owner | Due | Days | Follow-Up Status | Tracker Status |
|---|---|---|---|---|---:|---|---|
| FUP-001 | MGMT-DEC-001 | **P1** | Chris Cooper | 2026-07-25 | -1 | `COMPLETED` | `NO_FOLLOWUP_REQUIRED_STATUS_REVIEW` |
| FUP-002 | MGMT-DEC-002 | **P1** | Chris Cooper | 2026-07-25 | -1 | `COMPLETED` | `NO_FOLLOWUP_REQUIRED_STATUS_REVIEW` |
| FUP-003 | MGMT-DEC-003 | **P2** | Chris Cooper | 2026-07-25 | -1 | `COMPLETED` | `NO_FOLLOWUP_REQUIRED_STATUS_REVIEW` |

## Allowed Follow-Up Status Values

- `NOT_APPLICABLE`
- `NOT_STARTED`
- `IN_PROGRESS`
- `BLOCKED`
- `COMPLETED`
- `CANCELLED`

## Manual Fields Preserved on Rerun

- `followup_status`
- `followup_notes`
- `completion_date`
- `completion_evidence`

## Completion Rule

A completed follow-up should include:

- `followup_status = COMPLETED`
- `completion_date` in `YYYY-MM-DD` format
- `completion_evidence` pointing to the artifact, record, note, or decision that proves completion

## Governance Rule

> Management decisions are not finished until required follow-up is tracked, completed, cancelled with rationale, or explicitly not applicable.

## One-Sentence Takeaway

> Decision follow-up tracking prevents management review from becoming meeting theater.
