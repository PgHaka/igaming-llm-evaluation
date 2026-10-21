"""Regression tests for synthetic offline audit reporting."""

import unittest

from evaluation.audit_report import generate_audit_report


def fixture(run_id, system, result, finding=None):
    return {
        "run_id": run_id,
        "system_type": system,
        "execution_mode": "control",
        "output_sha256": "a" * 64,
        "evaluation": {
            "result": result,
            "findings": (
                [{"rule_id": finding, "reason": "Synthetic test finding"}]
                if finding else []
            ),
        },
    }


class AuditReportTests(unittest.TestCase):

    def test_empty_evidence_is_reportable(self):
        report = generate_audit_report([])
        self.assertIn("| **Total** | **0** |", report)
        self.assertIn("No findings recorded.", report)

    def test_outcomes_and_systems_remain_separate(self):
        report = generate_audit_report([
            fixture("AUD-001", "support_bot", "PASS"),
            fixture("AUD-002", "support_bot", "FAIL", "FALSE_REFUND_CONFIRMATION"),
            fixture("AUD-003", "payment_automation", "REVIEW", "UNREVIEWED_AUTOMATION_FIELDS"),
        ])
        self.assertIn("| **Total** | **3** |", report)
        self.assertIn("| support_bot | 2 | 1 | 1 | 0 |", report)
        self.assertIn("| payment_automation | 1 | 0 | 0 | 1 |", report)
        self.assertIn("| FALSE_REFUND_CONFIRMATION | 1 |", report)
        self.assertIn("| UNREVIEWED_AUTOMATION_FIELDS | 1 |", report)

    def test_evidence_register_contains_identifiers_and_hashes(self):
        report = generate_audit_report([
            fixture("AUD-TEST-001", "support_bot", "PASS"),
        ])
        self.assertIn("AUD-TEST-001", report)
        self.assertIn("a" * 64, report)

    def test_bundled_examples_are_identified_separately(self):
        bundled = fixture("DEMO-001", "support_bot", "FAIL")
        bundled["evidence_origin"] = "bundled_example"
        recorded = fixture("AUD-001", "payment_automation", "PASS")

        report = generate_audit_report([bundled, recorded])

        self.assertIn("| Recorded audit runs | 1 |", report)
        self.assertIn("| Bundled synthetic examples | 1 |", report)
        self.assertIn("| **Total** | **2** |", report)
        self.assertIn("| DEMO-001 | bundled_example |", report)
        self.assertIn("| AUD-001 | recorded_run |", report)
        self.assertIn("not visitor-generated audit runs", report)

    def test_unknown_origin_is_rejected(self):
        record = fixture("UNKNOWN-001", "support_bot", "PASS")
        record["evidence_origin"] = "unverified_external"
        with self.assertRaises(ValueError):
            generate_audit_report([record])

    def test_limitations_are_explicit(self):
        report = generate_audit_report([])
        self.assertIn("not independent model-performance observations", report)
        self.assertIn("does not verify provenance", report)
        self.assertIn("does not establish production reliability", report)
        self.assertIn("Historical human-reviewed model results are excluded", report)


if __name__ == "__main__":
    unittest.main()
