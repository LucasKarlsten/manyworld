"""Fast, database-free tests for the read-only Sweden UBI comparator."""
import unittest

from scripts.compare_sweden_ubi import METRICS, compare


def sample(seed=1, tick=60, sales=100, ubi=0):
    return {
        "run": "sample", "seed": seed, "tick": tick,
        "engine_semantics": 20, "currencies": ["USD"],
        "ubi_total": ubi, "goods_sales": sales,
        "active_employment_contracts": 9,
        "metrics_at_end": {k: 0.0 for k in METRICS},
    }


class ComparatorTests(unittest.TestCase):
    def test_deltas_are_treatment_minus_control(self):
        result = compare(sample(), sample(sales=140, ubi=420000))
        self.assertEqual(result["difference_ubi_minus_control"]["goods_sales"], 40)
        self.assertEqual(result["difference_ubi_minus_control"]["ubi_total"], 420000)

    def test_rejects_different_seed(self):
        with self.assertRaisesRegex(ValueError, "Seeds differ"):
            compare(sample(seed=1), sample(seed=2))

    def test_rejects_different_horizon(self):
        with self.assertRaisesRegex(ValueError, "horizons"):
            compare(sample(tick=30), sample(tick=60))

    def test_missing_metric_is_not_zero(self):
        b = sample()
        b["metrics_at_end"]["unemployment"] = None
        result = compare(sample(), b)
        self.assertIsNone(
            result["difference_ubi_minus_control"]["metrics_at_end"]["unemployment"]
        )


if __name__ == "__main__":
    unittest.main()
