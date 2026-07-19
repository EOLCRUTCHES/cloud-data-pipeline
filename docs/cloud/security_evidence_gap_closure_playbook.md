# Security Evidence Gap Closure Playbook

## Purpose

This playbook defines how evidence gaps move from open status to closure review.

## Gap Lifecycle

```text
Question asked
↓
Corpus searched
↓
No sufficient source found
↓
Evidence gap registered
↓
New evidence collected or generated
↓
Corpus rebuilt
↓
Gap register rerun
↓
Closure register generated
↓
Human reviewer closes, partially closes, or keeps gap open
```

## Closure Rules

| Status | Meaning |
|---|---|
| `CLOSURE_EVIDENCE_AVAILABLE_REVIEW_REQUIRED` | Evidence exists that may close the gap, but reviewer approval is required. |
| `PARTIAL_CLOSURE_EVIDENCE_REVIEW_REQUIRED` | Evidence addresses part of the gap, but residual findings remain. |
| `GAP_OPEN_EVIDENCE_NEEDED` | No matching closure evidence exists yet. |
| `GAP_REMAINS_RISK_OPEN` | Evidence shows the risk still exists. |
| `GAP_REMAINS_EVIDENCE_INCOMPLETE` | The evidence workflow did not run completely. |
| `RETRIEVAL_REVIEW_NEEDED` | The answer layer found related sources, but relevance or sufficiency needs review. |

## Governance Rule

> New evidence does not automatically close a gap. It creates a closure-review event.
