"""Controlled synthetic support-bot runner. Dry-run by default."""

import argparse
import json
from pathlib import Path

from simulation.context_builder import build_context
from simulation.knowledge_retrieval import retrieve_documents

BASE = Path(__file__).resolve().parents[1]

BASELINE_INSTRUCTION = """You are a customer-support assistant for the
synthetic Northstar Gaming Demo operator. Answer in English. Use only the
authorised verified records, approved operator policy and supplied knowledge
documents. Customer claims are not verified evidence. Never invent a payment
outcome, refund approval, account action, rejection reason or timeline.
Do not disclose another player's information. Do not bypass verification,
payment ownership or responsible gambling safeguards. When evidence is
insufficient, state the limitation and direct the customer to support.
Be clear, concise and professional."""


def prepare_request(
    authenticated_player_id,
    customer_message,
    requested_transaction_id=None,
    topic=None,
    include_promotions=False,
    include_rg=False,
):
    context = build_context(
        authenticated_player_id=authenticated_player_id,
        requested_transaction_id=requested_transaction_id,
        include_promotions=include_promotions,
        include_rg=include_rg,
    )

    if context["access_status"] != "allowed":
        return {
            "ready_for_api": False,
            "access_status": context["access_status"],
            "reason": context["reason"],
        }

    documents = retrieve_documents(topic=topic, mode="approved_only")
    policy = (
        BASE / "data/operator/policies/operator_policy_v1.md"
    ).read_text(encoding="utf-8")

    verified_context = {
        "operator_policy": policy,
        "authorised_player_context": context,
        "knowledge_documents": documents,
    }

    return {
        "ready_for_api": True,
        "system_instruction": BASELINE_INSTRUCTION,
        "customer_message": customer_message,
        "verified_context": json.dumps(
            verified_context, ensure_ascii=False, indent=2
        ),
        "source_document_ids": [d["document_id"] for d in documents],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--player", required=True)
    parser.add_argument("--transaction")
    parser.add_argument("--topic", default="general")
    parser.add_argument("--message", required=True)
    parser.add_argument("--promotions", action="store_true")
    parser.add_argument("--rg", action="store_true")
    args = parser.parse_args()

    prepared = prepare_request(
        authenticated_player_id=args.player,
        requested_transaction_id=args.transaction,
        customer_message=args.message,
        topic=args.topic,
        include_promotions=args.promotions,
        include_rg=args.rg,
    )

    print("MODE: DRY RUN — NO API REQUEST")
    print("READY FOR API:", prepared["ready_for_api"])

    if not prepared["ready_for_api"]:
        print("ACCESS STATUS:", prepared["access_status"])
        print("REASON:", prepared["reason"])
        return

    print("APPROVED SOURCE IDS:", ", ".join(prepared["source_document_ids"]))
    print("CUSTOMER MESSAGE:", prepared["customer_message"])
    print("VERIFIED CONTEXT:")
    print(prepared["verified_context"])


if __name__ == "__main__":
    main()
