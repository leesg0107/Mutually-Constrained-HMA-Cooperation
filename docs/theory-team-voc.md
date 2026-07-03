# Team Value-of-Computation: Formalization & Non-Separability Result

> Date: 2026-06-27. Resolves reviewer-risk R3 (the real technical centerpiece of algorithmic
> direction C): does per-agent value-of-computation, coupled by the team critical path, yield a
> genuine result the single-agent VoC lineage cannot? **Yes — with an honest altitude caveat (§7).**
> Derived here directly. Companion to `algorithmic-direction-C.md`.

---

## 1. Why we need this

Direction C's headline is a *per-agent* metareasoning allocator. The sharpest reviewer objection
(R3) is: "this is RARRL/single-agent value-of-computation run once per robot — the 'team' adds a
word, not a result." To defeat that, the paper needs a theorem showing the team problem is **not
separable** into N independent single-agent VoC problems — i.e., that deciding each robot's
coordination mode *locally* is provably wrong, and *why*. This section provides it.

---

## 2. Model

**Mission as a DAG.** A mission is a DAG `G = (V, ≺)` of subtasks over agents `i ∈ {1..N}`; `j ≺ i`
means subtask `i` cannot start until `j` finishes (precedence). For the wildfire example:
`map(drone) ≺ transport(UGV)`.

**Coordination mode (the decision variable).** For each agent `i` we choose a coordination
tightness `κ_i ∈ [0,1]` (continuous; binary `{react=0, delib=1}` for the cleanest proofs). `κ_i=0`
= run the fast pre-trained reactive policy, zero deliberation; `κ_i=1` = full LLM deliberation.

**Two cost components.**
- **Deliberation latency** `D_i(κ_i)`, non-decreasing, `D_i(0)=0`. (Optionally contended — §6.)
- **Execution time** `E_i(κ_i, κ_{≺i})` where `κ_{≺i}` are the modes of `i`'s **upstream** agents.
  This is the crux: `i`'s execution can depend on whether an *upstream* agent deliberated (a good
  upstream plan/map speeds `i`'s execution). Write the **cross-agent term** explicitly.

**Finish times (makespan).** With precedence, `i`'s start is the max finish of its predecessors:
```
f_i = max_{j ≺ i} f_j  +  D_i(κ_i)  +  E_i(κ_i, κ_{≺i})
```
Mission completion time (makespan) `T(κ) = max_i f_i`. Each mode must satisfy a success constraint
`p_i(κ_i, κ_{≺i}) ≥ 1−δ`.

**Two solvers.**
- **Decentralized / per-agent greedy** `κ^G`: each agent `i` picks `κ_i` to minimize its **own**
  completion-time contribution `D_i(κ_i) + E_i(κ_i, ·)` using only **local** information (its own
  latency and its own execution time). This is what a deployed *decentralized* per-agent VoC
  metareasoner (RARRL-per-robot) actually does — it cannot see the effect of `κ_i` on *other* agents.
- **Joint** `κ^*`: `argmin_κ T(κ)` over the whole team.

**Definition (inter-agent deliberation externality / coupling).** Agent `i` exerts an externality on
`i` via `κ_j` (j ≺ i) whenever `E_i(κ_i, κ_j)` actually depends on `κ_j`. Define the structural
coupling of an instance:
```
χ_struct = max_{j ≺ i}  | E_i(·, κ_j=0) − E_i(·, κ_j=1) |        (cross-agent benefit magnitude)
```
and the operational coupling = the **decentralization regret** `T(κ^G) − T(κ^*)` (the directly
measurable quantity — and exactly the "coupling" axis the measurement paper sweeps).

---

## 3. Theorem 1 (Separability under zero externality)

**Claim.** If no agent's execution time depends on any other agent's mode (`χ_struct = 0`) and there
is no shared-resource contention, then decentralized per-agent greedy is team-optimal for makespan:
`T(κ^G) = T(κ^*)`.

**Proof.** With `χ_struct=0`, `E_i` depends only on `κ_i`, so each agent's own duration
`d_i(κ_i) := D_i(κ_i)+E_i(κ_i)` is a function of `κ_i` alone. Greedy sets `κ_i^G = argmin_{κ_i}
d_i(κ_i)`, so `d_i(κ_i^G) ≤ d_i(κ_i)` for all `i` and all alternatives. Makespan over a DAG is a
non-decreasing function of each node's duration (every path length is a sum of durations; the max of
sums is monotone in each term). Hence minimizing every `d_i` simultaneously minimizes every path
length and therefore their max: `T(κ^G) ≤ T(κ)` for all `κ`, i.e. `κ^G` is optimal. ∎

**Reading.** When tasks are *uncoupled*, you may decide each robot's mode locally and cheaply — no
joint reasoning needed. This is the formal license for cheap decentralized routing at low coupling.

---

## 4. Theorem 2 (Unbounded sub-optimality under externality)

**Claim.** If some agent's execution depends on an upstream agent's mode (`χ_struct > 0`), then the
decentralization regret is unbounded: for any `R>1` there is an instance with
`T(κ^G) / T(κ^*) ≥ R`. Moreover `κ^G` is a *dominant-strategy* outcome (robust to the solution
concept), so the failure is not a coordination tie-break artifact.

**Proof (wildfire-shaped counterexample).** Two agents, `A ≺ B` (drone maps; UGV transports).
Modes binary. Set `D_A(react)=0, D_A(delib)=d`; `E_A=0` (A's own execution is mode-independent —
A's "deliberation" *produces a good map for B*, it doesn't change A's own task time); `D_B=0`; and
the **cross term**
```
E_B(κ_A=delib) = g   (good upstream plan → fast transport),
E_B(κ_A=react) = M   (bad/no plan → slow transport),     with M ≫ g > d > 0.
```
- `κ_A = delib`: `f_A = d`, `f_B = d + g`. Makespan `= d+g`.
- `κ_A = react`: `f_A = 0`, `f_B = M`. Makespan `= M`.

*Joint optimum*: `κ^* = (delib)`, `T(κ^*) = d+g`.

*Greedy*: A minimizes its **own** finish `f_A`: `f_A(react)=0 < f_A(delib)=d`, so `κ_A^G = react`
**regardless of B** (react is dominant for A — A bears the latency `d` but the benefit `M−g`
accrues entirely to B, which A's local objective cannot see). Thus `T(κ^G) = M`.

Therefore `T(κ^G)/T(κ^*) = M/(d+g) → ∞` as `M→∞`. ∎

**Reading.** The cost of deliberation (latency `d`) is paid by the *upstream* agent, but its benefit
(`M−g`) lands on a *downstream* agent on the critical path. A decentralized per-agent VoC
**systematically under-deliberates on upstream/bottleneck agents** because the payoff is non-local.
This is precisely the wildfire structure: a drone minimizing its *own* time would skip careful
mapping; the *team* needs it to map well so the UGV's transport is fast.

---

## 5. Corollary (the design rule — a genuinely new lever)

Combining Thms 1–2: **the coupling degree governs not just *which mode* each agent takes, but
*whether the mode can be decided locally at all*.**
- **Low coupling** (`χ ≈ 0`): decentralization regret ≈ 0 → decide per-agent locally and cheaply
  (decentralized metareasoning suffices).
- **High coupling** (`χ` large): decentralization regret is large → modes must be decided
  **jointly** (centralized metareasoning), and the allocation is dominated by the **critical-path /
  bottleneck** agent's deliberation.

So GarageNet's metareasoner has **two coupled levels**: (i) per-agent mode/κ selection, and (ii) a
*meta*-decision of decentralized-vs-joint mode selection, *itself* gated by coupling. This second
level is new — no surveyed work (RARRL single-agent; Raja-Lesser single-axis; MARLIN team-uniform)
has it — and it ties back to the latency thesis: **centralized joint metareasoning needs global
information and therefore costs latency**, so you pay for it only when coupling makes it worth it.
That is a *second* value-of-computation decision, one level up.

---

## 6. Extensions

**Continuous κ.** With `κ_i ∈ [0,1]`, greedy solves `∂/∂κ_i [D_i + E_i(κ_i)] = 0` ignoring
`Σ_{k : i ≺ k} ∂E_k/∂κ_i` (the downstream marginal benefit). The joint optimum's stationarity
includes that cross term; the gap between them is exactly the omitted downstream-benefit gradient —
a clean continuous analogue of Thm 2, and the formal handle for the "continuous coupling knob."

**Shared deliberation resource (contention → congestion game).** If deliberation draws on a shared
LLM-inference server of bounded throughput, `D_i` increases in the number of simultaneously
deliberating agents `|S|` (e.g., serialized: `D_i ∝ |S|`). Now agents impose a *negative* latency
externality on each other. Under a **sum/throughput** objective this is a congestion game; greedy =
Nash, and the price of anarchy bounds the regret. (Under makespan the negative externality is weaker;
the positive precedence externality of §4 is the dominant non-separability source — keep §4 as the
headline result and contention as a secondary mechanism.)

---

## 7. ⚠️ Honest assessment of the theory's depth

- **What it is:** a correct, clean **characterization**: coupling = inter-agent deliberation
  externality; zero externality => greedy optimal (Thm 1); any externality => unbounded regret
  (Thm 2); therefore coupling decides decentralized-vs-joint metareasoning (Corollary).
- **What it is NOT:** a deep new mathematical result. "Externalities break greedy / selfish routing"
  is, in the abstract, an expected fact (congestion games, scheduling with precedence). A pure
  theory venue would find Thms 1–2 unsurprising in isolation.
- **Where the value actually is** (and how to pitch it): not the *existence* of the gap but
  (a) **identifying inter-agent coupling with the cross-agent deliberation externality**, which makes
  the previously-fuzzy "coupling" axis *precise and measurable* (decentralization regret); and
  (b) the **Corollary's new lever** — coupling gates *decentralized-vs-joint* metareasoning, a
  decision no prior multi-robot-LLM system makes. Pitch as **"a formalization that turns coupling
  into a measurable quantity with an operational decision rule,"** not as a theorems-for-their-own-sake
  contribution. This altitude matches a robotics/MAS venue (CoRL/ICRA/AAMAS), not a COLT-style one.
- **Net effect on the paper:** R3 is resolved — the "team" is no longer decorative. The paper becomes
  **measurement (the crossing) + theory (coupling = externality => decentralized-vs-joint rule) +
  system (the allocator)**, which is a materially stronger and better-defended package than
  system-alone. It does *not* make this a theory paper; it gives the systems paper a spine.

---

## 8. How each piece feeds the paper

- **Thm 2 + the wildfire counterexample** → Section 3 (Problem Formulation) motivation: *why* a team
  metareasoner is needed (local VoC is provably wrong under coupling). Becomes a worked example/figure.
- **Operational coupling = decentralization regret** → unifies with the measurement paper's difficulty
  axis: the x-axis "coupling" is now *defined* as the thing that makes greedy fail, and is measurable.
- **Corollary (decentralized-vs-joint)** → a distinct, citable contribution and an ablation
  (decentralized-only vs joint-only vs coupling-gated meta-allocator).
- **Continuous-κ stationarity gap (§6)** → the precise object the learned "tightness knob" approximates.

## 9. Open theoretical follow-ups (optional)
- A *bounded* regret result: regret ≤ f(χ) for a concrete coupling measure χ (turn the unbounded
  worst case into an instance-dependent guarantee) — would strengthen the Corollary into a real rule.
- Approximation guarantee for a *cheap* coupling estimator gating decentralized-vs-joint (the gate's
  own latency vs the regret it avoids — connects to the deliberation-cost ledger).
- PoA bound for the contended/sum-objective congestion-game variant (§6).
