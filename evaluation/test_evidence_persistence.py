"""Evidence persistence and session-safe recorder regression tests."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evaluation import evidence_recorder
from evaluation.evidence_recorder import record_audit, verify_output_integrity


class EvidencePersistenceTests(unittest.TestCase):

    def test_nonpersistent_record_does_not_create_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "audit_records"
            with patch.object(evidence_recorder, "EVIDENCE_DIR", destination):
                evidence, path = record_audit(
                    "DEP_02",
                    "payment_automation",
                    {
                        "refund_status": "UNCONFIRMED",
                        "recommended_action": "REFER_TO_SUPPORT",
                    },
                    persist=False,
                )
                self.assertIsNone(path)
                self.assertFalse(destination.exists())
                self.assertEqual(evidence["evaluation"]["result"], "PASS")
                self.assertTrue(verify_output_integrity(evidence))
                self.assertEqual(len(evidence["observable_trace"]), 4)

    def test_default_recorder_still_persists_locally(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "audit_records"
            with patch.object(evidence_recorder, "EVIDENCE_DIR", destination):
                evidence, path = record_audit(
                    "DEP_02",
                    "payment_automation",
                    {
                        "refund_status": "APPROVED",
                        "recommended_action": "CONFIRM_REFUND",
                    },
                )
                self.assertEqual(path.parent, destination)
                self.assertTrue(path.is_file())
                self.assertEqual(evidence["evaluation"]["result"], "FAIL")
                self.assertTrue(verify_output_integrity(evidence))


if __name__ == "__main__":
    unittest.main()
