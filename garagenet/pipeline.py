"""End-to-end GarageNet pipeline: NL branch descriptions -> coupling estimates
-> gated per-agent mode allocation -> simulated execution.

The honest separation that makes this a real test of the architecture:
  * the allocator PLANS on the estimator's chi_hat (all it can know a priori),
  * reality EXECUTES on the true chi,
so estimation error propagates into measurable extra mission time instead of
being assumed away. Gate latencies run on each agent's own timeline (parallel),
so the charged routing latency is their max, plus the joint-escalation overhead
when the coupling gate escalates.

Scope note (2026-07-03 decision): no world model in the paper's loop — the
pipeline's inputs are the mission spec (branch texts, precedence, externality
structure) plus inter-robot information sharing; a learned world model is
platform roadmap, not paper scope.

Usage:
    python -m garagenet.pipeline
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, Optional, Sequence, Tuple

from garagenet.coupling_estimator import (
    BUCKETS,
    CouplingEstimator,
    FallbackGate,
    ProbeGate,
    RuleGate,
    TaskDescription,
)
from garagenet.estimator_eval import chi_star
from garagenet.mission import (
    DELIBERATE,
    POLICY,
    Branch,
    MissionInstance,
    MissionModel,
)


@dataclass(frozen=True)
class DescribedBranch:
    """A subtask as the team actually receives it: text + structure."""

    branch_id: str
    agent: int
    text: str
    upstream: Tuple[str, ...] = ()
    externality: float = 0.0
    true_bucket: Optional[str] = None  # ground truth (sim); unknown on robots


@dataclass(frozen=True)
class DescribedMission:
    mission_id: str
    branches: Tuple[DescribedBranch, ...]
    seed: int = 0

    def to_instance(self, chi: Dict[str, float]) -> MissionInstance:
        return MissionInstance(
            mission_id=self.mission_id,
            branches=tuple(
                Branch(
                    b.branch_id, b.agent, chi[b.branch_id],
                    upstream=b.upstream, externality=b.externality,
                )
                for b in self.branches
            ),
            seed=self.seed,
        )


@dataclass
class PipelineResult:
    gate_name: str
    modes: Dict[str, str]
    chi_hat: Dict[str, float]
    actual_makespan: float
    t_routing: float  # max per-agent gate latency + joint overhead if escalated
    escalated: bool
    detail: Dict[str, Dict[str, float]] = field(default_factory=dict)

    @property
    def total_time(self) -> float:
        return self.actual_makespan + self.t_routing


@dataclass
class GarageNetPipeline:
    """[2] estimator -> [3] gated allocator -> execution, end to end."""

    estimator: CouplingEstimator
    model: MissionModel = field(default_factory=MissionModel)
    externality_threshold: float = 5.0
    joint_overhead: float = 3.0

    def run(self, mission: DescribedMission) -> PipelineResult:
        m = self.model
        threshold = chi_star(m)

        # [2] estimate chi per branch from its description (parallel per agent)
        chi_hat: Dict[str, float] = {}
        gate_latencies = []
        for b in mission.branches:
            chi, latency = self.estimator.estimate(
                TaskDescription(text=b.text, true_bucket=b.true_bucket)
            )
            chi_hat[b.branch_id] = chi
            gate_latencies.append(latency)
        t_routing = max(gate_latencies, default=0.0)

        # [3] coupling-gated allocation, PLANNED ON chi_hat
        believed = mission.to_instance(chi_hat)
        max_ext = max((b.externality for b in mission.branches), default=0.0)
        escalated = max_ext > self.externality_threshold
        if not escalated:
            # decentralized greedy: deliberate iff chi_hat crosses chi*
            modes = {
                b.branch_id: DELIBERATE if chi_hat[b.branch_id] >= threshold else POLICY
                for b in mission.branches
            }
        else:
            # joint: minimize BELIEVED makespan over all assignments
            ids = [b.branch_id for b in mission.branches]
            best, best_t = None, float("inf")
            for combo in itertools.product((POLICY, DELIBERATE), repeat=len(ids)):
                modes_try = dict(zip(ids, combo))
                t, _ = m.simulate(believed, modes_try)
                if t < best_t:
                    best, best_t = modes_try, t
            modes = best
            t_routing += self.joint_overhead

        # execution: reality uses TRUE chi
        truth = mission.to_instance(
            {b.branch_id: BUCKETS[b.true_bucket] for b in mission.branches}
        )
        actual_makespan, detail = m.simulate(truth, modes)
        return PipelineResult(
            gate_name=self.estimator.name, modes=modes, chi_hat=chi_hat,
            actual_makespan=actual_makespan, t_routing=t_routing,
            escalated=escalated, detail=detail,
        )


# --------------------------------------------------------------------------- #
# Demo mission: the wildfire example, described in natural language
# --------------------------------------------------------------------------- #
def wildfire_described(externality: float = 60.0) -> DescribedMission:
    return DescribedMission(
        mission_id="wildfire-nl",
        branches=(
            DescribedBranch(
                "map-west", agent=0,
                text="Survey the western burn area and chart the fire line.",
                true_bucket="ND",
            ),
            DescribedBranch(
                "map-east", agent=1,
                text="Sweep the eastern sector and log hotspot readings.",
                true_bucket="ND",
            ),
            DescribedBranch(
                "transport", agent=2,
                text=(
                    "Work out among the team which casualties and fallen trees "
                    "to move first, allocating duties among yourselves."
                ),
                upstream=("map-west", "map-east"),
                externality=externality,
                true_bucket="CD",
            ),
        ),
    )


def main() -> None:
    mission = wildfire_described()
    model = MissionModel()
    cs = chi_star(model)
    print(f"mission: {mission.mission_id}  (externality=60 -> gate escalates; chi*={cs:.3f})\n")
    gates = (
        RuleGate(),
        ProbeGate(seed=0),
        FallbackGate(probe=ProbeGate(seed=0)),  # naive confidence: marker fired
        FallbackGate(
            probe=ProbeGate(seed=0), decision_threshold=cs, decision_margin=0.10,
            name="fallback+margin",
        ),
    )
    for est in gates:
        r = GarageNetPipeline(estimator=est, model=model).run(mission)
        modes = ", ".join(f"{k}={v[:6]}" for k, v in sorted(r.modes.items()))
        print(
            f"{r.gate_name:>15}: total {r.total_time:6.1f}s "
            f"(makespan {r.actual_makespan:.1f} + routing {r.t_routing:.2f}) "
            f"escalated={r.escalated}  [{modes}]"
        )
    print(
        "\nNote the naive fallback failure: 'to move FIRST' fires the ordering "
        "marker incidentally,\nso the rule is confidently wrong (chi=0.60 just "
        "below chi*) and the probe is never called;\nthe decision-margin "
        "fallback probes near the boundary and recovers the correct mode."
    )


if __name__ == "__main__":
    main()
