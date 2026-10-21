"""Offline preflight for all Golden Dataset v2 scenarios."""

import json
from collections import Counter
from pathlib import Path

from simulation.run_bot import prepare_request

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation/golden_cases_v2.json"
OUTPUT = ROOT / "results/automated/golden_preflight_v2.json"


def main():
    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    results = []

    for case in cases:
        prepared = prepare_request(
            authenticated_player_id=case["authenticated_player_id"],
            customer_message=case["customer_message"],
            requested_transaction_id=case["requested_transaction_id"],
            topic=case["topic"],
            include_promotions=case["include_promotions"],
            include_rg=case["include_rg"],
        )

        if prepared["ready_for_api"]:
            context = json.loads(prepared["verified_context"])
            player = context["authorised_player_context"]["player"]

            assert player["player_id"] == case["authenticated_player_id"], (
                case["case_id"], "Wrong player context"
            )

            if case["requested_transaction_id"]:
                transaction = context["authorised_player_context"]["transaction"]
                assert transaction["transaction_id"] == case[
                    "requested_transaction_id"
                ], (case["case_id"], "Wrong transaction context")

            assert all(
                doc["status"] == "approved"
                for doc in context["knowledge_documents"]
            ), (case["case_id"], "Unapproved knowledge document included")

            authorised = context["authorised_player_context"]

            if case["include_promotions"]:
                assert "player_promotions" in authorised, (
                    case["case_id"], "Missing player promotion context"
                )
                assert all(
                    row["player_id"] == case["authenticated_player_id"]
                    for row in authorised["player_promotions"]
                ), (case["case_id"], "Cross-player promotion data")

                assert "NSG-KB003" in prepared["source_document_ids"], (
                    case["case_id"], "Current approved bonus FAQ missing"
                )
                assert "NSG-KB002" not in prepared["source_document_ids"], (
                    case["case_id"], "Superseded bonus FAQ included"
                )
                assert "NSG-KB004" not in prepared["source_document_ids"], (
                    case["case_id"], "Draft bonus FAQ included"
                )

            if case["include_rg"]:
                assert "rg_events" in authorised, (
                    case["case_id"], "Missing responsible gambling context"
                )
                assert all(
                    row["player_id"] == case["authenticated_player_id"]
                    for row in authorised["rg_events"]
                ), (case["case_id"], "Cross-player RG data")

                assert authorised["rg_events"], (
                    case["case_id"], "Expected RG event missing"
                )
                assert "NSG-KB005" in prepared["source_document_ids"], (
                    case["case_id"], "Approved RG guidance missing"
                )

            result = {
                "case_id": case["case_id"],
                "preflight_status": "READY_FOR_MODEL",
                "source_document_ids": prepared["source_document_ids"],
                "model_evaluation": "NOT_EXECUTED",
            }
        else:
            assert case["case_id"] in {"SEC_01", "SEC_02"}, (
                case["case_id"], "Unexpected access denial"
            )
            assert prepared["access_status"] == "denied", (
                case["case_id"], prepared["access_status"]
            )

            result = {
                "case_id": case["case_id"],
                "preflight_status": "ACCESS_DENIED",
                "access_status": prepared["access_status"],
                "model_evaluation": "NOT_EXECUTED",
            }

        results.append(result)
        print(case["case_id"], result["preflight_status"])

    counts = Counter(row["preflight_status"] for row in results)

    assert len(results) == 32
    assert counts["READY_FOR_MODEL"] == 30
    assert counts["ACCESS_DENIED"] == 2

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "dataset": "golden_cases_v2",
                "execution_mode": "offline_preflight",
                "summary": dict(counts),
                "results": results,
            },
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    print("\nPREFLIGHT: PASS")
    print("READY FOR MODEL:", counts["READY_FOR_MODEL"])
    print("ACCESS DENIED:", counts["ACCESS_DENIED"])
    print("MODEL RESPONSES EVALUATED: 0")
    print("API REQUESTS EXECUTED: 0")
    print("EVIDENCE FILE:", OUTPUT)


if __name__ == "__main__":
    main()
