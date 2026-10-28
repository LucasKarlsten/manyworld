# Sweden UBI: experiment specification

Status: **draft v0.1** (design only; no UBI implementation or validated Swedish baseline)
Date: 2026-10-28

## Purpose

Create a 10–15 minute educational demonstration of Universal Basic Income (UBI) in a small, Sweden-inspired agent economy. Follow **five preselected people** through two parallel, comparable worlds, one without UBI and one with it. Show household choices and macroeconomic outcomes side by side. The aim is to *explore model mechanisms*, not to argue for or against UBI or predict Sweden's future.

## Questions

- Who receives money, who finances the reform, and what happens to existing benefits?
- What changes in disposable resources, consumption, debt and savings?
- Do employment, hours worked, job applications, education or business formation change, **if the selected behavior model actually supports those decisions**?
- How do firms respond to demand, staffing, wages and stockouts?
- Which results are robust across seeds, and which depend on assumptions?

## Experimental arms

1. **Control:** Swedish-inspired baseline with no UBI.
2. **Treatment:** The *same* baseline and pre-intervention world, with one explicit UBI policy introduced at a declared tick.

The amount, payment cadence, eligible population, interaction with benefits, tax treatment, and financing must be explicit in configuration and reporting. Initial prototype: **additive, untaxed UBI**, no automatic benefit removal; this is a modeling choice, **not** a claim that it is financially sustainable. Never label that scenario budget-neutral. Later alternatives (benefit replacement, tax-financed UBI) should be distinct experimental arms, not silently folded into the first.

The only intended experimental difference at intervention time is UBI assignment. Subsequent household, firm and fiscal outcomes may diverge. Persist resolved configuration, code commit, engine semantics, seed, pre-intervention checkpoint, intervention tick, model/provider details (if used), and measurement window for every run.

## Swedish inspiration: implement in stages

Distinguish **documented Swedish facts**, **calibration choices**, and **missing mechanics** in every config and chart. Do not apply a nominal municipal tax percentage directly as an effective tax rate.

| Domain | Starting design requirement | Initial state |
| --- | --- | --- |
| Labor | Different employment statuses, job-seeking and actual hours; separately report employment vs. labor-force unemployment | Needs calibration and metric-definition audit |
| Taxes | Simplified progressive income tax with documented assumptions; employer costs only if actually implemented | Missing in chosen recovery benchmark |
| Safety net | Clearly specified unemployment support and household transfers; avoid pretending to replicate all of Försäkringskassan | Missing in chosen recovery benchmark |
| Population | Mixture of workers, job-seekers, students, carers, founders and higher-income individuals | Requires targeted scenario design |
| Firms | Viable hiring, payroll, prices, inventory and shopping fulfillment | Recovery baseline is promising but stockouts remain |
| Currency | Single notional currency for mechanics; Swedish-facing labels only once units and scale are explicitly defined | Benchmark currently USD; **do not silently relabel USD as SEK** |
| Culture | Heterogeneous preferences for work, risk, education and free time, declared as hypotheses | Scripted behavior currently limited |

Public Swedish reference metrics should include source, date, population denominator and definition in a future `ASSUMPTIONS.md`. Real-world calibration is separate from validation of the internal ledger.

## Five tracked lives

Pick **five identifiable agents before intervention** and verify consistent origin identities across arms. Target archetypes (not guaranteed to exist in the seed world):

1. **Unemployed/benefit recipient**: job search, liquidity, training opportunity.
2. **Low-income or precarious worker**: work hours, bargaining, spending.
3. **Median-income household member**: work, taxes, savings, family time.
4. **High-income professional**: net fiscal position, savings, labor choices.
5. **Founder/wealthy owner**: payroll, hiring, demand, firm cash and investment.

Start with data-supported archetypes; do not present an owner of a tiny synthetic firm as a Swedish tech billionaire. Record starting age, household, occupation, income/assets, liabilities and relevant decision rules. If the world cannot represent a persona, either implement the mechanism or explicitly narrow the story.

For each (seed, arm, origin_agent_id, tick), export: account cash, savings, debt, receivables, wages accrued/paid, taxes, benefits, UBI payments, purchases, stockout failures, employment/contract status, job offers/applications, worked time, study and key events. Prefer historical ledger and employment intervals to present-time state. Death/departure is an outcome, not a reason to substitute a new person.

## What the codebase currently supports

Hive's read-only inspection identified paired experimental runs, ledgered transfers and balances, stored employment history, historical household positions, and replay APIs. The default scripted policy does **not** implement a general labor-versus-leisure optimization; income changes can affect liquidity/consumption mechanically, but a simulated decision to reduce hours must come from an explicit, inspectable mechanism.

Hive's 180-day baseline qualification reported:

- Candidate: `runs/life-course-recovery-benchmark.yaml`, standalone, semantics 20, scripted agents, single USD region, **no government tax or benefits**.
- Seed 1: 14 citizens, 3 firms, 9 employee contracts; 0% measured unemployment throughout; all three firms survived; 54 wage payments, no missed wages; ledger and SQLite checks passed.
- Final 60 days: 64 of 576 proposed purchases rejected (11.1%), all reported as stockouts.
- Exact replay and independent twin equivalence **not yet completed**. Qualification outputs are local, ignored `.crew-local/` artifacts, not committed evidence.

These findings are useful engineering checks, **not** proof of a stable Sweden-like economy. A zero-unemployment seed is insufficient for the unemployed persona. The 300-agent SimCity world and its high unemployment are a different profile, not a directly comparable control.

## Build sequence and acceptance gates

### M0: Define and freeze the experiment (this document)
- Agree which real-world features are approximations; use a strict distinction between observed model data and speculative interpretation.
- Fix persona selection rules and export schema before intervention.

### M1: Baseline qualification
- Start from recovery benchmark; add Swedish-inspired mechanisms deliberately and symmetrically.
- Increase population and job availability only with documented assumptions; never force employment outcomes to a desired result.
- Run sufficient warm-up and a minimum 90–180 days over multiple seeds.
- Record job capacity, labor-force denominator, employment, wages, firm survival, operating cash, fulfilled *and unmet affordable* demand, stockouts, ledger reconciliation and state replay.
- Proposed engineering gates: no overdue earned-wage write-offs; firms solvent and trading; reconciliation passes; replay reproduces recorded states; no persistent severe inventory failure. Set thresholds before evaluating candidate runs.

### M2: UBI policy, disabled by default
- Add explicit eligibility, payment amount/currency, interval, start tick, ledger transaction kind and idempotent payment identity.
- Ensure the government account shows deficits honestly; avoid creating funds without recording the corresponding liability/flow.
- Test zero-UBI equivalence, payment cadence, eligibility, balanced postings, retries, replay, and unchanged baseline when disabled.

### M3: Paired experiments
- Same code/version, seed and pre-intervention checkpoint; treatment differs only by UBI.
- Compare multiple paired seeds. Present ranges, not just one cinematic trajectory.
- Check whether post-treatment differences are explained by code mechanics, recorded agent decisions or randomness.

### M4: Presentation / replay
- Synchronized time slider: control on left, UBI on right; five individual life cards and a compact macro strip.
- Label all metrics with units, populations and model provenance.
- Precompute and save experiments; **do not depend on live LLM calls during the 15-minute presentation**.
- Suggested timing: 2 min premise/vote, 8 min paired replay and people, 5 min discussion of assumptions and evidence.

## Deliberate non-goals for v0.1

- A 1:1 replica of Swedish taxes, transfer administration or national economy.
- National forecasts, policy endorsement or statistical causal claims from five people.
- 300 independent LLMs, expensive live model calls, or a bespoke 3D frontend.
- Retuning parameters until the desired pro- or anti-UBI story appears.

## Next small action

Inspect the exact recovery config and define a baseline parameter table plus a small measurement script. Do **not** implement UBI or build a new frontend until a baseline and replay comparison are credible.

## Provenance

Internal technical observations above summarize the user-provided Hive inspection/qualification reports from 2026-10-28. Numeric Swedish calibration values require separately dated primary sources before use. This document is a design plan and has not itself executed a simulation.
