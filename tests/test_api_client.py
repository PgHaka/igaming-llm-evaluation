"""Offline API-client tests: no network access or API spending."""

import unittest
from unittest.mock import Mock, patch

from simulation.api_client import request_model_response


class TestAPIClient(unittest.TestCase):

    def setUp(self):
        self.arguments = {
            "api_key": "synthetic-test-key",
            "model": "test-model",
            "system_instruction": "Follow verified evidence.",
            "customer_message": "Was my deposit refunded?",
            "verified_context": '{"refund_status": "unknown"}',
            "max_output_tokens": 250,
        }

    @patch("simulation.api_client.requests.post")
    def test_response_and_usage_are_recorded(self, post):
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "id": "resp_synthetic_001",
            "model": "test-model-version",
            "status": "completed",
            "output": [{
                "type": "message",
                "content": [{
                    "type": "output_text",
                    "text": "The available record does not confirm a refund."
                }],
            }],
            "usage": {
                "input_tokens": 150,
                "output_tokens": 18,
                "total_tokens": 168,
            },
        }
        post.return_value = response

        result = request_model_response(**self.arguments)

        self.assertEqual(result["response_id"], "resp_synthetic_001")
        self.assertEqual(result["input_tokens"], 150)
        self.assertEqual(result["output_tokens"], 18)
        self.assertIn("does not confirm", result["answer"])

        payload = post.call_args.kwargs["json"]
        self.assertIs(payload["store"], False)
        self.assertEqual(payload["max_output_tokens"], 250)
        self.assertEqual(post.call_count, 1)

    @patch("simulation.api_client.requests.post")
    def test_missing_key_prevents_request(self, post):
        arguments = dict(self.arguments, api_key="")
        with self.assertRaises(ValueError):
            request_model_response(**arguments)
        post.assert_not_called()

    @patch("simulation.api_client.requests.post")
    def test_http_error_does_not_expose_secret(self, post):
        response = Mock()
        response.ok = False
        response.status_code = 401
        post.return_value = response

        with self.assertRaises(RuntimeError) as error:
            request_model_response(**self.arguments)

        self.assertNotIn("synthetic-test-key", str(error.exception))
        self.assertIn("401", str(error.exception))


if __name__ == "__main__":
    unittest.main()
