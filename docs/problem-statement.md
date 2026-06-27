# GarageNet — Problem Statement & Paper Outline

> Task-difficulty-gated coordination-mechanism routing for heterogeneous multi-robot teams.
> Date: 2026-06-27. Companion to `related-work-and-gap-analysis.md` (3 rounds of scooping check).
> Status: **framing / pre-experiment**. This document defines the problem, the L0–L2 construct,
> the metareasoning formalization, and the experimental protocol — not yet results.

---

## 1. One-paragraph problem statement

When a mission is issued to a **heterogeneous robot team** (each robot holding reusable skills —
map, scout, pick-and-place, transport, manipulate), the team must **finish decision-making as fast
as possible and complete the mission in minimum time**. Routing *every* decision through LLM
deliberation is too slow (inference latency dominates); routing *nothing* through deliberation
fails on ambiguous, divergent-goal tasks that need negotiation. The right amount and *kind* of
coordination depends on the **task's required coupling / difficulty**. GarageNet is a
**deployment-time router** that, per (sub)task, selects the **coordination MECHANISM** — LLM
deliberation (L0) / hybrid (L1) / pre-trained MARL-MAPF policy (L2) — so as to **minimize total
time = deliberation time + execution time**, subject to a success constraint. This is precisely a
**value-of-computation (VOC) / metareasoning** decision ("is deliberation worth its latency here?")
lifted from the single agent to the **robot team** and from "how long to think" to "**which
coordination mechanism to run**."

---

## 2. Why this matters (motivation)

- **The latency wall.** LLM-multi-robot systems (COHERENT, EMOS, SMART-LLM, CLiMRS) put deliberation
  on the critical path of *every* coordination step. For time-critical missions (wildfire, SAR) this
  is the binding cost — yet the field measures success/tokens/steps, almost never **wall-clock time**.
- **Tasks are not uniform.** A drone sweeping a burn area for mapping is a tightly-coupled,
  role-predefined problem solvable by a pre-trained MAPF/MARL policy in milliseconds — deliberating
  about it wastes the very time the mission cannot spare. Allocating "who maps, who transports, where
  to stage the injured" under ambiguity is a divergent-goal problem that *needs* negotiation.
- **Nobody routes by this axis.** Existing systems are single-paradigm (always deliberate) or fuse
  paradigms only at *training* time (MARLIN). The deliberate-vs-execute *mechanism* choice, made at
  deployment and gated by task difficulty with a *time* objective, is unoccupied (see gap analysis).

**Running example (used throughout the paper).** Wildfire suppression. Team = 1 heavy-equipment UGV
+ 2 UAV drones. Ideal: drones *immediately* run a pre-trained mapping/coverage policy (**L2**, no
deliberation) over the burn area and gather state; the heavy robot is *allocated* fallen-tree /
injured-person transport via brief negotiation (**L0/L1**) only where assignment is genuinely
ambiguous; everything coordinated for minimum total mission time.

---

## 3. The L0–L2 construct — formal definition

> **Design note (answers the reviewer's "why discrete levels?").** The discretization is an
> *operationalization*, not the scientific claim. The claim is that **a single per-task gating
> decision — deliberate vs. execute — has measurable value-of-computation that varies with task
> coupling**. L0/L1/L2 are three operating points on an underlying *deliberation-intensity*
> continuum, chosen because (a) they correspond to three *mechanically distinct* execution paths
> (full LLM dialogue / mixed / pure learned policy) with order-of-magnitude-different latency, and
> (b) Sliding Autonomy (Sellner et al. 2006) empirically showed a *small discrete* mode set captures
> most of the benefit of a continuum while staying controllable. We report the continuous trade-off
> (time-vs-difficulty per mode) so the discretization is auditable, not assumed.

Let a mission decompose into (sub)tasks `τ`. Each `τ` has a **required-coupling level** `c(τ)`
grounded in the iTax interdependence axis (Korsah, Stentz & Dias 2013):

| Level | Coordination mechanism | iTax coupling analogue | Task character | Latency profile |
|-------|------------------------|------------------------|----------------|-----------------|
| **L0** | **LLM deliberation / negotiation** (inter-robot dialogue) | XD/CD — cross-schedule / complex interdependence, ambiguous utilities | High-abstraction, divergent-goal, allocation under ambiguity ("plan the trip") | **High** (seconds; multiple inference rounds) |
| **L1** | **Hybrid** — LLM sets high-level structure, learned policy executes | ID/XD — in-/cross-schedule, structured but coupled | Structured-but-coupled; needs a plan *and* tight execution | **Medium** (one-shot LLM + fast policy) |
| **L2** | **Pre-trained MARL / MAPF policy** (no deliberation) | ND/ID — no/in-schedule deps, roles predefined | Tightly-coupled, role-predefined, reactive ("wolf pack hunt") | **Low** (policy forward pass, ms) |

`c(τ)` is **not** "how hard to execute" — it is **how much inter-robot coupling the decision
requires**, which is what determines whether deliberation pays off.

---

## 4. Formalization as team metareasoning (the theory anchor)

Ground the objective in **value of computation** (Russell & Wefald; Boddy & Dean 1989; Hansen &
Zilberstein 2001; Lin et al. 2015). For a (sub)task `τ` and candidate mechanism `m ∈ {L0, L1, L2}`:

- Let `T_deliberate(m, τ)` = expected deliberation/inference latency of mechanism `m` on `τ`.
- Let `T_execute(m, τ)` = expected execution time of the plan/policy `m` produces on `τ`.
- Let `p_success(m, τ)` = probability `m` completes `τ`.

**Router objective (per task):**
```
m*(τ) = argmin_m  E[ T_deliberate(m,τ) + T_execute(m,τ) ]   s.t.  p_success(m,τ) ≥ 1−δ
```
At the **mission** level, sum/critical-path over tasks under team resource & dependency constraints
(this is where heterogeneity and parallelism enter: drones' L2 mapping runs concurrently with the
UGV's L0/L1 allocation).

**The crux (the design question round 3 surfaced).** The router needs a **gating signal**
`ĉ(τ)` predicting `c(τ)` *cheaply and a priori*. Three candidate designs to evaluate:
1. **Taxonomy-rule gate** — classify `τ` into iTax ND/ID/XD/CD via task metadata → fixed mode. Zero
   added latency, no learning; the interpretable baseline.
2. **Learned lightweight gate** — a small classifier/policy mapping task features → mechanism,
   trained to optimize the time objective (analogue of Paglieri "Learning When to Plan", IBM "When
   to Reason", lifted to the team mechanism choice).
3. **Cheap-deliberation probe** — a single fast LLM call estimates coupling, then routes. **Must
   account for the probe's own latency in `T_deliberate`** — a router whose routing is slow defeats
   the purpose. This is the sharpest internal risk; measure it explicitly.

**Load-bearing novelty boundary:** the entire metareasoning lineage is single-agent or
single-LLM-query-routing. GarageNet's novelty = **(team) × (mechanism choice, not compute-budget) ×
(difficulty/coupling trigger) × (measured completion time)**. If any one collapses, a neighbor covers it.

---

## 5. Contributions (claimed)

C1. **A deployment-time coordination-mechanism router** for heterogeneous teams that selects L0/L1/L2
    per task by required coupling — the first to make the deliberate-vs-learned-policy choice at
    inference time, gated by task difficulty. *(no prior system; MARLIN is training-time)*

C2. **A VOC/metareasoning formulation** of multi-robot coordination-mode selection (§4), bringing the
    bounded-rationality lineage to robot *teams* (vs. the single-agent prior art).

C3. **The first empirical characterization of completion TIME per cooperation mode across a graded
    difficulty axis** — turning "which mode is faster" into measured curves. *(field measures
    tokens/steps/success, not time)*

C4. *(stretch)* **A coupling→mechanism mapping grounded in iTax** — the descriptive interdependence
    taxonomy turned prescriptive. *(must be built; no prior mapping exists)*

---

## 6. Experimental protocol

**Core experiment (validates C3, the empirical heart).** For the *same* task instances, run **all
three mechanisms** (L0 full LLM dialogue / L1 hybrid / L2 pre-trained policy) and an **oracle router**
and the **learned router**, measuring:

- **Primary metric: wall-clock completion time** = deliberation latency + execution time (report both
  components separately — the deliberation/execution split is the paper's signature plot).
- Secondary: success rate, sub-goal completion, tokens (for comparability with prior LLM-MR work).
- **Sweep a difficulty/coupling axis** → produce **time-vs-difficulty curves per mode**. The
  predicted crossing points (L2 wins at low coupling, L0 wins at high coupling, L1 between) are the
  falsifiable claim.

> **⚠️ Critical design insight (from benchmark feasibility study, `benchmark-feasibility.md` §4):**
> the difficulty axis MUST be one the **learned policy degrades on** — *reasoning/allocation
> complexity* (task novelty, goal ambiguity, heterogeneous-capability, temporal-ordering), **not
> pure spatial congestion**. On congestion alone an optimal MAPF/MARL policy wins at all levels and
> the LLM never wins → **no crossing**. The crossing exists only where a fixed policy fails but
> reasoning succeeds. State this explicitly to pre-empt "your crossing is a degenerate-axis artifact."

**Benchmark decision (from the feasibility study).** Primary = **PARTNR** (Habitat 3.0): only
candidate with both an LLM-dialogue arm and a learned arm on the same heterogeneous tasks, and its
task-type ladder (constraint-free → spatial → temporal → heterogeneous) is a *reasoning-coupling*
axis — the right instrument for the crossing. Build items: (1) wall-clock instrumentation [low];
(2) a genuine learned high-level **coordination** arm — PARTNR's only non-LLM coordinator is a
heuristic planner, so wrap a MAPF/MARL controller as the L2 arm [medium-high, the real cost];
(3) graded coupling axis [medium]. Fallbacks: **EMOS/Habitat-MAS** (real UAV-UGV drone+ground mix,
but learned arm unconfirmed) and **RWARE** (clean knobs, trivial timing, but no LLM arm + congestion
≠ crossing). Wildfire/UAV-UGV outdoor = custom build (Tier-3 demo). No prior work measures
LLM-vs-learned completion time across difficulty → measurement contribution un-scooped.

**Headline result to aim for:** the router tracks the lower envelope of the per-mode time curves at
near-zero routing overhead — i.e., difficulty-gated routing beats every fixed single-mode baseline on
total time without losing success.

**Benchmarks / simulators (candidates).**
- **PARTNR** (Habitat 3.0, arXiv:2411.00081) — 100k NL household tasks, heterogeneous agents,
  spatial/temporal constraints; strongest for the L0/L1 deliberation end. *Confirm it exposes a
  wall-clock time metric and a learned-policy arm.*
- **Habitat-MAS** (EMOS) — heterogeneous embodiments; currently steps/tokens → would need time wired in.
- **MAPF / MARL benchmarks** (RWARE/TA-RWARE, CH-MARL, MAPF suites) — for the L2 end (pre-trained
  policies, congestion as a difficulty proxy).
- **A wildfire/SAR scenario** (the running example) — heterogeneous UAV+UGV; ideally a sim that
  supports both an LLM-dialogue arm and a learned-policy arm on identical task instances.

**Baselines.** Always-L0 (COHERENT/EMOS-style), always-L2 (pure MARL/MAPF), fixed-hierarchy hybrid
(L1 only, cf. Hierarchical LLM+RL), MARLIN-style training-time fusion (if reproducible), oracle router
(upper bound), GarageNet learned router.

**Ablations.** Gating-signal design (taxonomy-rule vs. learned vs. probe, §4); routing overhead
accounting; mis-routing cost; sensitivity of crossing points to the difficulty definition.

---

## 7. Positioning & how to differentiate (from the gap analysis)

| Neighbor | Relation | One-line differentiation |
|----------|----------|--------------------------|
| **Metareasoning/VOC** (Boddy-Dean, Zilberstein, Hansen, Lin, Sung-Stone, Paglieri, IBM) | **Theory anchor** (grounding) | Single-agent / compute-budget; GarageNet = team × *mechanism* choice × time. |
| **Raja & Lesser** multi-agent meta-level control | **Closest structural prior** (grounding) | Selects *scheduling algorithms* for scheduling quality; GarageNet selects *paradigms* by difficulty for completion time. |
| **MARLIN** | **Closest system** (differentiate) | Training-time scaffold (episodes-to-perf); GarageNet = deployment-time router, completion-time metric. |
| **Sliding/Adjustable Autonomy** | **Conceptual neighbor** (differentiate) | Human-in-loop, performance/operator trigger; GarageNet all-robot, task-difficulty trigger, paradigm-spanning. |
| **iTax / Gerkey-Matarić** | **Trigger taxonomy** (build on) | Describes problem coupling; GarageNet prescribes a mechanism from it. |
| **Scalable-MR-LLMs / CLiMRS** | Adjacent (differentiate) | Condition on agent count / negotiation depth within one paradigm; no learned-policy arm, no time metric. |

**Top reviewer risks to pre-empt in the paper:** R2 "this is adjustable autonomy" (→ trigger +
paradigm-span + objective); R3 "why discrete levels" (→ §3 design note + reported continuum); R1
"MARLIN already switches" (→ train vs deploy + metric). Full list in gap analysis §5/§8.5.

---

## 8. Open items before/during build

1. **Gating-signal design & its latency** (§4 crux) — the make-or-break engineering question.
2. **Benchmark confirmation** — does PARTNR/Habitat (or a wildfire sim) expose both arms + a time
   metric on identical instances? (Else build the harness.)
3. **Round-4 scoop confirmation** (optional, pre-submission) — skill-based difficulty-gated method
   selection (Axis 2) and disaster-robotics LLM+policy hybrids (Axis 3) are OPEN only by weak negative.
4. **GarageNet ↔ this framing** — reconcile the original GarageNet project's task set & robot roster
   with the L0–L2 construct (needs access to that repo or a copy of its task spec here).

---

## 9. Suggested paper skeleton

1. Intro — the latency wall + the wildfire example + the deliberate-vs-execute question.
2. Related work — metareasoning/VOC; LLM-MR; MARL/MAPF; adjustable autonomy; MRTA taxonomies.
3. Problem formulation — §3 construct + §4 team-metareasoning objective.
4. Method — the router, the gating signal (3 designs), the mechanism library (L0/L1/L2 instantiations).
5. Experiments — §6 protocol; time-vs-difficulty curves; router vs. fixed-mode baselines; ablations.
6. Discussion — discrete-vs-continuous; when routing overhead dominates; failure modes.
7. Conclusion + limitations (sim-to-real, gating-signal generality).
