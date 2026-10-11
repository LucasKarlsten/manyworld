"""Inventory-aware scale recovery keeps the diagnostic control immutable."""
from copy import deepcopy
from pathlib import Path

import pytest

from agents.memory import Memory
from agents.policies import citizen_decision
from agents.prompts import ContextBuilder
from engine.actions import ActionExecutor
from reports.scale_economic_health import PROFILE_CONTRACTS
from run_config import load_config
from tests.conftest import make_agent, make_bank


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("ticks", [120, 1000])
def test_inventory_recovery_profile_changes_only_explicit_shopping_policy(ticks):
    original = load_config(ROOT / f"runs/acceptance/scale-270-recovery-{ticks}.yaml")
    path = f"runs/acceptance/scale-270-recovery-inventory-{ticks}.yaml"
    repaired = load_config(ROOT / path)
    expected = deepcopy(original)
    expected.setdefault("behavior", {})["inventory_aware_shopping"] = True
    assert repaired == expected
    assert not original.get("behavior", {}).get("inventory_aware_shopping", False)
    assert PROFILE_CONTRACTS[path] == {
        "required_ticks": ticks, "diagnostic": ticks == 120, "recovery_enabled": True,
    }


@pytest.mark.parametrize("enabled,accepted", [(False, 3), (True, 8)])
def test_shared_snapshot_quantity_guidance_prevents_early_buyers_exhausting_stock(
    economy, enabled, accepted,
):
    profile = "scale-270-recovery-inventory-120" if enabled else "scale-270-recovery-120"
    config = load_config(ROOT / f"runs/acceptance/{profile}.yaml")
    economy.config.update(config)
    bank = make_bank(economy, reserves=100_000_000)
    actors = [make_agent(economy, bank, name=f"Shopper {n}", cash=100_000,
                         population_tier="core" if n % 2 else "periphery")[0]
              for n in range(8)]
    firm = economy.firms.found_firm(
        0, actors[0], "Finite Stock", "retail",
        product={"product": "retail_good", "unit_price_cents": 500,
                 "base_input_cost_cents": 200, "output_per_worker": 5},
        opening_capital_cents=10_000,
    )
    economy.store.update("firms", firm, inventory=20)
    builder = ContextBuilder(economy, Memory(economy.store), config)
    contexts = [builder._citizen_context(economy.store.query_one(
        "SELECT * FROM agents WHERE id=?", (actor,)), 1, retrieve_memories=False)
        for actor in actors]
    executor = ActionExecutor(economy)
    before = economy.ledger.balance(economy.store.scalar(
        "SELECT account_id FROM firms WHERE id=?", (firm,)))
    for actor, context in zip(actors, contexts):
        actions = [a for a in citizen_decision(context)["actions"] if a["type"] == "buy_goods"]
        assert len(actions) == 1
        assert actions[0]["qty"] == (2 if enabled else 8)
        executor.execute_actions(1, actor, actions)
    statuses = dict(economy.store.query(
        "SELECT validation_status,COUNT(*) FROM action_proposals GROUP BY validation_status"))
    assert statuses.get("accepted", 0) == accepted
    assert statuses.get("rejected", 0) == 8 - accepted
    sold = 16 if enabled else 20
    assert economy.store.scalar("SELECT inventory FROM firms WHERE id=?", (firm,)) == 20 - sold
    assert economy.ledger.balance(economy.store.scalar(
        "SELECT account_id FROM firms WHERE id=?", (firm,))) - before == sold * 500
    assert economy.ledger.reconcile()[0]
