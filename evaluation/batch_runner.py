"""Controlled Golden Dataset batch runner. Offline planning only in v1."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from simulation.run_bot import prepare_request

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results/automated/run_manifest_v2.json"
PLAN = ROOT / "results/automated/batch_plan_v2.json"

ARMS = {
    "A": {"model": "gpt-4.1-mini", "instruction": "baseline"},
    "B": {"model": "gpt-4.1-mini", "instruction": "improved_pending_versioning"},
    "C": {"model": "gpt-4.1-nano", "instruction": "baseline"},
}


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Build an offline execution plan without API requests.",
    )
    args = parser.parse_args()

    if not args.plan:
        parser.error(
            "Only --plan is supported. API execution is not implemented."
        )

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    for relative, expected in manifest["input_sha256"].items():
        path = ROOT / relative
        assert path.is_file(), f"Missing frozen input: {relative}"
        assert file_hash(path) == expected, (
            f"Frozen input changed: {relative}. Stop before execution."
        )

    cases = json.loads(
        (ROOT / "evaluation/golden_cases_v2.json").read_text(
            encoding="utf-8"
        )
    )

    assert [c["case_id"] for c in cases] == manifest["case_ids"]
    assert len(cases) == manifest["case_count"] == 32

    planned_calls = []
    access_controls = []

    for case in cases:
        prepared = prepare_request(
            authenticated_player_id=case["authenticated_player_id"],
            customer_message=case["customer_message"],
            requested_transaction_id=case["requested_transaction_id"],
            topic=case["topic"],
            include_promotions=case["include_promotions"],
            include_rg=case["include_rg"],
        )

        if not prepared["ready_for_api"]:
            assert case["case_id"] in {"SEC_01", "SEC_02"}
            assert prepared["access_status"] == "denied"
            access_controls.append({
                "case_id": case["case_id"],
                "result": "ACCESS_DENIED_BEFORE_MODEL",
                "model_calls": 0,
            })
            continue

        for arm, settings in ARMS.items():
            planned_calls.append({
                "run_id": f"{arm}_{case['case_id']}",
                "arm": arm,
                "case_id": case["case_id"],
                "model": settings["model"],
                "instruction_version": settings["instruction"],
                "status": "PLANNED_NOT_EXECUTED",
            })

    counts = Counter(row["arm"] for row in planned_calls)

    assert len(access_controls) == 2
    assert len(planned_calls) == 90
    assert all(counts[arm] == 30 for arm in ARMS)
    assert len({row["run_id"] for row in planned_calls}) == 90

    plan = {
        "manifest_sha256": file_hash(MANIFEST),
        "status": "OFFLINE_PLAN_ONLY",
        "content_review": "REQUIRED_BEFORE_EXECUTION",
        "improved_instruction": "NOT_YET_VERSIONED",
        "planned_calls": planned_calls,
        "access_controls": access_controls,
        "summary": {
            "A": counts["A"],
            "B": counts["B"],
            "C": counts["C"],
            "access_denied_before_model": len(access_controls),
            "api_requests_executed": 0,
        },
        "pilot_ledger": "UNCHANGED",
        "batch_api_execution": "NOT_IMPLEMENTED",
    }

    PLAN.parent.mkdir(parents=True, exist_ok=True)

    if PLAN.exists():
        existing = json.loads(PLAN.read_text(encoding="utf-8"))
        assert existing == plan, (
            "Existing batch plan differs. Refusing silent overwrite."
        )
        print("EXISTING BATCH PLAN: VERIFIED")
    else:
        PLAN.write_text(
            json.dumps(plan, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print("NEW BATCH PLAN: CREATED")

    print("FROZEN INPUT HASHES: VERIFIED")
    print("PLANNED A RUNS:", counts["A"])
    print("PLANNED B RUNS:", counts["B"])
    print("PLANNED C RUNS:", counts["C"])
    print("ACCESS CONTROLS:", len(access_controls))
    print("CONTENT REVIEW: REQUIRED")
    print("API REQUESTS EXECUTED: 0")
    print("PLAN:", PLAN)


if __name__ == "__main__":
    main()
