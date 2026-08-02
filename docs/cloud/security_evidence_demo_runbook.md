# Security Evidence Automation MVP - Demo Runbook

## Demonstration Objective

Show how the prototype converts security evidence into bounded answers, visible gaps, human decisions, management follow-up, and executive posture.

## Time Limit

Five minutes.

The demonstration should explain the operating model rather than inventory every generated file.

## Core Message

> The system does not ask AI to be trustworthy by default. It creates a workflow that makes AI-assisted security claims bounded, traceable, reviewable, and management-owned.

---

## Pre-Demonstration Check

Before presenting:

- Confirm the latest artifact chain has been generated.
- Open the required files in advance.
- Confirm the demonstrated questions produce the expected results.
- Identify any current review-required conditions.
- Be prepared to explain unresolved conditions honestly.
- Do not demonstrate an unverified query.
- Do not represent simulated decisions as real organizational approvals.

## Files to Open

Open these files in this order:

1. `docs/cloud/security_evidence_portfolio_case_study.md`
2. `docs/cloud/security_evidence_control_narrative.md`
3. `ai/security_evidence_corpus_manifest.csv`
4. `docs/cloud/security_evidence_status_dashboard.md`
5. `ai/security_evidence_gap_register.csv`
6. `ai/security_evidence_traceability_exceptions.csv`
7. `ai/security_evidence_exception_management_decisions.csv`
8. `ai/security_evidence_decision_followup_tracker.csv`
9. `docs/cloud/security_evidence_management_closeout_summary.md`
10. `docs/cloud/security_evidence_executive_summary.md`

---

## 0:00-0:30 - State the Problem

### Show

`docs/cloud/security_evidence_portfolio_case_study.md`

### Say

Security teams often possess large amounts of evidence but lack a controlled way to connect that evidence to questions, findings, decisions, and closeout.

AI-assisted retrieval can make evidence easier to use, but it creates a second problem: the system may answer beyond the evidence or hide what is missing.

I built this prototype to demonstrate a governed evidence workflow rather than an inherently trusted chatbot.

---

## 0:30-1:15 - Explain the Architecture

### Show

`docs/cloud/security_evidence_control_narrative.md`

### Say

The workflow begins with collected and validated evidence. It packages that evidence into a controlled corpus, retrieves relevant evidence candidates, generates bounded answers, evaluates those answers, and registers unsupported questions as gaps.

The process then adds human adjudication, exception management, management decisions, follow-up, and closeout.

The governing rule is:

> No approved evidence, no confident answer.

### Emphasize

Retrieval does not equal truth.

A retrieved artifact is an evidence candidate until the workflow determines whether it supports the answer.

---

## 1:15-2:00 - Show the Evidence Layer

### Show

`ai/security_evidence_corpus_manifest.csv`

### Say

The corpus manifest identifies the evidence available to the answer layer.

Each record provides a traceable connection between the source artifact and the controlled evidence system.

The quality of the answer layer depends on:

- Evidence completeness
- Evidence approval
- Accurate metadata
- Retrieval quality
- Evaluation logic

The system cannot responsibly answer questions requiring evidence that the corpus does not contain.

---

## 2:00-3:00 - Demonstrate Bounded Answer Behavior

### Show

One verified supported question and its evidence references.

Then show one verified out-of-scope question that produces an abstention.

### Say

A supported question should produce an answer tied to specific evidence.

An unsupported or out-of-scope question should produce an insufficient-evidence response rather than an invented answer.

The desired decision table is:

| Expected Result | Actual Result | Evaluation |
|---|---|---|
| Answer | Answer | Pass |
| Abstain | Abstain | Pass |
| Answer | Abstain | Fail |
| Abstain | Answer | Fail |

This separates a safe refusal from an answer-layer malfunction.

### Demonstration Rule

Do not use a negative-test query until the evaluator correctly recognizes expected abstention.

If an evaluation defect remains open, describe it as a known prototype limitation rather than concealing or bypassing it.

---

## 3:00-4:00 - Trace One Item Through Governance

### Show

- `ai/security_evidence_gap_register.csv`
- `ai/security_evidence_traceability_exceptions.csv`
- `ai/security_evidence_exception_management_decisions.csv`
- `ai/security_evidence_decision_followup_tracker.csv`

### Say

An unsupported answer does not disappear into a log.

The workflow makes it visible as a gap or exception, identifies ownership, records a human or management decision, and determines whether follow-up is required.

A technical finding is not closed merely because somebody acknowledges it.

Closeout requires:

- Supporting evidence
- Documented rationale
- Authorized cancellation
- Accepted disposition
- Or an explicit determination that no follow-up is required

### Emphasize

The system separates:

```text
technical condition
human review
management decision
required action
verified closeout