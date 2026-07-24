# Security Evidence Exception Management Decision Log

Generated: `2026-07-24T20:55:45.946254+00:00`

Overall Status: **REVIEW_REQUIRED_INCOMPLETE_DECISIONS**

## Purpose

This log records management decisions made against exception review items.

It preserves decision owner, date, notes, follow-up requirement, follow-up owner, and follow-up date across reruns.

## Summary

| Field | Value |
|---|---:|
| Decision rows | `3` |
| Items requiring management attention | `3` |
| Pending decisions | `0` |
| Complete decisions | `0` |
| Invalid decisions | `0` |

## Management Decision Counts

| Decision | Count |
|---|---:|
| `START_ACTION` | `3` |

## Decision Completeness Counts

| Completeness Status | Count |
|---|---:|
| `DECISION_INCOMPLETE_decision_owner_decision_date_decision_notes_followup_required_yes_or_no` | `3` |

## Attention Items

| Decision ID | Priority | Review Status | Recommended Decision | Recorded Decision | Completeness | Issue |
|---|---|---|---|---|---|---|
| MGMT-DEC-001 | **P1** | `P1_NOT_STARTED` | `START_ACTION` | `START_ACTION` | **DECISION_INCOMPLETE_decision_owner_decision_date_decision_notes_followup_required_yes_or_no** | Answer-layer evaluation failed for question: What is the best firewall vendor for my company? |
| MGMT-DEC-002 | **P1** | `P1_NOT_STARTED` | `START_ACTION` | `START_ACTION` | **DECISION_INCOMPLETE_decision_owner_decision_date_decision_notes_followup_required_yes_or_no** | Answer-layer evaluation failed for question: What is the current USD to EUR exchange rate? |
| MGMT-DEC-003 | **P2** | `NOT_STARTED_NO_TARGET_DATE` | `START_ACTION` | `START_ACTION` | **DECISION_INCOMPLETE_decision_owner_decision_date_decision_notes_followup_required_yes_or_no** | Dashboard overall status is REVIEW_REQUIRED_EVALUATION_FAILURES. |

## Allowed Management Decisions

- `PENDING_DECISION`
- `START_ACTION`
- `CONTINUE_ACTION`
- `ESCALATE`
- `REASSIGN_OWNER`
- `ACCEPT_RISK`
- `DEFER_ACTION`
- `MARK_RESOLVED`
- `ADD_EVIDENCE`
- `CORRECT_RECORD`
- `NO_ACTION_REQUIRED`

## Manual Fields Preserved on Rerun

- `management_decision`
- `decision_owner`
- `decision_date`
- `decision_notes`
- `followup_required`
- `followup_date`
- `followup_owner`

## Decision Completeness Rule

Any non-pending decision should include:

- `decision_owner`
- `decision_date` in `YYYY-MM-DD` format
- `decision_notes`
- `followup_required` as `yes` or `no`

If `followup_required` is `yes`, also include:

- `followup_date` in `YYYY-MM-DD` format
- `followup_owner`

## Governance Rule

> Management review is not complete until decisions, rationale, owners, dates, and follow-up needs are recorded.

## One-Sentence Takeaway

> A review packet becomes governable when management decisions are recorded and follow-up is explicit.
