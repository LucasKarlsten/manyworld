# Milestone 2 — Five Lives, One Reform

Status: **prototype design**. No LLM personas or decision tracing are implemented by this document.

## Audience experience (10–15 minute presentation)

- **Day 0–4**: one ordinary pre-policy world. Introduce five named people, their actual starting conditions, and current actions.
- **Day 5**: the state announces and activates the UBI policy. The control world remains unchanged. The treatment world pays the first benefit on tick 5.
- **Day 6+**: select a person; follow their actions and outcomes side-by-side in the two runs. Show actual transaction/account/employment evidence, not generated storytelling.
- **Explore**: the audience selects personas and timeline events. Highlight the distinction between what an agent *wanted* and what the economy *executed*.

## Persona specifications (narrative templates, NOT populated agent records)

| Persona | Intended circumstances | Decision tensions | Required mechanics |
|---|---|---|---|
| Marcus | Unemployed adult, benefit-dependent | Job search vs. education; economic security | Real unemployment, applications, jobs, training |
| Sara | Lower-income, insecure employment | Extra shifts vs. stability | Work hours or shift choice, job offers |
| Johan | Middle-income worker | Work vs. family time and savings | Earnings, budget and optionally hours |
| Helena | Higher-income professional | Tax burden, savings, consumption | Higher wage, taxes, investment |
| Alexander | Firm founder and owner | Hiring and investment decisions | Real firm ownership, firm ledger, hiring |

Do **not** claim the current 14-citizen seed implements these personas. Select or create their records before filming/demo; validate actual income/status/ownership. No invented household structures, unemployment or skills.

## Behavioral contract (for a later LLM adapter)

The LLM receives: personal immutable profile, recent *observed* state, available legal actions with constraints, relevant public policy, and brief prior decisions. It returns a **structured action proposal** and a short public-facing explanation. It cannot directly change a balance, claim a job or invent a degree.

The engine validates and either executes or rejects the proposal with a reason. Save: tick, stable agent id, arm, proposed action, explanation, accepted/rejected, engine event ids, and state delta. Avoid storing private reasoning or credentials.

Sample action families to audit in Manyworld before implementation:
- buy / save / repay debt
- job search / accept job / adjust working time
- seek training
- invest / hire / change price

Only expose actions the engine actually supports. Unsupported intentions are not observed outcomes.

## Experimental integrity

1. Create baseline genesis and run **through tick 4**, with no UBI in either branch.
2. **Required before causal claims:** fork the *same* persisted tick-4 checkpoint to the two arms. Verify identical agent/account/employment state hashes at the split.
3. Activate reform on tick 5 only in treatment; emit an auditable policy event. UBI ledger posts must balance.
4. Use identical model/provider, persona profile, model temperature policy and decision cadence across worlds. Expect stochastic divergence; report multiple seeds.
5. Treatment is **additive, deficit-financed model USD** unless specifically redesigned. No Swedish calibration claims.
6. Never claim a difference in employment or education unless the simulator implements and logs the corresponding choices.

## Current minimal day-5 smoke test

Two new scenario configs: `runs/sweden-day5-control.yaml` and `runs/sweden-day5-ubi.yaml`.

```bash
python3 run.py --config runs/sweden-day5-control.yaml --ticks 40
python3 run.py --config runs/sweden-day5-ubi.yaml --ticks 40
```

Expected on treatment: UBI at ticks **5 and 35** for all eligible locals; expected in control: zero UBI payments. This checks scheduling and bookkeeping only.

**Known limitation:** these are independent fresh runs with a common seed, **not** a shared-checkpoint split; there are no actual LLM personas or interactive replay yet. The existing Sweden comparator can inspect the runs once generated.

## Next implementation gate

Audit the current action router, stored events and agents schema. Create a real five-person cohort with stable identities and a structured decision log. Only then implement an LLM adapter and finally the interactive replay UI.
