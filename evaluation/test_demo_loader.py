"""Regression tests for bundled synthetic demonstration evidence."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evaluation import demo_loader
from evaluation.demo_loader import load_bundled_examples


class DemoLoaderTests(unittest.TestCase):

    def test_bundled_examples_load_with_expected_outcomes(self):
        examples = load_bundled_examples()
        self.assertEqual(len(examples), 2)
        self.assertEqual(
            {r["evaluation"]["result"] for r in examples},
            {"PASS", "FAIL"},
        )
        self.assertTrue(all(
            r["evidence_origin"] == "bundled_example"
            for r in examples
        ))

    def test_modified_output_is_rejected(self):
        self.assert_rejects_change(
            lambda record: record.update(output="Tampered output")
        )

    def test_wrong_origin_is_rejected(self):
        self.assert_rejects_change(
            lambda record: record.update(evidence_origin="recorded_run")
        )

    def test_wrong_identifier_is_rejected(self):
        self.assert_rejects_change(
            lambda record: record.update(run_id="INCORRECT-ID")
        )

    def test_wrong_evidence_type_is_rejected(self):
        self.assert_rejects_change(
            lambda record: record.update(evidence_type="unknown")
        )

    def assert_rejects_change(self, change):
        source = demo_loader.DEMO_DIR / demo_loader.DEMO_FILES[0]
        record = json.loads(source.read_text(encoding="utf-8"))
        change(record)

        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / source.name
            destination.write_text(
                json.dumps(record, ensure_ascii=False),
                encoding="utf-8",
            )
            with patch.object(demo_loader, "DEMO_DIR", Path(temporary)):
                with patch.object(
                    demo_loader, "DEMO_FILES", (source.name,)
                ):
                    with self.assertRaises(ValueError):
                        load_bundled_examples()


if __name__ == "__main__":
    unittest.main()
