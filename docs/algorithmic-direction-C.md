# Algorithmic Direction C — Heterogeneous Coupling-Conditioned Cooperation

> Date: 2026-06-27. Deep scoop+grounding check (5 axes, ~25 sources, claims 3-vote-verified).
> Companion to `paper-proposal.md` — this is the chosen ALGORITHM-first direction and supersedes the
> measurement-first framing as the headline (the measurement/crossing becomes motivation + evaluation).
> Same 403-proxy caveat (abstract-level verification). Three key neighbors (CoMuRoS, RARRL, SLIM/β)
> are 2026 frontier preprints — provisional; re-check near submission.

---

## 0. The direction (what we are building)

In a heterogeneous multi-robot team, **different robots/sub-teams operate at different coordination
modes simultaneously, set by each robot's LOCAL situation/coupling**: some run a fast pre-trained
MARL/MAPF policy with zero deliberation (tight, reactive, role-predefined), others engage in slow
LLM deliberation/negotiation (ambiguous, high-coupling allocation). A metareasoning controller
allocates the coordination mode — ideally as a **continuous coupling/tightness knob** — per
robot/sub-team, jointly constrained by the **team critical path**, to minimize total mission
completion time (deliberation latency + execution). Wildfire example: the 2 drones immediately run a
learned mapping policy (no deliberation) while the UGV is allocated transport via brief LLM
deliberation — each agent's mode follows its local situation.

## 1. Verdict — OPEN (not scooped) ✅

No surveyed system instantiates the conjunction (runtime × per-agent × paradigm-split × continuous
knob × team-critical-path × completion-time). Every nearest neighbor matches **one** sub-dimension
and misses the rest.

## 2. Per-axis findings (scoop + grounding)

**AXIS 1 — simultaneous per-agent heterogeneous coordination modes: OPEN.** Closest + differentiators:
- **MARLIN** (2410.14383): LLM-negotiation + MARL, but switch is **training-time**, **team-uniform**
  (shared prompt), deployed policy is pure MARL — no runtime per-agent split, no continuous knob.
  *(the "MARLIN with extra steps" risk; differentiate on runtime-vs-training + per-agent-vs-team.)*
- **CoMuRoS** (Frontiers 2026 / 2511.22354): **one uniform paradigm** — a central Task-Manager LLM
  deliberates while every robot runs a local LLM; allocates **tasks, not modes**; no fast learned arm.
- **LAN2CB** (2507.16068): central LLM compiles one mission to code at **compile time**; homogeneous.
- **RARRL** (2603.16673): per-agent when-to-deliberate, but **single agent** — no team, no coupling.

**AXIS 2 — Tambe adjustable autonomy (most dangerous neighbor): differentiable, NO scoop.**
Scerri/Pynadath/Tambe (JAIR 2003): adjustable autonomy = transferring **decision-making control to
another entity (usually agent→HUMAN)** via a **discrete MDP transfer-of-control strategy** that
minimizes **miscoordination cost**. STEAM (Tambe JAIR 1997) = shared joint-intentions teamwork
knowledge for all members. EMICS/variable autonomy (1911.04848) = single robot + one human toggling
discrete autonomy levels. **No version switches between a deliberative and a learned-policy mode per
agent by task difficulty.** Four airtight differentiators for GarageNet:
1. **paradigm switched** = LLM-deliberation ↔ learned MARL/MAPF policy (not who-holds-control, agent↔human);
2. **trigger** = a-priori task coupling/difficulty (not environmental uncertainty/risk);
3. **objective** = minimize total mission completion time (not miscoordination cost);
4. **tightness** = continuous learned variable (not a discrete planned transfer sequence).

**AXIS 3 — continuous coupling/tightness knob: DOES NOT EXIST → must build (the core mechanism work).**
No work exposes inter-agent **coupling-degree** as a controllable inference-time input. Grounding to
build the knob on:
- **RARRL** (2603.16673) — learned, controllable per-agent compute/deliberation budget (single-agent
  VoC knob; the closest precursor — cite-differentiate as single-agent).
- **SLIM / β** (2605.21085, "Decoupling Communication from Policy", 2026) — **β = a normalized
  per-agent bandwidth budget** unifying sparsity/rounds/message-dim into one scalar; SLIM decouples
  the comms pathway from the policy latent. **The strongest existing mechanism for a coupling-budget
  scalar — build the tightness knob on this line** (beyond IC3Net's binary gate).
- **HyperMARL** (2412.04233, NeurIPS'25) — hypernetwork-conditioned per-agent params, but conditioned
  on **identity**, diversity learned **automatically**, explicitly **not** a dial-able input.
  Mechanism inspiration (hypernetwork/FiLM conditioning), not a coupling knob, not a scoop.

**AXIS 4 — coalition/auction formation allocates TASKS/MEMBERSHIP, not coordination MODE: OPEN.**
(2509.22469 = team-wide uniform auction over tasks.) GarageNet allocates **how each sub-team
coordinates** (paradigm + tightness), not who-does-what. *Caveat: one representative paper; broader
coalition literature needs a deeper sweep — see open items.*

**AXIS 5 — interface + decentralized metareasoning: partially grounded, key piece OPEN.**
Per-agent metareasoning that splits effort between local scheduling vs inter-agent coordination
exists (**Rubinstein/Smith/Zimmerman**, Metareasoning MIT Press 2011, DARPA Coordinators) and
deliberative/reactive **temporal** interleaving exists (**Jensen & Veloso**, AAAI'98) — but neither
does **per-agent paradigm allocation** nor **team-critical-path-coupled VoC choosing LLM-vs-policy**.
**The async interface** (a slow-deliberating LLM sub-team handing off to / staying consistent with a
fast-executing policy sub-team at different decision rates) is an **unsolved open problem** in the
surveyed literature.

## 3. The precise novel algorithmic atom (contribution claim)

> *"We introduce a metareasoning coordination-mode allocator for heterogeneous multi-robot teams
> that, at RUNTIME and PER ROBOT/SUB-TEAM, assigns a position on a CONTINUOUS coordination-tightness
> spectrum spanning a fast pre-trained reactive MARL/MAPF policy (zero deliberation) and slow
> LLM-based deliberation/negotiation, driven by each agent's LOCAL task coupling/difficulty and
> jointly constrained by the TEAM critical path, minimizing total mission completion time
> (deliberation latency + execution). Unlike MARLIN, the LLM-vs-policy choice is a deployment-time
> per-agent allocation, not a uniform training-time curriculum; unlike Tambe adjustable autonomy,
> control moves between two AI PARADIGMS (not agent↔human) on a CONTINUOUS dial (not a discrete MDP
> transfer sequence) and optimizes completion time (not miscoordination); unlike RARRL, the
> value-of-computation is solved JOINTLY across a team coupled by the critical path, not for a single
> agent; unlike coalition/auction methods, what is allocated is the COORDINATION MECHANISM/coupling
> level, not tasks or membership."*

**Must cite-and-differentiate:** (1) MARLIN 2410.14383; (2) Scerri/Pynadath/Tambe JAIR 2003 +
STEAM JAIR 1997; (3) RARRL 2603.16673; (4) Rubinstein/Smith/Zimmerman 2011 (metareasoning for
coordination); (5) SLIM/β 2605.21085 (tightness-knob mechanism grounding).

## 4. ⚠️ The three hard UNBUILT pieces — this is where the paper's weight (and risk) now sits

The direction is open, but novelty has migrated from "measure a phenomenon" to **"build three things
that do not yet exist."** Honest assessment: higher ceiling, higher cost/risk than the
measurement-first paper. The real technical depth reviewers will demand:

1. **The continuous coupling/tightness knob (R4 — riskiest underspecified piece).** How is the
   coupling-degree variable *defined and trained* so it is dial-able at inference? Candidates:
   bandwidth budget (β/SLIM style) · FiLM/hypernetwork conditioning scalar · adaptive-computation-time
   horizon · centralization-degree mixing coefficient. **No prior exposes coupling-degree as a
   controllable input — must be invented and validated.**
2. **Team-critical-path-coupled per-agent VoC (R3 — the real technical centerpiece).** Each agent
   solves its own value-of-computation, but jointly constrained so the **bottleneck agent's
   deliberation latency governs the allocation**. This (not the single-agent knob) must be the
   technical heart, ideally with the non-separability result (per-agent greedy ≠ team-optimal).
3. **The async deliberate↔execute interface (R6 — genuine open gap).** Consistency/handoff between a
   slow LLM-deliberating sub-team and a fast policy-executing sub-team at different decision rates.
   No surveyed work solves it; reviewers will probe for guarantees.

## 5. Updated reviewer-risk list (adversarial AC)

- **R1 "MARLIN with extra steps"** → training-time/team-uniform vs runtime/per-agent + continuous knob.
- **R2 "adjustable autonomy / transfer-of-control"** → AI-paradigm + continuous + completion-time vs
  human-transfer + discrete + miscoordination.
- **R3 "RARRL lifted naively"** → single-agent VoC vs team-critical-path-coupled VoC. *Put the team
  math at the center, or this lands.*
- **R4 "the knob is just HyperMARL/conditioned MARL"** → identity/auto-diversity vs dial-able
  coupling-degree. *Must give a precise knob definition + training procedure.*
- **R5 "coalition/auction already does heterogeneous allocation"** → tasks/membership vs coordination mode.
- **R6 "the async interface is hand-waved"** → genuine gap; needs a concrete consistency/handoff mechanism.

## 6. Remaining unknowns (candidate round)

1. Deeper coalition/organizational-design sweep (does any allocate coordination *mechanism* per sub-team?).
2. Exact definition+training of the continuous coupling knob (mechanism design, partly research not lit).
3. The async/mixed-timescale interface mechanism (design + any distributed-systems precedent).
4. Distributed/multi-agent VoC under a makespan/critical-path objective (literature check).

## 7. Key sources
- MARLIN 2410.14383 · CoMuRoS 2511.22354 · LAN2CB 2507.16068 · RARRL 2603.16673
- Scerri/Pynadath/Tambe JAIR 2003 (10312) · Tambe STEAM JAIR 1997 (cs/9709101) · EMICS 1911.04848
- SLIM/β 2605.21085 · HyperMARL 2412.04233
- Rubinstein/Smith/Zimmerman 2011 (CMU/DARPA Coordinators metareasoning) · Jensen & Veloso AAAI'98
- Uncertainty-aware coupled MRTA 2509.22469
