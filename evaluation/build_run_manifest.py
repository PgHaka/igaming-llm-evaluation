"""Build an immutable-input reference for a controlled model comparison."""

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/automated/run_manifest_v2.json"

INPUTS = [
    "evaluation/golden_cases_v2.json",
    "data/operator/policies/operator_policy_v1.md",
    "data/operator/records/players.csv",
    "data/operator/records/transactions.csv",
    "data/operator/records/promotions.csv",
    "data/operator/records/player_promotions.csv",
    "data/operator/records/responsible_gambling.csv",
    "data/operator/knowledge_base/kb_documents.csv",
    "simulation/context_builder.py",
    "simulation/knowledge_retrieval.py",
    "simulation/run_bot.py",
    "simulation/api_client.py",
    "evaluation/rule_engine.py",
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cases = json.loads(
        (ROOT / INPUTS[0]).read_text(encoding="utf-8")
    )

    assert len(cases) == 32
    assert len({case["case_id"] for case in cases}) == 32

    input_hashes = {}
    for relative in INPUTS:
        path = ROOT / relative
        assert path.is_file(), f"Missing required input: {relative}"
        input_hashes[relative] = sha256(path)

    manifest = {
        "manifest_version": "2.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "golden_cases_v2",
        "case_count": len(cases),
        "case_ids": [case["case_id"] for case in cases],
        "category_distribution": dict(
            sorted(Counter(case["category"] for case in cases).items())
        ),
        "input_sha256": input_hashes,
        "comparison_design": {
            "A": "baseline_instruction",
            "B": "improved_instruction_to_be_versioned",
            "C": "lower_cost_model_with_identical_verified_context",
        },
        "execution_status": "NOT_STARTED",
        "human_review_status": "REQUIRED",
        "api_requests_executed_by_manifest_builder": 0,
        "notes": (
            "Input fingerprints only. No model quality or improvement "
            "claims. Pilot API ledger remains separate and unchanged."
        ),
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if OUTPUT.exists():
        existing = json.loads(OUTPUT.read_text(encoding="utf-8"))
        assert existing["input_sha256"] == input_hashes, (
            "Existing manifest differs from current inputs. "
            "Do not silently overwrite frozen evidence."
        )
        print("EXISTING MANIFEST: INPUT HASHES VERIFIED")
    else:
        OUTPUT.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print("NEW MANIFEST: CREATED")

    print("GOLDEN CASES:", len(cases))
    print("HASHED INPUT FILES:", len(input_hashes))
    print("COMPARISON ARMS: A / B / C")
    print("EXECUTION STATUS: NOT_STARTED")
    print("API REQUESTS EXECUTED: 0")
    print("MANIFEST:", OUTPUT)


if __name__ == "__main__":
    main()
