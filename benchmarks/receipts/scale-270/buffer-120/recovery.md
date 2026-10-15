# Scale-270 economic health — f35fc3a790

Outcome: **PASSED**

## Identity

- Profile: `runs/acceptance/scale-270-recovery-buffer-120.yaml`
- Completed tick: `120`
- Seed: `42`
- Source commit: `d7809d11041dc8ec6481e10e408171b51190db41`

## Gates

- [x] `runtime_receipt_safe`
- [x] `identity_exact`
- [x] `horizon_completed`
- [x] `population_exact`
- [x] `communications_exact`
- [x] `provider_and_spend_exact`
- [x] `purchase_windows_healthy`
- [x] `unemployment_rebound_bounded`
- [x] `unemployment_final_mean_not_worse`
- [x] `production_and_inventory_healthy`
- [x] `unit_economics_valid`
- [x] `managed_insolvency_absent`
- [x] `labor_backlog_bounded`
- [x] `employment_currency_and_terms_valid`
- [x] `ledger_reconciles`
- [x] `sqlite_integrity`
- [x] `checkpoints_valid`
- [x] `exact_replay`
- [x] `source_immutable`
- [x] `resources_within_caps`
- [x] `demand_measurement_complete`
- [x] `inventory_accounting_valid`

## Economic summary

- First-window unemployment mean: `0.788216`
- Final-window unemployment mean: `0.6875`
- Latest purchase window: `{"attempts": 12014, "end_tick": 120, "passed": true, "rate": 0.000916, "rejected": 11, "start_tick": 61, "unresolved": 0}`

## Resource summary

- Peak RSS MiB: `1407.07`
- Minimum available memory GiB: `63.57`
- Database growth bytes/tick: `3960968.533333`
- Checkpoint p95 seconds: `2.944941`

## Contract v2: buffers and independent demand

Inventory buffers may be drawn down. Conservation, continued production, persistent empty stock and sustained depletion are checked per firm and region.

**Household demand adequacy is not certified.** Desired/affordable quantities are a stock-independent scripted-policy probe; actual seller choices can differ. The rejection gate alone cannot establish adequate service.

| Scope | Desired | Affordable | Submitted | Fulfilled | Limited by guidance | Unsubmitted affordable | Execution stock loss | Execution cash loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All regions | 101848 | 89312 | 31881 | 31826 | 57578 | 57905 | 55 | 0 |
| Region 1 (NSD) | 61864 | 49328 | 22673 | 22625 | 26802 | 27129 | 48 | 0 |
| Region 1 (USD) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Region 2 (IVC) | 22576 | 22576 | 4358 | 4355 | 18218 | 18218 | 3 | 0 |
| Region 3 (SCD) | 17408 | 17408 | 4850 | 4846 | 12558 | 12558 | 4 | 0 |

Inventory observation window: `[60, 120]`.
Declining windows and linear buffer coverage are retained in the JSON receipt. A short pass does not establish long-run sustainability.
