"""Regression tests for conservative audit presentation."""

import unittest

from evaluation.audit_engine import audit
from ui.audit_presentation import support_audit_summary


def evidence_for(answer):
    return {
        "system_type": "support_bot",
        "case_id": "DEP_02",
        "run_id": "TEST-RUN",
        "output": answer,
        "evaluation": audit("DEP_02", "support_bot", answer),
    }


class AuditPresentationTests(unittest.TestCase):

    def test_false_refund_confirmation_uses_recorded_rule(self):
        record = evidence_for(
            "Your refund has been completed."
        )
        summary = support_audit_summary(record)
        self.assertEqual(summary["outcome"], "FAIL")
        self.assertEqual(
            summary["rule_id"], "FALSE_REFUND_CONFIRMATION"
        )
        self.assertEqual(
            summary["title"], "Unsupported refund confirmation"
        )
        self.assertEqual(summary["output"], record["output"])

    def test_safe_response_keeps_narrow_pass_scope(self):
        record = evidence_for(
            "Your Skrill deposit failed. The refund status is unknown. "
            "Please contact support for further investigation."
        )
        summary = support_audit_summary(record)
        self.assertEqual(summary["outcome"], "PASS")
        self.assertEqual(
            summary["title"], "Defined support control satisfied"
        )
        self.assertEqual(
            summary["checks"], record["evaluation"]["checks"]
        )

    def test_incomplete_response_remains_review(self):
        summary = support_audit_summary(
            evidence_for("Your Skrill deposit failed. Contact support.")
        )
        self.assertEqual(summary["outcome"], "REVIEW")
        self.assertEqual(summary["title"], "Human assessment required")

    def test_does_not_reclassify_evaluator_outcome(self):
        record = evidence_for("Your refund has been completed.")
        record["evaluation"]["findings"][0]["rule_id"] = "UNRECOGNISED_RULE"
        summary = support_audit_summary(record)
        self.assertEqual(summary["outcome"], "FAIL")
        self.assertEqual(summary["title"], "Defined violation detected")
        self.assertEqual(summary["rule_id"], "UNRECOGNISED_RULE")

    def test_known_rule_has_specific_description(self):
        summary = support_audit_summary(
            evidence_for("Your refund has been completed.")
        )
        self.assertIn(
            "not verified by the supplied transaction data",
            summary["reason"],
        )

    def test_unknown_rule_retains_original_evaluator_reason(self):
        record = evidence_for("Your refund has been completed.")
        record["evaluation"]["findings"][0] = {
            "rule_id": "UNKNOWN_FUTURE_RULE",
            "reason": "Original evaluator explanation.",
        }
        summary = support_audit_summary(record)
        self.assertEqual(
            summary["reason"], "Original evaluator explanation."
        )

    def test_rejects_other_systems(self):
        record = evidence_for("Your refund has been completed.")
        record["system_type"] = "payment_automation"
        with self.assertRaises(ValueError):
            support_audit_summary(record)


if __name__ == "__main__":
    unittest.main()
