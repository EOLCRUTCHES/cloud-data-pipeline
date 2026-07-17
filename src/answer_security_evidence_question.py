from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse
import csv
import json
import re
import sys


CORPUS_JSONL = Path("ai/security_evidence_corpus.jsonl")
ANSWER_FILE = Path("ai/security_evidence_answer.md")
ANSWER_SOURCES_CSV = Path("ai/security_evidence_answer_sources.csv")
REPORT_FILE = Path("evidence/generated/security_evidence_answer_report.md")


DEFAULT_QUESTION = "What evidence supports the AWS cloud administrative access standard?"

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "do",
    "does",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "should",
    "that",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


def tokenize(text: str) -> list[str]:
    """Tokenize text for local evidence scoring."""
    tokens = re.findall(r"[a-zA-Z0-9_:-]+", text.lower())
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def load_corpus() -> list[dict[str, str]]:
    """Load local security evidence corpus."""
    if not CORPUS_JSONL.exists() or CORPUS_JSONL.stat().st_size == 0:
        return []

    records = []

    with CORPUS_JSONL.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()

            if not stripped:
                continue

            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError:
                records.append(
                    {
                        "document_id": f"CORPUS-PARSE-ERROR-{line_number}",
                        "source_path": CORPUS_JSONL.as_posix(),
                        "title": "Corpus Parse Error",
                        "artifact_family": "corpus_error",
                        "sha256": "",
                        "summary": f"Line {line_number} could not be parsed as JSON.",
                        "content": "",
                    }
                )

    return records


def searchable_text(record: dict[str, str]) -> str:
    """Build searchable text for one record."""
    parts = [
        record.get("document_id", ""),
        record.get("source_path", ""),
        record.get("title", ""),
        record.get("artifact_family", ""),
        record.get("summary", ""),
        record.get("content", ""),
    ]

    return "\n".join(parts)


def score_record(question: str, record: dict[str, str]) -> tuple[int, list[str]]:
    """Score a corpus record against the user's question."""
    question_terms = tokenize(question)
    text = searchable_text(record)
    token_counts = Counter(tokenize(text))

    matched_terms = sorted({term for term in question_terms if token_counts.get(term, 0) > 0})

    score = 0

    for term in question_terms:
        score += token_counts.get(term, 0)

    title_lower = record.get("title", "").lower()
    family_lower = record.get("artifact_family", "").lower()
    source_lower = record.get("source_path", "").lower()

    for term in question_terms:
        if term in title_lower:
            score += 8
        if term in family_lower:
            score += 4
        if term in source_lower:
            score += 3

    if question.lower() in text.lower():
        score += 20

    return score, matched_terms


def split_into_evidence_units(text: str) -> list[str]:
    """Split content into compact evidence units."""
    units = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("```"):
            continue

        if line.startswith("|---"):
            continue

        if len(line) < 8:
            continue

        units.append(line)

    return units


def extract_snippets(question: str, record: dict[str, str], max_snippets: int = 3) -> list[str]:
    """Extract source snippets that match the question terms."""
    question_terms = set(tokenize(question))
    units = split_into_evidence_units(record.get("content", ""))

    scored_units = []

    for unit in units:
        unit_terms = set(tokenize(unit))
        overlap = question_terms.intersection(unit_terms)

        if overlap:
            scored_units.append((len(overlap), unit))

    scored_units.sort(key=lambda item: item[0], reverse=True)

    snippets = []

    for _score, unit in scored_units[:max_snippets]:
        cleaned = unit.replace("|", " ").strip()
        if len(cleaned) > 260:
            cleaned = cleaned[:260].rstrip() + "..."
        snippets.append(cleaned)

    if not snippets and record.get("summary"):
        summary = record["summary"]
        if len(summary) > 260:
            summary = summary[:260].rstrip() + "..."
        snippets.append(summary)

    return snippets


def retrieve_sources(
    question: str,
    records: list[dict[str, str]],
    max_sources: int,
    minimum_score: int,
) -> list[dict[str, str]]:
    """Retrieve source records and extract snippets."""
    scored = []

    for record in records:
        score, matched_terms = score_record(question, record)

        if score >= minimum_score:
            snippets = extract_snippets(question, record)

            scored.append(
                {
                    "document_id": record.get("document_id", ""),
                    "title": record.get("title", ""),
                    "artifact_family": record.get("artifact_family", ""),
                    "source_path": record.get("source_path", ""),
                    "sha256": record.get("sha256", ""),
                    "score": score,
                    "matched_terms": ", ".join(matched_terms),
                    "snippets": snippets,
                    "summary": record.get("summary", ""),
                }
            )

    scored.sort(key=lambda row: row["score"], reverse=True)

    return scored[:max_sources]


def determine_answer_status(records: list[dict[str, str]], sources: list[dict[str, str]]) -> str:
    """Determine whether the answer is source-backed."""
    if not records:
        return "NO_CORPUS"

    if not sources:
        return "INSUFFICIENT_EVIDENCE"

    return "SOURCE_BACKED_REVIEW_REQUIRED"


def build_short_answer(question: str, status: str, sources: list[dict[str, str]]) -> str:
    """Build a constrained source-backed answer."""
    if status == "NO_CORPUS":
        return (
            "I cannot answer from the approved evidence corpus because the corpus is missing or empty. "
            "Run the corpus builder first."
        )

    if status == "INSUFFICIENT_EVIDENCE":
        return (
            "I cannot provide a confident answer from the approved evidence corpus because no source records "
            "matched the question strongly enough."
        )

    source_ids = ", ".join(source["document_id"] for source in sources[:3])

    return (
        f"The approved evidence corpus contains relevant support for this question. "
        f"The strongest source records are {source_ids}. Review the cited snippets below before treating the answer as final."
    )


def write_answer_file(question: str, status: str, sources: list[dict[str, str]]) -> None:
    """Write the human-facing constrained answer."""
    ANSWER_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    short_answer = build_short_answer(question, status, sources)

    lines = [
        "# Security Evidence Answer",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Question: **{question}**",
        "",
        f"Answer Status: **{status}**",
        "",
        "## Short Answer",
        "",
        short_answer,
        "",
    ]

    if sources:
        lines.extend(
            [
                "## Source-Backed Evidence",
                "",
            ]
        )

        for index, source in enumerate(sources, start=1):
            hash_prefix = source["sha256"][:12] if source.get("sha256") else "not_available"

            lines.extend(
                [
                    f"### Source {index}: {source['document_id']}",
                    "",
                    f"- Title: {source['title']}",
                    f"- Artifact family: `{source['artifact_family']}`",
                    f"- Source path: `{source['source_path']}`",
                    f"- SHA-256 prefix: `{hash_prefix}`",
                    f"- Retrieval score: `{source['score']}`",
                    f"- Matched terms: `{source['matched_terms'] or 'none'}`",
                    "",
                    "Relevant snippets:",
                    "",
                ]
            )

            for snippet in source["snippets"]:
                lines.append(f"- {snippet}")

            lines.append("")

    lines.extend(
        [
            "## Guardrail",
            "",
            "This answer is constrained to the local approved evidence corpus.",
            "",
            "If the needed evidence is not present in the corpus, the correct behavior is to say that the corpus does not support a confident answer.",
            "",
            "## Human Review",
            "",
            "A human reviewer should confirm whether the retrieved sources actually answer the question before using this output for a decision.",
            "",
        ]
    )

    ANSWER_FILE.write_text("\n".join(lines), encoding="utf-8")


def write_sources_csv(question: str, status: str, sources: list[dict[str, str]]) -> None:
    """Write answer sources to CSV."""
    ANSWER_SOURCES_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "question",
        "answer_status",
        "rank",
        "document_id",
        "title",
        "artifact_family",
        "source_path",
        "sha256",
        "score",
        "matched_terms",
        "snippets",
    ]

    with ANSWER_SOURCES_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for rank, source in enumerate(sources, start=1):
            writer.writerow(
                {
                    "question": question,
                    "answer_status": status,
                    "rank": rank,
                    "document_id": source["document_id"],
                    "title": source["title"],
                    "artifact_family": source["artifact_family"],
                    "source_path": source["source_path"],
                    "sha256": source["sha256"],
                    "score": source["score"],
                    "matched_terms": source["matched_terms"],
                    "snippets": " || ".join(source["snippets"]),
                }
            )


def write_report(
    question: str,
    records: list[dict[str, str]],
    status: str,
    sources: list[dict[str, str]],
) -> None:
    """Write execution report."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Security Evidence Answer Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{status}**",
        "",
        "## Purpose",
        "",
        "This report records a constrained answer attempt against the local security evidence corpus.",
        "",
        "The answer layer may only use retrieved source records from the approved corpus.",
        "",
        "## Question",
        "",
        question,
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Corpus records available | `{len(records)}` |",
        f"| Source records used | `{len(sources)}` |",
        "",
        "## Source Records",
        "",
        "| Rank | Document ID | Score | Source Path | Title |",
        "|---:|---|---:|---|---|",
    ]

    if sources:
        for rank, source in enumerate(sources, start=1):
            lines.append(
                f"| {rank} | {source['document_id']} | {source['score']} | "
                f"`{source['source_path']}` | {source['title']} |"
            )
    else:
        lines.append("| N/A | N/A | 0 | N/A | No source records used. |")

    lines.extend(
        [
            "",
            "## Control Logic",
            "",
            "| Control Concept | Implementation |",
            "|---|---|",
            "| Bounded generation | The answer file is built only from local corpus retrieval results. |",
            "| Source traceability | Each answer source includes document ID, path, and hash. |",
            "| No-source rule | If no corpus evidence is found, the output refuses a confident answer. |",
            "| Human review | The output is marked review-required before operational use. |",
            "",
            "## Generated Artifacts",
            "",
            f"- `{ANSWER_FILE.as_posix()}`",
            f"- `{ANSWER_SOURCES_CSV.as_posix()}`",
            "",
            "## One-Sentence Takeaway",
            "",
            "> A security assistant should not answer first and justify later; it should retrieve evidence first and answer only inside that boundary.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a constrained source-backed answer from the local security evidence corpus."
    )

    parser.add_argument(
        "question",
        nargs="*",
        help="Question to answer from the approved evidence corpus.",
    )

    parser.add_argument(
        "--max-sources",
        type=int,
        default=5,
        help="Maximum source records to use.",
    )

    parser.add_argument(
        "--minimum-score",
        type=int,
        default=3,
        help="Minimum retrieval score needed for a source to be used.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    question = " ".join(args.question).strip() if args.question else DEFAULT_QUESTION
    records = load_corpus()
    sources = retrieve_sources(
        question=question,
        records=records,
        max_sources=args.max_sources,
        minimum_score=args.minimum_score,
    )

    status = determine_answer_status(records, sources)

    write_answer_file(question, status, sources)
    write_sources_csv(question, status, sources)
    write_report(question, records, status, sources)

    print(f"Answer written to: {ANSWER_FILE}")
    print(f"Answer sources written to: {ANSWER_SOURCES_CSV}")
    print(f"Evidence report written to: {REPORT_FILE}")
    print(f"Corpus records available: {len(records)}")
    print(f"Source records used: {len(sources)}")
    print(f"Overall Status: {status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())