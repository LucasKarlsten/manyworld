"""No-network tests for the first Five Lives LLM smoke test."""
import unittest

from scripts.smoke_sweden_persona_llm import decode_decision, load_persona


class PersonaSmokeTests(unittest.TestCase):
    def test_marcus_loads(self):
        self.assertEqual(load_persona("marcus")["age"], 29)

    def test_valid_response(self):
        self.assertEqual(
            decode_decision('{"action":"search_job","explanation":"Jag söker jobb."}')["action"],
            "search_job",
        )

    def test_reject_unknown_action(self):
        with self.assertRaises(ValueError):
            decode_decision('{"action":"invent_money","explanation":"Jag hittar pengar."}')

    def test_reject_extra_fields(self):
        with self.assertRaises(ValueError):
            decode_decision('{"action":"wait","explanation":"Jag väntar.","chain_of_thought":"secret"}')


if __name__ == "__main__":
    unittest.main()
