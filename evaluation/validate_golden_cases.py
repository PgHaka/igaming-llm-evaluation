"""Validate Golden Dataset v2 against synthetic operator records."""

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation/golden_cases_v2.json"
RECORDS = ROOT / "data/operator/records"


def load_records(filename, key):
    with (RECORDS / filename).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == len({row[key] for row in rows}), filename
    return {row[key]: row for row in rows}


def validate():
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    players = load_records("players.csv", "player_id")
    transactions = load_records("transactions.csv", "transaction_id")

    assert len(cases) == 32, f"Expected 32 cases, found {len(cases)}"

    ids = [case["case_id"] for case in cases]
    assert len(ids) == len(set(ids)), "Duplicate case IDs"

    required = {
        "case_id", "category", "authenticated_player_id",
        "requested_transaction_id", "topic", "include_promotions",
        "include_rg", "customer_message", "expected_behaviour",
        "forbidden_claims", "severity", "ground_truth_source",
        "review_status",
    }

    privacy_denials = {"SEC_01", "SEC_02"}
    confirmed_denials = set()

    for case in cases:
        case_id = case["case_id"]

        assert required <= case.keys(), f"{case_id}: missing fields"
        assert case["authenticated_player_id"] in players, (
            f"{case_id}: unknown player"
        )
        assert case["severity"] in {
            "low", "medium", "high", "critical"
        }, f"{case_id}: invalid severity"

        assert isinstance(case["include_promotions"], bool)
        assert isinstance(case["include_rg"], bool)
        assert isinstance(case["forbidden_claims"], list)
        assert case["forbidden_claims"], f"{case_id}: no forbidden claims"

        for field in ("customer_message", "expected_behaviour"):
            assert isinstance(case[field], str) and case[field].strip(), (
                f"{case_id}: empty {field}"
            )

        transaction_id = case["requested_transaction_id"]
        if transaction_id is not None:
            assert transaction_id in transactions, (
                f"{case_id}: unknown transaction"
            )

            owner = transactions[transaction_id]["player_id"]
            authorised = owner == case["authenticated_player_id"]

            if case_id in privacy_denials:
                assert not authorised, (
                    f"{case_id}: expected cross-player access test"
                )
                confirmed_denials.add(case_id)
            else:
                assert authorised, (
                    f"{case_id}: unexpected cross-player transaction"
                )

        elif case_id in privacy_denials:
            raise AssertionError(
                f"{case_id}: privacy test missing transaction ID"
            )

        if case["category"] == "bonuses":
            assert case["include_promotions"], (
                f"{case_id}: promotions context not enabled"
            )

        if case["category"] == "responsible_gambling":
            assert case["include_rg"], (
                f"{case_id}: responsible gambling context not enabled"
            )

        assert case["review_status"] == "draft_requires_validation", (
            f"{case_id}: unexpected review status"
        )

    assert confirmed_denials == privacy_denials

    print("GOLDEN DATASET VALIDATION: PASS")
    print("TOTAL CASES:", len(cases))
    print("UNIQUE CASE IDS:", len(set(ids)))
    print("CROSS-PLAYER DENIAL SCENARIOS:", len(confirmed_denials))
    print("CATEGORY DISTRIBUTION:")
    for category, count in sorted(
        Counter(case["category"] for case in cases).items()
    ):
        print(f"  {category}: {count}")
    print("DATASET STATUS: STRUCTURALLY VALID; CONTENT REVIEW STILL REQUIRED")
    print("API REQUESTS EXECUTED: 0")


if __name__ == "__main__":
    validate()
