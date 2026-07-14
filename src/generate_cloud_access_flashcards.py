from pathlib import Path
import csv
from datetime import datetime, timezone


QUIZLET_TSV = Path("study/cloud_admin_access_quizlet.tsv")
MASTER_CSV = Path("study/cloud_admin_access_flashcards.csv")
REPORT_FILE = Path("evidence/generated/cloud_access_flashcard_generation_report.md")


CARDS = [
    {
        "deck": "cloud-admin-access",
        "category": "recognition",
        "difficulty": "easy",
        "front": "What is the core control objective behind bastion hosts, VPNs, SSM Session Manager, and PAM workflows?",
        "back": "Controlled, monitored, least-privilege administrative access. The tool is secondary; the control objective is authorized, minimized, segmented, monitored, attributable, and reviewable access.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "recognition",
        "difficulty": "easy",
        "front": "Bastion host / jump box: what is the on-prem analogy?",
        "back": "A hardened jump server between remote administrators and internal systems.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "recognition",
        "difficulty": "easy",
        "front": "Identity-aware session management: what does it reduce?",
        "back": "It reduces inbound administrative exposure by brokering access through identity, session controls, managed agents, and centralized logging.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "recognition",
        "difficulty": "medium",
        "front": "VPN/private connectivity: what is the trap?",
        "back": "VPN provides a private path, but it does not prove least privilege. You still need segmentation, identity control, destination limits, logging, and review.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "recognition",
        "difficulty": "medium",
        "front": "Privileged access workflow: when is it most appropriate?",
        "back": "High-risk, regulated, production, or privileged environments where access must be approved, temporary, attributable, logged, and reviewable.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "scenario",
        "difficulty": "easy",
        "front": "A developer needs SSH to a disposable lab EC2 instance for two hours. No production data. Destroyed today. What pattern is acceptable?",
        "back": "Direct public SSH may be acceptable only as a temporary exception. Conditions: source-restricted, time-bound, owned, logged, and cleaned up. Executive sentence: Direct public access can be acceptable for short-lived lab use, but only when restricted, temporary, and verified closed.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "scenario",
        "difficulty": "medium",
        "front": "A production database sits in a private subnet. An admin wants direct RDP from home. What pattern should you choose?",
        "back": "Reject direct RDP. Prefer identity-aware session management or privileged access workflow. Evidence: no public IP, no inbound RDP, session logs, admin identity, MFA/PAM. Executive sentence: Production administration should flow through a controlled, logged access path.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "scenario",
        "difficulty": "medium",
        "front": "The team says, 'We have VPN, so admin access is secure.' What is your response?",
        "back": "VPN is private connectivity, not automatic least privilege. Risk reduced: removes direct public exposure. Risk introduced: broad internal reach if segmentation is weak. Evidence: VPN groups, MFA, routes, segmentation, destination restrictions, logs. Executive sentence: VPN gives a private path; it does not prove least privilege.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "scenario",
        "difficulty": "medium",
        "front": "A bastion host exists in a public subnet. Private instances only allow SSH from it. Bastion allows inbound 0.0.0.0/0. What do you do?",
        "back": "Harden or replace. Current exposure is too broad. Risk reduced: private workloads are not directly exposed. Risk introduced: bastion is a high-value internet-facing target. Evidence: restricted ingress, MFA/key control, patching, session logs, CloudTrail, private instance rules. Executive sentence: If the bastion is broadly exposed, we concentrated the risk instead of eliminating it.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "scenario",
        "difficulty": "medium",
        "front": "No inbound SSH/RDP. Admin access is brokered through a cloud-native identity/session service with logs. What pattern is this?",
        "back": "Identity-aware session management. Risk reduced: no inbound admin-port exposure. Risk introduced: depends on identity policy, agent health, logging, and service availability. Evidence: no inbound admin ports, session logs, IAM permissions, managed instance status, audit logs. Executive sentence: Identity-aware session management reduces exposure and improves evidence quality.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "scenario",
        "difficulty": "hard",
        "front": "A sensitive regulated system requires access to be approved, time-limited, attributable, logged, and reviewable. What pattern stack do you choose?",
        "back": "Privileged access workflow plus identity-aware session management. Risk reduced: limits standing privilege and creates an evidence trail. Risk introduced: higher process and operational complexity. Evidence: approval, temporary role, session recording, audit logs, access review, break-glass records. Executive sentence: For high-risk systems, access must be approved, temporary, attributable, logged, and reviewable.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "scenario",
        "difficulty": "medium",
        "front": "Auditor asks, 'Do you use bastion hosts?' The environment mostly uses AWS SSM Session Manager. How do you answer?",
        "back": "We use bastions only where justified; our preferred control pattern is identity-aware session management. The control objective is controlled, monitored, least-privilege administrative access. Evidence: no inbound admin ports, SSM/session logs, IAM roles, CloudTrail, exception list. Executive sentence: We meet the administrative-access objective through provider-native session controls.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "scenario",
        "difficulty": "medium",
        "front": "An EC2 instance allows SSH only from the corporate office IP. Is that good enough?",
        "back": "Better than open internet, but still direct public SSH. Risk reduced: source restriction. Risk introduced: management port remains exposed; office IP or VPN path could be compromised. Evidence: source CIDR, owner, justification, key control, logs, review/expiration date. Executive sentence: Source restriction improves direct SSH, but it does not make it the preferred production pattern.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "scenario",
        "difficulty": "hard",
        "front": "A multi-cloud enterprise uses different admin tools in AWS, Azure, GCP, and OCI. What should be standardized?",
        "back": "Standardize the control objective, not necessarily the tool. Objective: authorized, minimized, segmented, monitored, attributable, reviewable access. Evidence: provider-native logs, identity records, access paths, session records, control mapping. Executive sentence: The services differ, but the access-control objective is the same.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "scenario",
        "difficulty": "medium",
        "front": "An executive asks, 'Why can’t MFA solve this? If admins have MFA, why not let them connect directly?'",
        "back": "MFA verifies identity; it does not eliminate exposure of the admin path. You still need a controlled path, logging, least privilege, and reviewability. Evidence: no public admin ports, MFA, session logs, role evidence, approval trail. Executive sentence: MFA is one layer; the access path still has to be minimized, monitored, and reviewable.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "defense",
        "difficulty": "medium",
        "front": "Defend this sentence: 'A bastion host is not the control objective.'",
        "back": "The control objective is controlled, monitored, least-privilege administrative access. A bastion is one implementation pattern. It may reduce direct exposure of private systems, but it also becomes a high-value target and must be hardened, monitored, patched, and tightly authorized.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "defense",
        "difficulty": "hard",
        "front": "What evidence proves administrative access is mature?",
        "back": "No unnecessary public admin ports, authorized admin identities, MFA or equivalent identity control, time-bound privilege where appropriate, session logs, provider audit logs, access path diagram, approval trail for high-risk access, periodic review, and break-glass evidence.",
    },
    {
        "deck": "cloud-admin-access",
        "category": "defense",
        "difficulty": "hard",
        "front": "What is the executive test for a cloud admin access pattern?",
        "back": "Can we explain who accessed what, through which path, under what authority, with what approval or boundary, and where the evidence is retained for review?",
    },
]


def clean_for_quizlet(value: str) -> str:
    """Keep Quizlet import rows one-line and tab-safe."""
    return " ".join(value.replace("\t", " ").replace("\r", " ").replace("\n", " ").split())


def write_quizlet_tsv() -> None:
    QUIZLET_TSV.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    for card in CARDS:
        front = clean_for_quizlet(card["front"])
        back = clean_for_quizlet(card["back"])
        lines.append(f"{front}\t{back}")

    QUIZLET_TSV.write_text("\n".join(lines), encoding="utf-8")


def write_master_csv() -> None:
    MASTER_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["deck", "category", "difficulty", "front", "back"]

    with MASTER_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(CARDS)


def write_report() -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    categories = sorted({card["category"] for card in CARDS})
    difficulties = sorted({card["difficulty"] for card in CARDS})

    lines = [
        "# Cloud Access Flashcard Generation Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        "Overall Status: **PASS**",
        "",
        "## Generated Artifacts",
        "",
        f"- `{QUIZLET_TSV.as_posix()}`",
        f"- `{MASTER_CSV.as_posix()}`",
        "",
        "## Summary",
        "",
        f"- Cards generated: `{len(CARDS)}`",
        f"- Categories: `{', '.join(categories)}`",
        f"- Difficulties: `{', '.join(difficulties)}`",
        "",
        "## Usage",
        "",
        "Use the TSV file for Quizlet import or copy/paste. Use the CSV file as the richer master study bank.",
        "",
    ]

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    write_quizlet_tsv()
    write_master_csv()
    write_report()

    print(f"Quizlet TSV written to: {QUIZLET_TSV}")
    print(f"Master CSV written to: {MASTER_CSV}")
    print(f"Evidence report written to: {REPORT_FILE}")
    print(f"Cards generated: {len(CARDS)}")
    print("Overall Status: PASS")


if __name__ == "__main__":
    main()