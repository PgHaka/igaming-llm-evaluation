"""Load version-controlled synthetic examples separately from recorded runs."""

import json
from pathlib import Path

from evaluation.evidence_recorder import verify_output_integrity

ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "demo_evidence"
DEMO_FILES = ("DEMO-SUPPORT-FAIL.json", "DEMO-AUTOMATION-PASS.json")


def load_bundled_examples():
    """Return validated demonstration fixtures; never include local audit runs."""
    examples = []
    for filename in DEMO_FILES:
        path = DEMO_DIR / filename
        record = json.loads(path.read_text(encoding="utf-8"))

        if record.get("run_id") != path.stem:
            raise ValueError(f"Demo identifier mismatch: {filename}")
        if record.get("evidence_type") != "synthetic_offline_audit":
            raise ValueError(f"Unexpected demo evidence type: {filename}")
        if record.get("evidence_origin") != "bundled_example":
            raise ValueError(f"Unexpected demo origin: {filename}")
        if not verify_output_integrity(record):
            raise ValueError(f"Demo output integrity failure: {filename}")

        examples.append(record)

    return examples
