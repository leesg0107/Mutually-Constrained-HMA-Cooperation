"""Synthetic environment encoding the theory model of docs/theory-team-voc.md.

PURPOSE — honest scope statement. This mock exists to (a) validate the harness
plumbing end-to-end (timing split, sweep, plots, statistics) and (b) render the
*predicted* curve shapes as a pipeline sanity check. It proves NOTHING about the
scientific bet; Phase-0's real answer comes from the PARTNR adapter. Every
number below is a labeled model parameter, not a measurement.

Model (wildfire-shaped, mirrors theory-team-voc.md §2 & §4):
  * An episode is a two-stage precedence chain: upstream "mapping" work by
    scout agents, downstream "transport" work whose execution time depends on
    whether a deliberated plan was installed — the cross-agent externality.
  * coupling axis (chi): with no plan, downstream execution degrades steeply
    with chi (a reactive policy has no a-priori allocation signal on ambiguous
    tasks); with a plan, execution stays near base. => crossing predicted.
  * congestion axis: execution inflates for EVERY arm equally (spatial
    contention slows plan-followers and reactive agents alike), and planning
    cannot remove it. => no crossing predicted (negative control).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from garagenet.interfaces import TaskInstance


@dataclass
class MockParams:
    """All model constants in one auditable place (seconds)."""

    base_execution: float = 20.0
    # coupling axis: unplanned execution penalty grows superlinearly with chi;
    # planned execution grows only mildly (a good plan absorbs the coupling).
    unplanned_coupling_penalty: float = 90.0
    planned_coupling_penalty: float = 8.0
    coupling_exponent: float = 2.0
    # congestion axis: uniform multiplicative slowdown, plan cannot remove it.
    congestion_penalty: float = 60.0
    # success model: reactive (unplanned) success decays with chi.
    unplanned_success_floor: float = 0.35
    noise_frac: float = 0.06  # lognormal-ish execution noise


class MockCouplingEnv:
    """Implements garagenet.interfaces.Environment (simulated-time)."""

    def __init__(self, params: Optional[MockParams] = None) -> None:
        self.params = params or MockParams()
        self._task: Optional[TaskInstance] = None
        self._plan: Optional[Dict[str, Any]] = None
        self._rng = random.Random(0)
        self._done = False

    # -- Environment protocol -------------------------------------------------
    def reset(self, task: TaskInstance) -> Dict[str, Any]:
        self._task = task
        self._plan = None
        self._done = False
        self._rng = random.Random(task.seed)
        return {"instruction": task.task_id, "axis": task.axis, "level": task.level}

    def install_plan(self, plan: Optional[Dict[str, Any]]) -> None:
        self._plan = plan

    def plan_quality_available(self) -> bool:
        return self._plan is not None

    def step(
        self, actions: Dict[int, Any]
    ) -> Tuple[Dict[str, Any], bool, Dict[str, Any]]:
        """Single macro-step: executes the whole mission and reports its
        simulated duration. (Phase-0 mock granularity; the PARTNR adapter
        steps at skill granularity instead.)"""
        if self._task is None or self._done:
            raise RuntimeError("call reset() first")
        p, t = self.params, self._task
        planned = self._plan is not None

        if t.axis == "coupling":
            chi = t.level
            penalty = (
                p.planned_coupling_penalty if planned else p.unplanned_coupling_penalty
            )
            sim_time = p.base_execution + penalty * (chi**p.coupling_exponent)
            success_p = 1.0 if planned else max(
                p.unplanned_success_floor, 1.0 - 0.5 * chi
            )
        else:  # congestion: uniform, plan-independent inflation
            sim_time = p.base_execution + p.congestion_penalty * t.level
            success_p = 1.0

        sim_time *= 1.0 + self._rng.gauss(0.0, p.noise_frac)
        sim_time = max(sim_time, 0.1)
        success = self._rng.random() < success_p
        self._done = True
        return (
            {"done": True},
            True,
            {"sim_time": sim_time, "success": success, "planned": planned},
        )
