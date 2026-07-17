from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import sys


CORPUS_JSONL = Path("ai/security_evidence_corpus.jsonl")
CORPUS_MANIFEST = Path("ai/security_evidence_corpus_manifest.csv")
REPORT_FILE = Path("evidence/generated/security_evidence_corpus_report.md")


SOURCE_PATHS = [
    Path("docs/cloud"),
    Path("security"),
    Path("evidence/generated"),
    Path("evidence/evidence_index.md"),
]


INCLUDED_SUFFIXES = {".md", ".csv", ".json", ".jsonl", ".txt"}


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hash of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify_artifact(path: Path) -> str:
    """Classify artifacts into broad security evidence families."""
    path_text = path.as_posix().lower()

    if "adr" in path_text:
        return "architecture_decision"

    if "permission" in path_text or "iam" in path_text:
        return "authorization_evidence"

    if "admin_port" in path_text or "access" in path_text:
        return "cloud_admin_access"

    if "exception" in path_text:
        return "exception_management"

    if "evidence_requirement" in path_text or "evidence_requirements" in path_text:
        return "evidence_requirements"

    if "workflow" in path_text:
        return "workflow_evidence"

    if "report" in path_text:
        return "evidence_report"

    if "manifest" in path_text or "index" in path_text:
        return "evidence_index"

    if path.suffix.lower() == ".csv":
        return "structured_data"

    return "general_security_artifact"


def infer_title(path: Path, text: str) -> str:
    """Infer a human-friendly title from the file content or path."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.replace("# ", "", 1).strip()

    return path.stem.replace("_", " ").replace("-", " ").title()


def summarize_text(text: str, max_chars: int = 500) -> str:
    """Create a simple extractive summary from the start of the file."""
    clean_lines = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("```"):
            continue
        clean_lines.append(stripped)

    summary = " ".join(clean_lines)

    if len(summary) > max_chars:
        return summary[:max_chars].rstrip() + "..."

    return summary


def collect_files() -> list[Path]:
    """Collect source files for the evidence corpus."""
    files = []

    for source in SOURCE_PATHS:
        if not source.exists():
            continue

        if source.is_file() and source.suffix.lower() in INCLUDED_SUFFIXES:
            files.append(source)
            continue

        if source.is_dir():
            for path in source.rglob("*"):
                if path.is_file() and path.suffix.lower() in INCLUDED_SUFFIXES:
                    if path.as_posix() in {
                        CORPUS_JSONL.as_posix(),
                        CORPUS_MANIFEST.as_posix(),
                    }:
                        continue
                    files.append(path)

    return sorted(set(files), key=lambda p: p.as_posix())


def build_corpus_records(files: list[Path]) -> list[dict[str, str]]:
    """Build corpus records from source files."""
    records = []
    generated_at = datetime.now(timezone.utc).isoformat()

    for index, path in enumerate(files, start=1):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")

        file_hash = sha256_file(path)
        artifact_family = classify_artifact(path)
        title = infer_title(path, text)
        summary = summarize_text(text)

        record = {
            "document_id": f"SEC-EVID-{index:04d}",
            "source_path": path.as_posix(),
            "title": title,
            "artifact_family": artifact_family,
            "file_type": path.suffix.lower().replace(".", ""),
            "sha256": file_hash,
            "size_bytes": str(path.stat().st_size),
            "generated_at": generated_at,
            "summary": summary,
            "content": text,
        }

        records.append(record)

    return records


def write_jsonl(records: list[dict[str, str]]) -> None:
    """Write JSONL corpus."""
    CORPUS_JSONL.parent.mkdir(parents=True, exist_ok=True)

    with CORPUS_JSONL.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_manifest(records: list[dict[str, str]]) -> None:
    """Write CSV manifest without full content."""
    CORPUS_MANIFEST.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "document_id",
        "source_path",
        "title",
        "artifact_family",
        "file_type",
        "sha256",
        "size_bytes",
        "generated_at",
        "summary",
    ]

    with CORPUS_MANIFEST.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for record in records:
            writer.writerow({field: record[field] for field in fieldnames})


def family_counts(records: list[dict[str, str]]) -> dict[str, int]:
    """Count records by artifact family."""
    counts = {}

    for record in records:
        family = record["artifact_family"]
        counts[family] = counts.get(family, 0) + 1

    return dict(sorted(counts.items()))


def write_report(records: list[dict[str, str]]) -> None:
    """Write markdown evidence report."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    counts = family_counts(records)
    total_bytes = sum(int(record["size_bytes"]) for record in records)

    lines = [
        "# Security Evidence Corpus Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        "Overall Status: **PASS**" if records else "Overall Status: **REVIEW**",
        "",
        "## Purpose",
        "",
        "This report records creation of a structured security evidence corpus for future AI-assisted evidence review.",
        "",
        "The corpus organizes existing project artifacts into document records with source paths, titles, artifact families, hashes, summaries, and full text content.",
        "",
        "## Generated Artifacts",
        "",
        f"- `{CORPUS_JSONL.as_posix()}`",
        f"- `{CORPUS_MANIFEST.as_posix()}`",
        "",
        "## Corpus Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Documents indexed | `{len(records)}` |",
        f"| Total source bytes | `{total_bytes}` |",
        "",
        "## Artifact Family Counts",
        "",
        "| Artifact Family | Count |",
        "|---|---:|",
    ]

    for family, count in counts.items():
        lines.append(f"| {family} | {count} |")

    lines.extend(
        [
            "",
            "## Document Manifest Preview",
            "",
            "| Document ID | Artifact Family | Source Path | Title |",
            "|---|---|---|---|",
        ]
    )

    for record in records[:20]:
        lines.append(
            f"| {record['document_id']} | {record['artifact_family']} | "
            f"`{record['source_path']}` | {record['title']} |"
        )

    if len(records) > 20:
        lines.append(f"| ... | ... | ... | `{len(records) - 20}` additional records omitted from preview |")

    lines.extend(
        [
            "",
            "## Security AI Relevance",
            "",
            "This artifact prepares the project for a security evidence assistant by creating a bounded, auditable source corpus.",
            "",
            "A future assistant should answer only from indexed evidence, cite source document IDs, and preserve traceability back to source files.",
            "",
            "## Governance Note",
            "",
            "The corpus includes hashes so downstream AI or automation workflows can detect whether source artifacts changed after indexing.",
            "",
            "## One-Sentence Takeaway",
            "",
            "> An evidence-aware AI system starts with a controlled corpus, not a pile of unstructured files.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    files = collect_files()
    records = build_corpus_records(files)

    write_jsonl(records)
    write_manifest(records)
    write_report(records)

    print(f"Corpus JSONL written to: {CORPUS_JSONL}")
    print(f"Corpus manifest written to: {CORPUS_MANIFEST}")
    print(f"Evidence report written to: {REPORT_FILE}")
    print(f"Documents indexed: {len(records)}")
    print("Overall Status: PASS" if records else "Overall Status: REVIEW")

    return 0


if __name__ == "__main__":
    sys.exit(main())