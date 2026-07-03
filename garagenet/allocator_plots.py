"""Phase-1 figure: allocator comparison (wildfire externality sweep + mixed
pipeline mission).

Usage:
    python -m garagenet.allocator_plots --out results/allocators_demo.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

from garagenet.allocators import all_allocators
from garagenet.mission import MissionModel, mixed_mission, wildfire_mission

# Fixed categorical order + colorblind-safe palette (validated: lightness band,
# chroma, CVD separation PASS; #de8f05 contrast WARN relieved by direct labels
# and per-series markers).
ALLOCATOR_STYLE = {
    "team-uniform": ("#0173b2", "o"),
    "greedy-local": ("#de8f05", "s"),
    "joint-oracle": ("#029e73", "^"),
    "coupling-gated": ("#d55e00", "D"),
}


def plot(out: Path, externalities=(0.0, 10.0, 30.0, 60.0, 120.0)) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    model = MissionModel()

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(11.5, 4.4), gridspec_kw={"width_ratios": [3, 2]}
    )

    # -- Panel 1: wildfire externality sweep (lines) -------------------------
    for alloc in all_allocators(model):
        xs, ys = [], []
        for ext in externalities:
            a = alloc.allocate(wildfire_mission(externality=ext))
            xs.append(ext)
            ys.append(a.total_time)
        color, marker = ALLOCATOR_STYLE[alloc.name]
        ax1.plot(xs, ys, marker=marker, label=alloc.name, color=color, lw=2, ms=6)
    ax1.set_xlabel("cross-agent externality (extra transport s per unmapped area)")
    ax1.set_ylabel("mission completion time (s, incl. routing)")
    ax1.set_title("Wildfire mission: who decides the modes matters", fontsize=11)
    ax1.legend(fontsize=9)
    ax1.grid(alpha=0.25)
    ax1.annotate(
        "greedy under-deliberates upstream\n(Thm 2: regret grows unboundedly)",
        xy=(120, 314.8), xytext=(52, 262),
        fontsize=8.5, color="#6a6a6a",
        arrowprops=dict(arrowstyle="->", color="#9a9a9a"),
    )
    ax1.annotate(
        "gate escalates to joint only when\ncoupling demands it (Corollary)",
        xy=(60, 107.0), xytext=(24, 168),
        fontsize=8.5, color="#6a6a6a",
        arrowprops=dict(arrowstyle="->", color="#9a9a9a"),
    )

    # -- Panel 2: mixed pipeline mission (bars, direct-labeled) --------------
    names, times, colors = [], [], []
    for alloc in all_allocators(model):
        a = alloc.allocate(mixed_mission())
        names.append(alloc.name)
        times.append(a.total_time)
        colors.append(ALLOCATOR_STYLE[alloc.name][0])
    bars = ax2.bar(names, times, color=colors, width=0.62)
    for bar, t in zip(bars, times):
        ax2.text(
            bar.get_x() + bar.get_width() / 2, t + 1.5, f"{t:.1f}s",
            ha="center", fontsize=9, color="#3a3a3a",
        )
    ax2.set_ylabel("mission completion time (s)")
    ax2.set_title(
        "Mixed pipeline: per-agent mixing vs team-uniform (A1)", fontsize=11
    )
    ax2.tick_params(axis="x", rotation=18, labelsize=8.5)
    ax2.grid(alpha=0.25, axis="y")
    ax2.set_ylim(0, max(times) * 1.18)

    fig.suptitle(
        "SYNTHETIC (executable theory model) — mechanism validation, not evidence",
        fontsize=9, color="#b30000", y=1.0,
    )
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path("results/allocators_demo.png"))
    args = ap.parse_args()
    print(plot(args.out))


if __name__ == "__main__":
    main()
