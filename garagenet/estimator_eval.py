"""Gating-signal ablation: accuracy / latency / downstream mis-routing cost per
estimator — the executable prototype of the paper's Figure 4b.

Downstream decision rule (from MissionModel's own-cost curves): a branch should
DELIBERATE iff its true chi exceeds the crossing point

    chi* = sqrt(llm_latency / (unplanned_penalty - planned_penalty))

(where deliberating starts paying for itself). An estimator is charged for
(a) the extra task time caused by wrong decisions near/across chi*, and
(b) its own latency on EVERY task — this is how a high-accuracy-but-slow probe
can lose to a zero-latency rule (the "slow router defeats the thesis" audit).

Usage:
    python -m garagenet.estimator_eval
"""

from __future__ import annotations

import argparse
import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Sequence

from garagenet.coupling_estimator import (
    BUCKETS,
    CouplingEstimator,
    FallbackGate,
    LearnedGate,
    ProbeGate,
    RuleGate,
    TaskDescription,
    generate_dataset,
)
from garagenet.mission import MissionModel


def chi_star(model: MissionModel) -> float:
    return math.sqrt(
        model.llm_latency
        / (model.unplanned_coupling_penalty - model.planned_coupling_penalty)
    )


def branch_time(model: MissionModel, chi: float, deliberate: bool) -> float:
    d = model.llm_latency if deliberate else 0.0
    pen = (
        model.planned_coupling_penalty
        if deliberate
        else model.unplanned_coupling_penalty
    )
    return d + model.base_execution + pen * (chi**model.coupling_exponent)


@dataclass
class EstimatorReport:
    name: str
    bucket_accuracy: float
    chi_mae: float
    mean_latency_s: float
    mean_misroute_cost_s: float  # task-time regret vs oracle decisions
    mean_total_overhead_s: float  # misroute cost + estimator latency

    def row(self) -> str:
        return (
            f"{self.name:>13} | acc {self.bucket_accuracy:5.1%} | "
            f"MAE {self.chi_mae:.3f} | lat {self.mean_latency_s * 1e3:8.2f}ms | "
            f"misroute {self.mean_misroute_cost_s:6.2f}s | "
            f"TOTAL overhead {self.mean_total_overhead_s:6.2f}s/task"
        )


def _nearest_bucket(chi: float) -> str:
    return min(BUCKETS, key=lambda b: abs(BUCKETS[b] - chi))


def evaluate(
    estimator: CouplingEstimator,
    tasks: Sequence[TaskDescription],
    model: MissionModel,
) -> EstimatorReport:
    threshold = chi_star(model)
    correct, maes, lats, misroutes = 0, [], [], []
    for t in tasks:
        chi_hat, latency = estimator.estimate(t)
        chi_true = t.true_chi
        assert chi_true is not None
        if _nearest_bucket(chi_hat) == t.true_bucket:
            correct += 1
        maes.append(abs(chi_hat - chi_true))
        lats.append(latency)
        decided = chi_hat >= threshold
        optimal = chi_true >= threshold
        misroutes.append(
            branch_time(model, chi_true, decided)
            - branch_time(model, chi_true, optimal)
        )
    return EstimatorReport(
        name=estimator.name,
        bucket_accuracy=correct / len(tasks),
        chi_mae=statistics.fmean(maes),
        mean_latency_s=statistics.fmean(lats),
        mean_misroute_cost_s=statistics.fmean(misroutes),
        mean_total_overhead_s=statistics.fmean(
            m + l for m, l in zip(misroutes, lats)
        ),
    )


def run(seed: int = 0) -> Dict[str, List[EstimatorReport]]:
    model = MissionModel()
    train = generate_dataset(n_per_bucket=40, seed=seed, style="canonical")
    tests = {
        "canonical (in-vocabulary — circular for rule-gate, read with care)":
            generate_dataset(n_per_bucket=40, seed=seed + 1, style="canonical"),
        "paraphrase (held-out wording — the honest, PARTNR-like condition)":
            generate_dataset(n_per_bucket=40, seed=seed + 2, style="paraphrase"),
    }
    estimators: List[CouplingEstimator] = [
        RuleGate(),
        LearnedGate().fit(train),
        ProbeGate(seed=seed),
        FallbackGate(probe=ProbeGate(seed=seed)),
    ]

    print(f"chi* (deliberate iff chi >= chi*): {chi_star(model):.3f}\n")
    all_reports: Dict[str, List[EstimatorReport]] = {}
    for label, test in tests.items():
        print(f"== {label} ==")
        reports = [evaluate(e, test, model) for e in estimators]
        for r in reports:
            print(r.row())
        print()
        all_reports[label] = reports
    print(
        "TOTAL overhead = mis-routing task-time regret + the estimator's own "
        "latency, both charged per task.\nOracle signal would score 0.00s."
    )
    return all_reports


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    run(seed=args.seed)


if __name__ == "__main__":
    main()
