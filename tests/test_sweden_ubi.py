"""Fast isolated regression tests for optional Sweden UBI fiscal payments.

Run: python -m unittest discover -s tests -p 'test_sweden_ubi.py' -v

Uses lightweight fiscal/ledger doubles; a full-world end-to-end test is still
required before claiming that the UBI experiment is validated.
"""
from __future__ import annotations

import unittest
from contextlib import nullcontext
from unittest.mock import Mock

from engine.government import Government


class FiscalStore:
    def __init__(self, ages):
        self.ages = dict(ages)
        self.paid = set()
        self.events = []
        self.balances = {100 + aid: 0 for aid in ages}
        self.balances[900] = 0

    def query(self, sql, params=()):
        if "FROM agents" in sql:
            lo, hi = params
            return [{"id": aid} for aid, age in sorted(self.ages.items())
                    if lo <= age <= hi]
        raise AssertionError(f"unexpected query: {sql}")

    def scalar(self, sql, params=(), default=None):
        if "FROM transactions" in sql:
            return 1 if params[0] in self.paid else None
        if "currency_code" in sql:
            return "USD"
        if "SUM(balance_cents)" in sql:
            return self.balances[900]
        raise AssertionError(f"unexpected scalar: {sql}")

    def savepoint(self, name):
        return nullcontext()

    def log_event(self, tick, kind, data, **kwargs):
        self.events.append((tick, kind, data))


class FiscalLedger:
    def __init__(self, store):
        self.store = store
        self.payments = []

    def agent_checking_id(self, agent_id):
        return 100 + agent_id

    def system_account(self, label, *, currency_code):
        self.currency = currency_code
        return 900

    def post(self, tick, kind, legs, memo=""):
        assert kind == "ubi_payment"
        assert sum(leg.delta_cents for leg in legs) == 0
        if memo in self.store.paid:
            raise AssertionError("duplicate payment")
        self.store.paid.add(memo)
        for leg in legs:
            self.store.balances[leg.account_id] += leg.delta_cents
        self.payments.append((tick, memo, legs))


class SwedenUBITests(unittest.TestCase):
    def make_gov(self, ages=None, **params):
        store = FiscalStore(ages or {1: 17, 2: 18, 3: 39, 4: 65})
        ledger = FiscalLedger(store)
        cfg = {
            "ubi_enabled": True,
            "ubi_amount_cents": 1_500_000,
            "ubi_first_tick": 30,
            "ubi_interval_ticks": 30,
            "ubi_min_age": 18,
            "ubi_max_age": 120,
            "election_interval_ticks": 0,
            "unemployment_benefit_cents": 0,
        }
        cfg.update(params)
        gov = Government(store, ledger, cfg, engine_semantics_version=20)
        return gov, store, ledger

    def test_disabled_is_noop(self):
        gov, store, ledger = self.make_gov(ubi_enabled=False)
        gov.run_nightly(30)
        self.assertEqual(ledger.payments, [])
        self.assertEqual(store.balances[900], 0)

    def test_age_eligibility_and_balanced_transfers(self):
        gov, store, ledger = self.make_gov()
        gov.run_nightly(30)
        self.assertEqual(len(ledger.payments), 3)
        self.assertEqual(store.balances[101], 0)  # minor
        for aid in (2, 3, 4):
            self.assertEqual(store.balances[100 + aid], 1_500_000)
        self.assertEqual(store.balances[900], -4_500_000)
        self.assertEqual(sum(store.balances.values()), 0)

    def test_payment_cadence_and_retry_idempotency(self):
        gov, store, ledger = self.make_gov(ages={1: 30})
        for tick in (1, 29, 30, 30, 31, 59, 60, 60, 61):
            gov.run_nightly(tick)
        self.assertEqual([row[0] for row in ledger.payments], [30, 60])
        self.assertEqual(store.balances[101], 3_000_000)
        self.assertEqual(store.balances[900], -3_000_000)

    def test_zero_amount_does_not_post(self):
        gov, store, ledger = self.make_gov(ubi_amount_cents=0)
        gov.run_nightly(30)
        self.assertFalse(ledger.payments)

    def test_negative_amount_rejected(self):
        gov, _, _ = self.make_gov(ubi_amount_cents=-1)
        with self.assertRaises(ValueError):
            gov.run_nightly(30)

    def test_locality_filter_excludes_nonresident(self):
        gov, store, ledger = self.make_gov(ages={1: 30, 2: 30})
        gov._is_local = Mock(side_effect=lambda aid, tick: aid == 1)
        gov.run_nightly(30)
        self.assertEqual(len(ledger.payments), 1)
        self.assertEqual(store.balances[101], 1_500_000)
        self.assertEqual(store.balances[102], 0)


if __name__ == "__main__":
    unittest.main()
