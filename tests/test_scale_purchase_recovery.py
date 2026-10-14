"""Inventory-aware scale recovery keeps the diagnostic control immutable."""
from copy import deepcopy
import asyncio
import hashlib
import json
from pathlib import Path

import pytest

from agents.memory import Memory
from agents.policies import citizen_decision
from agents.prompts import ContextBuilder
from engine.actions import ActionExecutor
from engine.checkpoint_manifest import finalize_sqlite_artifact
from reports.scale_economic_health import PROFILE_CONTRACTS
from run import open_run, replay_headless
from run_config import load_config
from tests.conftest import make_agent, make_bank
from world.replay_verify import verify_replay


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("ticks", [120, 1000])
def test_inventory_recovery_profile_changes_only_explicit_shopping_policy(ticks):
    original = load_config(ROOT / f"runs/acceptance/scale-270-recovery-{ticks}.yaml")
    path = f"runs/acceptance/scale-270-recovery-inventory-{ticks}.yaml"
    repaired = load_config(ROOT / path)
    expected = deepcopy(original)
    expected.setdefault("behavior", {}).update({
        "inventory_aware_shopping_activation_tick": 60,
        "inventory_aware_shopping_include_staff": True,
        "inventory_aware_shopping_reserve_bps": 2000,
    })
    assert repaired == expected
    assert not original.get("behavior", {}).get("inventory_aware_shopping", False)
    assert PROFILE_CONTRACTS[path] == {
        "required_ticks": ticks, "diagnostic": ticks == 120, "recovery_enabled": True,
    }


@pytest.mark.parametrize("enabled,tick,accepted", [
    (False, 1, 3), (True, 59, 3), (True, 60, 8),
])
def test_shared_snapshot_quantity_guidance_prevents_early_buyers_exhausting_stock(
    economy, enabled, tick, accepted,
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
        "SELECT * FROM agents WHERE id=?", (actor,)), tick, retrieve_memories=False)
        for actor in actors]
    executor = ActionExecutor(economy)
    before = economy.ledger.balance(economy.store.scalar(
        "SELECT account_id FROM firms WHERE id=?", (firm,)))
    for actor, context in zip(actors, contexts):
        actions = [a for a in citizen_decision(context)["actions"] if a["type"] == "buy_goods"]
        assert len(actions) == 1
        active = enabled and tick >= 60
        assert bool(context.get("inventory_aware_shopping_enabled")) == active
        assert actions[0]["qty"] == (2 if active else 8)
        executor.execute_actions(tick, actor, actions)
    statuses = dict(economy.store.query(
        "SELECT validation_status,COUNT(*) FROM action_proposals GROUP BY validation_status"))
    assert statuses.get("accepted", 0) == accepted
    assert statuses.get("rejected", 0) == 8 - accepted
    sold = 16 if enabled and tick >= 60 else 20
    assert economy.store.scalar("SELECT inventory FROM firms WHERE id=?", (firm,)) == 20 - sold
    assert economy.ledger.balance(economy.store.scalar(
        "SELECT account_id FROM firms WHERE id=?", (firm,))) - before == sold * 500
    assert economy.ledger.reconcile()[0]


@pytest.mark.parametrize("cached", [False, True])
@pytest.mark.parametrize("include_staff,reserve_bps,qty,accepted,remaining", [
    (False, 0, 6, 4, 0),
    (True, 0, 4, 6, 0),
    (False, 2000, 4, 6, 0),
    (True, 2000, 3, 6, 6),
    (True, 9999, 1, 6, 18),
])
def test_stock_guidance_accounts_for_staff_consumption_and_shared_snapshot_headroom(
    economy, cached, include_staff, reserve_bps, qty, accepted, remaining,
):
    config = load_config(ROOT / "runs/acceptance/scale-270-recovery-120.yaml")
    config.setdefault("behavior", {}).update({
        "inventory_aware_shopping_activation_tick": 60,
        "inventory_aware_shopping_include_staff": include_staff,
        "inventory_aware_shopping_reserve_bps": reserve_bps,
    })
    economy.config.update(config)
    bank = make_bank(economy, reserves=100_000_000)
    actors = [make_agent(
        economy, bank, name=f"Citizen {i}", cash=100_000,
        population_tier="core" if i % 2 else "periphery",
    )[0] for i in range(4)]
    actors += [make_agent(
        economy, bank, name=f"Staff {i}", cash=100_000,
        kind="staff", population_tier="core",
    )[0] for i in range(2)]
    make_agent(economy, bank, name="Critical staff", kind="staff", health="critical")
    dead, _ = make_agent(economy, bank, name="Deceased staff", kind="staff")
    economy.store.update("agents", dead, alive=0)
    firm = economy.firms.found_firm(
        0, actors[0], "Shared Stock", "retail",
        product={"product": "retail_good", "unit_price_cents": 500,
                 "base_input_cost_cents": 200, "output_per_worker": 5},
        opening_capital_cents=10_000,
    )
    economy.store.update("firms", firm, inventory=24)
    builder = ContextBuilder(economy, Memory(economy.store), config)
    if cached:
        builder.prepare_decision_cohort(economy.store.query("SELECT * FROM agents ORDER BY id"), 60)
    contexts = [builder._citizen_context(economy.store.query_one(
        "SELECT * FROM agents WHERE id=?", (actor,)), 60, retrieve_memories=False)
        for actor in actors]
    account = economy.store.scalar("SELECT account_id FROM firms WHERE id=?", (firm,))
    before = economy.ledger.balance(account)
    executor = ActionExecutor(economy)
    for actor, context in zip(actors, contexts):
        assert context["shopping_qty_cap"] == qty
        purchase, = [action for action in citizen_decision(context)["actions"]
                     if action["type"] == "buy_goods"]
        assert purchase["qty"] == qty
        executor.execute_actions(60, actor, [purchase])
    statuses = dict(economy.store.query(
        "SELECT validation_status,COUNT(*) FROM action_proposals GROUP BY validation_status"))
    assert statuses.get("accepted", 0) == accepted
    assert statuses.get("rejected", 0) == len(actors) - accepted
    assert economy.store.scalar("SELECT inventory FROM firms WHERE id=?", (firm,)) == remaining
    assert economy.ledger.balance(account) - before == (24 - remaining) * 500
    assert economy.ledger.reconcile()[0]


@pytest.mark.parametrize("cached", [False, True])
def test_staff_guidance_keeps_shoppers_and_stock_in_the_same_region(tmp_path, cached):
    config = load_config(ROOT / "runs/acceptance/scale-270-recovery-inventory-120.yaml")
    # Declared component fixture: all healthy residents and staff are awake.
    config["population"]["size"] = 12
    config["living_world"]["core_agents"] = 20
    for region, population in zip(config["living_world"]["regions"], [42, 4, 4]):
        region["population"] = population
    config["checkpoint_dir"] = str(tmp_path / "checkpoints")
    config["report_dir"] = str(tmp_path / "reports")
    store, world, _ = open_run(config, None, None, data_dir=tmp_path / "source")
    try:
        cohort = store.query("SELECT * FROM agents WHERE alive=1 AND health<>'critical' ORDER BY id")
        actor = next(row for row in cohort if row["kind"] == "citizen" and row["region_id"] == 1)
        local = [row for row in cohort if row["region_id"] == actor["region_id"]]
        assert any(row["kind"] == "staff" for row in local)
        assert len(local) < len(cohort)
        currency = store.scalar("SELECT currency_code FROM accounts WHERE id=?", (actor["checking_account_id"],))
        firms = store.query("SELECT * FROM firms WHERE json_extract(product_json,'$.output_per_worker')>0 ORDER BY id")
        seller = next(row for row in firms if row["currency_code"] == currency)
        stock = len(local) * 5
        for firm in firms:
            inventory = stock if firm["id"] == seller["id"] else (
                100_000 if firm["currency_code"] != currency else 0)
            store.update("firms", firm["id"], inventory=inventory)
        builder = ContextBuilder(world.economy, world.runtime.mem, config)
        if cached:
            builder.prepare_decision_cohort(cohort, 60)
        context = builder._citizen_context(actor, 60, retrieve_memories=False, read_only=True)
        assert sum(offer["inventory"] for offer in context["prices"]) == stock
        assert all(offer["currency_code"] == currency for offer in context["prices"])
        assert context["shopping_qty_cap"] == 4
        assert world.economy.ledger.reconcile()[0]
    finally:
        world.close()


@pytest.mark.parametrize("reserve", [-1, 10000, 2000.5, "2000", True, None])
def test_inventory_guidance_rejects_invalid_reserve(economy, reserve):
    config = {"behavior": {"inventory_aware_shopping_reserve_bps": reserve}}
    with pytest.raises(ValueError, match="inventory_aware_shopping_reserve_bps"):
        ContextBuilder(economy, Memory(economy.store), config)


@pytest.mark.parametrize("value", ["false", 1, None])
def test_inventory_guidance_requires_explicit_staff_boolean(economy, value):
    config = {"behavior": {"inventory_aware_shopping_include_staff": value}}
    with pytest.raises(ValueError, match="inventory_aware_shopping_include_staff"):
        ContextBuilder(economy, Memory(economy.store), config)


def test_inventory_activation_cutover_replays_exactly_without_changing_source(tmp_path):
    config = load_config(ROOT / "runs/acceptance/scale-270-recovery-inventory-120.yaml")
    # Declared component fixture: compress the cutover to tick 2 and population
    # to 50 agents. The separate profile regression pins the real tick-60 lane.
    config["population"]["size"] = 12
    config["living_world"]["core_agents"] = 20
    config["behavior"]["inventory_aware_shopping_activation_tick"] = 2
    config["behavior"]["act_every"] = 1
    config["budget"]["conversation_pairs"] = 0
    source_root, replay_root = tmp_path / "source", tmp_path / "replay"
    config["checkpoint_dir"] = str(source_root / "checkpoints")
    config["report_dir"] = str(source_root / "reports")
    store, world, run_id = open_run(config, None, None, data_dir=source_root)
    source = Path(store.path)
    try:
        for _ in range(3):
            asyncio.run(world.step())
        contexts = [json.loads(row["request_json"])["context"] for row in store.query(
            "SELECT request_json FROM llm_calls WHERE purpose IN ('decision','founder')")]
        assert any(c["tick"] == 1 for c in contexts)
        assert any(c["tick"] == 2 for c in contexts)
        for context in contexts:
            assert bool(context.get("inventory_aware_shopping_enabled")) == (context["tick"] >= 2)
        assert store.scalar("SELECT COUNT(*) FROM agents WHERE population_tier='periphery'") > 0
        assert world.economy.ledger.reconcile()[0]
    finally:
        world.close()
    finalize_sqlite_artifact(source)
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    replay_store, replay_world, _ = open_run(
        {}, None, run_id, data_dir=replay_root, replay_source_dir=source_root)
    try:
        asyncio.run(replay_headless(replay_world, 3))
        proof = verify_replay(source, replay_store.path)
        assert proof["exact"], proof["differences"]
        assert replay_world.economy.ledger.reconcile()[0]
    finally:
        replay_world.close()
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    assert not any(Path(str(source) + suffix).exists() for suffix in ("-wal", "-shm", "-journal"))
