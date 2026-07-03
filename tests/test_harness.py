"""Phase-0 harness tests: timing split, sweep integrity, and the two
pipeline-level sanity properties (mock crossing on the coupling axis; no
crossing on the congestion axis).

The mock-model assertions validate the PIPELINE (the harness detects a
crossing when the generating model contains one, and detects none when it
does not) — they are not evidence about the scientific bet.
"""

import time

import pytest

from garagenet.arms import L0Deliberation, L2ReactivePolicy, SimulatedLLM, default_arms
from garagenet.envs.mock import MockCouplingEnv
from garagenet.interfaces import TaskInstance
from garagenet.sweep import SweepConfig, find_crossings, run_sweep, summarize, write_csv
from garagenet.timing import TimingLedger


# --------------------------------------------------------------------------- #
# TimingLedger
# --------------------------------------------------------------------------- #
def test_ledger_simulated_accounting():
    ledger = TimingLedger()
    ledger.add_deliberation(2.5)
    ledger.add_execution(10.0)
    ledger.add_routing(0.1)
    assert ledger.t_deliberation == 2.5
    assert ledger.t_execution == 10.0
    assert ledger.t_routing == 0.1
    assert ledger.t_total == pytest.approx(12.6)


def test_ledger_real_time_accounting():
    ledger = TimingLedger()
    with ledger.deliberation():
        time.sleep(0.03)
    with ledger.execution():
        time.sleep(0.01)
    assert ledger.t_deliberation >= 0.025
    assert ledger.t_execution >= 0.005
    assert ledger.t_deliberation > ledger.t_execution


def test_ledger_rejects_bad_input():
    ledger = TimingLedger()
    with pytest.raises(KeyError):
        ledger.add("walltime", 1.0)
    with pytest.raises(ValueError):
        ledger.add_execution(-1.0)


def test_task_instance_validation():
    with pytest.raises(ValueError):
        TaskInstance(task_id="x", axis="difficulty", level=0.5)
    with pytest.raises(ValueError):
        TaskInstance(task_id="x", axis="coupling", level=1.5)


# --------------------------------------------------------------------------- #
# Arms on the mock env
# --------------------------------------------------------------------------- #
def test_l2_has_zero_deliberation():
    env = MockCouplingEnv()
    task = TaskInstance(task_id="t", axis="coupling", level=0.5, seed=1)
    r = L2ReactivePolicy().run_episode(env, task)
    assert r.t_deliberation == 0.0
    assert r.t_execution > 0.0


def test_l0_pays_deliberation_and_installs_plan():
    env = MockCouplingEnv()
    task = TaskInstance(task_id="t", axis="coupling", level=0.5, seed=1)
    r = L0Deliberation(llm=SimulatedLLM(seed=1)).run_episode(env, task)
    assert r.t_deliberation > 0.0
    assert r.info["rounds"] == 3


def test_deliberation_externality_speeds_downstream_execution():
    """The theory's cross-agent externality: planned execution must be faster
    than unplanned at high coupling (theory-team-voc.md §4)."""
    env = MockCouplingEnv()
    task = TaskInstance(task_id="t", axis="coupling", level=1.0, seed=7)
    r_l2 = L2ReactivePolicy().run_episode(env, task)
    r_l0 = L0Deliberation(llm=SimulatedLLM(seed=7)).run_episode(env, task)
    assert r_l0.t_execution < r_l2.t_execution


# --------------------------------------------------------------------------- #
# Sweep + crossing detection (pipeline sanity on the mock model)
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def coupling_summary():
    cfg = SweepConfig(axis="coupling", seeds=list(range(30)))
    return summarize(run_sweep(cfg))


@pytest.fixture(scope="module")
def congestion_summary():
    cfg = SweepConfig(axis="congestion", seeds=list(range(30)))
    return summarize(run_sweep(cfg))


def test_mock_crossing_exists_on_coupling_axis(coupling_summary):
    lo = coupling_summary[("coupling", 0.0)]
    hi = coupling_summary[("coupling", 1.0)]
    # L2 fastest at low coupling; L0 fastest at high coupling.
    assert lo["L2-policy"]["mean_total"] < lo["L0-deliberation"]["mean_total"]
    assert hi["L0-deliberation"]["mean_total"] < hi["L2-policy"]["mean_total"]
    assert find_crossings(coupling_summary), "expected >=1 crossing on coupling axis"


def test_mock_no_crossing_on_congestion_axis(congestion_summary):
    """Negative control: L2 must dominate at every congestion level."""
    for (_, _level), arms in congestion_summary.items():
        assert arms["L2-policy"]["mean_total"] < arms["L0-deliberation"]["mean_total"]
    assert not find_crossings(congestion_summary)


def test_csv_roundtrip(tmp_path):
    cfg = SweepConfig(axis="coupling", levels=[0.0, 1.0], seeds=[0, 1])
    results = run_sweep(cfg)
    out = tmp_path / "sweep.csv"
    write_csv(results, out)
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 1 + len(results)  # header + rows
    assert lines[0].startswith("axis,level,arm,seed,success,t_deliberation")


def test_default_arms_are_the_three_mechanisms():
    names = {a.name for a in default_arms()}
    assert names == {"L2-policy", "L1-hybrid", "L0-deliberation"}
