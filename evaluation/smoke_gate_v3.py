"""Offline gate for the three-run v3 smoke test. No network or reservations."""

import hashlib
import json
from pathlib import Path

from evaluation.batch_budget_v3 import check_budget
from evaluation.batch_ledger_v3 import initialise
from evaluation.prepare_batch_run_v3 import prepare_batch_run

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/automated"

SMOKE_RUNS = ("A_DEP_01", "B_DEP_01", "C_DEP_01")
MAX_CALLS = 3
MAX_ESTIMATED_USD = "0.02"
MAX_OUTPUT_TOKENS = 250


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preflight(run_id):
    if run_id not in SMOKE_RUNS:
        raise PermissionError("Run is outside the approved smoke-test scope.")

    pricing_path = RESULTS / "pricing_reference_v3.json"
    pricing = json.loads(pricing_path.read_text(encoding="utf-8"))

    if (
        pricing["checked_date_utc"] != "2026-10-21"
        or pricing["currency"] != "USD"
        or pricing["unit"] != "per_1_million_text_tokens"
        or pricing["pricing_mode"] != "standard"
        or pricing["cached_input_discount_assumed"] is not False
    ):
        raise PermissionError("Pricing reference requires review.")

    prepared = prepare_batch_run(run_id)
    ledger = initialise()

    if any(entry["run_id"] == run_id for entry in ledger["entries"]):
        raise PermissionError("Run already reserved; no automatic retries.")

    decision = check_budget(
        model=prepared["model"],
        pricing=pricing["models"],
        pricing_verified=True,
        estimated_input_tokens=prepared["input_utf8_bytes"],
        max_output_tokens=MAX_OUTPUT_TOKENS,
        max_calls=MAX_CALLS,
        max_estimated_usd=MAX_ESTIMATED_USD,
        ledger=ledger,
    )

    return {
        "run_id": run_id,
        "model": prepared["model"],
        "pricing_reference_sha256": sha256(pricing_path),
        "instruction_sha256": prepared["instruction_sha256"],
        "input_reservation": prepared["input_utf8_bytes"],
        "estimated_next_usd": decision["next_estimated_usd"],
        "estimated_cumulative_usd": decision["cumulative_estimated_usd"],
        "estimated_budget_usd": MAX_ESTIMATED_USD,
        "reservation_performed": False,
        "api_request_performed": False,
    }


if __name__ == "__main__":
    original = (
        RESULTS / "batch_api_usage_v3.json"
    ).read_bytes()

    for run_id in SMOKE_RUNS:
        result = preflight(run_id)
        print(
            f"{run_id}: PREFLIGHT PASS | "
            f"model={result['model']} | "
            f"estimated_USD={result['estimated_next_usd']}"
        )

    try:
        preflight("A_DEP_02")
    except PermissionError:
        print("RUN OUTSIDE SMOKE SCOPE: BLOCKED")
    else:
        raise AssertionError("Out-of-scope run accepted.")

    assert (
        RESULTS / "batch_api_usage_v3.json"
    ).read_bytes() == original
    assert initialise()["entries"] == []

    print("PRICING REFERENCE: CHECKED AGAINST SAVED METADATA")
    print("THREE-RUN OFFLINE GATE: PASS")
    print("REAL V3 LEDGER: UNCHANGED")
    print("API REQUESTS EXECUTED: 0")
