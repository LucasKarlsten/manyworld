# Inventory buffers and demand — 120-tick validation

The approved v2 contract passes the short scripted mechanics prerequisite. Household service adequacy is not certified. Formal 1,000-tick, observatory, live-provider/browser/Hermes and release work remain deferred.

## Demand remains visible

Ticks 60–120: desired 101,848; shadow affordable 89,312; submitted 31,881; fulfilled 31,826. Submitted-unit fill is 99.83% (denominator 31,881 units); fulfilled units relative to shadow affordable demand are 35.63% (denominator 89,312 units).

Guidance limits 57,578 shadow affordable units. Execution losses: stock 55, cash 0, other 0, pre-execution rejection 0. These figures must be considered before extending the experiment; low rejection is not evidence that households receive enough goods.

Desired and affordable demand come from a stock-independent copy of the same scripted policy using a complete local-currency catalog and the ordinary eight-unit cap. Shadow and actual choices can select different sellers/prices, so these quantities are not a nested accounting funnel. Stock and cash execution losses follow settlement order. The receipt includes regional quantities and zero-denominator handling.

| Region / currency | Shadow affordable units | Submitted units | Fulfilled units | Fulfilled / shadow affordable |
| --- | ---: | ---: | ---: | --- |
| 1 / NSD | 49,328 | 22,673 | 22,625 | 45.87% (denominator 49,328 units) |
| 1 / USD | 0 | 0 | 0 | unavailable — denominator 0 units |
| 2 / IVC | 22,576 | 4,358 | 4,355 | 19.29% (denominator 22,576 units) |
| 3 / SCD | 17,408 | 4,850 | 4,846 | 27.84% (denominator 17,408 units) |

## Contract and evidence

[Full CI on the frozen candidate](https://github.com/alinojoumi8/manyworld/actions/runs/38682198493) passed 48 jobs, including all sixteen Linux/Python 3.11 full-suite shards. Skipped jobs: City and price studies against the production backend, Hosted PostgreSQL / S3 integration, Dashboard production build. `candidate-ci.json` records the exact source commit and job outcomes. This is not browser/live-provider or release certification.

Frozen candidate `d7809d11041dc8ec6481e10e408171b51190db41` produced source `f35fc3a790`. It replays exactly across 133 tables; all 17 runtime checks and all 22 economic/integrity checks pass. Repeated canonical JSON/Markdown bytes match, all 48 retained artifact entries verify, and four checkpoint stock snapshots match the daily audit.

In this matched run, the audit leaves economic observations unchanged. The derived canonical comparison matches 127 of 130 common tables; proposals, events and calls retain differences because logical call identities include wall-clock latency. A separate exhaustive raw-row comparison verifies every proposal field and all event/call fields except explicitly named timestamps, call latency and the validated terminal report path. IDs, requests, responses, cache keys, prices and quantities remain equal. These are qualified observational comparisons, not cross-source exact replay. Three optional audit tables are added. Economic settings, population, seed and the 5% rejection limit remain unchanged. The aligned ticks 61–120 still produce 31,672 and sell 31,479 units. The v2 buffer and demand window is ticks 60–120; do not confuse that window with the older final-60-tick totals.

The earlier v2 attempt at `70ece3e` remains failed: checkpoint p95 was 5.148764 seconds against the unchanged 5-second cap. Tick 91 was the sole outlier, with 5.075369 seconds in the writer. The 3 warm copied-source writer trials took 2.806–2.928 seconds and did not reproduce or explain the stall. This candidate adds nested backup, finalization and manifest timings without changing checkpoint operations or the cap. Its pass is evidence for this run, not an established causal performance fix. The derived comparison matches 132 of 133 canonical tables against that source; calls retain wall-clock latency differences. The same separate raw-row projection confirms unchanged economic observations. `checkpoint-phase-parity-proof.json` and `delta.json` retain the exact differences, projection scope and both timing histories. Source-to-replay verification retains its existing canonical rules, including recorded call latency, across all 133 compared tables.

V2 replaces the strict per-firm closing-at-least-opening predicate prospectively. It requires daily conservation, continued production in rolling five-tick windows, no five-tick empty-stock streak, and no five consecutive completed ticks with positive rolling 30-tick net draw and linear stock cover at or below five ticks. Declining windows remain reported. A short pass does not establish long-run sustainability.

| Retained arm | Contract | Original outcome | Purchase rejection |
| --- | --- | --- | ---: |
| always-on-diagnostic | v1 | diagnostic_economic_failure | 8.2741% |
| timing-only-diagnostic | v1 | diagnostic_economic_failure | 5.2911% |
| staff-counting-diagnostic | v1 | diagnostic_economic_failure | 0.1471% |
| replenishment-v1-diagnostic | v1 | diagnostic_economic_failure | 0.0916% |
| buffer-v2-resource-diagnostic | v2 | failed | 0.0916% |
| recovery | v2 | passed | 0.0916% |

All older failed receipts are copied unchanged; the original [diagnostic A/B comparison](../ab-120/README.md) is untouched. Contract versions differ: no earlier failure is retrospectively promoted, and the new verdict is not evidence of an economic improvement over the preceding source. `delta.json` binds the configuration distinction, qualified observational comparison, hashes, checkpoint stock checks and exact denominators.

Raw SQLite sources/checkpoints and per-decision evidence remain private, local, immutable scientific artifacts. Only sanitized aggregate receipts and manifests are committed.
