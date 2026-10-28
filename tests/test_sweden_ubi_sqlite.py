"""SQLite integration tests for the experimental UBI fiscal layer.

Unlike test_sweden_ubi.py, these use Manyworld's actual Store, Ledger,
schema, events and transactions. No external model calls or world simulation.
Run: python3 -m unittest discover -s tests -p 'test_sweden_ubi_sqlite.py' -v
"""
import tempfile
import unittest
from pathlib import Path

from engine.government import Government
from engine.ledger import Ledger, SYS_GOV
from engine.store import Store


class TestSwedenUBISQLite(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(str(Path(self.tmp.name) / "ubi.sqlite3"))
        self.ledger = Ledger(self.store)
        self.citizens = {}
        for name, age in (("Minor", 17), ("Worker", 31), ("Retiree", 67)):
            agent = self.store.insert(
                "agents", name=name, kind="citizen", age=age, alive=1,
                retired=int(age >= 65))
            checking = self.ledger.create_account(
                "agent", agent, "checking", label=f"{name}:checking",
                currency_code="USD")
            self.store.execute(
                "UPDATE agents SET checking_account_id=? WHERE id=?",
                (checking, agent))
            self.citizens[name] = (agent, checking)
        self.gov = Government(self.store, self.ledger, {
            "tax_rate_bps": 3000,
            "unemployment_benefit_cents": 0,
            "election_interval_ticks": 0,
            "ubi_enabled": True,
            "ubi_amount_cents": 1_500_000,
            "ubi_first_tick": 30,
            "ubi_interval_ticks": 30,
            "ubi_min_age": 18,
            "ubi_max_age": 120,
        }, engine_semantics_version=20)
        self.gov.initialize()

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def balance(self, name):
        return self.ledger.balance(self.citizens[name][1])

    def test_real_ledger_cadence_idempotency_and_audit_trail(self):
        self.gov.run_nightly(29)
        self.assertEqual(self.store.scalar(
            "SELECT COUNT(*) FROM transactions WHERE kind='ubi_payment'"), 0)
        self.gov.run_nightly(30)
        self.gov.run_nightly(30)  # retry must not double-pay
        self.assertEqual(self.balance("Minor"), 0)
        self.assertEqual(self.balance("Worker"), 1_500_000)
        self.assertEqual(self.balance("Retiree"), 1_500_000)
        self.assertEqual(self.store.scalar(
            "SELECT COUNT(*) FROM transactions WHERE kind='ubi_payment'"), 2)
        self.assertEqual(self.store.scalar(
            "SELECT COUNT(*) FROM events WHERE kind='ubi_paid'"), 2)
        self.assertEqual(self.store.scalar(
            "SELECT balance_cents FROM accounts WHERE label=?",
            (SYS_GOV,)), -3_000_000)
        ok, diagnostics = self.ledger.reconcile()
        self.assertTrue(ok, diagnostics)
        self.gov.run_nightly(60)
        self.assertEqual(self.balance("Worker"), 3_000_000)
        self.assertEqual(self.store.scalar(
            "SELECT COUNT(*) FROM transactions WHERE kind='ubi_payment'"), 4)
        ok, diagnostics = self.ledger.reconcile()
        self.assertTrue(ok, diagnostics)

    def test_disabled_is_zero_ledger_mutation(self):
        self.gov.p["ubi_enabled"] = False
        self.gov.run_nightly(30)
        self.assertEqual(self.store.scalar(
            "SELECT COUNT(*) FROM transactions WHERE kind='ubi_payment'"), 0)
        self.assertEqual(self.store.scalar(
            "SELECT COUNT(*) FROM events WHERE kind='ubi_paid'"), 0)
        ok, diagnostics = self.ledger.reconcile()
        self.assertTrue(ok, diagnostics)


if __name__ == "__main__":
    unittest.main()
