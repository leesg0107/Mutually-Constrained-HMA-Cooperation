"""Sweep runner: arms x difficulty levels x seeds -> results CSV.

Usage:
    python -m garagenet.sweep --axis coupling   --out results/
    python -m garagenet.sweep --axis congestion --out results/
"""

from __future__ import annotations

import argparse
import csv
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from garagenet.arms import default_arms
from garagenet.envs.mock import MockCouplingEnv
from garagenet.interfaces import EpisodeResult, TaskInstance

CSV_FIELDS = [
    "axis", "level", "arm", "seed", "success",
    "t_deliberation", "t_execution", "t_routing", "t_total", "steps",
]


@dataclass
class SweepConfig:
    axis: str = "coupling"
    levels: Sequence[float] = field(
        default_factory=lambda: [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    )
    seeds: Sequence[int] = field(default_factory=lambda: list(range(20)))
    n_agents: int = 3


def run_sweep(cfg: SweepConfig, env=None, arms=None) -> List[EpisodeResult]:
    env = env if env is not None else MockCouplingEnv()
    results: List[EpisodeResult] = []
    for level in cfg.levels:
        for seed in cfg.seeds:
            task = TaskInstance(
                task_id=f"{cfg.axis}-{level:.2f}-s{seed}",
                axis=cfg.axis, level=level, n_agents=cfg.n_agents, seed=seed,
            )
            for arm in (arms if arms is not None else default_arms(seed=seed)):
                results.append(arm.run_episode(env, task))
    return results


def write_csv(results: List[EpisodeResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "axis": r.task.axis, "level": r.task.level, "arm": r.arm,
                "seed": r.task.seed, "success": int(r.success),
                "t_deliberation": f"{r.t_deliberation:.4f}",
                "t_execution": f"{r.t_execution:.4f}",
                "t_routing": f"{r.t_routing:.4f}",
                "t_total": f"{r.t_total:.4f}", "steps": r.steps,
            })


def summarize(
    results: List[EpisodeResult],
) -> Dict[Tuple[str, float], Dict[str, Dict[str, float]]]:
    """(axis, level) -> arm -> {mean_total, sd_total, mean_delib, mean_exec,
    success_rate, n}."""
    groups: Dict[Tuple[str, float, str], List[EpisodeResult]] = {}
    for r in results:
        groups.setdefault((r.task.axis, r.task.level, r.arm), []).append(r)
    out: Dict[Tuple[str, float], Dict[str, Dict[str, float]]] = {}
    for (axis, level, arm), rs in sorted(groups.items()):
        totals = [r.t_total for r in rs]
        out.setdefault((axis, level), {})[arm] = {
            "mean_total": statistics.fmean(totals),
            "sd_total": statistics.stdev(totals) if len(totals) > 1 else 0.0,
            "mean_delib": statistics.fmean(r.t_deliberation for r in rs),
            "mean_exec": statistics.fmean(r.t_execution for r in rs),
            "success_rate": statistics.fmean(int(r.success) for r in rs),
            "n": float(len(rs)),
        }
    return out


def find_crossings(
    summary: Dict[Tuple[str, float], Dict[str, Dict[str, float]]],
    arm_a: str = "L2-policy",
    arm_b: str = "L0-deliberation",
) -> List[float]:
    """Levels where the sign of mean_total(arm_a) - mean_total(arm_b) flips."""
    rows = sorted(summary.items())
    crossings, prev_sign = [], None
    for (_, level), arms in rows:
        if arm_a not in arms or arm_b not in arms:
            continue
        diff = arms[arm_a]["mean_total"] - arms[arm_b]["mean_total"]
        sign = diff > 0
        if prev_sign is not None and sign != prev_sign:
            crossings.append(level)
        prev_sign = sign
    return crossings


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--axis", choices=["coupling", "congestion"], default="coupling")
    ap.add_argument("--out", type=Path, default=Path("results"))
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--levels", type=int, default=6)
    args = ap.parse_args()

    cfg = SweepConfig(
        axis=args.axis,
        levels=[i / (args.levels - 1) for i in range(args.levels)],
        seeds=list(range(args.seeds)),
    )
    results = run_sweep(cfg)
    csv_path = args.out / f"sweep_{args.axis}.csv"
    write_csv(results, csv_path)

    summary = summarize(results)
    print(f"axis={cfg.axis}  episodes={len(results)}  ->  {csv_path}")
    for (_, level), arms in sorted(summary.items()):
        parts = [
            f"{arm}: {s['mean_total']:7.1f}s (d {s['mean_delib']:5.1f} / e "
            f"{s['mean_exec']:6.1f}, ok {s['success_rate']:.2f})"
            for arm, s in sorted(arms.items())
        ]
        print(f"  level {level:.2f}  " + " | ".join(parts))
    crossings = find_crossings(summary)
    print(f"L2-vs-L0 crossings at levels: {crossings or 'NONE'}")


if __name__ == "__main__":
    main()
