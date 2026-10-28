"""Validate the editable Five Lives design contract (no simulator integration yet)."""
import json
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "scenarios/sweden-ubi/personas.v1.json"


class FiveLivesBaselineTests(unittest.TestCase):
    def test_baseline_has_five_unique_personas(self):
        data = json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(len(data["personas"]), 5)
        ids = [p["id"] for p in data["personas"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {"marcus", "sara", "johan", "helena", "alexander"})

    def test_personas_are_non_prescriptive(self):
        data = json.loads(PATH.read_text(encoding="utf-8"))
        self.assertEqual(data["experiment"]["intervention_tick"], 5)
        for persona in data["personas"]:
            self.assertGreaterEqual(persona["age"], 18)
            self.assertTrue(persona["goals"])
            self.assertTrue(persona["candidate_actions"])
            self.assertTrue(persona["decision_tensions"])
            self.assertEqual(persona["economic_state"], "MUST_BE_BACKED_BY_ENGINE_DATA")


if __name__ == "__main__":
    unittest.main()
