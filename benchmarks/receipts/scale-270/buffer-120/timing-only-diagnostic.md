# Scale-270 economic health — 21eb569b27

Outcome: **DIAGNOSTIC_ECONOMIC_FAILURE**

## Identity

- Profile: `runs/acceptance/scale-270-recovery-inventory-120.yaml`
- Completed tick: `120`
- Seed: `42`
- Source commit: `fc4c55d3e46e4328ed2e1aa689b0c3d5c0e8e828`

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

- First-window unemployment mean: `0.80293`
- Final-window unemployment mean: `0.734375`
- Latest purchase window: `{"attempts": 12228, "end_tick": 120, "passed": false, "rate": 0.052911, "rejected": 647, "start_tick": 61, "unresolved": 0}`

## Resource summary

- Peak RSS MiB: `1409.21`
- Minimum available memory GiB: `72.08`
- Database growth bytes/tick: `3872836.266667`
- Checkpoint p95 seconds: `3.722033`
