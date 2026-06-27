# Related Work & Gap Analysis — Task-Difficulty-Gated Cooperation Levels for Heterogeneous Multi-Robot Teams

> Scooping check + gap analysis for the GarageNet "cooperation-level (L0–L2)" framing.
> Date: 2026-06-27. Method: fan-out web search (6 angles, 23 sources fetched) → claim
> extraction (95 claims) → 3-vote adversarial verification (25 verified, 0 killed) → synthesis.
> Scope caveat: arxiv/OpenReview returned 403 through the proxy during verification, so most
> claims rest on verbatim abstract quotes + convergent secondary summaries, not full-text reads.
> Re-run this check close to submission (the 2023–2026 LLM-multi-robot space moves fast).
>
> **Round 2 (2026-06-27, appended in §8):** deep-dive on MARLIN, iTax→mechanism scoop check,
> and the conceptual-validity question ("is a 'cooperation level' a meaningful construct?").
> 5 angles, 25 sources, 25 claims verified / 0 killed.
>
> **Round 3 (2026-06-27, appended in §9):** resolves the 3 axes round 2 left unverified —
> metareasoning/VOC (Axis 1, now the theory anchor), skill-based teams (Axis 2), disaster/SAR
> (Axis 3). 5 angles, 25 sources, 25 verified / 0 killed. **Verdict: publishable, un-scooped.**

---

## 0. The framing under test

**Thesis.** For heterogeneous multi-robot teams, the *level/type of cooperation a task
demands depends on the task's difficulty/abstractness*, and the team should **adaptively
select the most time-efficient coordination mode per task**:

- **L0 — Discussion / negotiation.** High-abstraction, divergent-goal, ambiguous tasks
  (analogy: friends planning a trip). Robots deliberate via LLM-agent dialogue.
- **L2 — Pre-trained policy.** Tightly-coupled, role-predefined tasks (analogy: a wolf pack
  hunting bison — roles fixed, move as one body). No discussion; run a pre-trained MARL / MAPF
  policy directly.
- **L1 — Hybrid.** Mixture of LLM discussion + learned policy.

**Distinctive bet.** Unlike wolves, robots can communicate long-range and deliberate
continuously, so the *cost* of discussion is **inference latency** — fast inference is what
makes the discussion mode viable. The intended contribution is to (a) classify tasks by the
cooperation level they demand, (b) route to discussion / policy / hybrid accordingly, and
(c) **experimentally measure completion TIME for the same task under each mode**.

---

## 1. Verdict

**NOT scooped — but it sits in a crowded neighborhood with several near-misses a reviewer
can weaponize.** No existing work does all four of the following at once:

1. selects the **coordination MODE** (deliberative LLM dialogue ↔ pre-trained MARL/MAPF ↔ hybrid)
2. **as a function of task difficulty / required-coupling**
3. and **switches between them at DEPLOYMENT time** (not during training),
4. and **measures per-task completion TIME** under each mode.

Drop any **one** of these four and an existing paper already covers it. The defensible wedge
is the **conjunction**. The single biggest unverified risk: an MRTA task-coupling taxonomy
(iTax / Gerkey–Matarić) may already imply a difficulty→coordination mapping — see §5.

---

## 2. The closest works (and exactly how they differ)

| # | Work | What it does | How it differs from L0–L2 |
|---|------|--------------|---------------------------|
| 1 | **MARLIN** — *MARL Guided by Language-Based Inter-Robot Negotiation* (arXiv:2410.14383) | Fuses LLM inter-robot **negotiation with MARL** and **"dynamically switches"** between RL and LLM negotiation. Validated on TurtleBot3. | **The #1 scooping risk.** But the switch is a **TRAINING accelerator** (fewer episodes to peak), not a deployment-time difficulty-gated mode selector; it deploys **one** trained policy; metric is **training time**, not per-task completion time. |
| 2 | **Scalable Multi-Robot Collaboration with LLMs** (arXiv:2309.15943, ICRA 2024) | Compares centralized / decentralized / 2 hybrid LLM topologies by success + token efficiency; "hybrid is best, optimum depends on a problem property." | The conditioning axis is **agent COUNT / scalability**, not task-difficulty deliberation-vs-policy. **All four arms are LLM dialogue** — no learned-policy arm. Cost = tokens, not wall-clock. |
| 3 | **CLiMRS** (arXiv:2602.06967) | Adaptive group **negotiation** for heterogeneous MR; ties **effort to task difficulty** (40%+ efficiency gain on complex tasks). | Difficulty-conditioning is **live** here — but it varies negotiation **DEPTH within one paradigm** (always LLM deliberation), never switches to a learned policy. |
| 4 | **Hierarchical Control in Multi-Agent Games: LLM Planning + RL Execution** (arXiv:2606.20014) | LLM as high-level strategic planner/commander; pre-trained RL policies do low-level reactive execution. | Closest hit for **L1/hybrid as an architecture**, but it's a **fixed** hierarchy (always LLM-on-top + RL-below), not a per-task router that *chooses* discussion vs. policy vs. hybrid by difficulty. No time-per-mode comparison. |
| 5 | **EMOS** — Embodiment-aware Heterogeneous MR OS (arXiv:2410.22662, ICLR 2025) | Hierarchical LLM agents, **fixed** discuss-then-execute pipeline on Habitat-MAS. | Coordination is **always** deliberation. Metrics = success / sub-goal / token usage / **sim-step count** — **no wall-clock time**, no learned-policy arm. |
| 6 | **COHERENT** (arXiv:2409.15146) | Heterogeneous MR via a **single centralized LLM planner** (Proposal–Execution–Feedback–Adjustment loop). | Coordination mechanism is **fixed** (always the same planning loop). No mode selection, no MARL/MAPF, no difficulty gate. |
| 7 | **SMART-LLM** (arXiv:2309.10062) | Centralized LLM planner: decompose → coalition → allocate. Conditions **coalition SIZE** on complexity. | One **fixed prompting pipeline**; conditions team size, not coordination paradigm. No robot-to-robot dialogue, no learned policy. |
| 8 | **IC3Net** — *Learning when to communicate* (arXiv:1812.09755, ICLR 2019) | Per-agent learned **binary gate**: broadcast a message or not, inside one learned controller. | Right *spirit* ("when to communicate"), **wrong granularity**: intra-paradigm **message gating**, not a switch between **coordination paradigms**. Pre-LLM; no deliberation, no latency notion. Cite as motivation, distinguish clearly. |
| 9 | **Learning When to Plan** (arXiv:2509.03581) | A **single** LLM agent trained (SFT/RL) to decide **when to deliberate (plan) vs. just act**. | The closest analogue to the *meta-controller* idea — but **single-agent**, and the choice is plan-vs-act, not **dialogue-vs-learned-multi-robot-policy**. Strong conceptual precedent to cite and extend to the team setting. |

---

## 3. Per sub-question findings

**Q1 — Difficulty-gated coordination-MODE switching?** No. Every LLM-MR system examined is
either single-paradigm (always deliberation/planning: COHERENT, EMOS, SMART-LLM, CLiMRS,
LLM-HBT) or a training-time fusion (MARLIN). The **deliberation-vs-learned-policy axis itself
is absent** from the LLM-multi-robot line. *(high confidence)*

**Q2 — "When to deliberate vs. run a learned policy," measured by completion time?** Not as a
function of task type, and **not by wall-clock time anywhere**. The LLM-MR line conditions on
agent count / coalition size and measures **tokens / steps / success**, never time-per-mode.
*(high confidence)*

**Q3 — Theory to ground L0–L2 (task coupling / interdependence)?** A grounding **exists** and
was surfaced in search but **not adversarially verified** (the verifier killed nothing but
also confirmed no claim here):
- **iTax** — Korsah, Stentz & Dias (2013), *A Comprehensive Taxonomy for MRTA* (Int. J.
  Robotics Research, 10.1177/0278364913496484): extends Gerkey–Matarić with a
  **degree-of-interdependence** axis — **No Dependencies (ND) → In-schedule (ID) →
  Cross-schedule (XD) → Complex (CD)**. This is an almost off-the-shelf scaffold for "how much
  cooperation a task demands" and maps suggestively onto L0/L1/L2.
- **Gerkey & Matarić (2004)** — ST-SR-IA / formal MRTA taxonomy (the iTax predecessor).
- **OPEN RISK:** whether anyone has already **built a difficulty→coordination-mode mapping on
  top of iTax** was not resolved. This is the biggest "maybe already exists" hole — verify
  directly (see §6). *(medium confidence on the gap; the taxonomy itself is real.)*

**Q4 — Inference-latency-as-cost: novel?** **Partially anticipated, not occupied.** Latency is
*recognized* as the dominant cost of LLM deliberation but never *centralized as the measured
tradeoff*:
- IJCAI-2025 EMAS survey (arXiv:2502.11518): "LLM-based planning and communication emerged as
  the dominant contributors to overall latency."
- LLM-HBT (arXiv:2510.09963): names "LLM inference latency" as a key limitation / future work.
- AgentBalance (arXiv:2512.11426): explicitly optimizes MAS topology under **token + latency
  budgets** — but for **web-software** MAS, not physical robots.
→ Must **sharpen**: robot **deliberation-latency vs. execution-latency** tradeoff, *measured as
  completion time per cooperation level*. Don't claim wholesale novelty. *(high confidence)*

**Q5 — Agents deciding whether to communicate at all?** Yes, two precedents at the wrong
granularity: **IC3Net** (intra-policy message gate) and **Learning When to Plan** (single-agent
plan-vs-act). Neither gates **between coordination paradigms** by task difficulty. Cite both as
lineage; the novelty is lifting the gate to the **paradigm/team** level. *(high confidence)*

**Q6 — Benchmark for same-task, multi-mode, time comparison?**
- **PARTNR** (Meta, arXiv:2411.00081, on **Habitat 3.0**): 100k NL household tasks, 60
  multi-room houses, explicit spatial/temporal/**heterogeneous** constraints → the **strongest
  candidate** for running the same task under different modes.
- **Habitat-MAS** (used by EMOS): viable but currently measured in **steps/tokens, not time**.
- **OPEN:** need to confirm a benchmark that exposes **both** a learned-policy arm **and** an
  LLM-dialogue arm on identical tasks **with a time metric** (candidates: Overcooked,
  RWARE/TA-RWARE, CH-MARL, MAPF benchmarks for the L2 end). *(not verified — see §6.)*

---

## 4. Publishable gaps (candidate contributions)

1. **A deployment-time, task-difficulty/coupling → coordination-mode ROUTER** that selects
   LLM-discussion (L0) vs. pre-trained MARL/MAPF (L2) vs. hybrid (L1). This exact object does
   not exist; MARLIN is train-time, the LLM-MR line is single-paradigm.
2. **First empirical characterization of completion TIME for the SAME task under each
   cooperation mode** — turning the abstract "which mode is more efficient" into measured
   curves over a difficulty axis. The whole field measures tokens/steps/success, not time.
3. **Grounding L0–L2 in an existing coupling/interdependence taxonomy** (iTax ND/ID/XD/CD)
   and building the **difficulty→mode mapping** on top — converts L0–L2 from intuition into a
   principled, citable axis. *(Contingent on §6 verification that this mapping isn't already done.)*
4. **Latency-centric cost model for multi-robot deliberation** — deliberation-latency vs.
   execution-latency as the thing the router trades off, measured, not just named.

The strongest single-paper framing is the **conjunction of #1 + #2** with #3 as theoretical
grounding and #4 as the cost model that motivates *why a router is needed at all*.

---

## 5. Reviewer risks ("this already exists") — and the rebuttal

- **R1 — "MARLIN already switches between RL and LLM negotiation."** → Distinguish **train-time
  fusion** (MARLIN: fewer episodes, deploys one policy) from **deploy-time difficulty-gated mode
  selection**; and **training-time metric** vs. **per-task completion-time metric**.
- **R2 — "Scalable-MR-LLMs already shows hybrid is best and mode depends on a problem
  property."** → Their property is **agent count**; all arms are LLM dialogue. Argue
  task-difficulty/coupling is a **different and better axis**, and that you add a genuine
  **learned-policy** arm.
- **R3 — "CLiMRS already adapts cooperation to task difficulty."** → It varies negotiation
  **DEPTH within one paradigm**, never switches **paradigm** (no learned-policy alternative).
- **R4 — "Latency-as-cost is already named (LLM-HBT, EMAS survey, AgentBalance)."** → They
  **name/budget** it in software MAS or as future work; nobody **centers and measures** it as
  the deliberation cost per cooperation level on physical-robot tasks.
- **R5 (latent) — "iTax already maps interdependence to coordination."** → Must pre-empt by
  citing iTax as the *grounding you build on* and showing the *mode-routing + time-measurement*
  is the new layer. Verify first (§6) so this doesn't become a real scoop.

---

## 6. Open questions to close before committing (highest-leverage next checks)

1. **iTax scoop check (top priority).** Does any work already map iTax/Gerkey–Matarić
   interdependence (ND/ID/XD/CD) onto a **choice of coordination mechanism** (deliberation vs.
   learned policy)? If yes → contribution #3 weakens and the framing must shift. If no → #3 is
   a clean, citable anchor.
2. **Benchmark with both arms + a time metric.** Confirm whether PARTNR/Habitat 3.0 (or
   Overcooked / RWARE / CH-MARL / a MAPF benchmark) can run the **same** task under an LLM-dialogue
   arm **and** a learned-policy arm and report **wall-clock completion time**.
3. **Re-scan 2025–2026 for a deployment-time mode router** keyed on task type — CLiMRS and
   AgentBalance are very recent; a direct competitor could appear at any 2026 venue.
4. **Operationalize robot latency** distinctly from AgentBalance's web-MAS budgeting and
   LLM-HBT's planning-latency framing (deliberation latency vs. execution latency on hardware/sim).

---

## 7. Key sources

- MARLIN — arXiv:2410.14383
- Scalable Multi-Robot Collaboration with LLMs — arXiv:2309.15943 (ICRA 2024)
- CLiMRS / Adaptive Group Negotiation for HMA — arXiv:2602.06967
- Hierarchical Control: LLM Planning + RL Execution — arXiv:2606.20014
- EMOS — arXiv:2410.22662 (ICLR 2025)
- COHERENT — arXiv:2409.15146
- SMART-LLM — arXiv:2309.10062
- IC3Net — arXiv:1812.09755 (ICLR 2019)
- Learning When to Plan — arXiv:2509.03581
- EMAS survey (latency) — arXiv:2502.11518 (IJCAI 2025)
- LLM-HBT — arXiv:2510.09963
- AgentBalance — arXiv:2512.11426
- iTax — Korsah, Stentz & Dias 2013, IJRR, doi:10.1177/0278364913496484
- Gerkey & Matarić MRTA taxonomy (2004)
- PARTNR benchmark (Habitat 3.0) — arXiv:2411.00081

---

## 8. Round 2 — MARLIN deep-dive, iTax→mechanism scoop check, and conceptual validity

> Method: 5 angles, 25 sources fetched, 25 claims 3-vote-verified / 0 killed. Same 403-proxy
> caveat (verbatim abstract quotes + secondary corroboration, not full PDF reads).

### 8.1 MARLIN verdict — leaves the GarageNet thesis fully open

MARLIN's RL↔LLM switching is **strictly a TRAINING-time acceleration**: LLM negotiation
produces plans that guide the MARL policy *during training*, alternating throughout training to
reach peak performance in fewer episodes. It is **not** a deployment-time router and **not**
difficulty-gated. The metric is **training-episodes-to-peak** (vs. a MAPPO baseline, eval every
250 episodes from ep. 100, 10 trials) — **not** per-task completion time or inference latency.
At deployment a **single** trained policy runs (no LLM, no mode switch). → MARLIN leaves the
entire GarageNet core thesis (difficulty-gated, **inference-time** mode router measured by
**completion time**) **open**. *(high confidence; arXiv:2410.14383, survey 2502.03814)*

**Newly surfaced near-neighbors (all favorable — none scoop):**
- **Yoshida & Sueoka 2025** — *Communication-Free Adaptive Swarm: LLM decision + MARL multi-policy
  control*. Two-tier (LLM selects a policy via "questionnaire-style prompts"; multiple MARL
  policies execute). Selection driven by **situational consensus**, not a difficulty metric or
  completion-time gate. Metric = "implicit consensus" + success/step-count, **not** latency. The
  closest LLM+MARL architecture, yet difficulty-gating and the deliberation-cost objective remain open.
- **Prompting Robot Teams with NL** (arXiv:2509.24575) — LLM decomposes intent→DFA **offline**,
  distilled into RNN+GNN; **no LLM at inference**, no mode switch.
- **LAN2CB** (arXiv:2507.16068) — NL→Python codegen pipeline; no RL/MARL/MAPF, no router.

### 8.2 iTax → coordination-mechanism mapping — scoop verdict: does NOT exist (gap confirmed)

iTax (Korsah, Stentz & Dias 2013) is a **descriptive** classification of MRTA *problems* by
**degree of interdependence** of agent-task utilities/constraints (ND / ID / XD / CD), mapped to
combinatorial-optimization models. It is **not** a prescription of which coordination *mechanism*
to use, and its axis is utility/cost interdependence — **not** task difficulty as a trigger for
selecting a decision-making *mode*.

**No work maps coupling/interdependence DEGREE → a CHOICE of coordination MECHANISM.** Closest:
- **Schneider, Sklar & Parsons (TAROS 2017)** — genuinely auto-selects a task-allocation
  mechanism from a **portfolio** via a trained classifier (real precursor to the meta-selection
  idea), **but** the signal is **spatial/environmental geometry** (task-location clusters, robot
  positions), not coupling/difficulty, and the portfolio is **two variants of the same auction
  family** (SSI vs. PSI) — not different reasoning paradigms (LLM vs. MARL vs. reactive).
- **Rossano et al. 2025** (arXiv:2509.22469) and **Wang et al. 2020** (the iTax CD[ST-MR-TA] case)
  each handle coupling with a **single** mechanism — they don't select among mechanisms by coupling.
→ **The coupling-degree→mechanism mapping is open** — this is a real opening for grounding L0–L2,
  but it must be *built*, not cited. *(high confidence)*

### 8.3 Conceptual validity — IS "cooperation level" a meaningful construct? (the deep question)

**Answer: the underlying idea is real and empirically validated — but the DISCRETE-LEVEL packaging
is contested, so the defensible novelty is the TRIGGER + OBJECTIVE, not the levels themselves.**

- **VALIDATED:** "Vary the coordination/autonomy level by situation" is an established, empirically
  validated construct. **Sliding Autonomy** (Sellner, Hiatt, Simmons, Singh — RSS 2006) is a
  shared-control spectrum (full autonomy ↔ teleoperation) for coordinated multi-robot assembly;
  the *when-to-switch* decision is driven by agents **modeling expected performance**
  (cost/benefit), and it was operationalized as a **small discrete set of modes** (4 strategies).
  Result: efficiency near full autonomy + restored reliability + lower operator workload. → The
  "adjust coordination level by situation, as a few discrete modes" pattern is proven to work.
- **CONTESTED:** Discretizing autonomy into **fixed levels** is recognized but **not settled**. A
  2025 systematic review finds the Levels-of-Automation literature "contains numerous seemingly
  contradictory critiques and recommendations"; the Kaber-2018 / Sheridan / Endsley / Miller
  exchange (Miller, *"The Risks of Discretization"*) shows fixed levels are useful as concepts but
  contested for engineering use.
- **IMPLICATION for L0–L2:** You **cannot** present a fixed L0/L1/L2 ladder as self-evidently
  valid. Its defensibility rests on **(i) the difficulty-gating trigger** (all-robot,
  task-difficulty-driven — vs. sliding autonomy's human-in-the-loop, performance/operator trigger)
  and **(ii) the per-task-completion-time / deliberation-cost objective**. You must explicitly
  address the **discrete-vs-continuous** critique (why 3 modes, not a continuum?).

**Four constructs GarageNet MUST differentiate itself from (one-liners):**
1. **Adjustable / Sliding Autonomy** (Sellner/Simmons 2006; Scerri/Tambe) — *human-in-the-loop*
   autonomy spectrum triggered by *performance/operator cost*. GarageNet: *all-robot*, triggered by
   *task difficulty/coupling*, spanning *reasoning paradigms* (LLM vs. learned policy).
2. **Levels of Automation** (Sheridan-Verplank; Parasuraman-Sheridan-Wickens 2000) — a descriptive
   *who-does-what* autonomy scale (and a contested one). GarageNet: not "how autonomous" but
   "*which coordination mechanism*," chosen for time.
3. **Mechanism-portfolio selection** (Schneider 2017) — selects an allocation mechanism by *spatial
   geometry*, within *one* (auction) family. GarageNet: selects across *paradigms* by *difficulty*.
4. **iTax coupling taxonomy** (Korsah 2013) — *describes* problems by interdependence. GarageNet:
   *prescribes* a mechanism from the coupling degree.

### 8.4 Updated GAP statement & single sharpest paper framing

**Gap (sharpened):** No system performs **deployment/inference-time selection of the coordination
*mechanism* (LLM deliberation ↔ hybrid ↔ pre-trained MARL/MAPF policy) as a function of task
difficulty/coupling, with the explicit objective of minimizing deliberation+execution time**
(treating LLM inference latency as the cost of deliberation), and *measures per-task completion
time per mode*. MARLIN is train-time; sliding autonomy is human-triggered/performance-based;
mechanism-portfolio work uses spatial signals within one family; iTax only describes.

**Sharpest single-paper framing:** *"A metareasoning router for heterogeneous multi-robot teams
that, per task, decides whether deliberation is worth its latency — selecting LLM discussion vs. a
pre-trained MARL/MAPF policy vs. hybrid by task difficulty/coupling — and the first empirical
characterization of completion time per cooperation mode across a difficulty axis."* Frame the
contribution as the **trigger + objective + measurement**, with L0–L2 as an *operationalization*,
not the headline claim. Ground the trigger in iTax coupling; ground the objective in **metareasoning
/ bounded rationality** (Russell & Wefald — "is it worth thinking more?").

### 8.5 Updated reviewer-risk list

- **R1 (MARLIN)** — *defused*: train-time vs. inference-time, episodes vs. completion-time.
- **R2 (Sliding/Adjustable Autonomy) — NEW, now the top conceptual risk.** "You've reinvented
  adjustable autonomy." Rebuttal: human-out-of-loop, *task-difficulty* (not performance/operator)
  trigger, spanning *reasoning paradigms*, optimizing *deliberation latency*.
- **R3 (LoA discretization)** — "Why discrete levels?" Must address discrete-vs-continuous head-on.
- **R4 (Yoshida & Sueoka swarm)** — "LLM-selects + MARL-executes already exists." Rebuttal: theirs
  is *consensus*-driven, not difficulty-gated, and not latency/time-optimized.
- **R5 (mechanism-portfolio, Schneider)** — "Auto-selecting a coordination mechanism is done."
  Rebuttal: spatial signal + single auction family vs. difficulty signal + cross-paradigm.

### 8.6 Still-open (NOT verified in round 2 — candidates for round 3)

These three axes had **no surviving verified claim** — absence is suggestive of a gap, not a proof:
1. **Metareasoning for multi-robot mode-selection** (Russell & Wefald bounded rationality; anytime;
   "learn when to plan" for LLM agents) applied to *multi-robot coordination-mode* choice — both
   the theoretical grounding for the objective **and** a potential scoop. **Highest-value next check.**
2. **Skill-library heterogeneous teams** selecting method (MAPF vs. MARL vs. simple skill vs.
   negotiation) **per task by difficulty** — "when is MAPF needed vs. simple path following?"
3. **Disaster-response / wildfire / SAR** heterogeneous (drones + ground) systems doing
   capability-based roles **and** difficulty-aware mode selection (esp. LLM+MARL hybrid).

### 8.7 Round-2 key sources

- MARLIN — arXiv:2410.14383 · LLM-MRS survey — arXiv:2502.03814
- Yoshida & Sueoka 2025 (Comm-Free Adaptive Swarm, LLM+MARL) — ResearchGate 398910704
- Prompting Robot Teams with NL — arXiv:2509.24575 · LAN2CB — arXiv:2507.16068
- iTax — Korsah, Stentz & Dias 2013, doi:10.1177/0278364913496484
- Schneider, Sklar & Parsons, TAROS 2017 — doi:10.1007/978-3-319-64107-2_33
- Rossano et al. 2025 — arXiv:2509.22469 · Wang et al. 2020 — S0921889020304000
- Sliding Autonomy — Sellner, Hiatt, Simmons, Singh, RSS 2006 — roboticsproceedings rss02/p03
- LoA systematic review 2025 — doi:10.1080/10447318.2025.2502978 (+ Miller, "Risks of Discretization")

---

## 9. Round 3 — resolving the 3 unverified axes (metareasoning, skill-based, disaster-response)

> Method: 5 angles, 25 sources, 25 claims 3-vote-verified / 0 killed. Same 403-proxy caveat
> (Axis-1 grounding rests on verbatim abstracts cross-checked across renderings, not full PDFs).
> **Updated overall verdict: thesis remains PUBLISHABLE and largely UN-SCOOPED.** Across all
> three axes the closest prior work is **GROUNDING, not scoop**.

### 9.1 Axis 1 — Metareasoning / deliberation-cost — VERDICT: OPEN, but richly GROUNDED ✅

GarageNet's objective ("only deliberate when it pays off, because LLM latency is the cost") **is
classical metareasoning / value-of-computation (VOC)**. This is the theoretical backbone the
framing was missing — a deep, citable lineage:

- **Boddy & Dean (IJCAI-89)** — *deliberation scheduling*: a problem is "time-dependent" when
  "time spent planning affects the utility of performance"; "deciding what to think about and when
  to act" = allocating time among anytime procedures. **The canonical deliberate-vs-act formulation.**
- **Zilberstein (1996)** — anytime algorithms "trade off deliberation time for quality of results."
- **Hansen & Zilberstein (2001)** — non-myopic meta-level control of *when to stop deliberating and act*.
- **Lin, Kolobov, Kamar, Horvitz (IJCAI'15)** — metareasoning for MDPs: trade "cost of planning vs.
  potential policy improvement."
- **Sezener (2018, arXiv:1811.03035)** — "when to act or compute" as an MDP (computation & action
  share time/energy).
- **Modern systems:** Sung & Stone, *Effort Allocation for Deadline-Aware TAMP* (arXiv:2410.05828) —
  metareasoning to allocate compute under a deadline with uncertain planning/execution times;
  Paglieri et al., *Learning When to Plan* (arXiv:2509.03581) — learn when to spend test-time compute
  (always-plan is expensive, never-plan caps performance); IBM, *When to Reason* (arXiv:2510.08731) —
  semantic router applying reasoning "only when beneficial."

**Every one is SINGLE-AGENT or single-LLM query-routing.** None selects among
LLM/hybrid/MARL **coordination mechanisms for a robot team** by task difficulty. → Axis 1 is
**grounding, not scoop.** This is now the recommended theoretical anchor for the whole paper.

### 9.2 Axis 1 sub-finding — the structurally CLOSEST prior work (important nuance)

**Raja & Lesser — meta-level control for multi-agent coordination** (CMU RI; AAMAS journal,
doi:10.1007/s10458-006-9008-z). A meta-level controller that **selects among multiple
scheduling/coordination algorithms by situation** in a **resource-bounded multi-agent** setting,
and explicitly critiques systems that "do not reason about the cost of deliberative computation …
[and] assume all deliberative computations are always done … in the same way." This is the
**closest structural match to the GarageNet router that exists** — and predates LLMs.

- **Why it's grounding, not scoop:** it selects *scheduling/negotiation algorithms* to improve
  one agent's resource-bounded scheduling quality — **not** LLM-vs-hybrid-vs-MARL coordination
  *mechanisms* for a robot team, **not** gated by task difficulty/coupling, **not** optimizing
  measured **completion time**. But it is the prior work whose *spirit* is nearest, so cite it
  prominently and differentiate on (paradigm-spanning mechanisms + difficulty trigger + time objective).

### 9.3 Axis 2 — Skill-library teams + difficulty-driven method selection — VERDICT: OPEN (weak negative)

**No surviving verified claim** of a skill/option-library heterogeneous-team system that selects
the coordination/planning **METHOD per task BY DIFFICULTY** (vs. merely allocating tasks). The
difficulty-gated *method-selection* move for skill-based teams appears **un-claimed**.
⚠️ **Caveat: absence of a verified claim ≠ confirmed absence.** A strong competitor could exist
undiscovered — flagged for round 4 (esp. "MAPF-only-when-needed" / adaptive coupling gated by
conflict/congestion density, which is a difficulty proxy).

### 9.4 Axis 3 — Disaster / wildfire / SAR heterogeneous teams — VERDICT: OPEN (weak negative)

**No surviving verified claim** of a wildfire/SAR/disaster heterogeneous (UAV+UGV) system that
does **difficulty-aware coordination-MODE selection** (deliberate vs. run a learned policy),
incl. any LLM+MARL/MAPF hybrid for disaster response. The **application space appears open** for
the wildfire framing. ⚠️ Same weak-negative caveat — confirm in round 4 before claiming it in print.

### 9.5 Most dangerous prior work (cross-cutting, re-confirmed): MARLIN — decisively differentiated

MARLIN (arXiv:2410.14383) is still the sharpest near-scoop (only confirmed LLM-negotiation + MARL
for a robot team), but round 3 nailed the differentiation: its LLM↔RL switch is **training-time
only**, a function of **training stage / plan-quality**, *not* per-task difficulty/coupling at
deployment; evaluated on 5 corridor-traversal variants vs. MAPPO/LLM-only, plotted vs. **training
episodes** — **no per-mode completion-time-vs-difficulty measurement at inference.** (Correction to
§8: it's 5 scenario variants, not a "single fixed task.") No 2025–2026 MARLIN follow-on extending
it to deployment-time/difficulty-gated selection surfaced.

> **Paper-ready differentiation sentence:** *"MARLIN uses the LLM as a training-time scaffold (mode
> depends on learning progress, measured in episodes-to-performance); GarageNet has no training-stage
> switch — it is a deployment-time router selecting the coordination mechanism per task by required
> coupling/difficulty, optimizing measured completion time, and is the first to report per-task
> completion time for each cooperation mode across a graded difficulty axis."*

### 9.6 Final verdict & sharpest one-sentence framing

**The GarageNet thesis remains publishable and un-scooped.** Recommended framing:

> *"GarageNet brings classical value-of-computation metareasoning to multi-robot teams as a
> deployment-time router that selects the coordination MECHANISM (LLM deliberation / hybrid /
> pre-trained MARL-MAPF policy) per task by required coupling, minimizing deliberation+execution
> time, with the first per-task completion-time measurement per cooperation mode across a difficulty axis."*

Positioning stack: **theory** = metareasoning/VOC (Boddy-Dean, Zilberstein, Hansen, Lin, Sung-Stone,
Paglieri); **closest structural prior** = Raja-Lesser multi-agent meta-level control (differentiate);
**closest system prior** = MARLIN (differentiate: train-time vs deploy-time); **conceptual neighbor**
= Sliding/Adjustable Autonomy (differentiate: human-triggered vs difficulty-triggered);
**task taxonomy to build the trigger on** = iTax coupling degree.

### 9.7 The crucial design question this surfaces (must answer before/while building)

How does GarageNet **operationalize "required coupling / task difficulty" as a measurable,
a-priori-computable gating signal**? The whole VOC lineage assumes a value-of-computation estimate.
GarageNet must specify **what predicts whether LLM deliberation pays off for a given task** — and
critically, **whether that predictor itself adds latency** that must be folded into the
deliberation-cost accounting. (A router whose routing decision is itself slow undercuts the thesis.)

### 9.8 Remaining unknowns (optional round 4)

1. **Axis 2 direct verification** — skill/option-library teams selecting *method by difficulty*;
   "MAPF-only-when-needed" / adaptive coupling gated by conflict density.
2. **Axis 3 direct verification** — disaster-robotics LLM+learned-policy hybrids 2023–2026.
3. **MARLIN forward-citation search** — any follow-on pushing it to deployment-time/difficulty gating.
4. **The gating-signal design** (§9.7) — partly a research-design question, not only a literature one.

### 9.9 Round-3 key sources

- Boddy & Dean, IJCAI-89 (deliberation scheduling) · Zilberstein 1996, AI Magazine 17(3)
- Hansen & Zilberstein 2001, AIJ (S0004-3702(00)00068-0) · Lin/Kolobov/Kamar/Horvitz, IJCAI'15
- Sezener 2018 — arXiv:1811.03035 · Sung & Stone 2024 — arXiv:2410.05828
- Paglieri et al. 2025 (Learning When to Plan) — arXiv:2509.03581 · IBM "When to Reason" — arXiv:2510.08731
- **Raja & Lesser, multi-agent meta-level control** — doi:10.1007/s10458-006-9008-z (closest structural prior)
- MARLIN — arXiv:2410.14383 + github.com/SooratiLab/MARLIN
