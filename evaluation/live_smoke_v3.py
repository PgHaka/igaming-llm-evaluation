"""Explicit, single-process, single-call live smoke runner for frozen v3."""

import argparse
import json
import os
import tempfile
from pathlib import Path

from evaluation import batch_ledger_v3 as ledger
from evaluation.prepare_batch_run_v3 import prepare_batch_run
from evaluation.smoke_gate_v3 import (
    SMOKE_RUNS, MAX_CALLS, MAX_ESTIMATED_USD,
    MAX_OUTPUT_TOKENS, RESULTS, preflight,
)
from simulation.api_client import request_model_response
from simulation.live_runner import load_config

CONFIRMATION = "I_APPROVE_ONE_PAID_V3_SMOKE_CALL"


def preserve_api_response(run_id, response):
    """Preserve returned synthetic response before ledger validation."""
    if run_id not in SMOKE_RUNS:
        raise PermissionError("Response outside smoke scope.")
    if not isinstance(response, dict):
        raise ValueError("API response must be a dictionary.")

    directory = RESULTS / "smoke_response_evidence_v3"
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / (run_id + ".json")

    # Never overwrite evidence from an earlier execution.
    if destination.exists():
        raise FileExistsError("Smoke response evidence already exists.")

    allowed = (
        "response_id", "model", "status", "answer",
        "input_tokens", "output_tokens", "total_tokens",
    )
    evidence = {
        "run_id": run_id,
        "source": "API_CLIENT_RETURN_BEFORE_LEDGER_VALIDATION",
        "response": {key: response.get(key) for key in allowed},
    }

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=directory,
        prefix=run_id + ".", suffix=".tmp", delete=False,
    ) as handle:
        temporary = Path(handle.name)
        os.chmod(temporary, 0o600)
        json.dump(evidence, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())

    # Exclusive creation: existing evidence must not be replaced.
    try:
        os.link(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)

    return destination


def execute_live(run_id, confirmation):
    if run_id not in SMOKE_RUNS:
        raise PermissionError("Run outside the three-run smoke scope.")
    if confirmation != CONFIRMATION:
        raise PermissionError("Explicit paid-call confirmation required.")

    # No key is loaded until all offline payload checks have passed.
    gate = preflight(run_id)
    prepared = prepare_batch_run(run_id)
    assert prepared["input_utf8_bytes"] == gate["input_reservation"]
    assert prepared["model"] == gate["model"]

    config = load_config()
    key = config["api_key"]
    if not key.startswith("sk-"):
        raise RuntimeError("Valid local API credential not configured.")

    pricing = json.loads(
        (RESULTS / "pricing_reference_v3.json").read_text(encoding="utf-8")
    )

    # Persist reservation before any network attempt. Never retry a run ID.
    reservation = ledger.reserve(
        run_id,
        allow_live=True,
        pricing=pricing["models"],
        pricing_verified=True,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        max_calls=MAX_CALLS,
        max_estimated_usd=MAX_ESTIMATED_USD,
    )
    assert reservation["estimated_input_tokens"] == gate["input_reservation"]

    try:
        response = request_model_response(
            api_key=key,
            **prepared["api_arguments"],
        )
    except Exception:
        ledger.record_outcome(
            run_id,
            error="LIVE_API_REQUEST_ERROR_OUTCOME_UNKNOWN",
        )
        raise RuntimeError(
            "Live request failed; provider processing or billing is unknown. "
            "Reservation consumed; no automatic retry."
        ) from None

    # Preserve actual returned evidence before any validation can reject it.
    # A preservation failure leaves the reservation untouched for review.
    preserve_api_response(run_id, response)

    # An incomplete response must remain reserved for manual review.
    # Do not silently classify it as a successful model answer.
    try:
        recorded = ledger.record_outcome(run_id, response=response)
    except (ValueError, TypeError, AssertionError):
        raise RuntimeError(
            "API returned an incomplete or mismatched response. "
            "Reservation retained for manual review; no retry."
        ) from None

    return {
        "run_id": recorded["run_id"],
        "status": recorded["status"],
        "model": recorded["model"],
        "response_id": recorded["outcome"]["response_id"],
        "answer": recorded["outcome"]["answer"],
        "input_tokens": recorded["outcome"]["input_tokens"],
        "output_tokens": recorded["outcome"]["output_tokens"],
        "estimated_reservation_usd": recorded["reserved_estimated_usd"],
        "billing_guarantee": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", choices=SMOKE_RUNS, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm", default="")
    args = parser.parse_args()

    gate = preflight(args.run_id)
    print("RUN:", gate["run_id"])
    print("MODEL:", gate["model"])
    print("ESTIMATED NEXT USD:", gate["estimated_next_usd"])
    print("ESTIMATED CAP USD:", MAX_ESTIMATED_USD)
    print("SECRET DISPLAYED: NO")

    if not args.execute:
        print("MODE: PREFLIGHT ONLY")
        print("API REQUESTS EXECUTED: 0")
        return

    result = execute_live(args.run_id, args.confirm)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
