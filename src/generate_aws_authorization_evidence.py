from pathlib import Path
from datetime import datetime, timezone


S3_REPORT_FILE = Path("evidence/generated/aws_s3_inventory_report.md")
AUTHZ_REPORT_FILE = Path("evidence/generated/aws_authorization_evidence_report.md")


def read_s3_report() -> str:
    """Read the AWS S3 inventory report if it exists."""
    if not S3_REPORT_FILE.exists():
        return ""

    return S3_REPORT_FILE.read_text(encoding="utf-8")


def detect_authorization_issue(report_text: str) -> dict[str, str]:
    """Detect authorization issues from the S3 inventory report."""
    lower_text = report_text.lower()

    finding = {
        "status": "REVIEW",
        "condition_detected": "No S3 report found or no authorization condition detected.",
        "action": "Unavailable",
        "interpretation": "Run the S3 inventory collector before generating this evidence report.",
    }

    if not report_text:
        return finding

    if "listallmybuckets" in lower_text or "listallmybuckets" in report_text:
        finding["status"] = "AUTHORIZATION_LIMIT_DETECTED"
        finding["condition_detected"] = "AWS policy blocked account-wide S3 bucket listing."
        finding["action"] = "s3:ListAllMyBuckets"
        finding["interpretation"] = (
            "The AWS principal appears authenticated but does not have permission "
            "to perform account-wide S3 bucket inventory."
        )
        return finding

    if "accessdenied" in lower_text or "access denied" in lower_text:
        finding["status"] = "AUTHORIZATION_LIMIT_DETECTED"
        finding["condition_detected"] = "AWS returned an access-denied response."
        finding["action"] = "Unknown or not parsed"
        finding["interpretation"] = (
            "The AWS principal appears authenticated but lacks permission for the requested action."
        )
        return finding

    if "overall status: **pass**" in lower_text:
        finding["status"] = "PASS"
        finding["condition_detected"] = "S3 inventory completed successfully."
        finding["action"] = "s3:ListAllMyBuckets"
        finding["interpretation"] = "The AWS principal was able to list S3 buckets."
        return finding

    return finding


def write_authorization_report(finding: dict[str, str]) -> None:
    """Write AWS authorization evidence report."""
    AUTHZ_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# AWS Authorization Evidence Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{finding['status']}**",
        "",
        "## Purpose",
        "",
        "This report interprets AWS authorization results from cloud evidence collection.",
        "",
        "It treats permission limits as useful cloud security evidence instead of simple script failure.",
        "",
        "## Authorization Finding",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Condition detected | {finding['condition_detected']} |",
        f"| AWS action | `{finding['action']}` |",
        f"| Interpretation | {finding['interpretation']} |",
        "",
        "## Security Interpretation",
        "",
        "Authorization failures can be useful evidence because they show how identity, policy, and scope affect cloud operations.",
        "",
        "A blocked read-only inventory action may indicate least privilege, permission boundaries, service control policies, or intentionally limited lab permissions.",
        "",
        "## Control Relevance",
        "",
        "| Control Concept | Relevance |",
        "|---|---|",
        "| Least privilege | The principal does not have unrestricted account-wide S3 inventory permission. |",
        "| Evidence collection scope | Automation can only collect evidence allowed by its assigned permissions. |",
        "| Cloud governance | Security evidence depends on identity, authorization, and policy design. |",
        "| Audit readiness | Authorization limits should be documented so evidence gaps are explainable. |",
        "",
        "## Risk Relevance",
        "",
        "| Risk | Explanation |",
        "|---|---|",
        "| Evidence collection gap | The automation may not see all cloud resources if permissions are too limited. |",
        "| Overprivileged automation | Granting broad read access may improve evidence collection but increase exposure. |",
        "| Misinterpreted failure | Access denial could be mistaken for script failure instead of a governance boundary. |",
        "",
        "## Portfolio Relevance",
        "",
        "This report demonstrates practical cloud security judgment: permission failures are not ignored, hidden, or treated as generic errors.",
        "",
        "They are captured as evidence and interpreted in terms of least privilege, evidence scope, and cloud governance.",
        "",
    ]

    AUTHZ_REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")

    print(f"AWS authorization evidence report written to: {AUTHZ_REPORT_FILE}")
    print(f"Overall Status: {finding['status']}")


def main() -> None:
    """Generate AWS authorization evidence from the S3 inventory report."""
    report_text = read_s3_report()
    finding = detect_authorization_issue(report_text)
    write_authorization_report(finding)


if __name__ == "__main__":
    main()