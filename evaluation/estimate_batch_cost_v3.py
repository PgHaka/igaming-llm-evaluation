"""Offline cost estimator. Requires explicitly supplied provider rates."""

import argparse
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from evaluation.batch_budget_v3 import amount

ROOT = Path(__file__).resolve().parents[1]
ESTIMATES = ROOT / "results/automated/input_size_estimates_v3.json"


def calculate(prices, selected=None):
    data = json.loads(ESTIMATES.read_text(encoding="utf-8"))
    rows = data["runs"]
    if selected is not None:
        rows = [row for row in rows if row["run_id"] in selected]
        assert len(rows) == len(selected), "Unknown or duplicate selected run ID"

    models = {"A": "gpt-4.1-mini", "B": "gpt-4.1-mini",
              "C": "gpt-4.1-nano"}
    totals = defaultdict(lambda: {
        "runs": 0, "input_estimate": 0,
        "output_reservation": 0, "estimated_usd": Decimal("0"),
    })

    for row in rows:
        arm = row["arm"]
        rates = prices[models[arm]]
        input_tokens = row["conservative_reserved_input_token_estimate"]
        output_tokens = 250

        estimate = (
            Decimal(input_tokens) * amount(rates["input_per_million_usd"])
            + Decimal(output_tokens) * amount(rates["output_per_million_usd"])
        ) / Decimal(1_000_000)

        item = totals[arm]
        item["runs"] += 1
        item["input_estimate"] += input_tokens
        item["output_reservation"] += output_tokens
        item["estimated_usd"] += estimate

    return totals


def display(title, totals):
    print("\n" + title)
    overall = Decimal("0")
    for arm in ("A", "B", "C"):
        item = totals[arm]
        overall += item["estimated_usd"]
        print(
            f"{arm}: runs={item['runs']} "
            f"input_estimate={item['input_estimate']} "
            f"output_reservation={item['output_reservation']} "
            f"estimated_USD={item['estimated_usd']:.8f}"
        )
    print(f"TOTAL ESTIMATED USD: {overall:.8f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mini-input", required=True)
    parser.add_argument("--mini-output", required=True)
    parser.add_argument("--nano-input", required=True)
    parser.add_argument("--nano-output", required=True)
    args = parser.parse_args()

    prices = {
        "gpt-4.1-mini": {
            "input_per_million_usd": str(amount(args.mini_input)),
            "output_per_million_usd": str(amount(args.mini_output)),
        },
        "gpt-4.1-nano": {
            "input_per_million_usd": str(amount(args.nano_input)),
            "output_per_million_usd": str(amount(args.nano_output)),
        },
    }

    display("FULL 90-RUN ESTIMATE", calculate(prices))
    display(
        "THREE-RUN SMOKE TEST",
        calculate(prices, {"A_DEP_01", "B_DEP_01", "C_DEP_01"}),
    )
    print("\nRATES: USER-SUPPLIED; NOT VERIFIED BY THIS SCRIPT")
    print("INPUT TOKENS: CONSERVATIVE BYTE-BASED ESTIMATES, NOT MEASURED")
    print("PROVIDER BILLING GUARANTEE: NO")
    print("API REQUESTS EXECUTED: 0")
