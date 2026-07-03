"""Phase-1 allocator tests: the theory's claims, replicated executably.

Each test names the theory/paper claim it validates:
  * Thm 1  (theory-team-voc.md §3): no externality -> greedy == joint.
  * Thm 2  (§4): externality -> greedy strictly suboptimal, unboundedly so.
  * Corollary (§5): the coupling gate matches joint where it matters and
    avoids joint's overhead where it doesn't.
  * A1 (idea-verdict §5): per-agent allocation beats the best team-uniform
    mode on heterogeneous-chi missions.
"""

import pytest

from garagenet.allocators import (
    CouplingGated,
    GreedyLocal,
    JointOracle,
    TeamUniform,
)
from garagenet.mission import (
    DELIBERATE,
    POLICY,
    MissionModel,
    mixed_mission,
    wildfire_mission,
)


@pytest.fixture()
def model():
    return MissionModel()  # deterministic (noise_frac=0)


# --------------------------------------------------------------------------- #
# Theorem 1: separability under zero externality
# --------------------------------------------------------------------------- #
def test_thm1_greedy_optimal_without_externality(model):
    mission = wildfire_mission(externality=0.0)
    greedy = GreedyLocal(model).allocate(mission)
    joint = JointOracle(model).allocate(mission)
    assert greedy.makespan == pytest.approx(joint.makespan)


# --------------------------------------------------------------------------- #
# Theorem 2: externality makes greedy strictly suboptimal, and the gap grows
# --------------------------------------------------------------------------- #
def test_thm2_greedy_suboptimal_under_externality(model):
    mission = wildfire_mission(externality=120.0)
    greedy = GreedyLocal(model).allocate(mission)
    joint = JointOracle(model).allocate(mission)
    assert greedy.makespan > joint.makespan
    # the failure mode is exactly theory §4: greedy skips upstream deliberation
    assert greedy.modes["map-west"] == POLICY
    assert joint.modes["map-west"] == DELIBERATE


def test_thm2_regret_grows_with_externality(model):
    regrets = []
    for ext in (30.0, 60.0, 120.0, 240.0):
        mission = wildfire_mission(externality=ext)
        g = GreedyLocal(model).allocate(mission).makespan
        j = JointOracle(model).allocate(mission).makespan
        regrets.append(g - j)
    assert regrets == sorted(regrets)  # monotone non-decreasing
    assert regrets[-1] > regrets[0] > 0


# --------------------------------------------------------------------------- #
# Corollary: the coupling gate
# --------------------------------------------------------------------------- #
def test_corollary_gate_stays_decentralized_at_low_coupling(model):
    gated = CouplingGated(model).allocate(wildfire_mission(externality=0.0))
    assert gated.info["escalated"] == 0.0
    assert gated.t_routing == 0.0
    assert gated.makespan == pytest.approx(
        GreedyLocal(model).allocate(wildfire_mission(externality=0.0)).makespan
    )


def test_corollary_gate_escalates_and_beats_greedy_at_high_coupling(model):
    mission = wildfire_mission(externality=120.0)
    gated = CouplingGated(model).allocate(mission)
    greedy = GreedyLocal(model).allocate(mission)
    joint = JointOracle(model).allocate(mission)
    assert gated.info["escalated"] == 1.0
    assert gated.t_routing > 0.0  # joint coordination is not free
    assert gated.total_time < greedy.total_time  # overhead pays for itself
    assert gated.makespan == pytest.approx(joint.makespan)


def test_corollary_gate_beats_always_joint_on_low_coupling_missions(model):
    """Where escalation is unnecessary, gating avoids joint's overhead."""
    mission = wildfire_mission(externality=0.0)
    gated = CouplingGated(model).allocate(mission)
    always_joint_total = JointOracle(model).allocate(mission).makespan + 3.0
    assert gated.total_time < always_joint_total


# --------------------------------------------------------------------------- #
# A1: per-agent allocation beats the best team-uniform mode
# --------------------------------------------------------------------------- #
def test_a1_per_agent_beats_team_uniform_on_mixed_chi(model):
    """Uniform POLICY thrashes the hard branch; uniform DELIBERATE stalls the
    scout->deliver pipeline; only a mixed assignment avoids both."""
    mission = mixed_mission()
    uniform = TeamUniform(model).allocate(mission)
    joint = JointOracle(model).allocate(mission)
    assert joint.makespan < uniform.makespan
    # and the winning assignment is genuinely mixed:
    assert set(joint.modes.values()) == {POLICY, DELIBERATE}
    assert joint.modes["scout-a"] == POLICY
    assert joint.modes["analyze"] == DELIBERATE


def test_wildfire_parallelism_drones_do_not_wait(model):
    """The A1 wildfire property: mapping branches start at t=0 regardless of
    the transport branch's mode — per-agent mixing implies no global stall."""
    mission = wildfire_mission(externality=120.0)
    joint = JointOracle(model).allocate(mission)
    _, detail = model.simulate(mission, joint.modes)
    assert detail["map-west"]["start"] == 0.0
    assert detail["map-east"]["start"] == 0.0
    assert detail["transport"]["start"] > 0.0  # waits only on precedence
