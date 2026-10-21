"""Access-controlled context retrieval for the synthetic evaluation bot.

The authenticated_player_id must come from a trusted simulation session,
never from instructions or identity claims inside a customer message.
"""

import csv
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RECORDS = BASE / "data" / "operator" / "records"


def load_records(filename, key):
    with (RECORDS / filename).open(encoding="utf-8-sig", newline="") as handle:
        return {row[key]: row for row in csv.DictReader(handle)}


def build_context(
    authenticated_player_id,
    requested_transaction_id=None,
    include_promotions=False,
    include_rg=False,
):
    """Return only records authorised for the simulated player session."""

    if not authenticated_player_id:
        return {
            "access_status": "denied",
            "reason": "No authenticated player session.",
        }

    players = load_records("players.csv", "player_id")
    player = players.get(authenticated_player_id)

    if player is None:
        return {
            "access_status": "denied",
            "reason": "Unknown authenticated player.",
        }

    context = {
        "access_status": "allowed",
        "player": player,
    }

    if requested_transaction_id is not None:
        transactions = load_records("transactions.csv", "transaction_id")
        transaction = transactions.get(requested_transaction_id)

        if transaction is None:
            return {
                "access_status": "not_found",
                "reason": "No verified transaction record found.",
            }

        if transaction["player_id"] != authenticated_player_id:
            return {
                "access_status": "denied",
                "reason": "Requested transaction is not authorised for this session.",
            }

        context["transaction"] = transaction

    if include_promotions:
        player_promotions = load_records(
            "player_promotions.csv", "player_promotion_id"
        )
        context["player_promotions"] = [
            row for row in player_promotions.values()
            if row["player_id"] == authenticated_player_id
        ]

        # Only campaign records linked to this player's promotion records.
        # Include their actual lifecycle and terms status as evidence;
        # expired or pending campaigns are NOT approved current offers.
        promotions = load_records("promotions.csv", "promotion_id")
        linked_ids = {
            row["promotion_id"]
            for row in context["player_promotions"]
        }
        missing_ids = linked_ids - promotions.keys()
        if missing_ids:
            raise ValueError("Linked promotion record is missing.")

        context["linked_promotions"] = [
            promotions[promotion_id]
            for promotion_id in sorted(linked_ids)
        ]

    if include_rg:
        rg_events = load_records("responsible_gambling.csv", "rg_event_id")
        context["rg_events"] = [
            row for row in rg_events.values()
            if row["player_id"] == authenticated_player_id
        ]

    return context
