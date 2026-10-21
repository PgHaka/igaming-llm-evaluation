"""Version-aware retrieval for the synthetic operator knowledge base."""

import csv
from datetime import date
from pathlib import Path

KB_PATH = (
    Path(__file__).resolve().parents[1]
    / "data" / "operator" / "knowledge_base" / "kb_documents.csv"
)

EVALUATION_DATE = date(2026, 10, 21)


def retrieve_documents(topic=None, mode="approved_only"):
    """Retrieve documents with explicit source metadata.

    approved_only: approved documents effective by the evaluation date.
    include_untrusted: deliberately include superseded/draft documents
                       for controlled adversarial testing.
    """
    if mode not in {"approved_only", "include_untrusted"}:
        raise ValueError(f"Unsupported retrieval mode: {mode}")

    with KB_PATH.open(encoding="utf-8-sig", newline="") as handle:
        documents = list(csv.DictReader(handle))

    selected = []

    for document in documents:
        if topic and document["topic"] not in {"general", topic}:
            continue

        if mode == "approved_only":
            if document["status"] != "approved":
                continue
            if date.fromisoformat(document["effective_date"]) > EVALUATION_DATE:
                continue

        selected.append(document)

    return selected
