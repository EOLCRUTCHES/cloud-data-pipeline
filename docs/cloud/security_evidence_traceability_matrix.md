# Security Evidence Traceability Matrix

Generated: `2026-07-24T20:54:44.238356+00:00`

Overall Status: **TRACEABILITY_COMPLETE**

## Purpose

This matrix maps security evidence artifacts to the control questions they support.

It prevents the evidence system from becoming a set of disconnected scripts and reports.

## Summary

| Field | Value |
|---|---:|
| Traceability rows | `20` |
| Traceable artifacts | `20` |
| Missing artifacts | `0` |
| Empty artifacts | `0` |
| Machine-readable artifacts | `13` |
| Human-readable artifacts | `7` |

## Matrix

| ID | Stage | Control Question | Artifact | Status | Signal |
|---|---|---|---|---|---|
| TRACE-001 | Permission Preflight | Was the collector authorized to inspect the required AWS evidence? | `security/aws_evidence_collector_permissions.csv` | **TRACEABLE** | AUTHORIZED=3 |
| TRACE-002 | Evidence Collection | What AWS administrative port exposure was observed? | `security/aws_admin_port_exposure_findings.csv` | **TRACEABLE** | no_rows |
| TRACE-003 | Evidence Workflow | Was collection packaged into a reviewable evidence workflow? | `docs/cloud/aws_admin_access_evidence_package.md` | **TRACEABLE** | status=PASS |
| TRACE-004 | Evidence Workflow | What was the latest workflow execution result? | `evidence/generated/aws_admin_access_evidence_workflow_report.md` | **TRACEABLE** | status=PASS |
| TRACE-005 | Corpus | Which approved evidence artifacts are available for retrieval? | `ai/security_evidence_corpus_manifest.csv` | **TRACEABLE** | records=57 |
| TRACE-006 | Corpus | What is the approved local evidence corpus content? | `ai/security_evidence_corpus.jsonl` | **TRACEABLE** | records=57 |
| TRACE-007 | Retrieval | Which evidence was retrieved for security questions? | `ai/security_evidence_query_results.csv` | **TRACEABLE** | QUERY-001=5; QUERY-002=5; QUERY-003=5; QUERY-004=5 |
| TRACE-008 | Answer Layer | Did the answer layer cite approved local evidence? | `ai/security_evidence_answer_sources.csv` | **TRACEABLE** | SEC-EVID-0010=1; SEC-EVID-0011=1; SEC-EVID-0037=1; SEC-EVID-0038=1; SEC-EVID-0043=1 |
| TRACE-009 | Answer Layer | What source-backed answer was generated? | `ai/security_evidence_answer.md` | **TRACEABLE** | status=SOURCE_BACKED_REVIEW_REQUIRED |
| TRACE-010 | Evaluation | Are answer guardrails passing? | `ai/security_evidence_eval_results.csv` | **TRACEABLE** | FAIL=2; PASS=3 |
| TRACE-011 | Gap Management | Which unsupported questions became managed evidence gaps? | `ai/security_evidence_gap_register.csv` | **TRACEABLE** | BOUNDARY_REVIEW=2; POSSIBLE_FALSE_POSITIVE_REVIEW=1; SUPPORTED=2 |
| TRACE-012 | Remediation Evidence | What evidence supports admin-port remediation? | `security/aws_admin_port_remediation_register.csv` | **TRACEABLE** | PUBLIC_ADMIN_EXPOSURE_CLEARED_PENDING_REVIEW=1 |
| TRACE-013 | Remediation Evidence | What human-readable remediation record exists? | `docs/cloud/aws_admin_port_remediation_record.md` | **TRACEABLE** | status=PUBLIC_ADMIN_EXPOSURE_CLEARED_PENDING_REVIEW |
| TRACE-014 | Gap Closure | Which gaps have closure evidence available? | `ai/security_evidence_gap_closure_register.csv` | **TRACEABLE** | CLOSURE_EVIDENCE_AVAILABLE_REVIEW_REQUIRED=1; NOT_A_GAP_SUPPORTED=2; RETRIEVAL_REVIEW_NEEDED=2 |
| TRACE-015 | Human Review | Who reviewed closure and what did they decide? | `ai/security_evidence_reviewer_decisions.csv` | **TRACEABLE** | CLOSE_GAP=5 |
| TRACE-016 | Adjudication | What is the final adjudicated status of each gap? | `ai/security_evidence_adjudicated_gap_status.csv` | **TRACEABLE** | CLOSED=5 |
| TRACE-017 | Adjudication | What is the human-readable adjudication summary? | `docs/cloud/security_evidence_adjudication_summary.md` | **TRACEABLE** | status=ADJUDICATION_COMPLETE |
| TRACE-018 | Status Dashboard | What is the current health of the evidence system? | `ai/security_evidence_status_summary.csv` | **TRACEABLE** | overall_status=REVIEW_REQUIRED_EVALUATION_FAILURES |
| TRACE-019 | Status Dashboard | What dashboard can an executive or auditor read? | `docs/cloud/security_evidence_status_dashboard.md` | **TRACEABLE** | status=REVIEW_REQUIRED_EVALUATION_FAILURES |
| TRACE-020 | Evidence Index | Where is the consolidated evidence index? | `evidence/evidence_index.md` | **TRACEABLE** | title=Evidence Index |

## Interpretation

- `TRACEABLE` means the artifact exists and can be tied to a control question.
- `TRACE_REVIEW_EMPTY_ARTIFACT` means the artifact exists but has no content.
- `TRACE_REVIEW_MISSING_ARTIFACT` means the expected artifact was not found.

## Governance Rule

> Every important evidence artifact should answer a named control question.

## One-Sentence Takeaway

> Traceability turns a pile of evidence files into a defensible control story.
