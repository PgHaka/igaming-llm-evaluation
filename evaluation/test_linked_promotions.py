"""Offline regression tests for access-controlled campaign context."""

import unittest

from simulation.context_builder import build_context


class LinkedPromotionTests(unittest.TestCase):
    def test_linked_active_campaign(self):
        context = build_context("NSG-P001", include_promotions=True)
        campaigns = context["linked_promotions"]
        self.assertEqual(len(campaigns), 1)
        self.assertEqual(campaigns[0]["promotion_id"], "NSG-B001")
        self.assertEqual(campaigns[0]["status"], "active")
        self.assertEqual(campaigns[0]["terms_status"], "approved")

    def test_expired_campaign_remains_identifiable(self):
        context = build_context("NSG-P003", include_promotions=True)
        campaign = context["linked_promotions"][0]
        self.assertEqual(campaign["promotion_id"], "NSG-B002")
        self.assertEqual(campaign["status"], "expired")

    def test_pending_campaign_is_not_misrepresented(self):
        context = build_context("NSG-P010", include_promotions=True)
        campaign = context["linked_promotions"][0]
        self.assertEqual(campaign["promotion_id"], "NSG-B003")
        self.assertEqual(campaign["status"], "pending_approval")
        self.assertEqual(campaign["terms_status"], "pending_review")

    def test_campaigns_excluded_by_default(self):
        context = build_context("NSG-P001")
        self.assertNotIn("linked_promotions", context)
        self.assertNotIn("player_promotions", context)

    def test_only_player_linked_campaigns_returned(self):
        context = build_context("NSG-P005", include_promotions=True)
        player_rows = context["player_promotions"]
        self.assertTrue(player_rows)
        self.assertTrue(
            all(row["player_id"] == "NSG-P005" for row in player_rows)
        )
        linked_ids = {row["promotion_id"] for row in player_rows}
        returned_ids = {
            row["promotion_id"] for row in context["linked_promotions"]
        }
        self.assertEqual(returned_ids, linked_ids)
        self.assertNotIn("NSG-B002", returned_ids)
        self.assertNotIn("NSG-B003", returned_ids)

    def test_cross_player_denial_returns_no_campaigns(self):
        context = build_context(
            "NSG-P001",
            requested_transaction_id="NSG-T005",
            include_promotions=True,
        )
        self.assertEqual(context["access_status"], "denied")
        self.assertNotIn("linked_promotions", context)
        self.assertNotIn("player_promotions", context)


if __name__ == "__main__":
    unittest.main(verbosity=2)
