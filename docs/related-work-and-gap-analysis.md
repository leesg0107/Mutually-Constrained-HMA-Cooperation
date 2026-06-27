# Related Work & Gap Analysis — Task-Difficulty-Gated Cooperation Levels for Heterogeneous Multi-Robot Teams

> Scooping check + gap analysis for the GarageNet "cooperation-level (L0–L2)" framing.
> Date: 2026-06-27. Method: fan-out web search (6 angles, 23 sources fetched) → claim
> extraction (95 claims) → 3-vote adversarial verification (25 verified, 0 killed) → synthesis.
> Scope caveat: arxiv/OpenReview returned 403 through the proxy during verification, so most
> claims rest on verbatim abstract quotes + convergent secondary summaries, not full-text reads.
> Re-run this check close to submission (the 2023–2026 LLM-multi-robot space moves fast).

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
