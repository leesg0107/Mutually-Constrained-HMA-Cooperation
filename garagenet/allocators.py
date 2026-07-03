"""Phase-1 allocators: who decides each branch's coordination mode, and how.

Four allocators, each realizing one cell of the theory/ablation grid
(docs/experiment-design.md, Experiment 2):

  * TeamUniform        — whole team shares ONE mode (the Phase-0 arms as a
                         router); the A1 baseline.
  * GreedyLocal        — decentralized per-agent VoC: each branch minimizes
                         its OWN d+e, blind to the externality it exerts
                         downstream (theory §2's kappa^G).
  * JointOracle        — exhaustive search over mode assignments, minimizing
                         makespan (theory's kappa^*; exponential — fine for
                         mission-sized DAGs, and it is the oracle bound).
  * CouplingGated      — the Corollary as a mechanism: run GreedyLocal when
                         the mission's externality is low; escalate to
                         JointOracle when it is high, PAYING a joint-
                         coordination latency overhead when escalating.

All allocators report their own decision latency so the "slow router defeats
the thesis" failure mode is audited (charged as routing time).
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, Iterable, Tuple

from garagenet.mission import (
    DELIBERATE,
    POLICY,
    MissionInstance,
    MissionModel,
)

Modes = Dict[str, str]


@dataclass
class Allocation:
    allocator: str
    modes: Modes
    makespan: float
    t_routing: float = 0.0  # decision latency charged to the mission
    info: Dict[str, float] = field(default_factory=dict)

    @property
    def total_time(self) -> float:
        return self.makespan + self.t_routing


# --------------------------------------------------------------------------- #
def _evaluate(model: MissionModel, mission: MissionInstance, modes: Modes) -> float:
    makespan, _ = model.simulate(mission, modes)
    return makespan


@dataclass
class TeamUniform:
    """Best single team-wide mode (an oracle over the 2 uniform assignments —
    generous to the baseline, which strengthens any win against it)."""

    model: MissionModel
    name: str = "team-uniform"

    def allocate(self, mission: MissionInstance) -> Allocation:
        best_modes, best_t = None, float("inf")
        for mode in (POLICY, DELIBERATE):
            modes = {b.branch_id: mode for b in mission.branches}
            t = _evaluate(self.model, mission, modes)
            if t < best_t:
                best_modes, best_t = modes, t
        assert best_modes is not None
        return Allocation(self.name, best_modes, best_t)


@dataclass
class GreedyLocal:
    """Decentralized per-agent VoC (theory kappa^G): each branch picks the mode
    minimizing its OWN deliberation + execution, assuming (optimistically) that
    upstream branches deliberate, and never seeing its downstream externality."""

    model: MissionModel
    name: str = "greedy-local"

    def allocate(self, mission: MissionInstance) -> Allocation:
        m = self.model
        modes: Modes = {}
        for b in mission.branches:
            own = {}
            for mode in (POLICY, DELIBERATE):
                d = m.llm_latency if mode == DELIBERATE else 0.0
                pen = (
                    m.planned_coupling_penalty
                    if mode == DELIBERATE
                    else m.unplanned_coupling_penalty
                )
                own[mode] = d + m.base_execution + pen * (b.chi**m.coupling_exponent)
            modes[b.branch_id] = min(own, key=own.get)
        return Allocation(self.name, modes, _evaluate(m, mission, modes))


@dataclass
class JointOracle:
    """Exhaustive makespan minimization (theory kappa^*)."""

    model: MissionModel
    name: str = "joint-oracle"

    def allocate(self, mission: MissionInstance) -> Allocation:
        ids = [b.branch_id for b in mission.branches]
        best_modes, best_t = None, float("inf")
        for combo in itertools.product((POLICY, DELIBERATE), repeat=len(ids)):
            modes = dict(zip(ids, combo))
            t = _evaluate(self.model, mission, modes)
            if t < best_t:
                best_modes, best_t = modes, t
        assert best_modes is not None
        return Allocation(self.name, best_modes, best_t)


@dataclass
class CouplingGated:
    """The Corollary (theory §5) as a mechanism.

    Gate signal = the mission's maximum externality (cheap, a-priori — read off
    the task structure). Low -> decentralized greedy suffices (Thm 1 regime).
    High -> escalate to joint allocation (Thm 2 regime), paying
    `joint_overhead` seconds of coordination latency for the escalation.
    """

    model: MissionModel
    externality_threshold: float = 5.0
    joint_overhead: float = 3.0  # cost of gathering global info + solving jointly
    name: str = "coupling-gated"

    def allocate(self, mission: MissionInstance) -> Allocation:
        max_ext = max((b.externality for b in mission.branches), default=0.0)
        if max_ext <= self.externality_threshold:
            inner = GreedyLocal(self.model).allocate(mission)
            return Allocation(
                self.name, inner.modes, inner.makespan,
                t_routing=0.0, info={"escalated": 0.0, "max_externality": max_ext},
            )
        inner = JointOracle(self.model).allocate(mission)
        return Allocation(
            self.name, inner.modes, inner.makespan,
            t_routing=self.joint_overhead,
            info={"escalated": 1.0, "max_externality": max_ext},
        )


def all_allocators(model: MissionModel) -> Iterable:
    return (
        TeamUniform(model),
        GreedyLocal(model),
        JointOracle(model),
        CouplingGated(model),
    )
