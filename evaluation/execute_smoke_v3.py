"""Controlled single-run smoke execution. Live API execution is not enabled."""

import json
from pathlib import Path

from evaluation import batch_ledger_v3 as ledger
from evaluation.prepare_batch_run_v3 import prepare_batch_run
from evaluation.smoke_gate_v3 import (
    MAX_CALLS, MAX_ESTIMATED_USD, MAX_OUTPUT_TOKENS,
    RESULTS, preflight,
)


def execute_one(run_id, *, api_key=None, api_request=None, test_mode=False):
    if not test_mode:
        raise PermissionError(
            "Live execution is disabled pending explicit approval."
        )

    if api_request is None:
        raise ValueError("An injected offline API stub is required.")

    if api_key != "OFFLINE_TEST_ONLY":
        raise PermissionError("Offline test credential required.")

    gate = preflight(run_id)
    prepared = prepare_batch_run(run_id)

    assert gate["input_reservation"] == prepared["input_utf8_bytes"]
    assert gate["model"] == prepared["model"]

    pricing = json.loads(
        (RESULTS / "pricing_reference_v3.json").read_text(encoding="utf-8")
    )

    reservation = ledger.reserve(
        run_id,
        allow_live=True,
        pricing=pricing["models"],
        pricing_verified=True,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        max_calls=MAX_CALLS,
        max_estimated_usd=MAX_ESTIMATED_USD,
    )

    assert reservation["model"] == prepared["model"]
    assert reservation["estimated_input_tokens"] == gate["input_reservation"]

    try:
        response = api_request(
            api_key=api_key,
            **prepared["api_arguments"],
        )
    except Exception:
        # Do not expose exception messages, credentials or request contents.
        ledger.record_outcome(
            run_id, error="OFFLINE_TEST_API_EXCEPTION"
        )
        raise RuntimeError("Offline API stub failed.") from None

    return ledger.record_outcome(run_id, response=response)


if __name__ == "__main__":
    raise SystemExit(
        "No CLI execution enabled. Run the separate offline mock test."
    )
