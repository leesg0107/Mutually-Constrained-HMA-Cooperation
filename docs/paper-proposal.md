# GarageNet — Paper Proposal (synthesized & adversarially stress-tested)

> Date: 2026-06-27. Built from 3 independent draft framings (measurement-first / router-first /
> theory-first) × adversarial reviewer critique of each, then synthesized. Companion to
> `problem-statement.md`, `benchmark-feasibility.md`, `related-work-and-gap-analysis.md`.
>
> **Strategic decision: MEASUREMENT-FIRST.** All three critiques independently concluded the
> measurement (wall-clock LLM-vs-learned-vs-hybrid completion time across a difficulty axis) is the
> one verified-un-scooped, least-attackable contribution; the router and the team-metareasoning
> theory are individually scoopable (Raja-Lesser owns "meta-controller selects coordination
> algorithm by situation"; the team-VOC objective alone is "a relabeled single-agent definition").
> So the paper leads with the measured **crossing**, anchors novelty on the **latency cliff**, and
> presents the router as the payoff and the theory as framing (upgradeable to a contribution iff the
> critical-path theorem in §C4 lands).

---

## Paper title

**"When Is Deliberation Worth Its Latency? A Systematic Characterization of Completion Time for
LLM-Deliberation vs. Learned-Policy Coordination in Heterogeneous Robot Teams — and a Router That
Captures the Gains."**

*(Working alt: "The Latency Cliff in Multi-Robot Coordination: Crossing Curves Between LLM
Deliberation and Learned Policies, and How to Route Around Them.")*

---

## Main contributions

1. **(Headline) A systematic, controlled characterization of per-task COMPLETION TIME — wall-clock
   deliberation latency + execution time, reported as a split — for three coordination mechanisms
   (L0 inter-robot LLM deliberation / L1 hybrid / L2 pre-trained MARL-MAPF policy) on *identical*
   heterogeneous-team task instances across a graded reasoning-coupling axis (PARTNR/Habitat 3.0).**
   We show optimal coordination is **non-monotone** in coupling and the per-mode time curves
   **cross** (L2 fastest at low coupling, L0 at high, L1 between). The crossing is shown to be a
   *representational* phenomenon, not an artifact: it **persists under L2 scaling** (model size /
   training budget / in-vs-out-of-distribution) and **vanishes on a pure-congestion negative-control
   axis** where we predict — and show — no crossing.

2. **Identification of the "latency cliff" as the mechanism behind the crossing.** Because the arms
   span reasoning substrates with **order-of-magnitude latency gaps** (LLM inference at seconds vs.
   a learned policy at milliseconds), the optimal-mechanism cost is non-monotone in coupling — a
   regime **impossible within a single (all-LLM) paradigm** and **absent in pre-LLM meta-control**
   (whose algorithms were comparably fast). This is the irreducible novelty atom that survives every
   scoop comparison.

3. **GarageNet — a deployment/inference-time, coupling-gated coordination-MECHANISM router** that
   exploits the measured crossings, shipped as a drop-in PARTNR `Planner` subclass. Its contribution
   is reported as **gap-to-oracle** (not "beats fixed modes," which is near-tautological), and its
   non-trivial burden is that the **gating signal's own latency is charged against the savings** — we
   show a *cheap gate that beats the deliberation it saves*, and that a naive "always-probe-with-LLM"
   gate destroys the time advantage. Gating-signal ablation (iTax-rule / lightweight-learned /
   cheap-LLM-probe, each with its latency folded in) is a primary result, not an afterthought.

4. **(Upgrade contribution — include iff the theorem lands) A team value-of-computation result.**
   Because team completion time is a **max over parallel heterogeneous subtask branches** (critical
   path), per-task *greedy* mechanism selection is provably **suboptimal** vs. joint routing; we
   bound the gap and derive a **predicted crossing coupling per iTax degree** that Figure 2 then
   verifies against measurement. *(If this theorem is not attained, demote to problem-formulation
   framing — do not claim it as a contribution; the paper still stands on 1–3.)*

5. **(Artifact) An open PARTNR measurement harness** — wall-clock instrumentation around
   `get_next_action` (deliberation) vs. skill-execution steps + a drop-in learned-coordination
   `Planner` subclass — making LLM-vs-learned completion-time measurement reproducible. *(Stated as
   a reproducibility artifact, not a novelty claim.)*

---

## Main differences from prior research

1. **vs MARLIN (arXiv:2410.14383):** MARLIN's LLM↔MARL switch is **training-time** (gated by
   learning progress; x-axis = episodes; deploys **one frozen policy**; the switch is *free at
   deploy*). Ours is a **per-task inference-time** switch (x-axis = coupling) whose **gate latency is
   charged every task** — and we report completion-time-vs-coupling, which MARLIN cannot.
2. **vs Scalable-MR-LLMs (2309.15943) & CLiMRS (2602.06967):** both adapt coordination **within one
   paradigm** (all-LLM; cost is **monotone** in their knob — agent-count / negotiation-depth), so
   they **cannot exhibit a crossing**. Our arms straddle the **latency cliff**, making the optimal
   cost non-monotone — the crossing is a regime change impossible inside a single paradigm.
3. **vs Raja & Lesser meta-level control (10.1007/s10458-006-9008-z):** the closest *structural*
   prior selects among coordination **algorithms** by situation, **pre-LLM, all comparably fast** (no
   latency cliff), optimizing **scheduling quality**. Ours spans reasoning **substrates** with an
   order-of-magnitude latency gap and optimizes **measured completion time** — the cliff is what
   makes the choice bite, and it did not exist when Raja-Lesser was written.
4. **vs Sliding/Adjustable Autonomy (Sellner/Simmons RSS'06; Scerri/Tambe) & LoA:** human-in-the-loop
   autonomy spectra triggered by **in-loop performance/operator** feedback. Ours is **all-robot**,
   triggered by an **a-priori task property computable without running the task**, spans **reasoning
   paradigms**, and optimizes **deliberation latency**. (We also heed Miller's *Risks of
   Discretization*: trigger+objective+measurement is the claim; L0/L1/L2 are audited operating points
   and we report the continuous trade-off — L1 is kept only if a region where it strictly dominates
   both L0 and L2 is demonstrated, else we report a clean 2-mode router.)
5. **vs iTax (Korsah 2013) & Schneider 2017 portfolio selection:** iTax only **describes** coupling
   (ND/ID/XD/CD); Schneider selects **within one auction family** by a **spatial** signal. Ours
   crosses **paradigms** and the coupling→mechanism mapping is **validated** (predicted crossing
   matches measured), not hand-asserted.
6. **vs single-paradigm LLM-multi-robot (EMOS / COHERENT / SMART-LLM):** these **always deliberate**
   and report success / tokens / sim-steps — **never wall-clock time**. We add a **non-LLM arm**
   (the only way the time metric can move) and measure completion time directly.

---

## Five figures / tables

1. **Figure 1 (headline) — Completion-time-vs-coupling crossing curves.** Wall-clock time (y, split
   into deliberation + execution) vs. graded reasoning-coupling (x) for L0/L1/L2, with confidence
   bands, marked crossing point(s), and the oracle lower envelope overlaid. *Proves:* optimal
   coordination is non-monotone; the curves cross; the deliberate-vs-execute choice flips with
   coupling (Contribs 1, 2).
2. **Figure 2 — The non-artifact panel (credibility-defining).** Three sub-panels: (a) **negative
   control** — same plot on a pure-congestion axis showing **no crossing** (L2 dominates everywhere);
   (b) **L2-capacity sweep** — crossing **persists** as the learned arm scales (size/budget/OOD),
   proving a *representational*, not under-training, cause; (c) **L2 standalone capability** per
   coupling level (it is a strong, fairly-tuned baseline, not a strawman). *Proves:* the crossing is
   a real property of reasoning coupling, pre-empting the fatal "engineered/under-trained-L2"
   objection (Contrib 1).
3. **Figure 3 — Cost-model + backbone sensitivity.** (a) Regression of `T_deliberate(coupling)` ≈
   flat vs. `T_execute(coupling)` ↑ rising — the load-bearing VOC premise; (b) **crossing location
   vs. LLM-backend latency** (small-fast vs. large-slow LLM) — converts "your result depends on which
   slow LLM you used" into a controlled, theory-confirming sensitivity result. *Proves:* the latency
   cliff drives the crossing and the finding is scoped/robust to backbone (Contribs 2, 4).
4. **Figure 4 — The router as gap-to-oracle + gating-signal ablation.** (a) Total mission time:
   always-L0/L1/L2, MARLIN-style train-time fusion (if reproducible), **oracle router (lower bound)**,
   GarageNet router — headline number is **gap-to-oracle**, with each gate's **own latency folded
   in**; (b) gating designs (rule / learned / cheap-probe) on an accuracy-vs-latency Pareto with
   mis-routing cost vs. distance-from-crossing; (c) **success-vs-time** as a full panel (guards
   against "L0 wins on time only by failing more"). *Proves:* the crossings are exploitable by a
   cheap a-priori gate and a slow gate defeats the thesis (Contrib 3).
5. **Table 1 — Positioning matrix + the MARLIN axis schematic.** Rows = MARLIN, Scalable-MR-LLMs,
   CLiMRS, EMOS/COHERENT/SMART-LLM, Sliding/Adjustable Autonomy, Raja-Lesser, iTax, Schneider'17,
   single-agent VOC (Sung-Stone/Paglieri/IBM); columns = robot-**team**? / **cross-paradigm**
   mechanism (latency-cliff)? / **difficulty-coupling** trigger? / **inference-time**? /
   **completion-time** metric? / **non-LLM** arm?. Inset schematic: MARLIN switch on *episodes* axis
   vs. ours on *coupling* axis. *Proves:* each column is **load-bearing for the measured outcome**
   (not merely unoccupied), so the conjunction is a mechanism, not a coincidence (all contribs).

---

## Suggested paper structure

- **Section 1: Introduction** — the latency wall on the mission critical path; the wildfire running
  example (1 heavy UGV + 2 drones: drones run L2 mapping immediately while the UGV is allocated
  transport via brief L0/L1); the deliberate-vs-execute question; measurement-led contributions.
- **Section 2: Related Work** — value-of-computation / metareasoning (theory anchor); LLM
  multi-robot coordination (MARLIN, Scalable-MR-LLMs, CLiMRS, EMOS/COHERENT/SMART-LLM); MARL/MAPF
  learned coordination; adjustable/sliding autonomy & levels-of-automation; Raja-Lesser meta-level
  control; MRTA interdependence taxonomies (iTax).
- **Section 3: Problem Formulation** — team value-of-computation objective (framing; the
  critical-path non-separability result here iff it lands); required coupling `c(τ)` grounded in
  iTax; L0/L1/L2 as auditable operating points on a deliberation-intensity continuum (discrete-vs-
  continuum note, per Miller).
- **Section 4: Measurement Methodology** — PARTNR/Habitat 3.0 harness; three mechanism arms on
  identical instances (L0 decentralized per-agent LLM, L1 hybrid, L2 drop-in learned-coordination
  `Planner` subclass); wall-clock instrumentation (deliberation vs. execution split); the graded
  reasoning-coupling axis **and** the congestion negative-control axis; the L2-capacity and
  LLM-backbone sweeps.
- **Section 5: The Crossing (core results)** — time-vs-coupling curves; deliberation/execution
  decomposition; crossing localization; the negative-control + L2-capacity + backbone-latency
  robustness battery.
- **Section 6: The Router** — exploiting the crossings; gating signal (rule / learned / cheap-probe)
  with latency folded in; gap-to-oracle; mis-routing cost; second-environment generalization
  (RWARE+LLM or EMOS) as a *figure*, not a sentence.
- **Section 7: Discussion** — the latency cliff as the mechanism; discrete-vs-continuum operating
  points audited via the continuous trade-off; when routing overhead dominates (the honest regime
  where GarageNet loses); sim-to-real and backbone scope; mis-routing/failure modes.
- **Section 8: Conclusion and Limitations** — measurement-first contribution; the validated
  coupling→mechanism mapping; gating-signal generality; sim-to-real.

---

## Why this shape (synthesis rationale) & the one risk that can kill it

**Why measurement-first.** The router alone reduces (structurally) to "Raja-Lesser with an LLM in the
portfolio"; the team-VOC objective alone is "a relabeled single-agent definition." The *measurement*
is the only contribution verified un-scooped across four research rounds and is figure-first
falsifiable — so it carries the paper, and the otherwise-scoopable router/theory become its payoff
and framing.

**The single fatal risk (flagged by all three critiques): the crossing looks engineered.** The axis
is chosen so the learned policy degrades, and the L2 arm is built by the authors — a hostile reviewer
says "any fixed-latency arm vs. any monotone-degrading arm crosses; you measured your own arm
construction." The defense is non-negotiable and must be built in from day one:
- **Negative control** (congestion axis → predicted & shown *no* crossing),
- **L2-capacity sweep** (crossing persists as L2 scales → representational, not under-trained),
- **predicted-before-measured** crossing location (pre-register from the coupling model),
- **L2 standalone capability** reported (not a strawman),
- **LLM-backbone latency sweep** (crossing shifts predictably, doesn't vanish arbitrarily),
- **statistical rigor** (seeds, N, disjoint CIs at the crossing).

If these hold, the crossing is a discovered phenomenon and the paper is strong. If the crossing
proves fragile to L2 scaling or backbone choice, that *itself* is the honest finding and reshapes
(not kills) the contribution.

**The optional upgrade.** If the critical-path non-separability theorem (Contrib 4) lands, the paper
gains a genuine team-specific theoretical result the single-agent VOC lineage cannot produce, and
Figure 2/Table-of-predicted-crossings becomes a validated theory→data bridge — elevating it from a
strong empirical paper to a theory+measurement+system paper.

---

# v2 — FINAL SHAPE (2026-07-03): measurement + theory + per-agent allocator

> Supersedes the measurement-first framing above as the working proposal. Incorporates
> algorithmic direction C (`algorithmic-direction-C.md`), the team-VoC theory
> (`theory-team-voc.md`), and the Phase-0/1 harness results (`garagenet/`). The v1 sections
> above remain valid as the fallback shape if Phase-1 gains do not materialize on PARTNR.

## Paper title (v2)

**"Deliberate Where It Pays: Per-Agent Allocation of LLM Deliberation and Learned Policies in
Heterogeneous Robot Teams"**

*(alt: "Some Robots Think, Others Act: Coupling-Gated Coordination for Time-Critical
Heterogeneous Teams")*

## Main contributions (v2)

1. **(Phenomenon)** The first systematic wall-clock characterization of LLM-deliberation vs.
   learned-policy vs. hybrid coordination on identical heterogeneous-team tasks across a
   reasoning-coupling axis — the **crossing curves**, with the full falsifiability battery
   (congestion negative control, L2-capacity sweep, backbone-latency sweep).
2. **(Theory)** Team value-of-computation: coupling ≡ the inter-agent deliberation externality.
   Thm 1 (no externality ⇒ per-agent greedy optimal), Thm 2 (any externality ⇒ unbounded
   decentralization regret; upstream agents systematically under-deliberate because the benefit
   lands downstream), Corollary (**coupling gates decentralized-vs-joint metareasoning** — a new
   lever; joint coordination itself costs latency and must be paid only when coupling demands it).
3. **(System)** The GarageNet allocator: **different robots in one team simultaneously run
   different coordination mechanisms** (immediate learned-policy execution ↔ LLM deliberation),
   assigned per robot by local task coupling on the mission critical path. Evaluated as
   gap-to-oracle with the allocator's own decision latency charged.
4. **(Artifact)** The open measurement harness + allocator suite (PARTNR `Planner`-compatible
   arms, 3-way timing ledger, coupling/congestion sweeps, crossing detector) — reproducibility,
   not novelty.

## The three claims already validated executably (mock/theory level)

| Claim | Result (synthetic, mechanism-validation only) |
|---|---|
| Thm 2 greedy failure | greedy 314.8s vs joint 104.0s at high externality; failure mode = upstream skips deliberation, exactly as proved |
| Corollary gate | matches joint (107.0 = 104.0 + 3.0 overhead) when escalation needed; matches greedy free (74.8s) when not |
| A1 per-agent mixing | mixed assignment 57.2s vs best team-uniform 100.1s (–43%) on the pipeline mission; drones/scouts never wait on others' dialogue |

Honest constraint discovered and kept: with purely independent parallel branches, makespan ties
(the hardest branch dominates) — **A1's gain requires precedence structure** (easy branches feeding
a downstream chain). PARTNR missions for Phase 1 must be selected/composed accordingly.

## Five figures (v2)

1. **Crossing curves** (Phase-0, real PARTNR): time-vs-coupling per arm, deliberation/execution
   split, oracle envelope. *(instrument built & pipeline-validated)*
2. **Falsifiability battery**: congestion no-crossing control + L2-capacity sweep + backbone-latency
   sweep. *(protocol pre-registered in partnr-setup-checklist.md §3)*
3. **Allocator comparison**: externality sweep (greedy blows up; gate escalates only when needed) +
   per-agent vs team-uniform bars. *(prototype: results/allocators_demo.png)*
4. **Wildfire timeline**: Gantt of per-agent modes — drones launch on policy at t=0 while the UGV
   deliberates; makespan vs the all-deliberate and all-policy timelines.
5. **Positioning matrix**: neighbors × {team? / cross-paradigm? / per-agent? / coupling-trigger? /
   deploy-time? / time-metric?} — only GarageNet has every column; each column shown load-bearing
   via an ablation.

## Structure (v2)

1. Introduction — the latency wall; the factory/wildfire intuition (some robots must think, others
   must move NOW); contributions.
2. Related Work — metareasoning/VoC; LLM-multi-robot; MARL/MAPF; adjustable autonomy; Raja-Lesser;
   MARLIN; coalition formation (allocates tasks, not modes); iTax.
3. Team Value-of-Computation — model, Thm 1/2, Corollary; coupling = measurable decentralization
   regret.
4. The GarageNet Allocator — coupling estimator, gated decentralized/joint metareasoner, mechanism
   spectrum, async interface; decision latency accounting.
5. Phase-0: the Crossing — measurement methodology + falsifiability battery on PARTNR.
6. Phase-1: Per-Agent Allocation — allocator vs fixed modes vs team-uniform vs oracle on
   precedence-structured missions.
7. Discussion — when mixing pays (precedence) and when it can't (independent parallel); routing
   overhead regime; discrete-vs-continuous (κ as future work if Phase-2 knob unbuilt).
8. Conclusion & Limitations.
