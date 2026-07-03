"""PARTNR adapter — the Phase-0 real-benchmark backend (skeleton).

Verified integration path (docs/benchmark-feasibility.md §3a):
  * PARTNR's `habitat_llm/planner/planner.py` defines a `Planner` base class
    with `get_next_action(instruction, observations, world_graph) ->
    (per-agent low-level actions, info, done)` and `reset()`.
  * `process_high_level_actions` decouples high-level skill assignment from
    low-level execution, and non-LLM planners already ship
    (`scripted_centralized_planner.py`, `random_rearrange_planner.py`).

Porting plan (each arm in garagenet/arms.py maps 1:1):
  L0  -> PARTNR's decentralized per-agent ReAct LLM planners (exists).
  L1  -> centralized one-shot LLM plan + skill execution (exists as variant).
  L2  -> NEW `Planner` subclass emitting skill assignments from a MARL/MAPF
         controller; reuse `process_high_level_actions` (wrapper, not rebuild).

Timing: wrap every planner `get_next_action` call in
`ledger.deliberation()` and every simulator/skill step in `ledger.execution()`
(real clocks — TimingLedger context managers), which reproduces the same CSV
schema as the mock sweep, so plots/stats run unchanged.

This module intentionally raises at import-time use if habitat_llm is absent,
so the rest of the package stays importable without Habitat installed.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from garagenet.interfaces import TaskInstance

try:  # pragma: no cover - only on machines with PARTNR installed
    import habitat_llm  # type: ignore  # noqa: F401

    HABITAT_AVAILABLE = True
except ImportError:  # pragma: no cover
    HABITAT_AVAILABLE = False


class PartnrEnv:
    """garagenet.interfaces.Environment backed by PARTNR (to be completed on a
    machine with Habitat 3.0 + partnr-planner installed)."""

    def __init__(self, episode_dataset: str = "data/datasets/partnr_episodes/v0_0"):
        if not HABITAT_AVAILABLE:
            raise ImportError(
                "habitat_llm not installed. Install facebookresearch/partnr-planner "
                "(see INSTALLATION.md there), then use this adapter. The mock env "
                "(garagenet.envs.mock) validates the harness without it."
            )
        self.episode_dataset = episode_dataset
        raise NotImplementedError(
            "Phase-0 TODO: instantiate EnvironmentInterface + evaluation runner, "
            "map TaskInstance -> PARTNR episode selection (coupling ladder = "
            "constraint-free -> spatial -> temporal -> heterogeneous task types), "
            "wire TimingLedger real clocks around get_next_action / env step."
        )

    # Environment protocol (signatures fixed so arms are already compatible)
    def reset(self, task: TaskInstance) -> Dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

    def step(
        self, actions: Dict[int, Any]
    ) -> Tuple[Dict[str, Any], bool, Dict[str, Any]]:  # pragma: no cover
        raise NotImplementedError

    def plan_quality_available(self) -> bool:  # pragma: no cover
        raise NotImplementedError

    def install_plan(self, plan: Optional[Dict[str, Any]]) -> None:  # pragma: no cover
        raise NotImplementedError
