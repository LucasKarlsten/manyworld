# 120-tick provider-free A/B — October 11, 2026

This comparison is operationally valid and **fails economic acceptance**. Recovery improves the baseline but still rejects 60.5285% of purchases in the final window, above the unchanged 5% cap. It does not close Stage 4, authorize the formal 1,000-tick run, or establish release readiness.

Both arms ran at commit `168a0677e124d7daa0c6b9ded7f25738c08d6cf3`, tree `5938a598af02d4db1d4e895d927b103e24db3664`, after [post-merge CI](https://github.com/alinojoumi8/manyworld/actions/runs/38129899677) passed. Each completed 120 ticks with seed 42, semantics 7, 308 living agents, 100 core/208 periphery agents, and regional counts 184/69/55. Exact replay compares 130 tables with no differences. All operational, artifact, integrity, resource, checkpoint and communication checks pass. Only the `supply_recovery` policy differs between effective arm configurations.

| Measure | Baseline | Recovery |
| --- | ---: | ---: |
| Final-window purchases rejected / attempted | 10,990 / 11,587 | 7,399 / 12,224 |
| Final-window purchase rejection | 94.8477% | 60.5285% |
| First-window mean unemployment | 79.4010% | 80.2930% |
| Final-window mean unemployment | 88.8021% | 73.4375% |
| Checkpoint p95, 18 samples, cap 5 s | 4.661407 s | 2.757068 s |
| Peak process RSS, cap 2,048 MiB | 1,319.21 MiB | 1,392.36 MiB |
| Database growth per tick, cap 8,388,608 bytes | 3,682,816 bytes | 3,836,177.066667 bytes |
| Minimum available RAM, floor 8 GiB | 90.23 GiB | 89.44 GiB |
| Scripted calls | 15,229 | 15,070 |
| Paid spend | USD 0 | USD 0 |

Both economic receipts return `diagnostic_economic_failure` (CLI exit 10), because both maintained 120-tick profiles are diagnostic profiles and every operational check passes. Baseline fails six economic checks; recovery fails only `purchase_windows_healthy`. The aggregate correctly remains `failed`, with `recovery_outcome_valid` and `recovery_economic_health` false. Exact replay does not substitute for economic acceptance. The canonical receipts and comparison retain the full gate evidence and deltas.

## Artifacts and verification

- [Baseline runtime](baseline.runtime.json), [economic receipt](baseline.json), and [rendering](baseline.md).
- [Recovery runtime](recovery.runtime.json), [economic receipt](recovery.json), and [rendering](recovery.md).
- [Canonical comparison](comparison.json) and [rendering](comparison.md).

The runtime receipts bind configuration hashes, source/replay hashes, checkpoint manifests, resource measurements and the tested source commit. Repeated immutable re-evaluation reproduced both economic JSON receipts byte-for-byte. All 96 source/replay artifact entries were checked against their original sizes, SHA-256 hashes and explicit absent sidecars. Run IDs are `12b077fde7` / `replay-12b077fde7-cecbb2c120` and `22602e3a92` / `replay-22602e3a92-2b506c3e74`.

SQLite bodies, private logs and earlier failed attempts remain local under ignored `reports/out/scale-270/`. The first attempt failed regional population; the second failed checkpoint p95 at 9.585220 s as well as purchases. Neither was promoted as a valid comparison or overwritten. This third, instrumented attempt does not establish the cause of the earlier checkpoint stall. In the copied tick-119 diagnostic fixture, missing historical checkpoint files were removed from its catalog; its retention workload differed from the failed source, so its short retention time does not rule out an original deletion stall. Total checkpoint duration and its 5-second cap remain authoritative.

## Commands

These are the executed CLI arguments with the interpreter normalized to a checkout's `.venv/bin/python`. Run from the tested checkout; a fresh reproduction requires a new empty `AB_ROOT` and will generate different run IDs.

```bash
AB_ROOT=reports/out/scale-270/ab-120-phases-20261011
.venv/bin/python scripts/run_scale_validation.py \
  --profile runs/acceptance/scale-270-baseline-120.yaml --ticks 120 \
  --label baseline-120 --output-dir "$AB_ROOT/baseline-output" \
  --data-dir "$AB_ROOT/baseline-data"
.venv/bin/python scripts/run_scale_validation.py \
  --profile runs/acceptance/scale-270-recovery-120.yaml --ticks 120 \
  --label recovery-120 --output-dir "$AB_ROOT/recovery-output" \
  --data-dir "$AB_ROOT/recovery-data"
.venv/bin/python -m reports.scale_economic_health \
  --source "$AB_ROOT/baseline-data/source/12b077fde7.db" \
  --replay "$AB_ROOT/baseline-data/replay/replay-12b077fde7-cecbb2c120.db" \
  --runtime-receipt "$AB_ROOT/baseline-output/baseline-120-12b077fde7.runtime.json" \
  --output "$AB_ROOT/sanitized/baseline"
.venv/bin/python -m reports.scale_economic_health \
  --source "$AB_ROOT/recovery-data/source/22602e3a92.db" \
  --replay "$AB_ROOT/recovery-data/replay/replay-22602e3a92-2b506c3e74.db" \
  --runtime-receipt "$AB_ROOT/recovery-output/recovery-120-22602e3a92.runtime.json" \
  --output "$AB_ROOT/sanitized/recovery"
```

Regenerate the aggregate from the published economic receipts with:

```bash
.venv/bin/python - <<'PY'
import json
from pathlib import Path
from reports.scale_economic_health import write_scale_ab_receipt
root = Path("benchmarks/receipts/scale-270/ab-120")
arms = [json.loads((root / f"{arm}.json").read_text()) for arm in ("baseline", "recovery")]
write_scale_ab_receipt(*arms, output=root / "comparison")
PY
```

Both evaluator invocations intentionally exit 10. The local orchestration initially expected exit 5 for an economically failing recovery diagnostic; that assertion was corrected after inspecting the saved outcome. No simulation was rerun for that orchestration error. The aggregate is generated through `reports.scale_economic_health.write_scale_ab_receipt`; a failed recovery remains failed in the aggregate. This evidence change fixes that helper to exclude only `checkpoint_dir` and `report_dir` from policy comparison. The original helper incorrectly compared separate artifact roots; its original failed aggregate is preserved locally. Cadence, retention, resource limits and every other effective setting remain compared. No simulation behavior, receipt hash, economic threshold or stored run was changed.

Next: diagnose persisted purchase rejections and add a governed fix with rejection, success, reconciliation and replay regressions. A fresh post-fix recovery must pass every gate before formal or live testing proceeds. [Issue 52](https://github.com/alinojoumi8/manyworld/issues/52) tracks the sequence; the [Atlassian audit](../../../../docs/qa/2026-10-11-manyworld-release-backlog.md) records the wider backlog.
