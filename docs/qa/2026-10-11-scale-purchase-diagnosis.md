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

New maintained profiles `scale-270-recovery-inventory-120.yaml` and `scale-270-recovery-inventory-1000.yaml` inherit their corresponding original recovery profiles and add only the existing inventory-aware shopping flag. Original baseline/recovery profiles and published failed receipts remain intact. Receipt evaluation recognizes each new profile explicitly and still binds persisted/effective configuration, horizon, population, semantics, artifacts and every original threshold. The repaired recovery is a configuration intervention; it is not the original policy-only A/B comparison.

No engine or policy implementation changes are required for this candidate. The existing opt-in flag is persisted and replayed already; historical configurations remain unchanged, so no new semantics version is introduced. Component tests cover shared-snapshot stock exhaustion, both population tiers, partial fill/rejection, inventory conservation and ledger reconciliation. A fresh source/replay must pass every 120-tick gate before Stage 4 closes; this one-tick diagnostic establishes no long-horizon result. The formal 1,000-tick and live/browser/Hermes checks remain later gates.
