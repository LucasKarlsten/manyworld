# Inventory buffers and independent demand, contract v2

Status: approved direction, implementation contract. The user approved ordinary
inventory buffers and separate demand measurement on October 14, 2026. This
amends the Stage 4 inventory predicate prospectively. The original v1 profiles,
receipts and failed experiments retain their original meaning and hashes.

## Scope and compatibility

Add a new `scale-270-recovery-buffer-120` profile extending the frozen inventory
repair profile. Keep its headcount, wages, shopping guidance, seed, population,
provider routes and every unrelated acceptance threshold unchanged. The
acceptance configuration and receipt identify contract version 2. Do not
overwrite the old inventory profile or reclassify an old result.

The instrumentation is explicitly enabled only for the maintained scripted
semantics-7 lane. It records observations, not economic effects. It does not
change orders, prices, money, production, prompts or random streams. Existing
runs without this opt-in retain their output. Three additive, opt-in audit tables
are included in exact replay; they are never excluded from comparison. No
source database is migrated during read-only evaluation.

The 1,000-tick experiment, observatory/viewer, browser/live-provider/Hermes tests
and release remain deferred. A 120-tick pass is limited evidence of these
mechanics, not proof of long-run sustainability or household welfare.

## Inventory acceptance

Record independent opening and closing stock for every active goods firm on
every tick, together with region and currency. For the complete measured
interval, require nonnegative integer stocks, a stable firm/region cohort,
opening equal to the previous close, exact daily conservation
`opening + production - goods sales = closing`, and agreement with terminal
firm rows. Unknown stock movements fail closed in this deliberately narrow
lane. Production and sales are derived independently from persisted events.

Keep continued production: every active goods firm must produce within each
complete five-tick response interval after warm-up. Permit ordinary temporary
drawdown and intermittent sell-outs. Fail a firm or region with five consecutive
zero closing stocks. For every rolling 30-tick interval, report positive net
draw (`sales - production`) and linear ticks-to-empty (`close * 30 / net draw`).
This is a diagnostic extrapolation, not a forecast. Fail sustained depletion
when net draw is positive and linear coverage is at most the five-tick response
horizon on five consecutive completed ticks. Confirming across a response
interval permits an isolated sell-out followed by replenishment. Check every
possible interval after warm-up, per firm and per region. Tick 60 is the first
measured day, tick 89 the first complete 30-tick endpoint; the earliest
confirmed low-cover streak can end at tick 93. A nonpositive draw or coverage
above the response horizon resets the streak. Large initial buffers
may run down while still covering the response horizon. Regional aggregation
cannot excuse a failing firm. Slow depletion is reported even when not unsafe
within this response horizon; it remains relevant to the deferred longer run.

The five- and 30-tick horizons come from the pinned recovery policy's existing
`demand_buffer_ticks` and `sales_observation_ticks`. They are defined before the
new experiment; they are not chosen from the three earlier endpoint shortfalls.
No percentage tolerance is added to conservation. Record the exact failing
intervals and show opening, production, sales, close and buffer coverage.

## Demand measurement

For every scheduled decision, record a stock-independent scripted-policy probe
at decision preparation. Use the same context, seed and competing priorities,
but the complete active local-currency goods catalog sorted by firm ID,
uniform hypothetical stock of eight per seller and the ordinary eight-unit cap.
Instrument the consumption branch of
the pure policy to report desired units (eight when that branch is eligible),
the existing spending budget and liquidity guard, the selected price, and
affordable units. A preempted/institutional decision is explicitly distinguished
from an eligible shopper. An empty catalog is an unpriced demand observation,
not zero desired demand. This is the scripted policy's demand, not an empirical
human need or a claim about live-model intent.

Persist the scheduled agent IDs so missing, duplicate or malformed observations
fail closed. Reconcile actual submitted quantities and rejected/partial orders
from `action_proposals` with fulfilled `goods_sale` quantities, per buyer/tick.
Capture purchase-time stock, price and checking cash in a third audit table to
separate stock clipping from affordability clipping for partial or rejected
orders. Bind the pre-clamp request and outcome to the immutable action-proposal
ID. Reconcile each dispatched proposal exactly once. Stock-then-cash losses
follow the executor's ordering; both constraints can bind. Other validation
failures remain separate. Audit snapshot/cohort/probe
retries are idempotent only for identical payloads; mismatches fail.
Report desired, affordable, submitted and fulfilled quantities separately,
including affordability loss, the quantity limited by guidance, unsubmitted
affordable demand, and execution shortfall. Do not attribute every unsubmitted
unit to a stockout: seller selection and competing actions can differ. The
shadow and actual decisions can select different prices; these quantities are
not a nested accounting funnel. Show orders above shadow affordable demand
separately and label shadow fill ratios accordingly (they may exceed one).

Publish unit fill rates with their exact denominators, including regional
breakdowns and zero-denominator handling. Preserve the original 5% attempt
rejection gate. Demand measurement completeness is a new mandatory integrity
gate. Demand adequacy is explicitly reported, not silently certified by the
attempt-rejection gate or by lowering a demand target. No new household-service
percentage is invented in this amendment. If the measurements show material
unserved demand, report it prominently before deciding the deferred work.

## Validation and integration

Write failing boundary tests before implementation: temporary drawdown/recovery,
persistent depletion, persistent empty stock, hidden regional/firm shortages,
missing/negative/inconsistent snapshots, uncensored demand with no stock,
affordability, guidance suppression, preemption, partial fills and rejected
orders. Verify default-off compatibility, unchanged decisions, ledger
reconciliation and exact source/replay including all three audit tables.

Obtain independent review of the contract and implementation. Run affected
regressions, then freeze the candidate SHA and run a fresh provider-free
120-tick source/replay without competing heavy jobs. Verify all runtime checks,
all economic/integrity checks, immutable source, complete artifact hashes and
byte-identical repeated report generation. Retain failed attempts separately.
Publish the contract distinction with the delta report; v1 and v2 inventory
verdicts are not directly comparable.

Only promote Stage 4 after a fresh passing result, required local checks,
independent review, exact-head CI, merge and post-merge verification. If a new
failure reveals another policy choice, preserve it and report the boundary;
do not tune targets to manufacture a pass.
