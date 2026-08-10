from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import csv
import sys


MANIFEST_FILE = Path(
    "ai/security_evidence_demo_release_manifest.csv"
)
VALIDATION_CSV = Path(
    "ai/security_evidence_demo_release_validation.csv"
)
VALIDATION_MD = Path(
    "docs/cloud/security_evidence_demo_release_validation.md"
)
REPORT_FILE = Path(
    "evidence/generated/"
    "security_evidence_demo_release_validation_report.md"
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


def load_manifest() -> tuple[str, list[dict[str, str]]]:
    if not MANIFEST_FILE.exists():
        raise FileNotFoundError(
            f"Release manifest not found: {MANIFEST_FILE}"
        )

    with MANIFEST_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError(
            "Release manifest contains no artifact rows."
        )

    required_fields = {
        "release_id",
        "artifact_name",
        "artifact_path",
        "artifact_status",
        "size_bytes",
        "sha256",
    }

    missing_fields = required_fields.difference(
        rows[0]
    )

    if missing_fields:
        formatted = ", ".join(
            sorted(missing_fields)
        )

        raise ValueError(
            f"Release manifest is missing fields: {formatted}"
        )

    release_ids = {
        row["release_id"].strip()
        for row in rows
    }

    if len(release_ids) != 1:
        raise ValueError(
            "Release manifest contains multiple release IDs."
        )

    return release_ids.pop(), rows


def validate_artifact(
    manifest_row: dict[str, str],
    validated_at: str,
) -> dict[str, str | int]:
    path = Path(
        manifest_row["artifact_path"]
    )

    expected_size = int(
        manifest_row["size_bytes"]
    )

    expected_hash = (
        manifest_row["sha256"]
        .strip()
        .lower()
    )

    if not path.exists():
        current_status = "Missing"
        current_size = 0
        current_hash = ""
        validation_result = "MISSING"

    else:
        current_size = path.stat().st_size

        current_status = (
            "Present"
            if current_size > 0
            else "Empty"
        )

        current_hash = hash_file(path)

        if current_status == "Empty":
            validation_result = "EMPTY"

        elif (
            current_size == expected_size
            and current_hash == expected_hash
        ):
            validation_result = "MATCH"

        else:
            validation_result = "MODIFIED"

    return {
        "validated_at": validated_at,
        "release_id": manifest_row["release_id"],
        "artifact_name": manifest_row["artifact_name"],
        "artifact_path": manifest_row["artifact_path"],
        "expected_status": manifest_row[
            "artifact_status"
        ],
        "current_status": current_status,
        "expected_size_bytes": expected_size,
        "current_size_bytes": current_size,
        "expected_sha256": expected_hash,
        "current_sha256": current_hash,
        "validation_result": validation_result,
    }


def determine_overall_status(
    rows: list[dict[str, str | int]],
) -> str:
    results = {
        str(row["validation_result"])
        for row in rows
    }

    if results == {"MATCH"}:
        return "RELEASE_INTEGRITY_VERIFIED"

    return "RELEASE_INTEGRITY_FAILED"


def write_validation_csv(
    rows: list[dict[str, str | int]],
) -> None:
    VALIDATION_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "validated_at",
        "release_id",
        "artifact_name",
        "artifact_path",
        "expected_status",
        "current_status",
        "expected_size_bytes",
        "current_size_bytes",
        "expected_sha256",
        "current_sha256",
        "validation_result",
    ]

    with VALIDATION_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)


def write_validation_markdown(
    release_id: str,
    rows: list[dict[str, str | int]],
    overall_status: str,
) -> None:
    VALIDATION_MD.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    counts = {
        result: sum(
            row["validation_result"] == result
            for row in rows
        )
        for result in [
            "MATCH",
            "MODIFIED",
            "MISSING",
            "EMPTY",
        ]
    }

    lines = [
        "# Security Evidence Demo Release Validation",
        "",
        f"Validated: `{rows[0]['validated_at']}`",
        "",
        f"Release ID: `{release_id}`",
        "",
        f"Integrity Status: **{overall_status}**",
        "",
        "## Validation Counts",
        "",
        f"- Match: `{counts['MATCH']}`",
        f"- Modified: `{counts['MODIFIED']}`",
        f"- Missing: `{counts['MISSING']}`",
        f"- Empty: `{counts['EMPTY']}`",
        "",
        "## Artifact Results",
        "",
        "| Artifact | Result | Current status | Path |",
        "|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['artifact_name']} "
            f"| {row['validation_result']} "
            f"| {row['current_status']} "
            f"| `{row['artifact_path']}` |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "`MATCH` means the current file has the same "
                "size and SHA-256 hash recorded in the release "
                "manifest."
            ),
            "",
            (
                "`MODIFIED`, `MISSING`, or `EMPTY` means the "
                "current working artifact no longer matches "
                "the recorded release."
            ),
            "",
            "## Governance Rule",
            "",
            (
                "> A failed integrity check does not prove "
                "malicious tampering. It proves only that the "
                "current artifact set is not identical to the "
                "recorded release."
            ),
            "",
        ]
    )

    VALIDATION_MD.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def write_report(
    release_id: str,
    rows: list[dict[str, str | int]],
    overall_status: str,
) -> None:
    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    failed_rows = [
        row
        for row in rows
        if row["validation_result"] != "MATCH"
    ]

    lines = [
        "# Security Evidence Demo Release Validation Report",
        "",
        f"Validated: `{rows[0]['validated_at']}`",
        "",
        f"Release ID: `{release_id}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        f"Artifacts checked: `{len(rows)}`",
        f"Exceptions found: `{len(failed_rows)}`",
        "",
        "## Generated Artifacts",
        "",
        f"- `{VALIDATION_CSV.as_posix()}`",
        f"- `{VALIDATION_MD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
    ]

    if failed_rows:
        lines.extend(
            [
                "## Exceptions",
                "",
            ]
        )

        for row in failed_rows:
            lines.append(
                f"- `{row['artifact_path']}`: "
                f"{row['validation_result']}"
            )

        lines.append("")

    REPORT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> int:
    try:
        release_id, manifest_rows = load_manifest()

    except (FileNotFoundError, ValueError) as error:
        print(f"Validation error: {error}")
        return 1

    validated_at = datetime.now(
        timezone.utc
    ).isoformat()

    validation_rows = [
        validate_artifact(
            row,
            validated_at,
        )
        for row in manifest_rows
    ]

    overall_status = determine_overall_status(
        validation_rows
    )

    write_validation_csv(
        validation_rows
    )

    write_validation_markdown(
        release_id,
        validation_rows,
        overall_status,
    )

    write_report(
        release_id,
        validation_rows,
        overall_status,
    )

    print(f"Release ID: {release_id}")
    print(f"Integrity status: {overall_status}")
    print(f"Validation CSV: {VALIDATION_CSV}")
    print(f"Validation summary: {VALIDATION_MD}")
    print(f"Validation report: {REPORT_FILE}")

    if overall_status == "RELEASE_INTEGRITY_VERIFIED":
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
    