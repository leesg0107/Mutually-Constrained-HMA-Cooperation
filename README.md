# Mutually-Constrained-HMA-Cooperation (GarageNet)

Research project: **task-difficulty-gated cooperation for heterogeneous multi-robot teams** —
when a mission arrives, decide *per robot* whether to deliberate (LLM dialogue), run a
pre-trained MARL/MAPF policy, or hybrid, to minimize total completion time
(deliberation latency + execution time).

## Documents (`docs/`, read in this order)

1. `related-work-and-gap-analysis.md` — 3-round scooping check; verdict: un-scooped.
2. `problem-statement.md` — problem definition, L0–L2 construct, team-VoC objective.
3. `benchmark-feasibility.md` — PARTNR chosen as primary benchmark (source-verified drop-in path).
4. `paper-proposal.md` — adversarially stress-tested paper framing (measurement-first).
5. `algorithmic-direction-C.md` — heterogeneous coupling-conditioned cooperation (chosen direction).
6. `theory-team-voc.md` — team value-of-computation; non-separability theorem (coupling = externality).
7. `idea-verdict-and-architecture.md` — go/no-go verdict, architecture atoms A1–A3, staged plan.

## Code: Phase-0 measurement harness (`garagenet/`)

Measures wall-clock completion time split into **deliberation / execution / routing** for three
coordination arms on identical task instances, swept along a **coupling** axis (crossing predicted)
and a **congestion** negative-control axis (no crossing predicted).

```
garagenet/interfaces.py      TaskInstance / EpisodeResult / Environment / CoordinationArm
garagenet/timing.py          TimingLedger — real + simulated clocks, 3-way split
garagenet/arms.py            L0 LLM-deliberation / L1 hybrid / L2 reactive policy
garagenet/envs/mock.py       synthetic env encoding the theory model (pipeline validation ONLY)
garagenet/sweep.py           arms x levels x seeds -> CSV + crossing detection
garagenet/plots.py           crossing plot with CI bands
garagenet/partnr_adapter.py  PARTNR backend skeleton (the real Phase-0 experiment)
garagenet/mission.py         Phase-1: mission DAG (precedence + cross-agent externality)
garagenet/allocators.py      Phase-1: team-uniform / greedy-local / joint-oracle / coupling-gated
garagenet/allocator_sweep.py Phase-1 experiment: allocators x externality sweep
garagenet/coupling_estimator.py  gating signal: rule / learned / LLM-probe / fallback gates
garagenet/estimator_eval.py  gating ablation: accuracy x latency x mis-routing cost
garagenet/pipeline.py        end-to-end: NL descriptions -> estimate -> gate -> allocate -> execute
```

Quickstart:

```bash
pip install -e ".[dev]"
pytest                                      # 35 tests
python -m garagenet.sweep --axis coupling   --out results/
python -m garagenet.sweep --axis congestion --out results/
python -m garagenet.plots results/sweep_coupling.csv results/sweep_congestion.csv \
    --out results/crossing.png
```

**Honest scope:** the mock environment validates the *pipeline* (the harness detects a crossing
when the generating model has one, and none on the control axis). It is not evidence. The
scientific answer comes from running the same arms through `partnr_adapter.py` on PARTNR
(Habitat 3.0) with real LLM latency — the next step of Phase 0.
