"""Regression tests for recorded output integrity."""

import copy
import unittest

from evaluation.evidence_recorder import (
    calculate_output_hash,
    verify_output_integrity,
)


class EvidenceIntegrityTests(unittest.TestCase):

    def setUp(self):
        self.output = {
            "refund_status": "UNCONFIRMED",
            "recommended_action": "REFER_TO_SUPPORT",
            "notes": "Älä confirm a refund without evidence.",
        }
        self.evidence = {
            "output": copy.deepcopy(self.output),
            "output_sha256": calculate_output_hash(self.output),
        }

    def test_original_output_verifies(self):
        self.assertTrue(verify_output_integrity(self.evidence))

    def test_modified_output_fails(self):
        changed = copy.deepcopy(self.evidence)
        changed["output"]["refund_status"] = "APPROVED"
        self.assertFalse(verify_output_integrity(changed))

    def test_missing_output_fails(self):
        self.assertFalse(verify_output_integrity({
            "output_sha256": self.evidence["output_sha256"]
        }))

    def test_missing_or_invalid_hash_fails(self):
        self.assertFalse(verify_output_integrity({"output": self.output}))
        changed = copy.deepcopy(self.evidence)
        changed["output_sha256"] = "invalid"
        self.assertFalse(verify_output_integrity(changed))

    def test_verification_does_not_mutate_evidence(self):
        before = copy.deepcopy(self.evidence)
        verify_output_integrity(self.evidence)
        self.assertEqual(self.evidence, before)

    def test_key_order_does_not_change_canonical_hash(self):
        reordered = dict(reversed(list(self.output.items())))
        self.assertEqual(
            calculate_output_hash(self.output),
            calculate_output_hash(reordered),
        )


if __name__ == "__main__":
    unittest.main()
