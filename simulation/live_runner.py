"""Explicit, locally configured single-call evaluation runner."""

import argparse
import json
from pathlib import Path

from simulation.run_bot import prepare_request
from simulation.api_client import request_model_response

BASE = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE / ".env"
RESULTS = BASE / "results" / "automated"
LEDGER = RESULTS / "api_usage.json"


def load_config():
    values = {}
    for line in CONFIG_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()

    return {
        "api_key": values.get("OPENAI_API_KEY", ""),
        "model": values["EVAL_BOT_MODEL"],
        "max_output_tokens": int(values["EVAL_BOT_MAX_OUTPUT_TOKENS"]),
        "max_calls": int(values["EVAL_BOT_MAX_API_CALLS"]),
        "max_estimated_usd": float(values["EVAL_BOT_MAX_ESTIMATED_USD"]),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    config = load_config()

    prepared = prepare_request(
        authenticated_player_id="NSG-P002",
        requested_transaction_id="NSG-T002",
        topic="general",
        customer_message=(
            "My Skrill deposit of EUR 22.36 failed. "
            "Has the refund already been completed?"
        ),
    )

    if not prepared["ready_for_api"]:
        raise RuntimeError("Authorised context was not available.")

    if not config["api_key"].startswith("sk-"):
        raise RuntimeError("Missing local API key.")

    if config["max_output_tokens"] > 250:
        raise RuntimeError("Output-token cap exceeds pilot limit.")

    if config["max_calls"] > 5 or config["max_calls"] < 1:
        raise RuntimeError("Invalid pilot call limit.")

    if config["max_estimated_usd"] > 0.10 or config["max_estimated_usd"] <= 0:
        raise RuntimeError("Invalid pilot spending configuration.")

    ledger = {"calls": []}
    if LEDGER.exists():
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    if len(ledger["calls"]) >= config["max_calls"]:
        raise RuntimeError("Recorded pilot API-call limit reached.")

    print("MODEL:", config["model"])
    print("MAX OUTPUT TOKENS:", config["max_output_tokens"])
    print("MAX RECORDED CALLS:", config["max_calls"])
    print("CONFIGURED ESTIMATED SPENDING LIMIT USD:", config["max_estimated_usd"])
    print("PREVIOUSLY RECORDED CALLS:", len(ledger["calls"]))
    print("AUTHORISED CONTEXT: YES")
    print("SOURCE IDS:", ", ".join(prepared["source_document_ids"]))
    print("SECRET DISPLAYED: NO")

    if not args.execute:
        print("MODE: PREFLIGHT ONLY")
        print("API REQUESTS EXECUTED: 0")
        return

    # Reserve a call before sending it. An uncertain outcome consumes a slot.
    # No automatic retries. This is a pilot counter, not a billing guarantee.
    RESULTS.mkdir(parents=True, exist_ok=True)
    entry = {
        "scenario": "FAILED_SKRILL_REFUND_UNKNOWN",
        "status": "reserved_before_request",
        "model_requested": config["model"],
    }
    ledger["calls"].append(entry)
    LEDGER.write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    try:
        result = request_model_response(
            api_key=config["api_key"],
            model=config["model"],
            system_instruction=prepared["system_instruction"],
            customer_message=prepared["customer_message"],
            verified_context=prepared["verified_context"],
            max_output_tokens=config["max_output_tokens"],
        )
    except Exception:
        entry["status"] = "outcome_unknown_or_failed"
        LEDGER.write_text(
            json.dumps(ledger, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        raise

    entry.update(result)
    entry["status"] = "response_recorded"
    LEDGER.write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("MODEL RESPONSE:", result["answer"])
    print("INPUT TOKENS:", result["input_tokens"])
    print("OUTPUT TOKENS:", result["output_tokens"])
    print("USAGE LEDGER:", LEDGER)


if __name__ == "__main__":
    main()
