from pathlib import Path
from datetime import datetime, timezone
import csv


SOURCE_MATRIX = Path("security/cloud_admin_access_patterns.csv")
RUBRIC_FILE = Path("security/cloud_admin_access_decision_rubric.csv")
DECISION_GUIDE_FILE = Path("docs/cloud/cloud_admin_access_decision_guide.md")
EVIDENCE_REPORT_FILE = Path("evidence/generated/cloud_admin_access_decision_guide_report.md")


REQUIRED_SOURCE_COLUMNS = [
    "pattern",
    "on_prem_analogy",
    "cloud_implementation",
    "primary_risk_reduced",
    "risk_introduced",
    "evidence_to_collect",
    "maturity_read",
    "aws_reference",
    "azure_equivalent",
    "gcp_equivalent",
    "oci_equivalent",
]


RUBRIC = [
    {
        "pattern": "Direct public SSH/RDP",
        "exposure_risk_1_low_5_high": "5",
        "standing_privilege_risk_1_low_5_high": "4",
        "logging_strength_1_weak_5_strong": "2",
        "operational_burden_1_low_5_high": "1",
        "governance_strength_1_weak_5_strong": "1",
        "default_decision": "Avoid for production; allow only for temporary lab use with time-bound, source-restricted access.",
        "executive_read": "Fast to set up, weak to defend.",
    },
    {
        "pattern": "Bastion host / jump box",
        "exposure_risk_1_low_5_high": "3",
        "standing_privilege_risk_1_low_5_high": "3",
        "logging_strength_1_weak_5_strong": "3",
        "operational_burden_1_low_5_high": "3",
        "governance_strength_1_weak_5_strong": "3",
        "default_decision": "Accept as a transitional pattern when hardened, patched, monitored, and limited to private workload access.",
        "executive_read": "Useful choke point, but now the choke point is high-value infrastructure.",
    },
    {
        "pattern": "VPN or private connectivity",
        "exposure_risk_1_low_5_high": "2",
        "standing_privilege_risk_1_low_5_high": "3",
        "logging_strength_1_weak_5_strong": "3",
        "operational_burden_1_low_5_high": "4",
        "governance_strength_1_weak_5_strong": "3",
        "default_decision": "Use when private network access is required, but pair it with segmentation, MFA, and narrow admin paths.",
        "executive_read": "Private path is better than public exposure, but private network access is not the same as least privilege.",
    },
    {
        "pattern": "Identity-aware session management",
        "exposure_risk_1_low_5_high": "1",
        "standing_privilege_risk_1_low_5_high": "2",
        "logging_strength_1_weak_5_strong": "5",
        "operational_burden_1_low_5_high": "2",
        "governance_strength_1_weak_5_strong": "5",
        "default_decision": "Prefer for modern cloud administration when the service supports logging, identity policy, and private workload access.",
        "executive_read": "Usually the best default because it reduces inbound exposure and improves evidence quality.",
    },
    {
        "pattern": "Privileged access workflow",
        "exposure_risk_1_low_5_high": "1",
        "standing_privilege_risk_1_low_5_high": "1",
        "logging_strength_1_weak_5_strong": "5",
        "operational_burden_1_low_5_high": "4",
        "governance_strength_1_weak_5_strong": "5",
        "default_decision": "Use for high-risk, regulated, privileged, or production environments where approval and time-bound access matter.",
        "executive_read": "Highest governance value when privilege must be temporary, approved, and reviewable.",
    },
]


SCENARIOS = [
    {
        "scenario": "Temporary lab or disposable sandbox",
        "recommended_pattern": "Direct public SSH/RDP may be acceptable only as a time-bound exception; identity-aware session management is still better if available.",
        "why": "The business risk is low, but internet-exposed management ports should still be source-restricted and temporary.",
        "minimum_evidence": "Security group/source restriction, expiration date, owner, purpose, and cleanup confirmation.",
    },
    {
        "scenario": "Private production workload",
        "recommended_pattern": "Identity-aware session management, VPN/private connectivity with segmentation, or hardened bastion as a transitional pattern.",
        "why": "Production administration should not depend on broad public management exposure.",
        "minimum_evidence": "No public inbound admin ports on private workloads, authorized admin identities, session logs, and route/security group evidence.",
    },
    {
        "scenario": "Regulated or high-risk system",
        "recommended_pattern": "Privileged access workflow plus identity-aware session management where possible.",
        "why": "The control objective is not only access; it is approved, time-bound, attributable, monitored, and reviewable access.",
        "minimum_evidence": "Approval trail, temporary privilege assignment, session recording/logging, break-glass review, and periodic access review.",
    },
    {
        "scenario": "Legacy lift-and-shift migration",
        "recommended_pattern": "VPN/private connectivity or bastion may be acceptable as a transition, with a roadmap toward identity-aware sessions and PAM.",
        "why": "Legacy administration often arrives with network assumptions that should be reduced over time.",
        "minimum_evidence": "Current access path, compensating controls, target-state pattern, migration owner, and retirement date for weaker access methods.",
    },
    {
        "scenario": "Multi-cloud enterprise",
        "recommended_pattern": "Normalize the control objective across providers and collect provider-native evidence for the same access pattern.",
        "why": "The services differ, but the governance question is the same: who accessed what, how, under what authority, and where is the evidence?",
        "minimum_evidence": "Provider-native logs, identity records, access path diagrams, session records, and cross-cloud control mapping.",
    },
]


def read_source_patterns() -> list[dict[str, str]]:
    """Read and validate the Day 53 source matrix."""
    if not SOURCE_MATRIX.exists():
        raise FileNotFoundError(f"Missing source matrix: {SOURCE_MATRIX}")

    with SOURCE_MATRIX.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames or []
        missing_columns = [column for column in REQUIRED_SOURCE_COLUMNS if column not in headers]

        if missing_columns:
            raise ValueError(
                "Source matrix is missing required columns: "
                + ", ".join(missing_columns)
                + f". Regenerate {SOURCE_MATRIX} using the Day 53 script."
            )

        rows = list(reader)

    if not rows:
        raise ValueError(f"Source matrix has headers but no pattern rows: {SOURCE_MATRIX}")

    return rows


def write_rubric() -> None:
    """Write the pattern decision rubric CSV."""
    RUBRIC_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(RUBRIC[0].keys())

    with RUBRIC_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(RUBRIC)


def find_pattern(patterns: list[dict[str, str]], pattern_name: str) -> dict[str, str]:
    """Find a pattern row by name."""
    for pattern in patterns:
        if pattern["pattern"] == pattern_name:
            return pattern

    return {
        "pattern": pattern_name,
        "on_prem_analogy": "Not found in source matrix",
        "cloud_implementation": "Not found in source matrix",
        "primary_risk_reduced": "Not found in source matrix",
        "risk_introduced": "Not found in source matrix",
        "evidence_to_collect": "Not found in source matrix",
        "maturity_read": "Not found in source matrix",
        "aws_reference": "Not found in source matrix",
        "azure_equivalent": "Not found in source matrix",
        "gcp_equivalent": "Not found in source matrix",
        "oci_equivalent": "Not found in source matrix",
    }


def build_decision_guide(patterns: list[dict[str, str]]) -> str:
    """Build the cloud access pattern decision guide markdown."""
    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Cloud Administrative Access Pattern Decision Guide",
        "",
        f"Generated: `{timestamp}`",
        "",
        "## Purpose",
        "",
        "This guide turns cloud administrative access patterns into architecture decision logic.",
        "",
        "The goal is to choose and defend an access pattern based on risk, evidence, operational burden, and governance maturity.",
        "",
        "## Core Control Objective",
        "",
        "The objective is not to deploy a specific named service.",
        "",
        "The objective is to ensure administrative access is authorized, minimized, segmented, monitored, time-appropriate, and reviewable.",
        "",
        "## Decision Rule",
        "",
        "Choose the weakest pattern only when the risk is low, the exposure is temporary, and the evidence is clear.",
        "",
        "Choose stronger patterns when the workload is production, regulated, privileged, externally exposed, or operationally critical.",
        "",
        "## Fast Decision Tree",
        "",
        "1. Does the workload need public inbound SSH/RDP?",
        "   - If yes, challenge the assumption.",
        "   - If no, prefer private or identity-aware access.",
        "",
        "2. Can administrative access be brokered through identity instead of network exposure?",
        "   - If yes, prefer identity-aware session management.",
        "   - If no, use private connectivity or a hardened bastion as a transitional pattern.",
        "",
        "3. Is the system production, regulated, privileged, or high impact?",
        "   - If yes, add privileged access workflow controls.",
        "   - If no, still require logging, owner, and cleanup evidence.",
        "",
        "4. Can the access decision be reviewed later?",
        "   - If no, the pattern is not mature enough.",
        "   - If yes, retain the evidence trail.",
        "",
        "## Pattern Rubric",
        "",
        "Scoring note: lower is better for risk and burden; higher is better for logging and governance strength.",
        "",
        "| Pattern | Exposure Risk | Standing Privilege Risk | Logging Strength | Operational Burden | Governance Strength | Default Decision |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]

    for row in RUBRIC:
        lines.append(
            f"| {row['pattern']} | "
            f"{row['exposure_risk_1_low_5_high']} | "
            f"{row['standing_privilege_risk_1_low_5_high']} | "
            f"{row['logging_strength_1_weak_5_strong']} | "
            f"{row['operational_burden_1_low_5_high']} | "
            f"{row['governance_strength_1_weak_5_strong']} | "
            f"{row['default_decision']} |"
        )

    lines.extend(
        [
            "",
            "## Scenario Recommendations",
            "",
            "| Scenario | Recommended Pattern | Why | Minimum Evidence |",
            "|---|---|---|---|",
        ]
    )

    for scenario in SCENARIOS:
        lines.append(
            f"| {scenario['scenario']} | {scenario['recommended_pattern']} | "
            f"{scenario['why']} | {scenario['minimum_evidence']} |"
        )

    lines.extend(
        [
            "",
            "## Pattern Defense Notes",
            "",
        ]
    )

    for row in RUBRIC:
        source = find_pattern(patterns, row["pattern"])
        lines.extend(
            [
                f"### {row['pattern']}",
                "",
                f"**Executive read:** {row['executive_read']}",
                "",
                f"**On-prem analogy:** {source['on_prem_analogy']}",
                "",
                f"**Cloud implementation:** {source['cloud_implementation']}",
                "",
                f"**Risk reduced:** {source['primary_risk_reduced']}",
                "",
                f"**Risk introduced:** {source['risk_introduced']}",
                "",
                f"**Evidence to collect:** {source['evidence_to_collect']}",
                "",
                f"**Multi-cloud translation:** AWS: {source['aws_reference']} | Azure: {source['azure_equivalent']} | GCP: {source['gcp_equivalent']} | OCI: {source['oci_equivalent']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Executive Summary Language",
            "",
            "Use this language when explaining the decision:",
            "",
            "> We are not selecting an access pattern because it is fashionable or provider-native. We are selecting it because it changes the risk profile in a defensible way and gives us evidence we can review later.",
            "",
            "## Final Carry-Forward",
            "",
            "A strong cloud access decision names the pattern, the risk tradeoff, the evidence trail, and the provider-native implementation.",
            "",
        ]
    )

    return "\n".join(lines)


def write_decision_guide(patterns: list[dict[str, str]]) -> None:
    """Write the decision guide markdown."""
    DECISION_GUIDE_FILE.parent.mkdir(parents=True, exist_ok=True)
    DECISION_GUIDE_FILE.write_text(build_decision_guide(patterns), encoding="utf-8")


def write_evidence_report(pattern_count: int) -> None:
    """Write an evidence report for decision guide generation."""
    EVIDENCE_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Cloud Access Pattern Decision Guide Generation Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        "Overall Status: **PASS**",
        "",
        "## Purpose",
        "",
        "This report records generation of the cloud administrative access pattern decision guide and rubric.",
        "",
        "## Source Artifact",
        "",
        f"- `{SOURCE_MATRIX.as_posix()}`",
        "",
        "## Generated Artifacts",
        "",
        f"- `{RUBRIC_FILE.as_posix()}`",
        f"- `{DECISION_GUIDE_FILE.as_posix()}`",
        "",
        "## Validation",
        "",
        f"- Source patterns read: `{pattern_count}`",
        f"- Required source columns present: `{len(REQUIRED_SOURCE_COLUMNS)}`",
        f"- Rubric entries generated: `{len(RUBRIC)}`",
        f"- Scenario recommendations generated: `{len(SCENARIOS)}`",
        "",
        "## Portfolio Relevance",
        "",
        "This artifact moves from cloud vocabulary to architecture decision-making.",
        "",
        "It demonstrates the ability to select administrative access patterns based on exposure, identity, logging, operational burden, governance strength, and evidence requirements.",
        "",
    ]

    EVIDENCE_REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Generate the Day 55 cloud access pattern decision guide."""
    patterns = read_source_patterns()

    write_rubric()
    write_decision_guide(patterns)
    write_evidence_report(pattern_count=len(patterns))

    print(f"Decision rubric written to: {RUBRIC_FILE}")
    print(f"Decision guide written to: {DECISION_GUIDE_FILE}")
    print(f"Evidence report written to: {EVIDENCE_REPORT_FILE}")
    print(f"Source patterns read: {len(patterns)}")
    print("Overall Status: PASS")


if __name__ == "__main__":
    main()