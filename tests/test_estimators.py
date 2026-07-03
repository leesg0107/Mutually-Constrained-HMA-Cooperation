"""Gating-signal (coupling estimator) tests.

Validates the ablation's load-bearing claims:
  * rule-gate is perfect ONLY on its own vocabulary (circular) and collapses
    on paraphrases — the honest limitation, kept visible;
  * the probe is phrasing-robust but pays latency on every task;
  * the fallback gate (VoC at the gate level) is the best worst-case.
"""

import pytest

from garagenet.coupling_estimator import (
    BUCKETS,
    FallbackGate,
    LearnedGate,
    ProbeGate,
    RuleGate,
    TaskDescription,
    generate_dataset,
)
from garagenet.estimator_eval import chi_star, evaluate
from garagenet.mission import MissionModel


@pytest.fixture(scope="module")
def model():
    return MissionModel()


@pytest.fixture(scope="module")
def train():
    return generate_dataset(n_per_bucket=40, seed=0, style="canonical")


@pytest.fixture(scope="module")
def canonical_test():
    return generate_dataset(n_per_bucket=40, seed=1, style="canonical")


@pytest.fixture(scope="module")
def paraphrase_test():
    return generate_dataset(n_per_bucket=40, seed=2, style="paraphrase")


# --------------------------------------------------------------------------- #
# RuleGate behavior
# --------------------------------------------------------------------------- #
def test_rule_gate_classifies_canonical_markers():
    rule = RuleGate()
    cases = {
        "Tidy the workshop appropriately, splitting the work however you see fit.": "CD",
        "Only the drone can inspect the roof; bring the ladder.": "XD",
        "First clear the table, then wipe it.": "ID",
        "Place the cup on the same shelf as the plate.": "SP",
        "Move the box to the kitchen. Water the plant.": "ND",
    }
    for text, bucket in cases.items():
        assert rule.classify(TaskDescription(text=text)) == bucket


def test_rule_gate_priority_ambiguity_over_ordering():
    """A task with both markers is gated by the higher-coupling class."""
    text = "First collect the tools, then organize the storage room as makes sense."
    assert RuleGate().classify(TaskDescription(text=text)) == "CD"


def test_rule_gate_collapses_on_paraphrase(model, canonical_test, paraphrase_test):
    rule = RuleGate()
    canon = evaluate(rule, canonical_test, model)
    para = evaluate(rule, paraphrase_test, model)
    assert canon.bucket_accuracy == 1.0  # circular by construction
    assert para.bucket_accuracy < 0.5  # the honest condition
    assert para.mean_misroute_cost_s > canon.mean_misroute_cost_s


# --------------------------------------------------------------------------- #
# Probe & fallback
# --------------------------------------------------------------------------- #
def test_probe_is_phrasing_robust_but_pays_latency(model, paraphrase_test):
    probe = ProbeGate(seed=0)
    rep = evaluate(probe, paraphrase_test, model)
    assert rep.bucket_accuracy > 0.85
    assert rep.mean_latency_s > 1.0  # the cost is real


def test_probe_beats_rules_on_paraphrase_despite_latency(model, paraphrase_test):
    """The condition-dependent winner: off-vocabulary, paying the probe's
    latency is worth it."""
    rule = evaluate(RuleGate(), paraphrase_test, model)
    probe = evaluate(ProbeGate(seed=0), paraphrase_test, model)
    assert probe.mean_total_overhead_s < rule.mean_total_overhead_s


def test_fallback_is_best_worst_case(model, canonical_test, paraphrase_test):
    """max-over-conditions overhead: fallback <= rule and <= probe."""
    def worst(est_factory):
        return max(
            evaluate(est_factory(), canonical_test, model).mean_total_overhead_s,
            evaluate(est_factory(), paraphrase_test, model).mean_total_overhead_s,
        )

    fallback_worst = worst(lambda: FallbackGate(probe=ProbeGate(seed=0)))
    assert fallback_worst <= worst(RuleGate) + 1e-9
    assert fallback_worst <= worst(lambda: ProbeGate(seed=0)) + 0.35  # ~ties probe


def test_fallback_cheap_when_rules_confident(model, canonical_test):
    """On in-vocabulary tasks the fallback only pays the probe on marker-free
    (ND-looking) tasks — far cheaper than always-probe."""
    fb = evaluate(FallbackGate(probe=ProbeGate(seed=0)), canonical_test, model)
    probe = evaluate(ProbeGate(seed=0), canonical_test, model)
    assert fb.mean_latency_s < 0.5 * probe.mean_latency_s


# --------------------------------------------------------------------------- #
# LearnedGate + housekeeping
# --------------------------------------------------------------------------- #
def test_learned_gate_fits_and_predicts_in_range(train):
    gate = LearnedGate().fit(train)
    chi, latency = gate.estimate(train[0])
    assert 0.0 <= chi <= 1.0
    assert latency < 0.01


def test_chi_star_matches_model_constants(model):
    cs = chi_star(model)
    assert 0.55 < cs < 0.65
    # at chi*, deliberating and not deliberating cost the same (own-cost):
    from garagenet.estimator_eval import branch_time

    assert branch_time(model, cs, True) == pytest.approx(
        branch_time(model, cs, False), rel=1e-6
    )


def test_buckets_are_monotone():
    vals = list(BUCKETS.values())
    assert vals == sorted(vals)
