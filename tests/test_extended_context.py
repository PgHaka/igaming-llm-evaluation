"""Regression tests for access-controlled bonus and RG context."""

import unittest

from simulation.context_builder import build_context


class TestExtendedContext(unittest.TestCase):

    def test_player_receives_only_own_bonus_records(self):
        context = build_context(
            authenticated_player_id="NSG-P005",
            include_promotions=True,
        )
        self.assertEqual(context["access_status"], "allowed")
        self.assertEqual(
            {row["player_id"] for row in context["player_promotions"]},
            {"NSG-P005"},
        )
        self.assertEqual(
            context["player_promotions"][0]["eligibility_status"],
            "ineligible_min_deposit",
        )

    def test_player_receives_only_own_rg_events(self):
        context = build_context(
            authenticated_player_id="NSG-P002",
            include_rg=True,
        )
        self.assertEqual(context["access_status"], "allowed")
        self.assertEqual(len(context["rg_events"]), 1)
        self.assertEqual(context["rg_events"][0]["event_status"], "requested")
        self.assertEqual(context["rg_events"][0]["confirmed_at"], "")

    def test_no_cross_player_records_in_combined_context(self):
        context = build_context(
            authenticated_player_id="NSG-P001",
            include_promotions=True,
            include_rg=True,
        )
        self.assertTrue(
            all(r["player_id"] == "NSG-P001" for r in context["player_promotions"])
        )
        self.assertTrue(
            all(r["player_id"] == "NSG-P001" for r in context["rg_events"])
        )

    def test_unauthenticated_session_receives_no_sensitive_records(self):
        context = build_context(
            authenticated_player_id=None,
            include_promotions=True,
            include_rg=True,
        )
        self.assertEqual(context["access_status"], "denied")
        self.assertNotIn("player", context)
        self.assertNotIn("player_promotions", context)
        self.assertNotIn("rg_events", context)


if __name__ == "__main__":
    unittest.main()
