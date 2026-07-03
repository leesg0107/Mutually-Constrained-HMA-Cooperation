# Experiment Design — What Exactly Gets Run

> Date: 2026-07-03. The plain-language definition of the problem and the two experiments,
> as agreed. Companion to `idea-verdict-and-architecture.md` (staged plan) and the
> `garagenet/` harness that implements it.

---

## The problem, in one sentence

> **When a mission hits a heterogeneous robot team, each robot should either DELIBERATE
> (LLM dialogue — seconds of inference latency, but resolves ambiguous/coupled allocation)
> or EXECUTE a pre-trained MARL/MAPF policy immediately (milliseconds, but fails or thrashes
> on coupled tasks) — chosen per robot by the task's coupling — and this beats always-deliberate
> and always-execute on total mission completion time.**

The cost structure that makes this a real question: LLM deliberation adds wall-clock latency
directly to the mission; the learned policy is nearly free to invoke but degrades (slow execution
or failure) as inter-robot coupling/ambiguity rises. "When is deliberation worth its latency?" is
therefore measurable.

---

## Experiment 1 (Phase 0) — the measurement. No mixing yet: same task, whole team uses ONE mechanism

**Environment:** PARTNR (Habitat 3.0), 2–3 heterogeneous robots (e.g., Spot + humanoid), household
cooperation missions. PARTNR's four task categories form the **coupling ladder** (x-axis):
constraint-free → spatial → temporal → heterogeneous-capability.

**One episode, three ways.** Take one task instance, e.g. *"move the cups to the kitchen, then wipe
the table; only the humanoid can reach the top shelf"*, and run it under each arm separately:

- **L0 (whole team deliberates):** per-robot LLM agents negotiate who-does-what-in-which-order,
  then execute. Measured: LLM inference time (deliberation) + movement time (execution).
- **L2 (whole team on policy):** zero deliberation; a pre-trained/scripted coordinator assigns
  skills immediately. Fast on easy tasks; expected to thrash or fail on temporal/heterogeneous ones.
- **L1 (hybrid):** one LLM call fixes the structure ("you take A, you take B, in this order"),
  the policy executes.

**Sweep** the coupling ladder, measure wall-clock completion time **split into deliberation vs
execution**, with success rate as a constraint.

**The falsifiable claim:** the per-arm time curves **cross** — L2 wins at low coupling (deliberation
is wasted latency), L0 wins at high coupling (the policy can't resolve it). **Negative control:** on
an axis that only raises spatial congestion, there must be NO crossing (the policy keeps winning).
Robustness battery: L2-capacity sweep, LLM-backbone latency sweep, statistics over seeds.

The `garagenet/` harness (arms, timing ledger, sweep, crossing detector, plots) is the measurement
instrument for exactly this experiment; the mock env validates the pipeline, and
`partnr_adapter.py` is the slot where PARTNR replaces the mock.

---

## Experiment 2 (Phase 1) — the mixing. Per-agent allocation WITHIN one mission

Once the crossing exists, run **different mechanisms on different robots simultaneously**:

> Wildfire mission: the two drones' "map the burn area" has low coupling → the allocator sends the
> drones out **immediately on the learned policy (L2)** — they do NOT wait for anyone's dialogue.
> The UGV's "transport fallen trees / injured people" is ambiguous (who/what/first) → the allocator
> gives the UGV a **brief LLM deliberation (L0)**. Both happen in parallel; mission time is the
> **makespan** over branches.

**What is compared (each row = one claimed novelty made falsifiable):**

| Comparison | What it proves |
|---|---|
| per-agent allocation vs best **team-uniform** router (whole team L0 or whole team L2) | mixing per robot is where the gain is (**A1**) |
| coupling-gated allocation vs always-decentralized vs always-joint mode selection | the theory's Corollary — coupling decides *where* the mode decision is made (**A2**) |
| allocator vs **oracle** (run every assignment, pick best) | how much of the achievable gain the allocator recovers (gap-to-oracle, the honest number) |
| allocator's own decision latency **charged to the ledger** | a slow router defeats its own thesis — audited, not hidden |

Metrics identical throughout: mission completion time = deliberation + execution (+ routing)
latency, under a success constraint.

---

## At a glance

```
Phase 0 (measure):  same task x [all-L0] vs [all-L1] vs [all-L2]  -> prove the crossing exists
Phase 1 (allocate): one mission, [drones=L2 launch now || UGV=L0 deliberates]
                    -> prove per-agent mixing beats every fixed mode and the team-uniform router
```

The system claim, precisely phrased: **"robots in one team are simultaneously assigned different
cooperation mechanisms (immediate MARL execution ↔ LLM deliberation) according to the coupling
their subtask demands, and that assignment minimizes total mission completion time."** Phase 0's
crossing is the phenomenon that makes this claim possible; Phase 1 is the claim itself.

---

## Scope decision (2026-07-03): no world model in the paper's loop

The paper does NOT require a learned world model. The pipeline's inputs are the mission spec
(branch descriptions, precedence/externality structure, team composition) plus **inter-robot
information sharing** (each robot's estimates and plans visible to the gate/allocator when
escalated). A persistent world model / memory / fine-tuned robot-dialogue LLM belongs to the
GarageNet *platform roadmap* (follow-up work: they shrink deliberation latency and widen L0's
viable region), not to this paper's claims. Implemented accordingly: `garagenet/pipeline.py`
consumes descriptions + structure only.
