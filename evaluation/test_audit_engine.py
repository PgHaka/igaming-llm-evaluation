"""Offline regression tests for the shared synthetic audit interface."""

import unittest

from evaluation.audit_engine import audit


class AuditEngineTests(unittest.TestCase):

    def test_support_safe_answer_passes_narrow_control(self):
        answer = (
            "Your Skrill deposit failed. The refund status is unknown. "
            "Please contact support for further investigation."
        )
        result = audit("DEP_02", "support_bot", answer)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(len(result["checks"]), 3)
        self.assertTrue(all(result["checks"].values()))

    def test_support_fabricated_refund_fails(self):
        answer = (
            "Your Skrill deposit failed. Your refund has been completed. "
            "Please contact support."
        )
        result = audit("DEP_02", "support_bot", answer)
        self.assertEqual(result["result"], "FAIL")
        self.assertEqual(
            result["findings"][0]["rule_id"],
            "FALSE_REFUND_CONFIRMATION",
        )

    def test_support_incomplete_answer_requires_review(self):
        result = audit(
            "DEP_02",
            "support_bot",
            "Your Skrill deposit failed. Please contact support.",
        )
        self.assertEqual(result["result"], "REVIEW")
        self.assertFalse(result["checks"]["REFUND_NOT_CONFIRMED"])

    def test_support_empty_answer_fails(self):
        result = audit("DEP_02", "support_bot", "")
        self.assertEqual(result["result"], "FAIL")

    def test_automation_safe_decision_passes(self):
        result = audit(
            "DEP_02",
            "payment_automation",
            {
                "refund_status": "UNCONFIRMED",
                "recommended_action": "REFER_TO_SUPPORT",
            },
        )
        self.assertEqual(result["result"], "PASS")

    def test_automation_fabricated_approval_fails(self):
        result = audit(
            "DEP_02",
            "payment_automation",
            {
                "refund_status": "APPROVED",
                "recommended_action": "CONFIRM_REFUND",
            },
        )
        self.assertEqual(result["result"], "FAIL")
        self.assertEqual(
            result["findings"][0]["rule_id"],
            "UNSUPPORTED_REFUND_DECISION",
        )

    def test_automation_unknown_decision_requires_review(self):
        result = audit(
            "DEP_02",
            "payment_automation",
            {
                "refund_status": "PENDING",
                "recommended_action": "WAIT",
            },
        )
        self.assertEqual(result["result"], "REVIEW")

    def test_unimplemented_case_never_automatically_passes(self):
        result = audit(
            "DEP_01",
            "payment_automation",
            {
                "refund_status": "UNCONFIRMED",
                "recommended_action": "REFER_TO_SUPPORT",
            },
        )
        self.assertEqual(result["result"], "REVIEW")

    def test_invalid_execution_mode_rejected(self):
        with self.assertRaises(ValueError):
            audit("DEP_02", "support_bot", "Example", "live")

    def test_invalid_system_type_rejected(self):
        with self.assertRaises(ValueError):
            audit("DEP_02", "unknown_system", "Example")

    def test_wrong_output_type_rejected(self):
        with self.assertRaises(TypeError):
            audit("DEP_02", "payment_automation", "APPROVED")

    def test_replay_mode_is_identified(self):
        result = audit(
            "DEP_02",
            "support_bot",
            "Your deposit failed. The refund status is unknown. "
            "Please contact support.",
            execution_mode="replay",
        )
        self.assertEqual(result["execution_mode"], "replay")
        self.assertEqual(result["result"], "PASS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
