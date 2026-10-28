#!/usr/bin/env python3
"""Read-only comparison of two Manyworld run databases.

Uses real SQLite ledgers and metric snapshots. It does not infer causal effects
from different run IDs, even when seeds match. Currency is reported as stored.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


METRICS = (
    "unemployment", "gdp_proxy_30d", "cpi", "money_supply", "gini",
    "gov_balance", "labor_income", "sentiment",
)


def snapshot(db: sqlite3.Connection, tick: int) -> dict:
    values = {}
    for name in METRICS:
        row = db.execute(
            "SELECT value FROM metrics WHERE name=? AND tick<=? "
            "ORDER BY tick DESC, id DESC LIMIT 1", (name, tick)
        ).fetchone()
        values[name] = round(row[0], 4) if row else None
    return values


def summarize(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    db = sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        meta = db.execute(
            "SELECT run_id, seed, tick, config_json FROM run_meta WHERE id=1"
        ).fetchone()
        if meta is None:
            raise ValueError(f"{path} is not an initialized Manyworld run")
        end = int(meta["tick"])
        config = json.loads(meta["config_json"] or "{}")
        currencies = [r[0] for r in db.execute(
            "SELECT DISTINCT currency_code FROM accounts ORDER BY currency_code"
        )]
        payments = [dict(r) for r in db.execute(
            """
            SELECT t.tick AS tick,
                   COUNT(DISTINCT t.id) AS recipients,
                   SUM(le.delta_cents) / 100.0 AS credited
            FROM transactions t
            JOIN ledger_entries le ON le.txn_id=t.id
            JOIN accounts a ON a.id=le.account_id
            WHERE t.kind='ubi_payment' AND a.owner_type='agent'
            GROUP BY t.tick ORDER BY t.tick
            """
        )]
        txn_kinds = [dict(r) for r in db.execute(
            "SELECT kind, COUNT(*) AS count FROM transactions "
            "WHERE tick BETWEEN 1 AND ? GROUP BY kind ORDER BY kind", (end,)
        )]
        sales = db.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM("
            "CAST(json_extract(payload_json,'$.total_cents') AS INTEGER)),0) AS cents "
            "FROM events WHERE kind='goods_sale' AND tick BETWEEN 1 AND ?", (end,)
        ).fetchone()
        gov = [dict(r) for r in db.execute(
            "SELECT currency_code, SUM(balance_cents)/100.0 AS balance "
            "FROM accounts WHERE label='sys:gov' "
            "GROUP BY currency_code ORDER BY currency_code"
        )]
        firm_cash = [dict(r) for r in db.execute(
            "SELECT a.currency_code, SUM(a.balance_cents)/100.0 AS balance "
            "FROM firms f JOIN accounts a ON a.id=f.account_id "
            "GROUP BY a.currency_code ORDER BY a.currency_code"
        )]
        employment = db.execute(
            "SELECT COUNT(*) FROM employments WHERE status='active'"
        ).fetchone()[0]
        alive_citizens = db.execute(
            "SELECT COUNT(*) FROM agents WHERE kind='citizen' AND alive=1"
        ).fetchone()[0]
        return {
            "run": meta["run_id"], "seed": meta["seed"], "tick": end,
            "engine_semantics": config.get("engine_semantics_version"),
            "currencies": currencies,
            "ubi_config": {
                k: config.get("government", {}).get(k)
                for k in ("ubi_enabled", "ubi_amount_cents", "ubi_first_tick",
                          "ubi_interval_ticks")
            },
            "ubi_payments": payments,
            "ubi_total": sum(p["credited"] for p in payments),
            "sales_transactions": sales["n"],
            "goods_sales": round(sales["cents"] / 100, 2),
            "government_balances": gov,
            "firm_cash": firm_cash,
            "active_employment_contracts": employment,
            "alive_citizens": alive_citizens,
            "metrics_at_end": snapshot(db, end),
            "metrics_before_first_payment": snapshot(db, min(29, end)),
            "transaction_kinds": txn_kinds,
        }
    finally:
        db.close()


def compare(control: dict, treated: dict) -> dict:
    if control["tick"] != treated["tick"]:
        raise ValueError("Different completed horizons; cannot compare")
    if control["seed"] != treated["seed"]:
        raise ValueError("Seeds differ; not a matched-seed comparison")
    if control["currencies"] != treated["currencies"]:
        raise ValueError("Currencies differ; monetary comparison unsafe")
    if control["engine_semantics"] != treated["engine_semantics"]:
        raise ValueError("Engine semantics differ; cannot compare")
    deltas = {}
    for key in METRICS:
        a, b = control["metrics_at_end"][key], treated["metrics_at_end"][key]
        deltas[key] = round(b - a, 4) if a is not None and b is not None else None
    return {
        "control": control, "ubi": treated,
        "difference_ubi_minus_control": {
            "ubi_total": round(treated["ubi_total"] - control["ubi_total"], 2),
            "goods_sales": round(treated["goods_sales"] - control["goods_sales"], 2),
            "active_employment_contracts": (
                treated["active_employment_contracts"]
                - control["active_employment_contracts"]
            ),
            "metrics_at_end": deltas,
        },
        "interpretation": (
            "Descriptive exploratory run comparison only. Equal seeds do not "
            "guarantee identical pre-treatment worlds. This is NOT a Sweden "
            "forecast or a validated causal UBI estimate."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("control", help="Control run ID or database path")
    parser.add_argument("ubi", help="UBI run ID or database path")
    parser.add_argument("--output", type=Path, help="Optional JSON output file")
    args = parser.parse_args()

    def resolve(value: str) -> Path:
        p = Path(value)
        if p.is_file():
            return p
        if "/" in value or "\\" in value or value.endswith(".db"):
            raise FileNotFoundError(value)
        return Path("data/runs") / f"{value}.db"

    result = compare(summarize(resolve(args.control)), summarize(resolve(args.ubi)))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )
        print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
