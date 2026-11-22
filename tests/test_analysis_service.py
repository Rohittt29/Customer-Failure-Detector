import json
import unittest
from unittest.mock import Mock

from analysis_service import AnalysisError, MAX_CONVERSATION_CHARS, analyze_conversation, parse_analysis, validate_conversation


class AnalysisValidationTests(unittest.TestCase):
    def setUp(self):
        self.transcript = "Agent: You have to wait.\nCustomer: This is frustrating."
        self.payload = dict(
            failure_point="The agent did not help", root_cause="Lack of ownership",
            customer_emotion="Frustrated", ideal_response="Let me investigate.", cx_score=7,
            evidence={"failure_point": ["You have to wait."], "root_cause": [],
                      "customer_emotion": ["This is frustrating."]},
            next_actions=["Investigate the issue", "Update the customer"],
        )

    def parse(self, payload):
        return parse_analysis(json.dumps(payload), self.transcript)

    def test_valid_result_and_export(self):
        result = self.parse(self.payload).to_dict()
        self.assertEqual(result["cx_score"], 7)
        self.assertEqual(result["evidence"]["failure_point"], ["You have to wait."])
        self.assertEqual(result["next_actions"], self.payload["next_actions"])

    def test_fabricated_quotes_are_not_presented_as_evidence(self):
        self.payload["evidence"]["failure_point"].append("I refuse to help")
        result = self.parse(self.payload)
        self.assertEqual(result.evidence["failure_point"], ["You have to wait."])
        self.assertEqual(result.evidence["root_cause"], [])

    def test_invalid_responses(self):
        for value in (None, True, -1, 11, "NaN", "Infinity"):
            with self.subTest(score=value), self.assertRaises(AnalysisError):
                self.parse({**self.payload, "cx_score": value})
        for field, value in (("root_cause", ""), ("evidence", {}), ("next_actions", []),
                             ("next_actions", ["valid", 2])):
            with self.subTest(field=field), self.assertRaises(AnalysisError):
                self.parse({**self.payload, field: value})
        for text in ("not json", "[]", "null"):
            with self.subTest(text=text), self.assertRaises(AnalysisError):
                parse_analysis(text, self.transcript)

    def test_request_to_result_with_mocked_provider(self):
        client = Mock()
        client.models.generate_content.return_value.text = json.dumps(self.payload)
        result = analyze_conversation("test-key", self.transcript, client=client)
        self.assertEqual(result.next_actions[0], "Investigate the issue")
        self.assertIn(self.transcript, client.models.generate_content.call_args.kwargs["contents"])

    def test_conversation_bounds(self):
        self.assertEqual(validate_conversation("  hello  "), "hello")
        for text in ("  ", "x" * (MAX_CONVERSATION_CHARS + 1)):
            with self.assertRaises(AnalysisError):
                validate_conversation(text)


if __name__ == "__main__":
    unittest.main()
