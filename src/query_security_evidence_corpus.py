from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse
import csv
import json
import re
import sys


CORPUS_JSONL = Path("ai/security_evidence_corpus.jsonl")
QUERY_RESULTS_CSV = Path("ai/security_evidence_query_results.csv")
REPORT_FILE = Path("evidence/generated/security_evidence_query_report.md")


DEFAULT_QUERIES = [
    "public administrative port exposure security group",
    "evidence collector permissions ec2 describe security groups",
    "cloud administrative access decision standard exception",
    "authorized minimized segmented monitored attributable reviewable",
]


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}


def tokenize(text: str) -> list[str]:
    """Tokenize text for simple local retrieval."""
    tokens = re.findall(r"[a-zA-Z0-9_:-]+", text.lower())
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def load_corpus() -> list[dict[str, str]]:
    """Load evidence corpus records from JSONL."""
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
                        "summary": f"Line {line_number} could not be parsed as JSON.",
                        "content": "",
                    }
                )

    return records


def searchable_text(record: dict[str, str]) -> str:
    """Build searchable text from a corpus record."""
    parts = [
        record.get("document_id", ""),
        record.get("source_path", ""),
        record.get("title", ""),
        record.get("artifact_family", ""),
        record.get("summary", ""),
        record.get("content", ""),
    ]

    return "\n".join(parts)


def score_record(query: str, record: dict[str, str]) -> tuple[int, list[str]]:
    """Score one record against one query."""
    query_terms = tokenize(query)
    text = searchable_text(record)
    text_lower = text.lower()
    token_counts = Counter(tokenize(text))

    matched_terms = sorted({term for term in query_terms if token_counts.get(term, 0) > 0})

    score = 0

    for term in query_terms:
        score += token_counts.get(term, 0)

    title_lower = record.get("title", "").lower()
    family_lower = record.get("artifact_family", "").lower()
    source_lower = record.get("source_path", "").lower()

    for term in query_terms:
        if term in title_lower:
            score += 5
        if term in family_lower:
            score += 3
        if term in source_lower:
            score += 2

    if query.lower() in text_lower:
        score += 15

    return score, matched_terms


def run_queries(records: list[dict[str, str]], queries: list[str], max_results: int) -> list[dict[str, str]]:
    """Run retrieval queries against the local corpus."""
    all_results = []

    for query_index, query in enumerate(queries, start=1):
        scored = []

        for record in records:
            score, matched_terms = score_record(query, record)

            if score > 0:
                scored.append(
                    {
                        "query_id": f"QUERY-{query_index:03d}",
                        "query": query,
                        "document_id": record.get("document_id", ""),
                        "title": record.get("title", ""),
                        "artifact_family": record.get("artifact_family", ""),
                        "source_path": record.get("source_path", ""),
                        "score": score,
                        "matched_terms": ", ".join(matched_terms),
                        "summary": record.get("summary", ""),
                    }
                )

        scored.sort(key=lambda row: row["score"], reverse=True)

        for rank, row in enumerate(scored[:max_results], start=1):
            row["rank"] = rank
            all_results.append(row)

    return all_results


def write_results_csv(results: list[dict[str, str]]) -> None:
    """Write query results to CSV."""
    QUERY_RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "query_id",
        "query",
        "rank",
        "document_id",
        "title",
        "artifact_family",
        "source_path",
        "score",
        "matched_terms",
        "summary",
    ]

    with QUERY_RESULTS_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow(result)


def group_results_by_query(results: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Group retrieval results by query text."""
    grouped = {}

    for result in results:
        query = result["query"]
        grouped.setdefault(query, []).append(result)

    return grouped


def write_report(records: list[dict[str, str]], queries: list[str], results: list[dict[str, str]]) -> None:
    """Write markdown report for retrieval results."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    status = "PASS" if records and results else "REVIEW"
    grouped = group_results_by_query(results)

    lines = [
        "# Security Evidence Retrieval Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{status}**",
        "",
        "## Purpose",
        "",
        "This report records bounded retrieval against the local security evidence corpus.",
        "",
        "The retrieval layer searches only indexed project evidence and returns source-backed results.",
        "",
        "## Retrieval Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Corpus records available | `{len(records)}` |",
        f"| Queries executed | `{len(queries)}` |",
        f"| Results returned | `{len(results)}` |",
        "",
        "## Query Results",
        "",
    ]

    if not records:
        lines.extend(
            [
                "No corpus records were available.",
                "",
                "Run:",
                "",
                "```powershell",
                "python src\\build_security_evidence_corpus.py",
                "```",
                "",
            ]
        )
    elif not results:
        lines.append("No matching evidence records were returned.")
        lines.append("")

    for query in queries:
        lines.extend(
            [
                f"### Query: `{query}`",
                "",
                "| Rank | Document ID | Score | Artifact Family | Source | Title |",
                "|---:|---|---:|---|---|---|",
            ]
        )

        query_results = grouped.get(query, [])

        if query_results:
            for result in query_results:
                lines.append(
                    f"| {result['rank']} | {result['document_id']} | {result['score']} | "
                    f"{result['artifact_family']} | `{result['source_path']}` | {result['title']} |"
                )
        else:
            lines.append("| N/A | N/A | 0 | N/A | N/A | No matching records found. |")

        lines.append("")

    lines.extend(
        [
            "## Control Logic",
            "",
            "| Control Concept | How This Retrieval Layer Supports It |",
            "|---|---|",
            "| Bounded retrieval | Searches only the approved local evidence corpus. |",
            "| Source traceability | Every result includes document ID and source path. |",
            "| Human review | Results are ranked and summarized for inspection, not auto-approved. |",
            "| AI readiness | Future AI answers can be constrained to retrieved source records. |",
            "",
            "## Governance Note",
            "",
            "This is a retrieval layer, not an autonomous answer engine.",
            "",
            "A future security assistant should cite retrieved document IDs and avoid answering from outside the controlled corpus.",
            "",
            "## One-Sentence Takeaway",
            "",
            "> Retrieval is the bridge between controlled evidence and bounded security AI.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query the local security evidence corpus."
    )

    parser.add_argument(
        "query",
        nargs="*",
        help="Optional custom query. If omitted, default evidence queries are used.",
    )

    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum results per query.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    records = load_corpus()

    if args.query:
        queries = [" ".join(args.query)]
    else:
        queries = DEFAULT_QUERIES

    results = run_queries(
        records=records,
        queries=queries,
        max_results=args.max_results,
    )

    write_results_csv(results)
    write_report(records, queries, results)

    print(f"Query results written to: {QUERY_RESULTS_CSV}")
    print(f"Retrieval report written to: {REPORT_FILE}")
    print(f"Corpus records available: {len(records)}")
    print(f"Queries executed: {len(queries)}")
    print(f"Results returned: {len(results)}")
    print("Overall Status: PASS" if records and results else "Overall Status: REVIEW")

    return 0


if __name__ == "__main__":
    sys.exit(main())