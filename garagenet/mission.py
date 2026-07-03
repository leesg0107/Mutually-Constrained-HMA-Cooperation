"""Mission model for Phase-1: per-agent mode allocation over a precedence DAG.

Implements the theory model of docs/theory-team-voc.md §2 as a simulator:

  * A mission is a DAG of branches (subtasks), each owned by an agent, each
    with its own local coupling chi_b.
  * Mode per branch: DELIBERATE (pay LLM latency, get a plan) or POLICY
    (zero deliberation).
  * Execution time depends on (a) the branch's own mode vs its chi, and
    (b) the cross-agent externality: whether UPSTREAM branches deliberated
    (theory §4 — a mapped burn area speeds the transport branch).
  * Mission completion time = makespan over the DAG:
        f_b = max(f_u for u in upstream) + D_b + E_b(mode_b, upstream modes)

Same honest scope as envs/mock.py: this is the theory rendered executable so
allocators can be built and validated against it; it is not evidence. The
PARTNR adapter replaces the simulator, not the allocators.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Sequence, Tuple

DELIBERATE = "deliberate"
POLICY = "policy"


@dataclass(frozen=True)
class Branch:
    """One subtask, owned by one agent."""

    branch_id: str
    agent: int
    chi: float  # local coupling in [0,1]
    upstream: Tuple[str, ...] = ()  # precedence: must finish first
    # Extra execution seconds this branch pays PER upstream branch that did
    # NOT deliberate (the cross-agent externality magnitude, theory §4's M-g).
    externality: float = 0.0


@dataclass(frozen=True)
class MissionInstance:
    mission_id: str
    branches: Tuple[Branch, ...]
    seed: int = 0

    def branch(self, branch_id: str) -> Branch:
        for b in self.branches:
            if b.branch_id == branch_id:
                return b
        raise KeyError(branch_id)

    def toposorted(self) -> List[Branch]:
        done: Dict[str, Branch] = {}
        remaining = list(self.branches)
        while remaining:
            progressed = False
            for b in list(remaining):
                if all(u in done for u in b.upstream):
                    done[b.branch_id] = b
                    remaining.remove(b)
                    progressed = True
            if not progressed:
                raise ValueError("cycle in mission DAG")
        return list(done.values())


@dataclass
class MissionModel:
    """Cost model (seconds); constants mirror envs/mock.MockParams."""

    base_execution: float = 20.0
    unplanned_coupling_penalty: float = 90.0
    planned_coupling_penalty: float = 8.0
    coupling_exponent: float = 2.0
    llm_latency: float = 30.0  # one deliberation episode (dialogue) per branch
    noise_frac: float = 0.0  # deterministic by default; tests rely on it

    def simulate(
        self, mission: MissionInstance, modes: Mapping[str, str]
    ) -> Tuple[float, Dict[str, Dict[str, float]]]:
        """Returns (makespan, per-branch {start, deliberation, execution, finish}).

        Deliberation runs on the branch's own timeline (each agent has its own
        LLM), so parallel branches deliberate in parallel.
        """
        rng = random.Random(mission.seed)
        finish: Dict[str, float] = {}
        detail: Dict[str, Dict[str, float]] = {}
        for b in mission.toposorted():
            mode = modes[b.branch_id]
            if mode not in (DELIBERATE, POLICY):
                raise ValueError(f"unknown mode {mode!r} for {b.branch_id}")
            start = max((finish[u] for u in b.upstream), default=0.0)
            d = self.llm_latency if mode == DELIBERATE else 0.0
            penalty = (
                self.planned_coupling_penalty
                if mode == DELIBERATE
                else self.unplanned_coupling_penalty
            )
            e = self.base_execution + penalty * (b.chi**self.coupling_exponent)
            # cross-agent externality: pay for every upstream that skipped
            # deliberation (theory §4's M-g term).
            e += b.externality * sum(
                1 for u in b.upstream if modes[u] != DELIBERATE
            )
            if self.noise_frac:
                e *= 1.0 + rng.gauss(0.0, self.noise_frac)
            finish[b.branch_id] = start + d + e
            detail[b.branch_id] = {
                "start": start, "deliberation": d, "execution": e,
                "finish": finish[b.branch_id],
            }
        return max(finish.values()), detail


def wildfire_mission(
    externality: float, mapping_chi: float = 0.1, transport_chi: float = 0.7,
    seed: int = 0,
) -> MissionInstance:
    """The running example (theory §4): 2 drone mapping branches upstream of
    1 UGV transport branch whose execution depends on the maps' quality."""
    return MissionInstance(
        mission_id=f"wildfire-ext{externality:.0f}",
        branches=(
            Branch("map-west", agent=0, chi=mapping_chi),
            Branch("map-east", agent=1, chi=mapping_chi),
            Branch(
                "transport", agent=2, chi=transport_chi,
                upstream=("map-west", "map-east"), externality=externality,
            ),
        ),
        seed=seed,
    )


def mixed_mission(seed: int = 0) -> MissionInstance:
    """Heterogeneous-chi mission where NO team-uniform mode can be right (A1).

    Structure matters: with purely independent parallel branches, makespan is
    dominated by the hardest branch and uniform-vs-mixed ties (an honest
    finding from the first version of this fixture). The uniform mode only
    loses on makespan when the easy branches FEED a downstream chain:
      * uniform POLICY   -> the hard branch thrashes (dominates makespan);
      * uniform DELIBERATE -> the easy scout branches stall 1 LLM-latency,
        delaying the downstream deliver chain (the "drones wait" pathology);
      * mixed            -> scouts launch immediately, hard branch deliberates.
    """
    return MissionInstance(
        mission_id="mixed-pipeline",
        branches=(
            Branch("scout-a", agent=0, chi=0.05),
            Branch("scout-b", agent=1, chi=0.10),
            Branch("deliver", agent=2, chi=0.05, upstream=("scout-a", "scout-b")),
            Branch("analyze", agent=3, chi=0.95),
        ),
        seed=seed,
    )
