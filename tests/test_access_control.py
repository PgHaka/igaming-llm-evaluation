"""Security regression tests for synthetic player-record access."""

import unittest

from simulation.context_builder import build_context


class TestAccessControl(unittest.TestCase):

    def test_authenticated_player_sees_own_transaction(self):
        context = build_context(
            authenticated_player_id="NSG-P002",
            requested_transaction_id="NSG-T002",
        )
        self.assertEqual(context["access_status"], "allowed")
        self.assertEqual(context["transaction"]["transaction_id"], "NSG-T002")

    def test_other_players_transaction_is_denied(self):
        context = build_context(
            authenticated_player_id="NSG-P001",
            requested_transaction_id="NSG-T002",
        )
        self.assertEqual(context["access_status"], "denied")
        self.assertNotIn("transaction", context)
        self.assertNotIn("22.36", str(context))

    def test_unknown_session_is_denied(self):
        context = build_context(
            authenticated_player_id=None,
            requested_transaction_id="NSG-T002",
        )
        self.assertEqual(context["access_status"], "denied")
        self.assertNotIn("transaction", context)

    def test_unknown_transaction_is_not_invented(self):
        context = build_context(
            authenticated_player_id="NSG-P001",
            requested_transaction_id="NSG-T999",
        )
        self.assertEqual(context["access_status"], "not_found")
        self.assertNotIn("transaction", context)


if __name__ == "__main__":
    unittest.main()
