"""Read-only v2 stock-buffer and independently observed scripted-demand evidence."""
from __future__ import annotations

from collections import Counter, defaultdict
from bisect import bisect_right
import json
import sqlite3


def _int(value, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError("invalid nonnegative integer in inventory/demand audit")
    return value


def _object(raw):
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("invalid audit object")
    return value


def _stocks(raw):
    values = json.loads(raw)
    if not isinstance(values, list) or not values:
        raise ValueError("missing inventory cohort")
    result = {}
    for value in values:
        if not isinstance(value, dict) or set(value) != {"firm_id", "region_id", "currency_code", "inventory"}:
            raise ValueError("invalid inventory snapshot")
        firm = _int(value["firm_id"], 1)
        _int(value["region_id"], 1)
        _int(value["inventory"])
        if firm in result or not isinstance(value["currency_code"], str) or not value["currency_code"]:
            raise ValueError("duplicate firm or missing currency")
        result[firm] = value
    return result


def _trajectory(days, response, observation):
    failures = []
    empty_streak = low_cover_streak = 0
    maximum_empty = maximum_low_cover = 0
    declining = []
    missing_production = []
    for index, day in enumerate(days):
        empty_streak = empty_streak + 1 if day["closing"] == 0 else 0
        maximum_empty = max(maximum_empty, empty_streak)
        if index + 1 >= response:
            block = days[index + 1 - response:index + 1]
            if sum(item["production"] for item in block) == 0:
                missing_production.append([block[0]["tick"], day["tick"]])
        unsafe = False
        if index + 1 >= observation:
            block = days[index + 1 - observation:index + 1]
            draw = sum(item["sales"] - item["production"] for item in block)
            if draw > 0:
                unsafe = day["closing"] * observation <= draw * response
                declining.append({
                    "window": [block[0]["tick"], day["tick"]],
                    "net_draw_units": draw, "closing_inventory": day["closing"],
                    "linear_ticks_to_empty": round(day["closing"] * observation / draw, 6),
                    "within_response_horizon": unsafe,
                })
        low_cover_streak = low_cover_streak + 1 if unsafe else 0
        maximum_low_cover = max(maximum_low_cover, low_cover_streak)
    if maximum_empty >= response:
        failures.append("persistent_empty_stock")
    if maximum_low_cover >= response:
        failures.append("sustained_depletion")
    if missing_production:
        failures.append("production_interrupted")
    return {
        "opening_inventory": days[0]["opening"],
        "terminal_inventory": days[-1]["closing"],
        "production_units": sum(day["production"] for day in days),
        "accepted_sale_units": sum(day["sales"] for day in days),
        "maximum_empty_stock_ticks": maximum_empty,
        "maximum_unsafe_depletion_ticks": maximum_low_cover,
        "missing_production_windows": missing_production,
        "declining_windows": declining,
        "failures": failures, "passed": not failures,
    }


def buffer_inventory_evidence(connection, ticks, thresholds):
    """Conserve every observed day; judge post-warmup buffers at firm/region level."""
    try:
        start = _int(thresholds["warmup_ticks"], 1)
        response = _int(thresholds["inventory_response_ticks"], 1)
        observation = _int(thresholds["inventory_observation_ticks"], response)
        if ticks - start + 1 < observation + response - 1:
            raise ValueError("insufficient completed inventory observation horizon")
        rows = list(connection.execute("SELECT * FROM scale_inventory_audit ORDER BY tick"))
        if [row["tick"] for row in rows] != list(range(1, ticks + 1)):
            raise ValueError("inventory audit ticks incomplete or unexpected")
        cohort = _stocks(rows[0]["opening_json"])
        production, sales = Counter(), Counter()
        for row in connection.execute("SELECT tick,kind,payload_json FROM events WHERE kind IN ('production','goods_sale') ORDER BY tick,id"):
            tick = _int(row["tick"], 1)
            payload = _object(row["payload_json"])
            firm = _int(payload["firm_id"], 1)
            if firm not in cohort or tick > ticks:
                raise ValueError("goods flow outside the observed cohort")
            target, field = (production, "units") if row["kind"] == "production" else (sales, "qty")
            target[tick, firm] += _int(payload[field], 1)
        days = defaultdict(list)
        previous = None
        for row in rows:
            tick = row["tick"]
            opening, closing = _stocks(row["opening_json"]), _stocks(row["closing_json"])
            if set(opening) != set(cohort) or set(closing) != set(cohort):
                raise ValueError("inventory cohort changed")
            for firm in cohort:
                for snapshot in (opening[firm], closing[firm]):
                    if (snapshot["region_id"], snapshot["currency_code"]) != (cohort[firm]["region_id"], cohort[firm]["currency_code"]):
                        raise ValueError("inventory region/currency changed")
                if previous is not None and opening[firm] != previous[firm]:
                    raise ValueError("opening inventory differs from previous close")
                before, after = opening[firm]["inventory"], closing[firm]["inventory"]
                made, sold = production[tick, firm], sales[tick, firm]
                if before + made - sold != after:
                    raise ValueError(f"inventory conservation failed at tick {tick}, firm {firm}")
                if tick >= start:
                    days[firm].append({"tick": tick, "opening": before, "closing": after,
                                       "production": made, "sales": sold})
            previous = closing
        terminal = {}
        names = {}
        for row in connection.execute("SELECT id,name,region_id,currency_code,inventory,product_json FROM firms WHERE status IN ('private','listed') ORDER BY id"):
            if _object(row["product_json"]).get("output_per_worker", 0) > 0:
                firm = _int(row["id"], 1)
                terminal[firm] = {"firm_id": firm, "region_id": row["region_id"],
                                  "currency_code": row["currency_code"], "inventory": _int(row["inventory"])}
                names[firm] = row["name"]
        if terminal != previous:
            raise ValueError("terminal inventory does not match closing snapshot")
        firms = [{"firm_id": firm, "name": names[firm], **_trajectory(days[firm], response, observation)} for firm in sorted(cohort)]
        region_days = {}
        for firm, identity in cohort.items():
            key = (identity["region_id"], identity["currency_code"])
            if key not in region_days:
                region_days[key] = [{**day, **{field: 0 for field in ("opening", "closing", "production", "sales")}} for day in days[firm]]
            for aggregate, day in zip(region_days[key], days[firm]):
                for field in ("opening", "closing", "production", "sales"):
                    aggregate[field] += day[field]
        regions = [{"region_id": key[0], "currency_code": key[1], **_trajectory(region_days[key], response, observation)} for key in sorted(region_days)]
        return all(row["passed"] for row in firms + regions), {
            "contract": "buffer-demand-v2", "measured_window": [start, ticks],
            "conservation_window": [1, ticks], "daily_conservation_exact": True,
            "active_goods_firms": firms, "regions": regions,
            "depletion_note": "Linear depletion diagnostics are not forecasts; a 120-tick pass does not establish long-run sustainability.",
        }
    except (sqlite3.Error, ValueError, TypeError, KeyError) as exc:
        return False, {"contract": "buffer-demand-v2", "daily_conservation_exact": False,
                       "error": str(exc), "active_goods_firms": [], "regions": []}


DEMAND_FIELDS = ("desired_units", "affordable_units", "unpriced_units", "affordability_limited_units", "guidance_limited_units")
ACTUAL_FIELDS = ("submitted_units", "fulfilled_units", "stock_limited_units", "cash_limited_units",
                 "other_execution_shortfall_units", "pre_execution_rejected_units", "rejected_orders", "partial_orders")


def _demand_totals(rows):
    totals = {field: sum(row[field] for row in rows) for field in DEMAND_FIELDS + ACTUAL_FIELDS}
    totals["decision_observations"] = len(rows)
    totals["eligible_consumption_decisions"] = sum(row["eligibility"] == "eligible" for row in rows)
    totals["unsubmitted_affordable_units"] = sum(max(0, row["affordable_units"] - row["submitted_units"]) for row in rows)
    totals["submitted_above_probe_units"] = sum(max(0, row["submitted_units"] - row["affordable_units"]) for row in rows)
    totals["execution_shortfall_units"] = totals["submitted_units"] - totals["fulfilled_units"]
    for name, denominator in (("submitted_unit_fill_rate", "submitted_units"),
                              ("shadow_affordable_unit_fill_rate", "affordable_units"),
                              ("shadow_desired_unit_fill_rate", "desired_units")):
        totals[name] = round(totals["fulfilled_units"] / totals[denominator], 6) if totals[denominator] else None
    return totals


def demand_evidence(connection, ticks, thresholds):
    """Require complete observation/order evidence; expose, never hide, rationing."""
    try:
        start = _int(thresholds["warmup_ticks"], 1)
        actors = {row["id"]: row for row in connection.execute(
            "SELECT a.id,a.region_id,c.id AS checking_account_id,COALESCE(NULLIF(c.currency_code,''),'USD') AS currency_code "
            "FROM agents a LEFT JOIN accounts c ON c.id=a.checking_account_id")}
        firms = {row["id"]: row for row in connection.execute("SELECT id,status,currency_code,product_json FROM firms")}
        goods = {firm_id: row for firm_id, row in firms.items() if row["status"] in {"private", "listed"}
                 and _object(row["product_json"]).get("output_per_worker", 0) > 0}
        openings = {row["tick"]: _stocks(row["opening_json"]) for row in connection.execute(
            "SELECT tick,opening_json FROM scale_inventory_audit ORDER BY tick")}
        # Prefix sums bind each execution snapshot to independently observed
        # opening stock and the goods events before its settlement boundary.
        goods_events = {}
        goods_ids = [0]
        flow_ids, flow_sums = defaultdict(list), defaultdict(lambda: [0])
        for row in connection.execute("SELECT id,tick,kind,payload_json FROM events WHERE kind IN ('production','goods_sale') ORDER BY id"):
            payload = _object(row["payload_json"])
            firm = _int(payload["firm_id"], 1)
            quantity = _int(payload["units" if row["kind"] == "production" else "qty"], 1)
            key = (row["tick"], firm)
            goods_events[row["id"]] = (row["tick"], row["kind"], payload)
            goods_ids.append(row["id"])
            flow_ids[key].append(row["id"])
            flow_sums[key].append(flow_sums[key][-1] + (quantity if row["kind"] == "production" else -quantity))
        goods_positions = {event_id: index for index, event_id in enumerate(goods_ids)}
        # Night production precedes all market purchases in this fixed lane.
        # Every dispatch, including a rejection, must continue the previous
        # goods boundary rather than selecting a convenient historical stock.
        tick_boundaries = {}
        tick_end_boundaries = {}
        last_goods = 0
        sales_started = set()
        for event_id in goods_ids[1:]:
            tick, kind, _ = goods_events[event_id]
            tick_boundaries.setdefault(tick, last_goods)
            if kind == "production":
                if tick in sales_started:
                    raise ValueError("goods production occurs after market settlement")
                tick_boundaries[tick] = event_id
            else:
                sales_started.add(tick)
            last_goods = event_id
            tick_end_boundaries[tick] = event_id
        last_completed = 0
        for tick in range(1, ticks + 1):
            tick_boundaries.setdefault(tick, last_completed)
            last_completed = tick_end_boundaries.get(tick, last_completed)
        consumed_sales = set()
        expected = set()
        audit_ticks = list(connection.execute("SELECT tick,decision_agent_ids_json FROM scale_inventory_audit ORDER BY tick"))
        if [row["tick"] for row in audit_ticks] != list(range(1, ticks + 1)):
            raise ValueError("demand cohort ticks incomplete")
        for row in audit_ticks:
            ids = json.loads(row["decision_agent_ids_json"])
            if not isinstance(ids, list) or ids != sorted(set(ids)):
                raise ValueError("invalid scheduled demand cohort")
            expected.update((row["tick"], _int(agent, 1)) for agent in ids)
        observations = {}
        for row in connection.execute("SELECT * FROM scale_demand_audit ORDER BY tick,agent_id"):
            key = (_int(row["tick"], 1), _int(row["agent_id"], 1))
            if key in observations:
                raise ValueError("duplicate demand observation")
            probe = _object(row["observation_json"])
            if _int(probe.get("schema_version"), 1) != 1 or probe.get("eligibility") not in {"eligible", "policy_preempted"}:
                raise ValueError("unknown demand observation contract")
            for field in DEMAND_FIELDS + ("budget_cents", "liquid_cash_cents", "shopping_qty_cap"):
                _int(probe[field])
            _int(probe["shopping_qty_cap"], 1)
            region = _int(row["region_id"], 1)
            currency = row["currency_code"]
            actor = actors.get(key[1])
            if actor is None or (region, currency) != (actor["region_id"], actor["currency_code"]):
                raise ValueError("demand identity differs from actor region or checking currency")
            desired, affordable = probe["desired_units"], probe["affordable_units"]
            if (desired != (8 if probe["eligibility"] == "eligible" else 0)
                    or desired != affordable + probe["affordability_limited_units"] + probe["unpriced_units"]
                    or probe["guidance_limited_units"] != max(0, affordable - probe["shopping_qty_cap"])):
                raise ValueError("demand probe quantities do not reconcile")
            if desired and not probe["unpriced_units"]:
                reference = goods.get(_int(probe["reference_firm_id"], 1))
                if reference is None or reference["currency_code"] != currency:
                    raise ValueError("demand reference is outside the local-currency goods cohort")
                price = _int(probe["reference_price_cents"], 1)
                expected_affordable = (max(1, min(8, probe["budget_cents"] // price))
                                       if probe["liquid_cash_cents"] > 2 * price else 0)
                if affordable != expected_affordable:
                    raise ValueError("demand affordability does not match policy")
            elif (probe["reference_firm_id"] is not None or probe["reference_price_cents"] is not None
                  or affordable != 0 or probe["affordability_limited_units"] != 0
                  or probe["unpriced_units"] != desired):
                raise ValueError("inconsistent unpriced/preempted demand shape")
            if probe["unpriced_units"] and any(firm["currency_code"] == currency for firm in goods.values()):
                raise ValueError("unpriced demand despite an available price catalog")
            observations[key] = {**probe, "region_id": region, "currency_code": currency,
                                 **{field: 0 for field in ACTUAL_FIELDS}}
        if not expected or set(observations) != expected:
            raise ValueError("demand observations do not match the scheduled cohort")
        audits = {row["proposal_id"]: row for row in connection.execute("SELECT * FROM scale_purchase_audit ORDER BY proposal_id")}
        consumed_audits = set()
        accepted = Counter()
        for row in connection.execute("SELECT * FROM action_proposals WHERE action_type='buy_goods' ORDER BY tick,id"):
            key = (_int(row["tick"], 1), _int(row["actor_id"], 1))
            if key not in observations:
                raise ValueError("purchase outside the observed decision cohort")
            observation = observations[key]
            payload, result = _object(row["payload_json"]), _object(row["result_json"])
            requested, firm = _int(payload["qty"], 1), _int(payload["firm_id"], 1)
            status = row["validation_status"]
            if status not in {"accepted", "rejected"} or result.get("ok") is not (status == "accepted"):
                raise ValueError("unresolved or inconsistent purchase proposal")
            filled = _int(result["qty"], 1) if status == "accepted" else 0
            if filled > requested:
                raise ValueError("purchase fulfilled more than submitted")
            observation["submitted_units"] += requested
            observation["fulfilled_units"] += filled
            observation["rejected_orders"] += status == "rejected"
            observation["partial_orders"] += 0 < filled < requested
            accepted[key + (firm,)] += filled
            audit = audits.get(row["id"])
            if audit is None:
                if status != "rejected" or result.get("reason") not in {
                    "actor missing", "actor not alive", "qty must be positive",
                    "citizen is occupied by a frontier task",
                }:
                    raise ValueError("dispatched purchase is missing execution audit")
                observation["pre_execution_rejected_units"] += requested
                continue
            consumed_audits.add(row["id"])
            if ((audit["tick"], audit["buyer_id"], audit["firm_id"], audit["requested_units"])
                    != (key[0], key[1], firm, requested) or _object(audit["result_json"]) != result):
                raise ValueError("purchase audit identity or result differs from proposal")
            stock_lost = cash_lost = other_lost = 0
            # The executor clamps stock before checking the account/currency,
            # then clamps by cash. This ordered decomposition is not exclusive
            # causal attribution: both constraints can bind on the same order.
            stock = audit["stock_units"]
            reason = audit["unavailable_reason"]
            if reason not in {None, "firm unavailable", "no account", "currency mismatch"}:
                raise ValueError("unknown purchase audit unavailability")
            seller, buyer = firms.get(firm), actors[key[1]]
            actual_unavailability = ("firm unavailable" if seller is None or seller["status"] == "bankrupt"
                                    else "no account" if buyer["checking_account_id"] is None
                                    else "currency mismatch" if buyer["currency_code"] != seller["currency_code"] else None)
            if reason != actual_unavailability:
                raise ValueError("purchase availability differs from the fixed actor/firm cohort")
            before, after = _int(audit["preceding_goods_event_id"]), _int(audit["following_goods_event_id"])
            if before not in goods_positions or after not in goods_positions or before > after:
                raise ValueError("invalid purchase goods-event boundary")
            if before != tick_boundaries[key[0]]:
                raise ValueError("purchase boundary does not continue prior dispatches")
            if before and goods_events[before][0] > key[0]:
                raise ValueError("purchase boundary belongs to a later tick")
            if filled:
                if goods_positions[after] != goods_positions[before] + 1:
                    raise ValueError("purchase is not bound to exactly one goods event")
                if after in consumed_sales:
                    raise ValueError("goods sale consumed by more than one proposal")
                consumed_sales.add(after)
                event_tick, event_kind, sale = goods_events[after]
                price = _int(audit["unit_price_cents"])
                if (event_tick != key[0] or event_kind != "goods_sale"
                        or (sale.get("buyer_id"), sale.get("firm_id"), sale.get("qty")) != (key[1], firm, filled)
                        or result.get("unit_price_cents") != price or result.get("total_cents") != filled * price
                        or sale.get("unit_price_cents") != price or sale.get("total_cents") != filled * price):
                    raise ValueError("purchase price or settlement differs from its goods sale")
            elif before != after:
                raise ValueError("rejected purchase emitted a goods event")
            tick_boundaries[key[0]] = after
            expected_reason = None
            if stock is not None:
                stock = _int(stock)
                opening = openings[key[0]][firm]["inventory"]
                reconstructed = opening + flow_sums[key[0], firm][bisect_right(flow_ids[key[0], firm], before)]
                if stock != reconstructed:
                    raise ValueError("purchase stock differs from opening plus preceding goods flows")
                _int(audit["unit_price_cents"])
                stock_lost = max(0, requested - stock)
            if reason == "firm unavailable":
                if any(audit[field] is not None for field in ("stock_units", "unit_price_cents", "cash_cents")):
                    raise ValueError("unavailable firm has purchase limits")
            elif stock is None or (reason == "no account" and audit["cash_cents"] is not None):
                raise ValueError("purchase audit has inconsistent account/stock shape")
            elif reason != "no account":
                _int(audit["cash_cents"])
            if reason is not None:
                other_lost = requested - stock_lost
                expected_fill = 0
                expected_reason = ("firm unavailable" if reason == "firm unavailable" else "out of stock" if stock == 0
                                   else "no account" if reason == "no account"
                                   else "cross-border purchases require a trade shipment and FX")
            else:
                stock = _int(stock)
                price, cash = _int(audit["unit_price_cents"]), _int(audit["cash_cents"])
                stock_available = min(requested, stock)
                expected_fill = min(stock_available, cash // price if price else stock_available)
                cash_lost = stock_available - expected_fill
                if not expected_fill:
                    expected_reason = "out of stock" if stock == 0 else "insufficient funds"
            if expected_fill != filled:
                raise ValueError("purchase result differs from recorded stock/cash limits")
            if not filled and result.get("reason") != expected_reason:
                raise ValueError("purchase rejection differs from stock/account/cash ordering")
            observation["stock_limited_units"] += stock_lost
            observation["cash_limited_units"] += cash_lost
            observation["other_execution_shortfall_units"] += other_lost
        if consumed_audits != set(audits):
            raise ValueError("orphan purchase execution audit")
        if consumed_sales != {event_id for event_id, event in goods_events.items() if event[1] == "goods_sale"}:
            raise ValueError("goods sales are not consumed exactly once by purchase audits")
        sold = Counter()
        for row in connection.execute("SELECT tick,payload_json FROM events WHERE kind='goods_sale' ORDER BY tick,id"):
            payload = _object(row["payload_json"])
            key = (_int(row["tick"], 1), _int(payload["buyer_id"], 1), _int(payload["firm_id"], 1))
            sold[key] += _int(payload["qty"], 1)
        if +accepted != +sold:
            raise ValueError("fulfilled orders differ from goods sale events")
        measured = [value for (tick, _), value in observations.items() if tick >= start]
        if not measured:
            raise ValueError("missing post-warmup demand observations")
        region_rows = defaultdict(list)
        for row in measured:
            region_rows[row["region_id"], row["currency_code"]].append(row)
        totals = _demand_totals(measured)
        if totals["execution_shortfall_units"] != sum(totals[field] for field in (
                "stock_limited_units", "cash_limited_units", "other_execution_shortfall_units", "pre_execution_rejected_units")):
            raise ValueError("execution shortfall does not reconcile")
        return True, {
            "contract": "buffer-demand-v2", "measured_window": [start, ticks],
            "observation_coverage_window": [1, ticks], "scheduled_decisions": len(expected),
            "observed_decisions": len(observations), "totals": totals,
            "regions": [{"region_id": key[0], "currency_code": key[1], **_demand_totals(region_rows[key])} for key in sorted(region_rows)],
            "demand_adequacy_certified": False,
            "interpretation": "Desired/affordable units are a stock-independent scripted-policy counterfactual. Actual seller choice may differ; shadow fill ratios can exceed one. Measurement completeness and low rejection do not certify adequate household service.",
            "execution_decomposition": "Requested units are limited by stock, then cash; other validation failures are separate. Both stock and cash constraints may bind.",
        }
    except (sqlite3.Error, ValueError, TypeError, KeyError) as exc:
        return False, {"contract": "buffer-demand-v2", "error": str(exc),
                       "demand_adequacy_certified": False}
