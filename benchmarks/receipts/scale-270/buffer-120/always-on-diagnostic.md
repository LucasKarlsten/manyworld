# Scale-270 economic health — 7ce4c5cc41

Outcome: **DIAGNOSTIC_ECONOMIC_FAILURE**

## Identity

- Profile: `runs/acceptance/scale-270-recovery-inventory-120.yaml`
- Completed tick: `120`
- Seed: `42`
- Source commit: `559301d11b2f0242f3d180a77c0823932353090f`

## Gates

- [x] `runtime_receipt_safe`
- [x] `identity_exact`
- [x] `horizon_completed`
- [x] `population_exact`
- [x] `communications_exact`
- [x] `provider_and_spend_exact`
- [ ] `purchase_windows_healthy`
- [x] `unemployment_rebound_bounded`
- [x] `unemployment_final_mean_not_worse`
- [ ] `production_and_inventory_healthy`
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

## Economic summary

- First-window unemployment mean: `0.846029`
- Final-window unemployment mean: `0.780078`
- Latest purchase window: `{"attempts": 12944, "end_tick": 120, "passed": false, "rate": 0.082741, "rejected": 1071, "start_tick": 61, "unresolved": 0}`

## Resource summary

- Peak RSS MiB: `1418.68`
- Minimum available memory GiB: `79.03`
- Database growth bytes/tick: `3894852.266667`
- Checkpoint p95 seconds: `4.707457`
