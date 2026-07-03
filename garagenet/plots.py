"""Crossing plot: mean completion time vs difficulty per arm, with 95% CI bands
and a deliberation/execution split panel.

Usage:
    python -m garagenet.plots results/sweep_coupling.csv results/sweep_congestion.csv \
        --out results/crossing.png
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ARM_ORDER = ["L2-policy", "L1-hybrid", "L0-deliberation"]
ARM_COLORS = {  # colorblind-safe triad
    "L2-policy": "#0173b2",
    "L1-hybrid": "#de8f05",
    "L0-deliberation": "#029e73",
}


def load(csv_path: Path) -> Dict[Tuple[str, float, str], List[dict]]:
    groups: Dict[Tuple[str, float, str], List[dict]] = defaultdict(list)
    with csv_path.open() as f:
        for row in csv.DictReader(f):
            groups[(row["axis"], float(row["level"]), row["arm"])].append(row)
    return groups


def _stats(rows: List[dict], key: str) -> Tuple[float, float]:
    vals = [float(r[key]) for r in rows]
    n = len(vals)
    mean = sum(vals) / n
    if n < 2:
        return mean, 0.0
    sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1))
    return mean, 1.96 * sd / math.sqrt(n)  # 95% CI half-width


def plot(csv_paths: List[Path], out: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(
        1, len(csv_paths), figsize=(6.0 * len(csv_paths), 4.4), squeeze=False
    )
    for ax, csv_path in zip(axes[0], csv_paths):
        groups = load(csv_path)
        axis_name = next(iter(groups))[0] if groups else "?"
        for arm in ARM_ORDER:
            pts = sorted(
                (lvl, _stats(rows, "t_total"))
                for (a, lvl, arm_), rows in groups.items()
                if arm_ == arm
            )
            if not pts:
                continue
            xs = [p[0] for p in pts]
            ys = [p[1][0] for p in pts]
            ci = [p[1][1] for p in pts]
            color = ARM_COLORS.get(arm)
            ax.plot(xs, ys, marker="o", label=arm, color=color)
            ax.fill_between(
                xs, [y - c for y, c in zip(ys, ci)],
                [y + c for y, c in zip(ys, ci)], alpha=0.18, color=color,
            )
        ax.set_xlabel(f"{axis_name} level")
        ax.set_ylabel("completion time (s)")
        title = {
            "coupling": "Reasoning-coupling axis (crossing predicted)",
            "congestion": "Congestion axis (negative control: no crossing)",
        }.get(axis_name, axis_name)
        ax.set_title(title, fontsize=11)
        ax.legend(fontsize=9)
        ax.grid(alpha=0.25)
    fig.suptitle(
        "SYNTHETIC (mock model) — pipeline validation only, not evidence",
        fontsize=9, color="#b30000", y=1.0,
    )
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csvs", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=Path("results/crossing.png"))
    args = ap.parse_args()
    print(plot(args.csvs, args.out))


if __name__ == "__main__":
    main()
