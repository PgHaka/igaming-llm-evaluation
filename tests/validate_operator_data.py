"""Cross-file integrity checks for the synthetic Northstar Gaming Demo fixture."""

import csv
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RECORDS = BASE / "data" / "operator" / "records"
KB = BASE / "data" / "operator" / "knowledge_base"

checks = 0


def check(condition, message):
    global checks
    checks += 1
    if not condition:
        raise AssertionError(message)


def load(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    check(bool(rows), f"Empty dataset: {path.name}")
    return rows


def unique(rows, field):
    values = [row[field] for row in rows]
    check(all(values), f"Empty {field}")
    check(len(values) == len(set(values)), f"Duplicate {field}")
    return {row[field]: row for row in rows}


players = unique(load(RECORDS / "players.csv"), "player_id")
transactions = unique(load(RECORDS / "transactions.csv"), "transaction_id")
promotions = unique(load(RECORDS / "promotions.csv"), "promotion_id")
rg_events = unique(load(RECORDS / "responsible_gambling.csv"), "rg_event_id")
player_promotions = unique(
    load(RECORDS / "player_promotions.csv"), "player_promotion_id"
)
documents = unique(load(KB / "kb_documents.csv"), "document_id")

check(len(players) == 10, "Unexpected player count")
check(len(transactions) == 14, "Unexpected transaction count")
check(len(promotions) == 3, "Unexpected promotion count")
check(len(rg_events) == 6, "Unexpected RG event count")
check(len(player_promotions) == 7, "Unexpected player-promotion count")
check(len(documents) == 6, "Unexpected KB document count")

for tx in transactions.values():
    check(tx["player_id"] in players, f"Unknown player in {tx['transaction_id']}")
    check(float(tx["amount_eur"]) > 0, f"Invalid amount: {tx['transaction_id']}")
    check(
        tx["status"] in {"completed", "failed", "pending"},
        f"Invalid transaction status: {tx['transaction_id']}",
    )
    if tx["transaction_type"] == "withdrawal":
        check(
            tx["refund_status"] == "not_applicable",
            f"Unexpected withdrawal refund status: {tx['transaction_id']}",
        )

for row in player_promotions.values():
    check(row["player_id"] in players, "Unknown bonus player")
    check(row["promotion_id"] in promotions, "Unknown promotion")
    tx_id = row["linked_transaction_id"]
    if tx_id:
        check(tx_id in transactions, f"Unknown linked transaction: {tx_id}")
        check(
            transactions[tx_id]["player_id"] == row["player_id"],
            f"Cross-player transaction reference: {tx_id}",
        )
    check(
        (row["award_status"] == "awarded")
        == bool(row["verified_award_amount_eur"]),
        f"Bonus award inconsistency: {row['player_promotion_id']}",
    )

for event in rg_events.values():
    check(event["player_id"] in players, "Unknown RG player")
    check(
        (event["event_status"] == "active") == bool(event["confirmed_at"]),
        f"RG confirmation inconsistency: {event['rg_event_id']}",
    )

for player in players.values():
    if player["self_exclusion_status"] == "active":
        check(
            any(
                event["player_id"] == player["player_id"]
                and event["event_type"] == "self_exclusion"
                and event["event_status"] == "active"
                for event in rg_events.values()
            ),
            f"Active self-exclusion without confirmed event: {player['player_id']}",
        )

for document in documents.values():
    check(
        document["status"] in {"approved", "superseded", "draft"},
        f"Invalid document status: {document['document_id']}",
    )
    replacement = document["superseded_by"]
    if replacement:
        check(replacement in documents, f"Missing replacement: {replacement}")
        check(
            document["status"] == "superseded"
            and documents[replacement]["status"] == "approved",
            f"Invalid document replacement: {document['document_id']}",
        )

print("NORTHSTAR GAMING DEMO — DATA INTEGRITY")
print(f"Datasets: 6 | Records: {sum(map(len, [players, transactions, promotions, rg_events, player_promotions, documents]))}")
print(f"Integrity assertions passed: {checks}")
print("RESULT: PASS")
