"""End-to-end pipeline tests: NL descriptions -> estimation -> gated
allocation -> execution with honest error propagation."""

import pytest

from garagenet.coupling_estimator import (
    FallbackGate,
    ProbeGate,
    RuleGate,
    TaskDescription,
)
from garagenet.estimator_eval import chi_star
from garagenet.mission import DELIBERATE, POLICY, MissionModel
from garagenet.pipeline import GarageNetPipeline, wildfire_described


@pytest.fixture()
def model():
    return MissionModel()


def test_pipeline_runs_end_to_end(model):
    r = GarageNetPipeline(estimator=RuleGate(), model=model).run(wildfire_described())
    assert set(r.modes) == {"map-west", "map-east", "transport"}
    assert r.actual_makespan > 0
    assert r.escalated  # externality=60 > threshold


def test_estimation_error_propagates_to_mission_time(model):
    """The rule gate misreads the paraphrased CD transport branch ('move
    first' fires the ordering marker incidentally) -> wrong mode -> slower
    ACTUAL mission, even though its routing latency is near zero."""
    rule = GarageNetPipeline(estimator=RuleGate(), model=model).run(
        wildfire_described()
    )
    probe = GarageNetPipeline(estimator=ProbeGate(seed=0), model=model).run(
        wildfire_described()
    )
    assert rule.modes["transport"] == POLICY  # the confident mistake
    assert probe.modes["transport"] == DELIBERATE
    assert probe.total_time < rule.total_time  # despite paying probe latency


def test_naive_fallback_inherits_false_confidence(model):
    """Trigger #1 (marker fired = confident) cannot catch incidental markers:
    the naive fallback makes the same transport mistake as the rule gate."""
    naive = GarageNetPipeline(
        estimator=FallbackGate(probe=ProbeGate(seed=0)), model=model
    ).run(wildfire_described())
    assert naive.modes["transport"] == POLICY


def test_margin_fallback_recovers_near_boundary(model):
    """Trigger #2: chi=0.60 lands within the decision margin of chi*=0.605,
    so the margin fallback probes and recovers the correct mode."""
    cs = chi_star(model)
    margin = GarageNetPipeline(
        estimator=FallbackGate(
            probe=ProbeGate(seed=0), decision_threshold=cs, decision_margin=0.10
        ),
        model=model,
    ).run(wildfire_described())
    probe = GarageNetPipeline(estimator=ProbeGate(seed=0), model=model).run(
        wildfire_described()
    )
    assert margin.modes["transport"] == DELIBERATE
    assert margin.total_time == pytest.approx(probe.total_time, rel=0.05)


def test_margin_fallback_stays_cheap_away_from_boundary(model):
    """Far from chi*, a fired marker is still trusted without probing."""
    cs = chi_star(model)
    gate = FallbackGate(
        probe=ProbeGate(seed=0), decision_threshold=cs, decision_margin=0.10
    )
    # canonical CD text: chi=0.95, far above chi* -> no probe, ~zero latency
    chi, latency = gate.estimate(
        TaskDescription(
            text="Tidy the workshop appropriately, splitting the work however you see fit.",
            true_bucket="CD",
        )
    )
    assert chi == 0.95
    assert latency < 0.01


def test_routing_latency_is_max_over_parallel_gates(model):
    """Per-agent gates run in parallel: routing = max gate latency (+ joint
    overhead when escalated), not the sum."""
    probe = ProbeGate(seed=0)
    r = GarageNetPipeline(estimator=probe, model=model).run(wildfire_described())
    # 3 probes of ~2.5s each: sum would be ~7.5s; max+overhead stays under ~6.5
    assert r.t_routing < 6.5
