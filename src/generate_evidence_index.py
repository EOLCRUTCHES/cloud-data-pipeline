from pathlib import Path
from datetime import datetime, timezone


EVIDENCE_DIR = Path("evidence/generated")
INDEX_FILE = Path("evidence/evidence_index.md")


def get_markdown_files() -> list[Path]:
    """Return generated markdown evidence files."""
    if not EVIDENCE_DIR.exists():
        return []

    return sorted(EVIDENCE_DIR.glob("*.md"))


def build_index(markdown_files: list[Path]) -> str:
    """Build a markdown evidence index."""
    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Evidence Index",
        "",
        f"Generated: `{timestamp}`",
        "",
        "## Purpose",
        "",
        "This index lists generated evidence artifacts created by the cloud-data-pipeline project.",
        "",
        "The purpose is to make validation, audit, and control-support evidence easy to locate.",
        "",
        "## Generated Evidence",
        "",
    ]

    if not markdown_files:
        lines.append("No generated evidence files found.")
    else:
        lines.append("| Evidence File | Location |")
        lines.append("|---|---|")

        for file in markdown_files:
            display_name = file.stem.replace("_", " ").title()
            lines.append(f"| {display_name} | `{file}` |")

    lines.extend(
        [
            "",
            "## Portfolio Relevance",
            "",
            "This evidence index demonstrates that generated validation outputs are tracked and organized instead of being treated as disposable console output.",
            "",
            "This pattern will later support security control evidence, audit packages, AI evidence retrieval, and provenance tracking.",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    """Generate the evidence index."""
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)

    markdown_files = get_markdown_files()
    index_content = build_index(markdown_files)

    INDEX_FILE.write_text(index_content, encoding="utf-8")

    print(f"Evidence index written to: {INDEX_FILE}")


if __name__ == "__main__":
    main()