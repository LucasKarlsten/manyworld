"""Configuration regression checks for Sweden baseline and UBI treatment.

Run: python3 -m unittest discover -s tests -p 'test_sweden_ubi_config.py' -v
"""
import unittest
from run_config import load_config


class SwedenUBIConfigTests(unittest.TestCase):
    def test_baseline_and_treatment_differ_only_in_ubi_policy(self):
        baseline = load_config("runs/sweden-baseline.yaml")
        treated = load_config("runs/sweden-ubi.yaml")
        self.assertEqual(baseline["seed"], treated["seed"])
        self.assertEqual(baseline["engine_semantics_version"],
                         treated["engine_semantics_version"])
        self.assertEqual(baseline["firms"], treated["firms"])
        self.assertEqual(baseline["population"], treated["population"])
        self.assertEqual(baseline["supply_recovery"],
                         treated["supply_recovery"])
        self.assertEqual(baseline["llm"], treated["llm"])
        gov_a, gov_b = baseline["government"], treated["government"]
        for key in gov_a.keys() | gov_b.keys():
            if key not in {"ubi_enabled", "ubi_amount_cents"}:
                self.assertEqual(gov_a.get(key), gov_b.get(key), key)
        self.assertFalse(gov_a["ubi_enabled"])
        self.assertTrue(gov_b["ubi_enabled"])
        self.assertEqual(gov_b["ubi_amount_cents"], 1_500_000)
        self.assertEqual(gov_a["election_interval_ticks"], 0)

    def test_no_paid_models_configured(self):
        for path in ("runs/sweden-baseline.yaml", "runs/sweden-ubi.yaml"):
            config = load_config(path)
            llm = config["llm"]
            self.assertEqual(llm["default_route"]["provider"], "scripted")
            self.assertFalse(llm.get("routes"))


if __name__ == "__main__":
    unittest.main()
