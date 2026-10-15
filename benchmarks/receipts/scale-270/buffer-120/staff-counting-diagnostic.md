# Scale-270 economic health — fd708a3063

Outcome: **DIAGNOSTIC_ECONOMIC_FAILURE**

## Identity

- Profile: `runs/acceptance/scale-270-recovery-inventory-120.yaml`
- Completed tick: `120`
- Seed: `42`
- Source commit: `48ecbcd3d3cb6d9518a4c1e57518980b9f025199`

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

- First-window unemployment mean: `0.80293`
- Final-window unemployment mean: `0.734375`
- Latest purchase window: `{"attempts": 12238, "end_tick": 120, "passed": true, "rate": 0.001471, "rejected": 18, "start_tick": 61, "unresolved": 0}`

## Resource summary

- Peak RSS MiB: `1406.65`
- Minimum available memory GiB: `68.39`
- Database growth bytes/tick: `3872631.466667`
- Checkpoint p95 seconds: `2.918095`
