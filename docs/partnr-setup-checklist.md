# PARTNR Setup & Phase-0 Execution Checklist

> Date: 2026-07-03. Hand-off checklist for running the REAL Phase-0 experiment on a GPU machine.
> Everything in `garagenet/` is designed so that completing this checklist plugs the real
> benchmark into the already-tested pipeline (sweep → CSV → crossing plots → stats).

## 0. Machine requirements

- Linux + NVIDIA GPU (Habitat 3.0 rendering; ≥8 GB VRAM comfortable), ~100 GB disk for datasets.
- Conda/mamba. CUDA driver compatible with the habitat-sim build you install.
- For the L0 arm: either (a) local LLM serving (vLLM + Llama-3-8B-Instruct — PARTNR's default
  HF path) or (b) an API backend (`plan_config.llm=openai_chat`). Local serving is preferred:
  latency is then a *measured system property*, not a network artifact (still report both).

## 1. Install PARTNR (upstream instructions are authoritative)

```bash
git clone https://github.com/facebookresearch/partnr-planner   # MIT, ICLR'25
cd partnr-planner
# Follow INSTALLATION.md exactly (conda env, habitat-sim, habitat-lab, habitat-llm).
# Then download the PARTNR episode datasets (data/datasets/partnr_episodes/v0_0)
# and the HSSD scenes per the repo's data scripts.
```

**Smoke tests (must pass before any GarageNet work):**
1. Run the shipped heuristic baseline: `habitat_llm/conf/baselines/heuristic_full_obs.yaml`.
2. Run one decentralized LLM baseline: `decentralized_zero_shot_react_summary.yaml`
   (first with a small/cheap backend to validate wiring).
3. Confirm per-episode logs contain success/percent-complete and step counts.

## 2. GarageNet integration (maps 1:1 to `garagenet/partnr_adapter.py` TODOs)

- [ ] **PartnrEnv adapter**: instantiate PARTNR's `EnvironmentInterface`/evaluation runner inside
      `PartnrEnv.reset/step`; map our `TaskInstance` → episode selection.
- [ ] **Timing wiring**: wrap every planner `get_next_action` call in `ledger.deliberation()` and
      every sim/skill step in `ledger.execution()` (real clocks — `TimingLedger` context managers).
      Log per-call latencies, not just totals (needed for the latency-distribution figure).
- [ ] **L0 arm**: reuse PARTNR's decentralized per-agent ReAct planners as-is.
- [ ] **L1 arm**: centralized one-shot LLM plan + skill execution (PARTNR variant config).
- [ ] **L2 arm (the one new component)**: a `Planner` subclass emitting skill assignments from a
      non-LLM coordinator; reuse `process_high_level_actions`. Ladder of increasing strength —
      (1) scripted/heuristic (exists upstream — start here), (2) MAPF-based assignment,
      (3) trained MARL policy. *The L2-capacity sweep for the robustness battery is exactly this
      ladder.*
- [ ] **Coupling ladder**: episode buckets by PARTNR task type
      (constraint-free → spatial → temporal → heterogeneous-capability), each mapped to a nominal
      level in [0,1]; keep scene/object difficulty matched across buckets.
- [ ] **Congestion control axis**: same task type, increasing agent/obstacle density
      (negative-control axis — no crossing predicted).

## 3. Phase-0 protocol (the pre-registered claims)

Pre-register BEFORE looking at results (docs/paper-proposal.md, Figure 2 battery):
1. Crossing exists on the coupling ladder (L2 fastest at low, L0 at high, L1 between).
2. NO crossing on the congestion axis (L2 dominates).
3. Crossing persists as L2 strength scales (scripted → MAPF → MARL): it may shift right,
   must not vanish.
4. Crossing shifts predictably with LLM backend latency (fast vs slow backbone).

Run matrix: {3 arms} × {coupling ladder ≥4 levels + congestion ≥4 levels} × {≥10 episodes/cell}
× {≥2 LLM backends} × {L2 ladder ≥2 strengths}. Report mean ± 95% CI; the crossing claim requires
disjoint CIs on each side. Output the same CSV schema as the mock sweep — plots/stats run unchanged.

## 4. Go/No-Go gate (from docs/idea-verdict-and-architecture.md §6)

- **GO** → Phase 1: port the allocators (`garagenet/allocators.py`) onto PARTNR missions with
  precedence structure (multi-stage episodes), measure per-agent mixing vs team-uniform.
- **NO crossing** (after the full battery) → pivot to the negative-result measurement paper;
  the harness, protocol, and theory all survive the pivot.
