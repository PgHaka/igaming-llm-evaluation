"""Regression tests for document approval and version handling."""

import unittest

from simulation.knowledge_retrieval import retrieve_documents


class TestKnowledgeRetrieval(unittest.TestCase):

    def test_normal_mode_returns_only_approved_documents(self):
        documents = retrieve_documents()
        self.assertEqual(len(documents), 4)
        self.assertTrue(all(d["status"] == "approved" for d in documents))

    def test_bonus_retrieval_excludes_old_and_draft_terms(self):
        documents = retrieve_documents(topic="bonuses")
        ids = {d["document_id"] for d in documents}
        self.assertIn("NSG-KB003", ids)
        self.assertNotIn("NSG-KB002", ids)
        self.assertNotIn("NSG-KB004", ids)

    def test_adversarial_mode_preserves_source_status(self):
        documents = retrieve_documents(
            topic="bonuses", mode="include_untrusted"
        )
        statuses = {d["document_id"]: d["status"] for d in documents}
        self.assertEqual(statuses["NSG-KB002"], "superseded")
        self.assertEqual(statuses["NSG-KB004"], "draft")

    def test_invalid_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            retrieve_documents(mode="anything")


if __name__ == "__main__":
    unittest.main()
