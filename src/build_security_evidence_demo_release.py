from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import csv
import sys


ARTIFACTS = {
    "Portfolio case study": Path(
        "docs/cloud/security_evidence_portfolio_case_study.md"
    ),
    "Demo runbook": Path(
        "docs/cloud/security_evidence_demo_runbook.md"
    ),
    "Demo readiness": Path(
        "docs/cloud/security_evidence_demo_readiness.md"
    ),
    "Control narrative": Path(
        "docs/cloud/security_evidence_control_narrative.md"
    ),
    "Evidence corpus manifest": Path(
        "ai/security_evidence_corpus_manifest.csv"
    ),
    "Status dashboard": Path(
        "docs/cloud/security_evidence_status_dashboard.md"
    ),
    "Gap register": Path(
        "ai/security_evidence_gap_register.csv"
    ),
    "Traceability exceptions": Path(
        "ai/security_evidence_traceability_exceptions.csv"
    ),
    "Management decisions": Path(
        "ai/security_evidence_exception_management_decisions.csv"
    ),
    "Decision follow-up tracker": Path(
        "ai/security_evidence_decision_followup_tracker.csv"
    ),
    "Management closeout summary": Path(
        "docs/cloud/security_evidence_management_closeout_summary.md"
    ),
    "Executive summary": Path(
        "docs/cloud/security_evidence_executive_summary.md"
    ),
}

LATEST_MANIFEST = Path(
    "ai/security_evidence_demo_release_manifest.csv"
)
RELEASE_DIRECTORY = Path(
    "evidence/releases/security_evidence_demo"
)
SUMMARY_FILE = Path(
    "docs/cloud/security_evidence_demo_release.md"
)


def hash_file(path: Path) -> str:
    digest = sha256()

    with path.open("rb") as file:
        for block in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def inspect_artifacts() -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []

    for name, path in ARTIFACTS.items():
        if not path.exists():
            status = "Missing"
            size = 0
            digest = ""
        else:
            size = path.stat().st_size
            status = "Present" if size > 0 else "Empty"
            digest = hash_file(path)

        rows.append(
            {
                "artifact_name": name,
                "artifact_path": path.as_posix(),
                "artifact_status": status,
                "size_bytes": size,
                "sha256": digest,
            }
        )

    return rows


def calculate_release_digest(
    rows: list[dict[str, str | int]],
) -> str:
    canonical_lines = [
        "|".join(
            [
                str(row["artifact_path"]),
                str(row["artifact_status"]),
                str(row["size_bytes"]),
                str(row["sha256"]),
            ]
        )
        for row in sorted(
            rows,
            key=lambda item: str(item["artifact_path"]),
        )
    ]

    canonical_content = "\n".join(
        canonical_lines
    ).encode("utf-8")

    return sha256(canonical_content).hexdigest()


def determine_release_status(
    rows: list[dict[str, str | int]],
) -> str:
    statuses = {
        str(row["artifact_status"])
        for row in rows
    }

    if "Missing" in statuses:
        return "RELEASE_BLOCKED_MISSING_ARTIFACTS"

    if "Empty" in statuses:
        return "RELEASE_BLOCKED_EMPTY_ARTIFACTS"

    return "RELEASE_CREATED"


def write_manifest(
    path: Path,
    rows: list[dict[str, str | int]],
    release_id: str,
    generated_at: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "release_id",
        "generated_at",
        "artifact_name",
        "artifact_path",
        "artifact_status",
        "size_bytes",
        "sha256",
    ]

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "release_id": release_id,
                    "generated_at": generated_at,
                    **row,
                }
            )


def write_summary(
    rows: list[dict[str, str | int]],
    release_id: str,
    release_digest: str,
    release_status: str,
    generated_at: str,
    versioned_manifest: Path | None,
) -> None:
    SUMMARY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lines = [
        "# Security Evidence Demo Release",
        "",
        f"Generated: `{generated_at}`",
        "",
        f"Release Status: **{release_status}**",
        "",
        f"Release ID: `{release_id}`",
        "",
        f"Release Digest: `{release_digest}`",
        "",
        "## Artifact Integrity",
        "",
        "| Artifact | Status | Size | SHA-256 |",
        "|---|---|---:|---|",
    ]

    for row in rows:
        artifact_hash = str(row["sha256"])

        short_hash = (
            artifact_hash[:16] + "..."
            if artifact_hash
            else ""
        )

        lines.append(
            f"| {row['artifact_name']} "
            f"| {row['artifact_status']} "
            f"| {row['size_bytes']} "
            f"| `{short_hash}` |"
        )

    lines.extend(
        [
            "",
            "## Release Files",
            "",
            (
                "- Latest manifest: "
                f"`{LATEST_MANIFEST.as_posix()}`"
            ),
            (
                "- Summary: "
                f"`{SUMMARY_FILE.as_posix()}`"
            ),
        ]
    )

    if versioned_manifest is not None:
        lines.append(
            "- Versioned manifest: "
            f"`{versioned_manifest.as_posix()}`"
        )

    lines.extend(
        [
            "",
            "## Governance Rule",
            "",
            "> The manifest identifies the exact artifact "
            "versions included in this release. It does not "
            "prove that their findings or conclusions are "
            "correct.",
            "",
        ]
    )

    SUMMARY_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> int:
    rows = inspect_artifacts()

    release_digest = calculate_release_digest(
        rows
    )

    release_id = (
        f"SED-{release_digest[:12].upper()}"
    )

    release_status = determine_release_status(
        rows
    )

    generated_at = datetime.now(
        timezone.utc
    ).isoformat()

    write_manifest(
        LATEST_MANIFEST,
        rows,
        release_id,
        generated_at,
    )

    versioned_manifest: Path | None = None

    if release_status == "RELEASE_CREATED":
        versioned_manifest = (
            RELEASE_DIRECTORY
            / f"{release_id.lower()}_manifest.csv"
        )

        if not versioned_manifest.exists():
            write_manifest(
                versioned_manifest,
                rows,
                release_id,
                generated_at,
            )

    write_summary(
        rows,
        release_id,
        release_digest,
        release_status,
        generated_at,
        versioned_manifest,
    )

    print(f"Release status: {release_status}")
    print(f"Release ID: {release_id}")
    print(f"Release digest: {release_digest}")
    print(f"Latest manifest: {LATEST_MANIFEST}")
    print(f"Summary: {SUMMARY_FILE}")

    if versioned_manifest is not None:
        print(
            "Versioned manifest: "
            f"{versioned_manifest}"
        )

    if release_status == "RELEASE_CREATED":
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())