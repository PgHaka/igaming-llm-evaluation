"""Markdown reporting for recorded synthetic offline audit evidence."""

from collections import Counter
from datetime import datetime, timezone


VALID_RESULTS = ("PASS", "FAIL", "REVIEW")
SYSTEMS = ("support_bot", "payment_automation")


def generate_audit_report(records):
    """Build a descriptive report without inferring production reliability."""
    records = list(records)

    counts = Counter(r["evaluation"]["result"] for r in records)
    systems = Counter(r["system_type"] for r in records)
    findings = Counter(
        f["rule_id"]
        for record in records
        for f in record["evaluation"]["findings"]
    )

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    origins = Counter(
        r.get("evidence_origin", "recorded_run") for r in records
    )
    unknown_origins = set(origins) - {"recorded_run", "bundled_example"}
    if unknown_origins:
        raise ValueError(
            f"Unsupported evidence origins: {sorted(unknown_origins)}"
        )

    lines = [
        "# Operator AI Audit — Evidence Summary",
        "",
        f"Generated: {generated}",
        "",
        "**Evidence scope:** Synthetic offline audit records only.",
        "",
        "## Evidence origin",
        "",
        "| Origin | Entries |",
        "|---|---:|",
        f"| Recorded audit runs | {origins['recorded_run']} |",
        f"| Bundled synthetic examples | {origins['bundled_example']} |",
        "",
        "Bundled examples are supplied demonstration fixtures, not "
        "visitor-generated audit runs or independent model observations.",
        "Legacy records without an origin field are classified as recorded runs.",
        "",
        "## Recorded outcomes",
        "",
        "| Outcome | Recorded runs |",
        "|---|---:|",
    ]

    for result in VALID_RESULTS:
        lines.append(f"| {result} | {counts[result]} |")

    lines.extend([
        f"| **Total** | **{len(records)}** |",
        "",
        "## System-level summary",
        "",
        "| System | Runs | PASS | FAIL | REVIEW |",
        "|---|---:|---:|---:|---:|",
    ])

    for system in SYSTEMS:
        subset = [
            r for r in records if r["system_type"] == system
        ]
        local = Counter(r["evaluation"]["result"] for r in subset)
        lines.append(
            f"| {system} | {systems[system]} | "
            f"{local['PASS']} | {local['FAIL']} | {local['REVIEW']} |"
        )

    lines.extend([
        "",
        "## Recorded finding categories",
        "",
    ])

    if findings:
        lines.extend([
            "| Rule ID | Occurrences |",
            "|---|---:|",
        ])
        for rule_id, count in sorted(
            findings.items(), key=lambda item: (-item[1], item[0])
        ):
            lines.append(f"| {rule_id} | {count} |")
    else:
        lines.append("No findings recorded.")

    lines.extend([
        "",
        "## Evidence register",
        "",
        "| Run ID | Origin | System | Result | Mode | Output SHA-256 |",
        "|---|---|---|---|---|---|",
    ])

    for record in records:
        lines.append(
            f"| {record['run_id']} | "
            f"{record.get('evidence_origin', 'recorded_run')} | "
            f"{record['system_type']} | "
            f"{record['evaluation']['result']} | "
            f"{record['execution_mode']} | "
            f"`{record['output_sha256']}` |"
        )

    lines.extend([
        "",
        "## Interpretation and limitations",
        "",
        "- PASS means only that the implemented deterministic control was satisfied.",
        "- FAIL means a defined violation was detected by the implemented control.",
        "- REVIEW means automatic assessment was insufficient or inconclusive.",
        "- Repeated control runs are not independent model-performance observations.",
        "- Recorder events describe the local evaluation workflow, not upstream execution.",
        "- SHA-256 supports output-integrity checking; it does not verify provenance.",
        "- This report does not establish production reliability or operator compliance.",
        "- Historical human-reviewed model results are excluded from these totals.",
        "- No live model execution or real payment action is represented here.",
        "",
    ])

    return "\n".join(lines)
