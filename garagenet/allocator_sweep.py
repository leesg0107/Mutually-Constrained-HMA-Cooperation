"""Phase-1 experiment: allocators x externality sweep on the wildfire mission,
plus the mixed-chi mission for the A1 (per-agent vs team-uniform) claim.

Usage:
    python -m garagenet.allocator_sweep
"""

from __future__ import annotations

import argparse

from garagenet.allocators import all_allocators
from garagenet.mission import MissionModel, mixed_mission, wildfire_mission


def run(externalities=(0.0, 10.0, 30.0, 60.0, 120.0)) -> None:
    model = MissionModel()

    print("=== Wildfire mission (2 mapping branches -> 1 transport branch) ===")
    print("externality = extra transport seconds per non-deliberated map\n")
    header = f"{'ext':>6} | " + " | ".join(
        f"{a.name:>14}" for a in all_allocators(model)
    )
    print(header)
    print("-" * len(header))
    for ext in externalities:
        mission = wildfire_mission(externality=ext)
        cells = []
        for alloc in all_allocators(model):
            a = alloc.allocate(mission)
            n_delib = sum(1 for m in a.modes.values() if m == "deliberate")
            cells.append(f"{a.total_time:7.1f}s d{n_delib}")
        print(f"{ext:>6.0f} | " + " | ".join(f"{c:>14}" for c in cells))

    print(
        "\n(dN = number of branches that deliberate; total includes the "
        "allocator's own routing latency)"
    )

    print(
        "\n=== Mixed-chi pipeline mission "
        "(scouts chi=.05/.10 -> deliver; analyze chi=.95 in parallel) ==="
    )
    mission = mixed_mission()
    for alloc in all_allocators(model):
        a = alloc.allocate(mission)
        modes = ", ".join(f"{k}={v[:6]}" for k, v in sorted(a.modes.items()))
        print(f"{a.allocator:>14}: {a.total_time:7.1f}s   [{modes}]")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()
    run()


if __name__ == "__main__":
    main()
