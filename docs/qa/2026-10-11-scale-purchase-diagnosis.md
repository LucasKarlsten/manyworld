# Scale purchase rejection diagnosis — October 11, 2026

## Authoritative failure

The unchanged recovery source `22602e3a92` at commit `168a067` completed 120 ticks and exact replay across 130 tables. Its [published diagnostic receipt](../../benchmarks/receipts/scale-270/ab-120/recovery.json) fails only purchase rejection: 7,399 of 12,224 proposals in ticks 61–120 (60.5285%, limit 5%). All 7,399 rejections have `result_json.reason = "out of stock"`; none is an affordability or currency rejection. Source queries used SQLite `mode=ro&immutable=1`.

The first rejected purchase is proposal 42 at tick 1: actor 25 requests eight `retail_good` units from firm 8. Its authoritative scripted request (model call 24) advertises 20 units at 784 NSD cents, active supply recovery, and no inventory-aware shopping flag or quantity cap. Earlier proposals 8, 33 and 35 from actors 8, 21 and 22 consume 8, 8 and 4 units; the fourth shopper receives nothing. The engine correctly partially fills the third purchase, rejects the empty-stock fourth purchase, and routes successful sales through the ledger.

In ticks 61–120 the cohort requests 89,746 units. Production and goods-sale events both total 27,720 units; tick 61 alone produces and sells 462 units. All 12 goods firms have seven active employees at the end, their configured recovery cap, and zero closing inventory. Final unemployment is 0.734375; labor, unit economics and ledger checks already pass. The first-party policy/context boundary explains the stockouts: recovery distributes seller selection by stock but still requests up to eight units per shopper from a shared morning snapshot. The scale profiles omit the existing opt-in `behavior.inventory_aware_shopping` quantity guidance. The same option is already used by the life-course recovery benchmark.

## Controlled diagnostic

Two disposable copies of the tick-119 checkpoint were resumed for one tick, with operational paths confined to each copy. The only policy difference was `behavior.inventory_aware_shopping: true`. The original checkpoint's SHA-256 remained unchanged. This is a copied-state diagnostic, not fresh acceptance evidence.

| Tick 120 | Accepted | Rejected | Requested quantities | Ledger |
| --- | ---: | ---: | --- | --- |
| Original profile | 82 | 117 | 17 at 1, 5 at 2, 177 at 8 | reconciled |
| Existing inventory guidance enabled | 197 | 2 | 57 at 1, 142 at 2 | reconciled |

Raw copied databases, logs and `probe.json` remain ignored under `reports/out/scale-270/purchase-diagnostic-20261011/`. Both branches execute ordinary scripted decisions and engine settlement. No proposal is removed, no rejected attempt is reclassified, and no gate is relaxed.

## Governed repair and evidence boundary

New maintained profiles `scale-270-recovery-inventory-120.yaml` and `scale-270-recovery-inventory-1000.yaml` inherit their corresponding original recovery profiles. They retain `behavior.inventory_aware_shopping_activation_tick: 60`, opt into staff counting and a 2,000-basis-point stock margin, and allow up to eight workers per firm instead of seven. The bounded capacity change follows the recorded hiring assessments below. Quantity guidance still starts at tick 60, but earlier hiring can now differ from the original workforce ramp. Original baseline/recovery profiles and published failed receipts remain intact. Receipt evaluation recognizes each new profile explicitly and still binds persisted/effective configuration, horizon, population, semantics, artifacts and every original threshold. The repaired recovery is a separate intervention from the original policy-only A/B comparison.

The engine and settlement policy remain unchanged. Context generation gains two explicitly persisted options whose defaults preserve historical observations and quantities; no new semantics version is needed to retain old behavior. Component tests cover shared-snapshot stock exhaustion, both population tiers, staff consumption, regional isolation, partial fill/rejection, inventory conservation and ledger reconciliation. A fresh source/replay must pass every 120-tick gate before Stage 4 closes; a one-tick diagnostic establishes no long-horizon result. The formal 1,000-tick and live/browser/Hermes checks remain later gates.

## Why guidance must follow the workforce ramp

The first configuration candidate, commit `559301d`, enabled guidance from the start. Its fresh source `7ce4c5cc41` completed 120 ticks but failed both purchase windows: 1,079/12,952 (8.33%) at ticks 60–119 and 1,071/12,944 (8.27%) at ticks 61–120. Every rejection remained out of stock. The completed replay is exact across 130 tables and all 17 runtime checks pass, with zero provider spend. Final economic evaluation also fails production/inventory health; the diagnosis below explains this second failure. The failed candidate and its original configuration remain preserved in a separate checkout.

The demand-limited hiring boundary explains why the successful fully staffed checkpoint-copy trial did not establish fresh-run success. At tick 2, firm 3's founder (actor 89, model call 151) observes 21 sales plus 104 unmet units in the original recovery, yielding demand-limited headcount 2 and one allowed hire. Guidance from the start instead records 16 sales and no unmet units, yielding demand-limited headcount 0 and no allowed hire. Both assessments have cash-limited headcount 24, identical prices, costs, wages and margins. Actual employment first diverges at tick 6. By tick 59 all 12 original goods firms have seven workers; the first candidate has only three to six each. Measured-window production falls from 27,720 to 23,309 units, with 23,299 sold.

The next candidate used the already supported activation option to preserve this ramp and then cap quantities. Tests pin tick 59 versus tick 60 and verify exact source/replay across a compressed cutover fixture. Its full source result below demonstrates why the timing change alone is insufficient.

## October 13: production shortfall and stopped validation

Three firms sold more than they produced in ticks 61–120. Their carried stock covered the difference; this is not evidence of negative inventory or a ledger imbalance. Persisted tick-61 contexts (model calls 7500 and 7556) advertise stock after that tick's production. Subtracting the corresponding production events gives opening stock of 8, 12 and 7 units. The complete window reconciles exactly:

| Firm | Opening stock | Produced | Sold | Closing stock | Production shortfall |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2 — Retail Co 2 | 8 | 1,380 | 1,388 | 0 | 8 |
| 4 — Services Co 4 | 12 | 1,616 | 1,618 | 10 | 2 |
| 8 — Retail Co 8 | 7 | 2,247 | 2,254 | 0 | 7 |

The maintained acceptance contract explicitly requires each active goods firm's final-window production to cover accepted sales. Carried inventory therefore does not waive this failure. The evaluator now exposes `production_shortfall_units` alongside its existing totals; its decision and thresholds are unchanged. Regression fixtures cover surplus production, exact coverage and one/seven-unit shortfalls despite positive closing inventory, while retaining exact replay and ledger checks.

The local validation orchestrator stopped before its broader tests or revised source run because it incorrectly assumed the previous attempt would fail only purchases. The corrected sequence explicitly recognizes both diagnosed failures, reproduces the original failed receipt using the frozen `559301d` checkout, verifies its artifacts, and only then starts the revised candidate's tests and fresh run. Neither historical failure becomes acceptance. Source SHA-256 remains `d740129ec88c9cea1bf42220ecfdf7469bfd0346a518591f511c4e0e9a0d3ad3`.

## Timing-only result and shared-stock guidance

The fresh source `21eb569b27` at `fc4c55d` completed 120 ticks. Its first 59 ticks exactly match the original recovery's 826 staffing records, 708 per-firm production totals and 708 sales totals. All 12 goods firms retain seven workers. However, purchase rejection is still 643/12,234 (5.2558%) for ticks 60–119 and 647/12,228 (5.2911%) for ticks 61–120. Firms 1, 2, 3, 7, 8, 10 and 11 have final-window production shortfalls of 1, 6, 2, 8, 20, 5 and 3 units respectively. The source therefore cannot pass the unchanged economic contract; its separate replay and complete runtime receipt are retained independently.

The context builder counts only `kind='citizen'` when dividing visible inventory among scheduled shoppers. Staff seats also buy goods through ordinary scripted decisions. At tick 61, region 1 has 95 citizen purchase proposals requesting 380 units and 23 staff proposals requesting 35 more. Staff actor 7's recorded context (call 7527) advertises 406 units and a quantity cap of four. Staff consumption is absent from the denominator. Both core and peripheral citizens are already counted; missing periphery was ruled out by tracing the scheduler and runtime.

Independent weighted seller choices also compete against the same morning snapshot. Spending the entire per-capita stock allowance leaves little margin for uneven selection. The revised candidate adds two opt-in controls:

- `behavior.inventory_aware_shopping_include_staff: true` includes healthy, living scheduled staff as potential shoppers. Uncached contexts apply the same kind and region boundary; modern citizen contexts retain adult/residency filtering.
- `behavior.inventory_aware_shopping_reserve_bps: 2000` calculates quantity guidance from 80% of visible stock. It retains the existing one-unit minimum and eight-unit maximum. This is a proposal-sizing margin, not an engine reservation: all inventory remains available for ordinary settlement.

The defaults are `false` and `0`, preserving existing configurations and replay behavior. Both controls affect quantity guidance only after its configured activation. Invalid boolean or basis-point settings fail explicitly. A mixed citizen/staff regression demonstrates the original depletion, correct counting, the additional margin, successful and rejected settlements, and exact ledger conservation. Separate tests cover cached/uncached contexts, regional isolation and a replay across activation. These tests are prerequisites; the revised candidate still needs a fresh 120-tick source, replay and passing receipt.

## Capacity limit after the shopping repair

Source `fd708a3063` at commit `48ecbcd` completed 120 ticks with purchase rejection of 17/12,245 (0.1388%) for ticks 60–119 and 18/12,238 (0.1471%) for ticks 61–120, both below the unchanged 5% ceiling. Four goods firms still fail the per-firm production rule:

| Firm | Opening stock, tick 61 | Production, ticks 61–120 | Accepted sales | Closing stock | Production shortfall |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2 | 19 | 2,100 | 2,103 | 16 | 3 |
| 3 | 15 | 1,680 | 1,695 | 0 | 15 |
| 4 | 5 | 1,680 | 1,683 | 2 | 3 |
| 8 | 37 | 2,940 | 2,953 | 24 | 13 |

These are legitimate stock drawdowns, not negative inventory. Tick-61 calls 7525 and 7562 independently anchor morning inventory; production events 90674/90675/90676/90680 identify that morning's additions. Tick-1 contexts independently anchor genesis stock. Event-by-event reconstruction for all 12 firms remains nonnegative and matches the four retained checkpoints (105/112/119/120) and terminal inventory. Aggregate production is 27,720 against 27,698 sales, with aggregate stock increasing from 226 to 248. Aggregate coverage does not waive individual failures. The closed source SHA-256 remains `0da59131715bcdc3fcc1bb1dde5b4cd3a0a06c60a10ac3464a6e76883697fd41` after the read-only inspection. Replay and the full runtime/economic receipt remain pending at this diagnosis stage.

All four failed firms have seven workers. During ticks 61–120, their recorded founder assessments support another worker while cash and wage checks pass, but the configured headcount ceiling blocks hiring: firm 2 has 26 such assessments, firm 3 has 31, firm 4 has 33 and firm 8 has 22. The latest examples are:

| Firm | Tick / call ID | Demand-supported workers | Configured ceiling | Cash-supported additional workers | Safe wage ceiling / actual wage, cents |
| --- | --- | ---: | ---: | ---: | ---: |
| 2 | 113 / 14203 | 8 | 7 | 105 | 24,840 / 15,000 |
| 3 | 119 / 14851 | 8 | 7 | 22 | 15,072 / 15,000 |
| 4 | 118 / 14746 | 8 | 7 | 71 | 15,072 / 15,000 |
| 8 | 89 / 11070 | 8 | 7 | 60 | 31,416 / 15,000 |

The next candidate changes only `supply_recovery.max_headcount_per_firm` from seven to eight in the repaired profiles. It uses the existing assessment and ordinary job/application/offer settlement. Recorded-input regressions show the old profile allows zero hires while the repaired profile permits one, and still rejects excessive wages, insufficient cash, absent demand and a ninth worker. Six profile/assessment cases fail before the configuration change and pass after it. The original diagnostic profiles, economic thresholds, engine semantics, ledger and historical artifacts remain unchanged.

This is a capacity experiment supported by a specific blocked hire, not evidence of acceptance. Binding assessments already occur before tick 60, so this candidate must not claim identical warmup history. More output can also raise stock-based purchasing; a fresh source/replay must demonstrate actual hiring, production and every existing gate. Further ceiling increases are not justified merely to obtain a passing seed. Formal 1,000-tick, browser, live-provider and Hermes follow-ons remain deferred by the user.
