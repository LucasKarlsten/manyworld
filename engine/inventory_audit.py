"""Additive scientific observations for the opt-in scripted semantics-7 lane.

These tables are intentionally absent in historical runs. They never enter
agent prompts, the event/memory spine, or any economic decision, and exact
replay compares them like every other persisted world-state table.
"""
from __future__ import annotations

import json

from engine.store import Store, load_json


CONTRACT = "buffer-demand-v2"


class InventoryAudit:
    @classmethod
    def from_config(cls, store: Store, config: dict) -> InventoryAudit | None:
        setting = config.get("observability", {}).get("scale_inventory_contract")
        if setting is None:
            return None
        if setting != CONTRACT:
            raise ValueError("unknown scale_inventory_contract")
        if config.get("engine_semantics_version") != 7:
            raise ValueError("inventory audit requires semantics 7")
        llm = config.get("llm", {})
        routes = [llm.get("default_route", {})] + list(llm.get("routes", {}).values())
        if any(route.get("provider") != "scripted" or route.get("model") != "scripted"
               for route in routes) or llm.get("decision_policy"):
            raise ValueError("inventory audit requires unmodified scripted policies")
        if llm.get("local_currency_action_surfaces") is not True:
            raise ValueError("inventory audit requires local currency action surfaces")
        return cls(store)

    def __init__(self, store: Store):
        self.store = store
        # Execute separately: executescript would implicitly commit the world's
        # transaction on resume. Optional tables do not migrate old sources.
        store.execute("""CREATE TABLE IF NOT EXISTS scale_inventory_audit (
            tick INTEGER PRIMARY KEY, opening_json TEXT NOT NULL,
            closing_json TEXT, decision_agent_ids_json TEXT)""")
        store.execute("""CREATE TABLE IF NOT EXISTS scale_demand_audit (
            tick INTEGER NOT NULL, agent_id INTEGER NOT NULL,
            region_id INTEGER, currency_code TEXT NOT NULL,
            observation_json TEXT NOT NULL, PRIMARY KEY(tick,agent_id))""")
        store.execute("""CREATE TABLE IF NOT EXISTS scale_purchase_audit (
            proposal_id INTEGER PRIMARY KEY, tick INTEGER NOT NULL, buyer_id INTEGER NOT NULL,
            firm_id INTEGER NOT NULL, requested_units INTEGER NOT NULL,
            stock_units INTEGER, unit_price_cents INTEGER, cash_cents INTEGER,
            unavailable_reason TEXT, result_json TEXT)""")

    def _bind(self, tick: int, column: str, value: str) -> None:
        # Callers supply internal column constants, never user-provided SQL.
        row = self.store.query_one(f"SELECT {column} FROM scale_inventory_audit WHERE tick=?", (tick,))
        if row is None or (row[0] is not None and row[0] != value):
            raise ValueError("inventory audit tick identity mismatch")
        self.store.execute(f"UPDATE scale_inventory_audit SET {column}=? WHERE tick=?", (value, tick))

    def _stocks(self) -> str:
        rows = []
        for row in self.store.query(
                "SELECT id,region_id,currency_code,inventory,product_json FROM firms "
                "WHERE status IN ('private','listed') ORDER BY id"):
            if int((load_json(row["product_json"], {}) or {}).get("output_per_worker", 0)) > 0:
                rows.append({"firm_id": int(row["id"]), "region_id": row["region_id"],
                             "currency_code": row["currency_code"], "inventory": row["inventory"]})
        return json.dumps(rows, sort_keys=True, separators=(",", ":"))

    def open_tick(self, tick: int) -> None:
        value = self._stocks()
        self.store.execute("INSERT OR IGNORE INTO scale_inventory_audit(tick,opening_json) VALUES (?,?)", (tick, value))
        self._bind(tick, "opening_json", value)

    def close_tick(self, tick: int) -> None:
        self._bind(tick, "closing_json", self._stocks())

    def record_cohort(self, tick: int, agents) -> None:
        ids = sorted(int(agent["id"]) for agent in agents)
        self._bind(tick, "decision_agent_ids_json", json.dumps(ids, separators=(",", ":")))

    def goods_catalog(self, currency: str) -> list[dict]:
        """Price terms without filtering or weighting by the available stock."""
        result = []
        for row in self.store.query(
                "SELECT id,product_json FROM firms WHERE status IN ('private','listed') "
                "AND currency_code=? ORDER BY id", (currency,)):
            product = load_json(row["product_json"], {}) or {}
            if int(product.get("output_per_worker", 0)) > 0:
                result.append({"firm_id": int(row["id"]), "currency_code": currency,
                               "product": product.get("product", "goods"),
                               "price": int(product.get("unit_price_cents", 500)),
                               "inventory": 8})
        return result

    def record_demand(self, tick: int, agent, currency: str, observation: dict) -> None:
        values = (tick, int(agent["id"]), agent["region_id"], currency,
                  json.dumps(observation, sort_keys=True, separators=(",", ":")))
        self.store.execute(
            "INSERT OR IGNORE INTO scale_demand_audit VALUES (?,?,?,?,?)", values)
        row = self.store.query_one("SELECT * FROM scale_demand_audit WHERE tick=? AND agent_id=?", values[:2])
        if tuple(row) != values:
            raise ValueError("demand audit identity mismatch")

    def record_purchase(self, proposal_id: int, tick: int, buyer: int, firm_id: int, qty: int, firms) -> None:
        firm = firms.get(firm_id)
        stock = price = cash = None
        reason = None
        if not firm or firm["status"] == "bankrupt":
            reason = "firm unavailable"
        else:
            stock, price = int(firm["inventory"]), int(firms.product(firm)["unit_price_cents"])
            account = firms.ledger.agent_checking_id(buyer)
            if account is None:
                reason = "no account"
            else:
                currency = self.store.scalar("SELECT currency_code FROM accounts WHERE id=?", (account,))
                cash = firms.ledger.balance(account)
                if str(currency or "USD") != str(firm["currency_code"] or "USD"):
                    reason = "currency mismatch"
        self.store.execute(
            "INSERT INTO scale_purchase_audit(proposal_id,tick,buyer_id,firm_id,requested_units,"
            "stock_units,unit_price_cents,cash_cents,unavailable_reason) VALUES (?,?,?,?,?,?,?,?,?)",
            (proposal_id, tick, buyer, firm_id, qty, stock, price, cash, reason))

    def complete_purchase(self, proposal_id: int, result: dict) -> None:
        self.store.execute("UPDATE scale_purchase_audit SET result_json=? WHERE proposal_id=?",
                           (json.dumps(result, sort_keys=True, default=str), proposal_id))
