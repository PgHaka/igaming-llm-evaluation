"""Local evidence recorder for synthetic audit demonstrations.

Persists observable audit inputs, outputs and evaluator findings.
Never claims to expose a model's private reasoning.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from evaluation.audit_engine import audit

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "results/audit_demo"


def record_audit(case_id, system_type, output, execution_mode="control"):
    """Evaluate one supplied output and persist its observable evidence."""

    if execution_mode not in {"control", "replay"}:
        raise ValueError("Evidence recorder supports control and replay only")

    result = audit(
        case_id=case_id,
        system_type=system_type,
        output=output,
        execution_mode=execution_mode,
    )

    timestamp = datetime.now(timezone.utc).isoformat()
    run_id = f"AUD-{uuid.uuid4().hex[:12].upper()}"

    serialized_output = json.dumps(
        output, ensure_ascii=False, sort_keys=True
    )

    output_sha256 = hashlib.sha256(
        serialized_output.encode("utf-8")
    ).hexdigest()

    trace = [
        {
            "step": 1,
            "event": "OUTPUT_RECEIVED",
            "detail": (
                "Previously supplied output received for offline evaluation."
            ),
        },
        {
            "step": 2,
            "event": "CONTROL_SELECTED",
            "detail": {
                "case_id": case_id,
                "system_type": system_type,
                "execution_mode": execution_mode,
            },
        },
        {
            "step": 3,
            "event": "DETERMINISTIC_EVALUATION",
            "detail": {
                "evaluator_version": result["evaluator_version"],
                "checks": result["checks"],
                "findings": result["findings"],
            },
        },
        {
            "step": 4,
            "event": "RESULT_RECORDED",
            "detail": {
                "result": result["result"],
                "output_sha256": output_sha256,
            },
        },
    ]

    evidence = {
        "run_id": run_id,
        "recorded_at_utc": timestamp,
        "evidence_type": "synthetic_offline_audit",
        "source_claim": (
            "Supplied fixture" if execution_mode == "control"
            else "Supplied replay output; provenance not independently verified"
        ),
        "case_id": case_id,
        "system_type": system_type,
        "execution_mode": execution_mode,
        "output": output,
        "output_sha256": output_sha256,
        "evaluation": result,
        "observable_trace": trace,
        "limitations": [
            "No live model or operator system was executed by this recorder.",
            "A control PASS is not proof of general production reliability.",
            "The trace records observable software events, not model reasoning.",
        ],
    }

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    destination = EVIDENCE_DIR / f"{run_id}.json"

    with destination.open("x", encoding="utf-8") as handle:
        json.dump(evidence, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    return evidence, destination
