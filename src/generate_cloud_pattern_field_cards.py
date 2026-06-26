from pathlib import Path
from datetime import datetime, timezone
import csv


SOURCE_MATRIX = Path("security/cloud_admin_access_patterns.csv")
FIELD_CARD_FILE = Path("docs/cloud/cloud_admin_access_field_cards.md")
EVIDENCE_REPORT_FILE = Path("evidence/generated/cloud_pattern_field_card_report.md")


EXECUTIVE_SENTENCES = {
    "Direct public SSH/RDP": (
        "Direct public administrative access is usually a weak pattern because it exposes management ports "
        "instead of forcing access through a controlled administrative path."
    ),
    "Bastion host / jump box": (
        "A bastion host is not the control objective; it is one way to provide controlled, monitored access "
        "into private systems."
    ),
    "VPN or private connectivity": (
        "Private connectivity reduces public exposure, but it still requires segmentation, identity controls, "
        "and evidence that access is limited."
    ),
    "Identity-aware session management": (
        "Identity-aware session management often improves on classic bastions by reducing inbound exposure "
        "and centralizing authorization and logging."
    ),
    "Privileged access workflow": (
        "Privileged access workflows are mature when they limit standing privilege, require approval, "
        "and preserve an auditable access trail."
    ),
}


def read_patterns() -> list[dict[str, str]]:
    """Read cloud administrative access patterns from the source CSV."""
    if not SOURCE_MATRIX.exists():
        raise FileNotFoundError(
            f"Missing source matrix: {SOURCE_MATRIX}. Run Day 53 first."
        )

    with SOURCE_MATRIX.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def get_value(pattern: dict[str, str], key: str) -> str:
    """Return a safe display value from a pattern row."""
    value = pattern.get(key, "").strip()
    if value:
        return value
    return "Not documented"


def build_field_cards(patterns: list[dict[str, str]]) -> str:
    """Build the portable field-card markdown."""
    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Cloud Administrative Access Pattern Field Cards",
        "",
        f"Generated: `{timestamp}`",
        "",
        "## Purpose",
        "",
        "These field cards convert cloud administrative access patterns into portable study notes.",
        "",
        "The goal is pattern fluency: understand what each pattern replaces, why it exists, what risk it reduces, what risk it introduces, and what evidence proves it is working.",
        "",
        "## Study Rule",
        "",
        "For each pattern, be able to explain it using this sentence:",
        "",
        "> This pattern is the cloud version of _____. It reduces _____. It introduces _____. I would prove it with _____.",
        "",
        "---",
        "",
    ]

    for index, pattern in enumerate(patterns, start=1):
        pattern_name = get_value(pattern, "pattern")
        executive_sentence = EXECUTIVE_SENTENCES.get(
            pattern_name,
            "This pattern should be evaluated by the access path it creates, the risk it reduces, the risk it introduces, and the evidence it produces.",
        )

        lines.extend(
            [
                f"## Card {index}: {pattern_name}",
                "",
                "### On-Prem Analogy",
                "",
                get_value(pattern, "on_prem_analogy"),
                "",
                "### Cloud Implementation",
                "",
                get_value(pattern, "cloud_implementation"),
                "",
                "### Risk Reduced",
                "",
                get_value(pattern, "primary_risk_reduced"),
                "",
                "### Risk Introduced",
                "",
                get_value(pattern, "risk_introduced"),
                "",
                "### Evidence to Collect",
                "",
                get_value(pattern, "evidence_to_collect"),
                "",
                "### Multi-Cloud Translation",
                "",
                "| Provider | Equivalent Pattern / Service Area |",
                "|---|---|",
                f"| AWS | {get_value(pattern, 'aws_reference')} |",
                f"| Azure | {get_value(pattern, 'azure_equivalent')} |",
                f"| GCP | {get_value(pattern, 'gcp_equivalent')} |",
                f"| OCI | {get_value(pattern, 'oci_equivalent')} |",
                "",
                "### Executive Sentence",
                "",
                executive_sentence,
                "",
                "### Memory Drill",
                "",
                f"> {pattern_name}: What does it replace, what risk does it reduce, what risk does it introduce, and what evidence proves it?",
                "",
                "---",
                "",
            ]
        )

    lines.extend(
        [
            "## Final Carry-Forward",
            "",
            "Do not memorize cloud services as isolated vocabulary.",
            "",
            "Memorize the access pattern, the risk tradeoff, and the evidence trail.",
            "",
        ]
    )

    return "\n".join(lines)


def write_evidence_report(pattern_count: int) -> None:
    """Write a small evidence report proving the field cards were generated."""
    EVIDENCE_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Cloud Pattern Field Card Generation Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        "Overall Status: **PASS**",
        "",
        "## Purpose",
        "",
        "This report records generation of portable cloud administrative access pattern field cards.",
        "",
        "## Source Artifact",
        "",
        f"- `{SOURCE_MATRIX.as_posix()}`",
        "",
        "## Generated Artifact",
        "",
        f"- `{FIELD_CARD_FILE.as_posix()}`",
        "",
        "## Summary",
        "",
        f"- Pattern cards generated: `{pattern_count}`",
        "",
        "## Portfolio Relevance",
        "",
        "This artifact supports cloud architecture fluency by converting an evidence matrix into a portable study object.",
        "",
        "It reinforces the ability to translate on-prem systems engineering intuition into cloud implementation, risk, evidence, and multi-cloud equivalency.",
        "",
    ]

    EVIDENCE_REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Generate cloud pattern field cards from the Day 53 pattern matrix."""
    patterns = read_patterns()

    if not patterns:
        raise ValueError(f"No patterns found in source matrix: {SOURCE_MATRIX}")

    FIELD_CARD_FILE.parent.mkdir(parents=True, exist_ok=True)

    field_card_markdown = build_field_cards(patterns)
    FIELD_CARD_FILE.write_text(field_card_markdown, encoding="utf-8")

    write_evidence_report(pattern_count=len(patterns))

    print(f"Cloud pattern field cards written to: {FIELD_CARD_FILE}")
    print(f"Evidence report written to: {EVIDENCE_REPORT_FILE}")
    print(f"Pattern cards generated: {len(patterns)}")
    print("Overall Status: PASS")


if __name__ == "__main__":
    main()