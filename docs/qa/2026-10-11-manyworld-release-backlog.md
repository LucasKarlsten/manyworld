# Manyworld release backlog audit — October 11, 2026

Jira was read live at `alinojoumi8.atlassian.net` using `project = MW ORDER BY key ASC`; the complete page returned 38 issues (`isLast=true`): seven epics and 31 child tasks. No issues were Done: 23 To Do and 15 Blocked, including epics. This records tracker state, not proof that every implementation is missing.

The tracker still references October 8 main `f27005b`. The audited GitHub main is `37d0f486d61ad52bc0deccb3f1a13b23c16d2097`, with no open PRs before this diagnostic change. PRs [126](https://github.com/alinojoumi8/manyworld/pull/126), [127](https://github.com/alinojoumi8/manyworld/pull/127), and [128](https://github.com/alinojoumi8/manyworld/pull/128) are merged. Post-merge CI [38087214153](https://github.com/alinojoumi8/manyworld/actions/runs/38087214153) passed. None of these facts completes a candidate-specific release evidence package.

## Immediate sequence

1. Diagnose checkpoint performance with phase measurements, preserving the 5-second p95 cap and failed runs.
2. Finish the provider-free 120-tick comparison for [GitHub issue 52](https://github.com/alinojoumi8/manyworld/issues/52). The fixed-cohort retry preserved 308 living agents, regions 184/69/55, and exact replay across 130 tables; it failed checkpoint p95 (9.585220 seconds) and purchase rejection (60.5285%, cap 5%).
3. Repair purchase behavior under the maintained versioning and ledger contracts; pass the recovery and 1,000-tick gates before the scoped live-provider and browser/Hermes checks.
4. Reconcile MW-8/MW-9 against merged repairs, then freeze MW-10's candidate and produce MW-11's complete nine-gate local package. Existing branch cleanup does not settle every MW-8 planning or roadmap criterion.
5. Retain the independent connector, hosted, research and final production gates below. A local 100-Hermes rehearsal does not replace MW-14's independent public-HTTPS certification, and the 1,000-tick run does not replace MW-35's 1,000-agent or multi-decade study.

Jira workflow states were left unchanged because their full acceptance criteria have not been established. No deployment, independent certification, or research campaign was executed by this audit. Owners, estimates, dates and separate campaign approvals remain to be settled where the tickets require them.

## Jira inventory

| Issue | Work | State |
| --- | --- | --- |
| [MW-1](https://alinojoumi8.atlassian.net/browse/MW-1) | Establish the current delivery baseline and local release evidence | To Do |
| [MW-2](https://alinojoumi8.atlassian.net/browse/MW-2) | Certify five independent external-agent connectors | To Do |
| [MW-3](https://alinojoumi8.atlassian.net/browse/MW-3) | Validate Commons rollout and hosted resilience | To Do |
| [MW-4](https://alinojoumi8.atlassian.net/browse/MW-4) | Complete live calibration and long-horizon acceptance | To Do |
| [MW-5](https://alinojoumi8.atlassian.net/browse/MW-5) | Complete household, education and economic mechanisms | To Do |
| [MW-6](https://alinojoumi8.atlassian.net/browse/MW-6) | Validate research outcomes and researcher workflows | To Do |
| [MW-7](https://alinojoumi8.atlassian.net/browse/MW-7) | Close final audits and the production release decision | To Do |
| [MW-8](https://alinojoumi8.atlassian.net/browse/MW-8) | Reconcile main, feature branches and the delivery roadmap | To Do |
| [MW-9](https://alinojoumi8.atlassian.net/browse/MW-9) | Verify main's dependency, origin and replay hardening fixes | To Do |
| [MW-10](https://alinojoumi8.atlassian.net/browse/MW-10) | Select and freeze one clean release candidate | To Do |
| [MW-11](https://alinojoumi8.atlassian.net/browse/MW-11) | Produce all nine local reproducibility-v1 receipts | To Do |
| [MW-12](https://alinojoumi8.atlassian.net/browse/MW-12) | Prepare the independent HTTPS certification target and approval records | To Do |
| [MW-13](https://alinojoumi8.atlassian.net/browse/MW-13) | Obtain the independent MCP certification receipt | Blocked |
| [MW-14](https://alinojoumi8.atlassian.net/browse/MW-14) | Obtain the native Hermes HTTPS certification receipt | Blocked |
| [MW-15](https://alinojoumi8.atlassian.net/browse/MW-15) | Obtain the native OpenClaw HTTPS certification receipt | Blocked |
| [MW-16](https://alinojoumi8.atlassian.net/browse/MW-16) | Obtain the independent Python client certification receipt | Blocked |
| [MW-17](https://alinojoumi8.atlassian.net/browse/MW-17) | Obtain the independent TypeScript client certification receipt | Blocked |
| [MW-18](https://alinojoumi8.atlassian.net/browse/MW-18) | Complete the frozen Commons multi-arm experiment | Blocked |
| [MW-19](https://alinojoumi8.atlassian.net/browse/MW-19) | Record hosted Commons UI and privacy acceptance | Blocked |
| [MW-20](https://alinojoumi8.atlassian.net/browse/MW-20) | Record hosted operational readiness for the approved target | Blocked |
| [MW-21](https://alinojoumi8.atlassian.net/browse/MW-21) | Prove hosted backup, cold restore and rollback | Blocked |
| [MW-22](https://alinojoumi8.atlassian.net/browse/MW-22) | Prove hosted tenant isolation, revocation and bounded load | Blocked |
| [MW-23](https://alinojoumi8.atlassian.net/browse/MW-23) | Complete all ten fresh V9 MiniMax Oracle arms | Blocked |
| [MW-24](https://alinojoumi8.atlassian.net/browse/MW-24) | Pass the corrected 30-day live rumor pilot | Blocked |
| [MW-25](https://alinojoumi8.atlassian.net/browse/MW-25) | Complete the separately approved 365-day acceptance campaign | Blocked |
| [MW-26](https://alinojoumi8.atlassian.net/browse/MW-26) | Complete W5 estate, household and cohort acceptance | To Do |
| [MW-27](https://alinojoumi8.atlassian.net/browse/MW-27) | Complete W6 education and labor-capacity contracts | To Do |
| [MW-28](https://alinojoumi8.atlassian.net/browse/MW-28) | Add the remaining W7 production and supplier-network slices | To Do |
| [MW-29](https://alinojoumi8.atlassian.net/browse/MW-29) | Complete W7 housing occupancy, rents and materials-backed construction | To Do |
| [MW-30](https://alinojoumi8.atlassian.net/browse/MW-30) | Complete W8 bank funding regimes and credit-risk contracts | To Do |
| [MW-31](https://alinojoumi8.atlassian.net/browse/MW-31) | Complete W8 firm disclosure, ownership and corporate-action links | To Do |
| [MW-32](https://alinojoumi8.atlassian.net/browse/MW-32) | Verify W0–W3 research eligibility, metrics and dual price benchmarks | To Do |
| [MW-33](https://alinojoumi8.atlassian.net/browse/MW-33) | Complete the City and Price Lab researcher workflow acceptance | To Do |
| [MW-34](https://alinojoumi8.atlassian.net/browse/MW-34) | Evaluate current Jev v4 decision effectiveness and advice rollout | Blocked |
| [MW-35](https://alinojoumi8.atlassian.net/browse/MW-35) | Complete W9 held-out, demographic-horizon and scale validation | To Do |
| [MW-36](https://alinojoumi8.atlassian.net/browse/MW-36) | Complete fresh exact-candidate provenance and supply-chain audits | To Do |
| [MW-37](https://alinojoumi8.atlassian.net/browse/MW-37) | Execute the separately authorized deployment and rollback receipt | Blocked |
| [MW-38](https://alinojoumi8.atlassian.net/browse/MW-38) | Assemble the 16-gate production package and record the release decision | To Do |

## Checkpoint evidence limits

A diagnostic copy of recovery checkpoint tick 119 was resumed for one scripted tick and stopped at tick 120. Preparation took 0.000684 seconds, writer 4.255447 seconds, catalog recording 0.001337 seconds (including 0.000928 seconds retention). Writer profiling measured SQLite backup at 3.192 seconds and manifest generation at 1.036 seconds. Original checkpoint hash was unchanged. Paths and catalog references were rehomed only inside the disposable copy; this is a diagnostic, not acceptance or replay evidence.

This did not reproduce the 9.585220-second outlier and does not establish its cause. The earlier closed-database copy-only trials (2.63–2.73 seconds) also omitted preparation and catalog/retention. Do not replace the failed receipt with these measurements or relax its limit. The harness now records per-checkpoint phase timings for subsequent trials; total checkpoint duration remains authoritative.
