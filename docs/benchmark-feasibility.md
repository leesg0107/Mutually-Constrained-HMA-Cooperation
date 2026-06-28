# Benchmark Feasibility Study — GarageNet Tier-1 Experiment

> Date: 2026-06-27. Deep-research (5 angles, 25 sources, 25 verified / 0 killed, 2 refuted).
> Question: which simulator can run BOTH an LLM-deliberation coordination arm AND a learned
> (MARL/MAPF) coordination arm on the SAME task instances, measure wall-clock completion time
> (deliberation-latency + execution-time), and sweep a controllable coupling/difficulty axis to
> produce the per-mode **time-vs-difficulty crossing** plot.
> Companion to `problem-statement.md` §6.

---

## 1. Headline results

- **No benchmark ships the full setup.** None natively (a) runs both paradigms on identical tasks
  AND (b) reports wall-clock time split into deliberation + execution AND (c) exposes a continuous
  coupling knob. Every candidate gives ~2 of 3; the third must be built.
- **Measurement contribution appears UN-scooped.** No benchmark or paper reports wall-clock
  completion time comparing an LLM-coordination arm vs. a learned-policy arm across a difficulty
  axis. (Medium confidence — absence-of-evidence over the candidate set, not an exhaustive sweep.)
- **No native outdoor wildfire / UAV-UGV.** All candidates are indoor/tabletop/grid; the wildfire
  scenario is a **custom build** (Tier-3 demo only). EMOS has the closest embodiment mix.

## 2. Ranked recommendation

### 🥇 Primary — PARTNR (Meta, Habitat 3.0; arXiv:2411.00081, ICLR'25, MIT)
The only candidate shipping **both** a runnable LLM-deliberation arm (centralized + decentralized
per-agent LLM, ReAct, swappable Llama-3 / OpenAI backends) **and** a learned execution arm
(neural nav/pick/place skills) **and** a heuristic planner, on the **same heterogeneous human-robot
tasks** (Spot + humanoid in Habitat 3.0), with built-in difficulty **types**
(constraint-free / spatial / temporal / heterogeneous-capability).

| 7-point | Assessment |
|---|---|
| 1. Heterogeneous agents | ✅ Spot robot + humanoid; heterogeneous-capability task category |
| 2. LLM-dialogue arm | ✅ native (centralized & decentralized; Llama-3-8B / OpenAI) |
| 3. Learned-policy arm | ⚠️ **partial** — learned arm is **low-level motor skills UNDER an LLM planner**, NOT a learned high-level MARL/MAPF *coordination* policy. The genuine non-LLM coordination baseline is the **heuristic planner**. |
| 4. Wall-clock time | ❌ reports % complete, success, sim-steps, planning-cycles — **no wall-clock**; instrument with `time.perf_counter` (low effort) |
| 5. Coupling knob | ⚠️ discrete task **types**, not a continuous knob; centralized config is a coordination-free oracle. Must engineer a graded coupling axis. |
| 6. License/maintenance | ✅ MIT, ICLR'25, Meta-maintained (`facebookresearch/partnr-planner`) |
| 7. Existing baselines | ✅ LLM/heuristic/learned-skill baselines published |

### 🥈 Fallback A — EMOS / Habitat-MAS (arXiv:2410.22662, ICLR'25)
**Best for the heterogeneous UAV-UGV story.** Native Fetch, Stretch, **DJI-M100 drone**, Spot — a
genuine drone+ground mix — with an LLM group-discussion arm (embodiment-aware, URDF "Robot Resume").
But metrics are steps/tokens (no wall-clock), **indoor-only**, and crucially its **learned/RL
policy arm on the same tasks is UNCONFIRMED** (the PPO-baseline claim was refuted 1-2). Use if the
UAV-UGV embodiment narrative matters and after verifying the learned arm.

### 🥉 Fallback B — RWARE (uoe-agents; arXiv:2006.07869)
**MARL-native, cleanest controllable knobs, trivial timing.** Knobs: warehouse size, #agents N,
requested shelves R (easy R=2N / hard R=N/2) → congestion as a coupling proxy; timing via
`time.perf_counter` around deliberation vs `env.step`. **But NO LLM arm** — must be built from
scratch. ⚠️ See §4 — pure congestion may not produce a crossing.

### Disqualified as primary (why)
- **RoCo/RoCoBench** (2307.04738) — strong LLM arm (GPT-4/Claude) + heterogeneous arms, but **no
  learned MARL/MAPF arm** on the same tasks (all baselines are LLM variants); steps/attempts only.
- **MAPF / League of Robot Runners** — congestion knob + planner-latency instrumentation, but **pure
  search, no LLM arm**; throughput metric. Good as the *learned arm* only.
- **CH-MARL** (2208.13626) — heterogeneous (humanoid+drone) but **pure MARL**, pre-LLM (2022),
  learned message-passing not dialogue; maintenance unconfirmed.
- **BEHAVIOR-1K / OmniGibson, SMACv2/MeltingPot** — either no paired LLM-vs-learned arm or no
  coordination-coupling difficulty axis suited to the crossing claim.

## 3. Top-pick build items (PARTNR) + rough effort

1. **Wall-clock instrumentation** — wrap LLM planning calls and skill execution; log
   deliberation-latency vs execution-time per task. **Low (days).**
2. **Genuine learned high-level COORDINATION arm (the real cost)** — wrap a MAPF/MARL high-level
   controller (or distill a policy) as a drop-in alternative to the LLM planner on the same tasks.
   ✅ **VERIFIED feasible as a WRAPPER (not from-scratch) — see §3a.** The remaining cost is
   *producing* the policy (train MARL / wire a MAPF solver to emit skill assignments), which is
   standard; the PARTNR integration is a single `Planner` subclass. **Medium (weeks).**
3. **Graded coupling axis** — turn discrete task types into a monotonic difficulty sweep
   (shared-resource contention, # co-decision agents, goal ambiguity, temporal-ordering depth).
   **Medium (weeks).**

## 3a. ✅ Source verification — the L2 learned-coordination arm is a WRAPPER (de-risked)

Read of PARTNR source (`facebookresearch/partnr-planner`, main) resolves the make-or-break unknown:

- **`habitat_llm/planner/planner.py` defines a clean `Planner` base class.** A subclass implements
  only two methods:
  ```python
  def get_next_action(self, instruction: str, observations: Dict, world_graph: Dict[int, "WorldGraph"])
        -> Tuple[Dict[int, Any], Dict[str, Any], bool]:   # -> (per-agent low-level actions, info, done)
  def reset(self) -> None
  ```
- **Planning is explicitly decoupled from execution.** The base provides `process_high_level_actions`
  that translates **high-level skill assignments → low-level commands**. So a coordinator only needs
  to emit *which skill each agent runs next*; PARTNR handles the motor execution.
- **Non-LLM planners ALREADY implement this interface** — the planner dir ships
  `scripted_centralized_planner.py` and `random_rearrange_planner.py` (alongside `llm_planner.py`,
  `centralized_llm_planner.py`, `zero_shot_react_planner.py`, `thoughtless_llm_planner.py`, `rag.py`).
  These are the **templates to copy** for an L2 controller.

**Verdict:** the L2 arm (MAPF/MARL high-level coordination) is a **drop-in `Planner` subclass**
reusing `process_high_level_actions` — a wrapper job, **not** a from-scratch sim integration. The
L0 (LLM dialogue) and L1 (hybrid) arms already exist as planner variants. **Wall-clock timing**
goes in the eval loop: time `get_next_action` (deliberation) vs. skill-execution steps separately.
This materially de-risks the project's biggest engineering unknown. *(Source: WebFetch of the
public repo README + `planner/` directory + `planner.py`, 2026-06-27.)*

## 4. ⚠️ Critical design insight — the difficulty axis must be one the LEARNED policy degrades on

The crossing claim ("L2 wins at low coupling, L0 wins at high coupling") only holds if difficulty is
the kind that **degrades the learned policy faster than deliberation latency hurts**. There are two
distinct "difficulty" axes and they behave oppositely:

- **Congestion / conflict density** (RWARE, MAPF) → an optimal MAPF/MARL policy keeps winning at ALL
  levels; an LLM is bad at low-level pathfinding and **never** wins. → **NO crossing.** (This is why
  RWARE-alone is a weak primary despite its clean knob.)
- **Allocation ambiguity / task novelty / heterogeneous-capability reasoning** (PARTNR's temporal /
  heterogeneous categories) → a fixed learned policy fails on novel/ambiguous allocation; reasoning
  succeeds. With easy low-ambiguity tasks where the policy is faster, **the crossing appears.**

**Implication:** the coupling axis must index **reasoning/allocation complexity**, not just
spatial congestion. This is exactly why **PARTNR's task-type ladder is the right instrument** and a
pure-congestion gridworld is not. State this explicitly in the paper to pre-empt "your crossing is
an artifact of a degenerate difficulty axis."

## 5. Recommended minimal setup for the crossing plot (Tier-1)

1. **Env:** PARTNR tasks, ordered along a reasoning-coupling ladder (constraint-free → spatial →
   temporal → heterogeneous), optionally refined into a finer graded sweep (§3.3).
2. **Three arms on identical instances:** L0 = decentralized per-agent LLM dialogue; L2 = learned/
   MAPF high-level coordination policy (§3.2); L1 = hybrid (LLM sets structure, policy executes).
3. **Metric:** wall-clock = deliberation-latency + execution-time (report split), plus success/PC.
4. **Sweep** the coupling ladder → plot time-vs-coupling per arm → identify crossing(s).
5. **Router:** oracle (lower-bound) + a lightweight learned/rule gate; show it tracks the lower
   envelope at near-zero routing overhead (account for the gate's own latency — §4 of problem-statement).
6. **Secondary (generalization):** repeat the crossing on a second env (RWARE with an added LLM arm,
   or EMOS) to show it is not a PARTNR artifact.

## 6. Open items to verify before committing

- ✅ **RESOLVED (§3a):** PARTNR admits a learned high-level coordination policy as a drop-in
  `Planner` subclass — the L2 arm is a wrapper, not a from-scratch build.
- Is the LLM-vs-learned **crossing observable** at realistic agent counts given Habitat sim speed?
- Can a clean monotonic coupling knob be engineered on PARTNR's discrete types?
- Does EMOS expose a runnable learned/PPO arm on the same tasks (refuted-but-not-disproven)? If yes,
  EMOS rises toward co-primary for the UAV-UGV story.

## 7. Sources
- PARTNR — arXiv:2411.00081 · github.com/facebookresearch/partnr-planner
- EMOS / Habitat-MAS — arXiv:2410.22662 · github.com/SgtVincent/EMOS
- RWARE — arXiv:2006.07869 · github.com/uoe-agents/robotic-warehouse
- RoCo — arXiv:2307.04738 · MAPF/LRR — arXiv:2404.16162 · CH-MARL — arXiv:2208.13626
