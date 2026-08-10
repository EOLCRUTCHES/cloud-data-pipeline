# Security Evidence Demo Release Validation

Validated: `2026-08-10T13:19:50.070062+00:00`

Release ID: `SED-3D13EAC3C2E3`

Integrity Status: **RELEASE_INTEGRITY_VERIFIED**

## Validation Counts

- Match: `12`
- Modified: `0`
- Missing: `0`
- Empty: `0`

## Artifact Results

| Artifact | Result | Current status | Path |
|---|---|---|---|
| Portfolio case study | MATCH | Present | `docs/cloud/security_evidence_portfolio_case_study.md` |
| Demo runbook | MATCH | Present | `docs/cloud/security_evidence_demo_runbook.md` |
| Demo readiness | MATCH | Present | `docs/cloud/security_evidence_demo_readiness.md` |
| Control narrative | MATCH | Present | `docs/cloud/security_evidence_control_narrative.md` |
| Evidence corpus manifest | MATCH | Present | `ai/security_evidence_corpus_manifest.csv` |
| Status dashboard | MATCH | Present | `docs/cloud/security_evidence_status_dashboard.md` |
| Gap register | MATCH | Present | `ai/security_evidence_gap_register.csv` |
| Traceability exceptions | MATCH | Present | `ai/security_evidence_traceability_exceptions.csv` |
| Management decisions | MATCH | Present | `ai/security_evidence_exception_management_decisions.csv` |
| Decision follow-up tracker | MATCH | Present | `ai/security_evidence_decision_followup_tracker.csv` |
| Management closeout summary | MATCH | Present | `docs/cloud/security_evidence_management_closeout_summary.md` |
| Executive summary | MATCH | Present | `docs/cloud/security_evidence_executive_summary.md` |

## Interpretation

`MATCH` means the current file has the same size and SHA-256 hash recorded in the release manifest.

`MODIFIED`, `MISSING`, or `EMPTY` means the current working artifact no longer matches the recorded release.

## Governance Rule

> A failed integrity check does not prove malicious tampering. It proves only that the current artifact set is not identical to the recorded release.
