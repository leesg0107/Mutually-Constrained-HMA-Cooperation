# Idea Verdict & Buildable Architecture — Go/No-Go Assessment

> Date: 2026-06-28. Synthesizes 5 verified research rounds (3 scoop/gap rounds, benchmark
> feasibility + PARTNR source check, direction-C check) + the team-VoC theory (theory-team-voc.md)
> + 3 adversarially-critiqued paper framings (paper-proposal.md). This is the pre-implementation
> judgment: is the idea solid, is the contribution certain, is the level sufficient, and can a
> meaningfully-novel architecture actually be built.

---

## 1. VERDICT (summary)

| Question | Verdict |
|---|---|
| Is the idea solid? | **Yes, conditionally** — it rests on ONE falsifiable empirical bet (§2). Un-scooped across 5 targeted verification rounds. |
| Is the contribution certain? | **The measurement is near-certain; the theory is certain-but-modest; the architecture is novel-but-must-be-built.** Three axes back each other up (§3). |
| Is the level sufficient (수준)? | **Solid full-paper at CoRL / ICRA / IROS / AAMAS.** Not a landmark; a well-defended phenomenon+theory+system paper. Ceiling rises if the continuous knob works (§4). |
| Can a novel architecture be built, meaningfully? | **Yes — 3 genuinely-new atoms, each mapped to a measurable gain claim, buildable in stages with kill criteria (§5–6).** The riskiest atom (continuous knob) is a stretch stage, not a dependency. |

**Overall: GO — with the staged plan of §6, entering at Phase 0 (measurement harness), because every
later phase has a publishable fallback if its bet fails.**

---

## 2. The one bet everything rests on (be honest about this)

**The bet:** on identical heterogeneous-team tasks, completion-time curves of {LLM-deliberation,
learned-policy} coordination **cross** along a reasoning-coupling axis, and the crossing is
**robust** (persists under L2 scaling, vanishes on a congestion control axis, shifts predictably
with LLM latency).

- If TRUE → the phenomenon motivates the theory (coupling=externality) and the architecture
  (per-agent allocation), and the whole 3-axis paper stands.
- If FALSE (e.g., L2 always wins, or crossing vanishes with a stronger L2) → the honest finding
  becomes "deliberation never pays at these latencies" — still publishable as a negative/measurement
  result, but a weaker paper. **This is why Phase 0 runs first.**

Everything else (scooping, feasibility, theory) has been de-risked; this empirical bet cannot be —
it can only be tested. That is normal and healthy for a paper whose headline is a phenomenon.

---

## 3. Contribution certainty, per axis

| Axis | Claim | Certainty | Basis |
|---|---|---|---|
| **Measurement** | First systematic wall-clock characterization of LLM-vs-learned-vs-hybrid coordination across a coupling axis; crossing curves | **High** (un-scooped, verified round 1–4; field measures tokens/steps only) | Needs the §2 bet to yield a *crossing*; even without one, the characterization itself is new |
| **Theory** | coupling = inter-agent deliberation externality; Thm 1 (separable ⇔ no externality), Thm 2 (unbounded decentralization regret; wildfire counterexample), Corollary (coupling gates decentralized-vs-joint metareasoning) | **Certain but modest depth** — a characterization that makes "coupling" measurable (= decentralization regret), not deep math | Already derived (theory-team-voc.md); pitch as formalization, never as standalone theory |
| **Architecture** | Per-agent runtime allocation of coordination mode (deliberate vs execute, ideally continuous κ), critical-path-aware | **Novel (Axis-1/3 verified open) but unbuilt** — the weight sits on 3 atoms below | Direction-C round: no per-agent simultaneous paradigm split exists; no dial-able coupling knob exists |

The three axes **mutually insure**: if the architecture underdelivers, measurement+theory still make
a paper; if the crossing is weaker than hoped, the architecture demo + theory still carry; only a
total failure of §2's bet forces the negative-result reframe.

---

## 4. Level assessment (수준) — calibrated, no flattery

- **Realistic tier:** strong full paper at **CoRL / ICRA / IROS / AAMAS** (AAMAS fits the
  metareasoning frame best; CoRL fits the embodied experiment best). The package —
  phenomenon + formalization + system, with the falsifiability battery — is *above the median*
  accepted systems paper because the defense work is pre-done.
- **Not:** a NeurIPS/ICML theory contribution (Thms 1–2 are characterizations), nor a landmark
  "new paradigm" paper.
- **What raises the ceiling** (in order of leverage):
  1. the **continuous κ knob actually working** (would be the first dial-able cooperation-tightness
     variable — a citable mechanism others reuse);
  2. a **bounded-regret gate** (regret ≤ f(χ) for a cheap coupling estimator — turns the Corollary
     into a guarantee);
  3. a **real-robot or wildfire-sim demo** making the per-agent split visceral.
- **What lowers it:** shipping without the falsifiability battery (→ "engineered crossing" rejection),
  or letting the architecture story run ahead of what is actually built (→ "MARLIN with extra steps").

---

## 5. The architecture — GarageNet allocator (buildable, with the novelty located precisely)

**Named components (build order ≠ novelty order):**

```
Mission DAG ──> [1] Coupling estimator  χ̂(τ_i)        (cheap, a-priori; its latency is charged)
                     │
                     v
            [2] Team metareasoner (the allocator)
                     ├── Corollary gate: χ̂ low → decentralized per-agent VoC
                     │                   χ̂ high → joint critical-path allocation (Thm 2 regime)
                     v
            per-agent mode assignment  κ_i ∈ [0,1]  (Phase 1: κ_i ∈ {0,1})
                     │
                     v
            [3] Mechanism spectrum, per agent
                     ├── κ=0: pre-trained reactive MARL/MAPF policy (zero deliberation)
                     ├── κ=1: LLM deliberation/negotiation (PARTNR ReAct planners)
                     └── 0<κ<1: κ-conditioned policy (Phase 2; β/SLIM-style budget conditioning)
                     │
                     v
            [4] Async interface: slow-deliberating agents publish plan constraints;
                fast-executing agents treat them as non-blocking updates (Phase 3)
```

**Genuinely new atoms (each verified open, each tied to a measurable gain claim):**

| # | New atom | Verified-open by | The gain claim that makes it *meaningful* |
|---|---|---|---|
| A1 | **Per-agent simultaneous paradigm split at runtime** (some robots deliberate while others execute, in one team) | Direction-C Axis 1 (no system does it) | Per-agent allocation beats the best **team-uniform** router on makespan (drones needn't wait for the UGV's deliberation) |
| A2 | **Coupling-gated decentralized-vs-joint metareasoning** (the Corollary as a mechanism) | theory-team-voc Corollary (no prior has this lever) | Coupling-gated allocation beats always-decentralized (by Thm-2 regret) AND always-joint (by joint's own latency) |
| A3 | **Continuous cooperation-tightness κ as a trained, dial-able input** | Direction-C Axis 3 (does not exist; grounding = SLIM/β, RARRL, HyperMARL) | κ-conditioned policy beats the best discrete {0,1} allocation on mid-coupling tasks (the L1 region), and its optimum tracks the §6-theory stationarity point |
| — | *Assembled, not claimed:* LLM arm, reactive arm, PARTNR harness, gating classifiers | (PARTNR ships these / standard) | reproducibility artifact only |

**The meaningfulness test is built in:** each atom's gain claim is an ablation the experiments run.
If a gain is ≈0, that atom is dropped from the contribution list honestly (e.g., if A3's continuous
knob never beats discrete, the paper ships with A1+A2 and reports the negative — Axis-1 novelty
survives without it).

---

## 6. Staged implementation plan with kill criteria (the "철저하게" part)

| Phase | Build | Validates | Kill / pivot criterion | Fallback if killed |
|---|---|---|---|---|
| **0. Measurement harness** (PARTNR + timing + L2 wrapper `Planner` subclass; coupling ladder; congestion control axis) | wall-clock split instrumentation; 2 arms on identical tasks | §2's bet: does a robust crossing exist? | No crossing after L2-capacity sweep + backbone sweep → **pivot to negative-result measurement paper** | Negative/characterization paper (weaker but publishable) |
| **1. Discrete per-agent allocator** (A1+A2: κ_i∈{0,1}, coupling estimator, Corollary gate, oracle + learned gate) | per-agent split beats team-uniform router; coupling-gated beats always-dec/always-joint | Gains vs team-uniform ≈ 0 → A1 not meaningful on this benchmark → re-examine task DAG structure (needs real precedence externality, wildfire-shaped tasks) | Ship measurement+theory+router-as-payoff (the paper-proposal.md shape) |
| **2. Continuous κ knob** (A3: β/SLIM-style budget-conditioned policy; κ swept at inference) | knob beats discrete in the mid-coupling region; tracks stationarity prediction | Continuous never beats discrete → report negative, keep A1+A2 | Paper ships with discrete allocator; knob becomes future work |
| **3. Async interface** (non-blocking constraint publication between deliberating/executing subteams) | removes the "hand-waved interface" (R6) objection; enables true simultaneity | If a simple freeze-and-handoff suffices empirically, ship that and scope the general problem as future work | Simple synchronous handoff (weaker but honest) |

**Effort reality-check (from verified feasibility):** Phase 0 = days-to-2-weeks (instrumentation low;
L2 wrapper verified drop-in; the *coupling ladder design* is the real thinking). Phase 1 = ~weeks
(the allocator is a `Planner` subclass orchestrating existing arms). Phase 2 = the research-grade
risk (training a κ-conditioned MARL policy; weeks-to-months). Phase 3 = design + engineering.

---

## 7. Final honest statement

The idea is **solid and the contribution is defensible**, because five adversarial verification
rounds failed to find the conjunction anywhere, the theory gives the axis a precise measurable
meaning, and the feasibility path is source-verified. It is **not risk-free**: it stands on one
empirical bet (the crossing), one research-grade mechanism (the κ knob), and one unsolved design
problem (the async interface) — but the staged plan makes each of these a *gate with a fallback*
rather than a cliff. The correct next action is **Phase 0**, because it is cheap, it tests the only
thing that cannot be de-risked by reading, and every subsequent investment decision hangs on its
answer.
