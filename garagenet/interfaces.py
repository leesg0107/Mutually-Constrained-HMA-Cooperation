"""Core interfaces for the GarageNet Phase-0 measurement harness.

Design mirrors PARTNR's planner abstraction (habitat_llm/planner/planner.py):
a coordination arm receives (instruction, observations, world state) and emits
per-agent high-level actions until the episode reports done. This keeps every
arm a drop-in `Planner`-subclass candidate when ported onto PARTNR (verified
in docs/benchmark-feasibility.md §3a).

Terminology (docs/theory-team-voc.md):
  coupling  chi  — reasoning/allocation interdependence; the axis the learned
                   policy is predicted to degrade on (crossing expected).
  congestion     — spatial-contention control axis (NO crossing expected;
                   negative-control from docs/paper-proposal.md Figure 2a).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, Tuple


@dataclass(frozen=True)
class TaskInstance:
    """One episode's task specification.

    Exactly one of the two difficulty knobs is swept per experiment; the other
    is held at its baseline (0.0).
    """

    task_id: str
    axis: str  # "coupling" | "congestion"
    level: float  # difficulty knob in [0, 1] along `axis`
    n_agents: int = 3
    seed: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.axis not in ("coupling", "congestion"):
            raise ValueError(f"unknown axis: {self.axis!r}")
        if not 0.0 <= self.level <= 1.0:
            raise ValueError(f"level must be in [0,1], got {self.level}")


@dataclass
class EpisodeResult:
    """Outcome of running one arm on one task instance.

    Times are wall-clock seconds. The deliberation/execution split is the
    paper's signature quantity; routing time is charged separately so a slow
    gate is auditable (docs/problem-statement.md §4 crux).
    """

    task: TaskInstance
    arm: str
    success: bool
    t_deliberation: float
    t_execution: float
    t_routing: float = 0.0
    steps: int = 0
    info: Dict[str, Any] = field(default_factory=dict)

    @property
    def t_total(self) -> float:
        return self.t_deliberation + self.t_execution + self.t_routing


class CoordinationArm(Protocol):
    """One coordination mechanism (L0 / L1 / L2 / router).

    `run_episode` must charge all planner-side latency to the ledger's
    deliberation clock and all environment stepping to its execution clock.
    """

    name: str

    def run_episode(self, env: "Environment", task: TaskInstance) -> EpisodeResult:
        ...


class Environment(Protocol):
    """Minimal episodic environment contract (satisfied by MockCouplingEnv now,
    by the PARTNR adapter later)."""

    def reset(self, task: TaskInstance) -> Dict[str, Any]:
        """Start an episode; returns initial observations."""
        ...

    def step(
        self, actions: Dict[int, Any]
    ) -> Tuple[Dict[str, Any], bool, Dict[str, Any]]:
        """Apply per-agent high-level actions.

        Returns (observations, done, info). info["sim_time"] is the simulated
        wall-clock cost of this step in seconds — used instead of real time in
        simulation so results are machine-independent; the PARTNR adapter
        substitutes real timers.
        """
        ...

    def plan_quality_available(self) -> bool:
        """Whether a deliberated plan has been installed for this episode."""
        ...

    def install_plan(self, plan: Optional[Dict[str, Any]]) -> None:
        """Install the (possibly None) output of deliberation; execution speed
        may depend on it — this is the cross-agent externality channel."""
        ...
