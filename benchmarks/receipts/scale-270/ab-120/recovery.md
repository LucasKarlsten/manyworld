# Scale-270 economic health — 22602e3a92

Outcome: **DIAGNOSTIC_ECONOMIC_FAILURE**

## Identity

- Profile: `runs/acceptance/scale-270-recovery-120.yaml`
- Completed tick: `120`
- Seed: `42`
- Source commit: `168a0677e124d7daa0c6b9ded7f25738c08d6cf3`

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

## Economic summary

- First-window unemployment mean: `0.80293`
- Final-window unemployment mean: `0.734375`
- Latest purchase window: `{"attempts": 12224, "end_tick": 120, "passed": false, "rate": 0.605285, "rejected": 7399, "start_tick": 61, "unresolved": 0}`

## Resource summary

- Peak RSS MiB: `1392.36`
- Minimum available memory GiB: `89.44`
- Database growth bytes/tick: `3836177.066667`
- Checkpoint p95 seconds: `2.757068`
