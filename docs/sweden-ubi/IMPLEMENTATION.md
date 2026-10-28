# UBI implementation status (2026-10-28)

**Prototype committed; execution not verified.** This work was performed via GitHub connector, without access to the user's WSL environment or installed dependencies.

## Delivered

- `engine/government.py`: opt-in, adult citizen UBI payment integrated into the fiscal nightly phase; balanced checking/government ledger legs; per-recipient transaction memo and existing-transaction guard; logged events.
- `runs/sweden-baseline.yaml`: inherits existing life-course recovery profile with a government and frozen fiscal election mechanism.
- `runs/sweden-ubi.yaml`: inherits the baseline and turns on an additive, untaxed 30-tick payment starting at tick 30.

## Important caveats

- The settings are **NOT Swedish tax calibration**. Flat 30% withholding was selected as an illustrative placeholder. Inherited currency remains USD and **15,000 model dollars is not 15,000 SEK**. Real Swedish taxes, jobseeking behavior and social insurance are not implemented.
- Model-level UBI is **not yet wired into a native paired-experiment manifest**. These two YAMLs can be run independently, but equal seeds alone do not guarantee matched initial states across policy changes.
- Current recovery seed may have zero unemployed citizens. Five target personas are **not yet constructed**.
- Replay, cross-run equivalence, payment assertions, financial reporting, and 90/180-tick requalification **remain to be tested**.
- This prototype does not try to model a balanced budget; negative treasury balances represent deficits. Adding UBI does not replace unemployment benefits.
- The existing fiscal configuration merge mechanism must be checked with a config loader smoke test, especially nested sections.

## Local smoke test

```bash
git switch feature/sweden-ubi
git pull fork feature/sweden-ubi    # substitute origin if your remote differs
python run.py --config runs/sweden-baseline.yaml --ticks 35
python run.py --config runs/sweden-ubi.yaml --ticks 35
```

Use independent run data paths if the CLI would otherwise reuse existing data. Inspect each run's transaction ledger for `ubi_payment` at tick 30 (none in control), and run the built-in reconciliation checks. Check configured age eligibility and that treasury and checking movements offset exactly. Verify no UBI payment before tick 30.

## Next acceptance checks

1. Baseline with fiscal layer produces no regressions in payroll/solvency.
2. Treatment: one payment for each eligible citizen at ticks 30, 60, 90... and none for minors.
3. Re-executing due-tick payment does not duplicate transactions.
4. Ledger per-currency sum and cached balances reconcile.
5. Compare common pre-intervention checkpoint, not just equal seed.
6. Add structured outcomes and five origin-matched personas before presentation.
