"""Append-only-by-run-ID reservation ledger for controlled batch evaluation.

A reservation is persisted before a network request. Unknown outcomes are
never automatically retried. No API calls are made by this module.
"""

import hashlib
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/automated/batch_api_usage_v3.json"
PLAN = ROOT / "results/automated/batch_plan_v3.json"
CONFIG = ROOT / "results/automated/comparison_config_v3.json"
ESTIMATES = ROOT / "results/automated/input_size_estimates_v3.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def initialise():
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    config = json.loads(CONFIG.read_text(encoding="utf-8"))

    assert config["batch_plan_sha256"] == digest(PLAN)
    assert len(plan["planned_calls"]) == 90

    expected = {
        "version": "3.0",
        "plan_sha256": digest(PLAN),
        "comparison_config_sha256": digest(CONFIG),
        "entries": [],
    }

    LEDGER.parent.mkdir(parents=True, exist_ok=True)

    if LEDGER.exists():
        existing = json.loads(LEDGER.read_text(encoding="utf-8"))
        assert existing["plan_sha256"] == expected["plan_sha256"]
        assert existing["comparison_config_sha256"] == expected[
            "comparison_config_sha256"
        ]
        return existing

    # Exclusive creation prevents silently replacing an existing ledger.
    with LEDGER.open("x", encoding="utf-8") as handle:
        json.dump(expected, handle, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())

    return expected


def reserve(
    run_id, *, allow_live=False, pricing=None, pricing_verified=False,
    max_output_tokens=None, max_calls=None, max_estimated_usd=None,
):
    if not allow_live:
        raise PermissionError("Live reservation requires explicit authorisation.")

    ledger = initialise()
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    planned = {item["run_id"]: item for item in plan["planned_calls"]}

    if run_id not in planned:
        raise ValueError("Run ID is not in the frozen plan.")

    if any(entry["run_id"] == run_id for entry in ledger["entries"]):
        raise ValueError("Run ID already reserved. Automatic retry prohibited.")

    # Bind the reservation to the frozen plan and saved input estimates.
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    estimates = json.loads(ESTIMATES.read_text(encoding="utf-8"))
    assert estimates["batch_plan_sha256"] == digest(PLAN)
    assert estimates["comparison_config_sha256"] == digest(CONFIG)
    assert estimates["manifest_sha256"] == config["manifest_sha256"]
    assert len(estimates["runs"]) == 90

    matches = [
        row for row in estimates["runs"] if row["run_id"] == run_id
    ]
    assert len(matches) == 1, "Exactly one saved input estimate required."
    estimate = matches[0]
    assert estimate["arm"] == planned[run_id]["arm"]
    assert estimate["case_id"] == planned[run_id]["case_id"]
    assert estimate["estimation_method"] == (
        "one_token_per_utf8_byte_not_measured"
    )
    estimated_input_tokens = estimate[
        "conservative_reserved_input_token_estimate"
    ]
    assert estimated_input_tokens == estimate["input_utf8_bytes"]
    assert isinstance(estimated_input_tokens, int)
    assert estimated_input_tokens > 0

    # Import locally to avoid a circular module import.
    from evaluation.batch_budget_v3 import check_budget

    budget_decision = check_budget(
        model=planned[run_id]["model"],
        pricing=pricing or {},
        pricing_verified=pricing_verified,
        estimated_input_tokens=estimated_input_tokens,
        max_output_tokens=max_output_tokens,
        max_calls=max_calls,
        max_estimated_usd=max_estimated_usd,
        ledger=ledger,
    )

    entry = {
        "reserved_estimated_usd": budget_decision["next_estimated_usd"],
        "estimated_cumulative_usd": budget_decision["cumulative_estimated_usd"],
        "estimated_input_tokens": estimated_input_tokens,
        "max_output_tokens": max_output_tokens,
        "run_id": run_id,
        "arm": planned[run_id]["arm"],
        "case_id": planned[run_id]["case_id"],
        "model": planned[run_id]["model"],
        "status": "RESERVED_BEFORE_NETWORK",
        "outcome": "UNKNOWN_UNTIL_RECORDED",
    }

    ledger["entries"].append(entry)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=LEDGER.parent,
        prefix=LEDGER.name + ".",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        json.dump(ledger, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(temporary, LEDGER)
    return entry


def record_outcome(run_id, *, response=None, error=None):
    """Persist one terminal outcome; never overwrite an existing outcome."""
    if (response is None) == (error is None):
        raise ValueError("Provide exactly one of response or error.")

    ledger = initialise()
    matches = [
        entry for entry in ledger["entries"]
        if entry["run_id"] == run_id
    ]
    if len(matches) != 1:
        raise ValueError("Exactly one prior reservation is required.")

    entry = matches[0]
    if entry["status"] != "RESERVED_BEFORE_NETWORK":
        raise ValueError("Terminal outcome already recorded.")

    if response is not None:
        required = {
            "response_id", "model", "status", "answer",
            "input_tokens", "output_tokens", "total_tokens",
        }
        if not isinstance(response, dict) or not required <= response.keys():
            raise ValueError("Incomplete API response metadata.")
        # The provider may return the dated snapshot of a requested alias.
        # Accept only explicitly reviewed alias/snapshot pairs.
        approved_snapshots = {
            "gpt-4.1-mini": {"gpt-4.1-mini", "gpt-4.1-mini-2025-04-14"},
            "gpt-4.1-nano": {"gpt-4.1-nano", "gpt-4.1-nano-2025-04-14"},
        }
        if response["model"] not in approved_snapshots.get(
            entry["model"], {entry["model"]}
        ):
            raise ValueError("Returned model does not match reserved model.")
        if response["status"] != "completed" or not response["answer"]:
            raise ValueError("Incomplete or empty response requires review.")
        entry["status"] = "COMPLETED"
        entry["outcome"] = {
            key: response[key] for key in sorted(required)
        }
    else:
        if not isinstance(error, str) or not error:
            raise ValueError("A nonempty sanitised error is required.")
        if len(error) > 160 or not all(
            character.isalnum() or character in " _;:=-."
            for character in error
        ):
            raise ValueError("Error must be a short sanitised identifier.")
        entry["status"] = "ERROR"
        entry["outcome"] = error
        entry["provider_processing_or_billing"] = "UNKNOWN"

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=LEDGER.parent,
        prefix=LEDGER.name + ".",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        json.dump(ledger, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(temporary, LEDGER)
    return entry


if __name__ == "__main__":
    ledger = initialise()
    assert ledger["version"] == "3.0"
    assert ledger["entries"] == [], "Ledger already contains reservations."

    try:
        reserve("A_DEP_01")
    except PermissionError:
        print("UNAUTHORISED RESERVATION: BLOCKED")
    else:
        raise AssertionError("Unauthorised reservation was accepted.")

    try:
        reserve("NOT_A_PLANNED_RUN", allow_live=True)
    except ValueError:
        print("UNKNOWN RUN ID: BLOCKED")
    else:
        raise AssertionError("Unknown run ID was accepted.")

    assert initialise()["entries"] == []
    print("BATCH LEDGER V3: INITIALISED")
    print("PLAN AND CONFIG HASHES: VERIFIED")
    print("RESERVED RUNS: 0")
    print("API REQUESTS EXECUTED: 0")
