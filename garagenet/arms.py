"""Coordination arms: L0 (LLM deliberation), L1 (hybrid), L2 (reactive policy).

Each arm is a future PARTNR `Planner`-subclass candidate: it consumes a task,
optionally deliberates (producing a plan the environment can exploit — the
cross-agent externality channel), then executes, charging every second to the
correct clock on a TimingLedger.

Deliberation latency is supplied by a pluggable `DeliberationModel` so the same
arms run (a) fully simulated, (b) with recorded real-LLM latency traces, or
(c) with a live LLM client — without changing arm logic.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from garagenet.interfaces import Environment, EpisodeResult, TaskInstance
from garagenet.timing import TimingLedger


# --------------------------------------------------------------------------- #
# Deliberation models
# --------------------------------------------------------------------------- #
class DeliberationModel(Protocol):
    """Produces (plan, latency_seconds) for a task. Latency is what the arm
    charges to the deliberation clock in simulated mode."""

    def deliberate(self, task: TaskInstance, rounds: int) -> tuple[Dict[str, Any], float]:
        ...


@dataclass
class SimulatedLLM:
    """Latency model for multi-round inter-robot LLM dialogue.

    latency = rounds * (base + per_agent * n_agents), jittered. Defaults are
    order-of-magnitude placeholders (seconds per ReAct round incl. context
    growth); replace with recorded traces from a real backend before drawing
    any scientific conclusion.
    """

    base_round_latency: float = 6.0
    per_agent_latency: float = 2.0
    jitter_frac: float = 0.15
    seed: int = 0

    def deliberate(
        self, task: TaskInstance, rounds: int
    ) -> tuple[Dict[str, Any], float]:
        rng = random.Random((task.seed << 8) ^ self.seed ^ rounds)
        per_round = self.base_round_latency + self.per_agent_latency * task.n_agents
        latency = rounds * per_round * (1.0 + rng.gauss(0.0, self.jitter_frac))
        return {"allocation": "deliberated", "rounds": rounds}, max(latency, 0.05)


# --------------------------------------------------------------------------- #
# Arms
# --------------------------------------------------------------------------- #
@dataclass
class L2ReactivePolicy:
    """Pre-trained MARL/MAPF policy: zero deliberation, immediate execution."""

    name: str = "L2-policy"

    def run_episode(self, env: Environment, task: TaskInstance) -> EpisodeResult:
        ledger = TimingLedger()
        env.reset(task)
        env.install_plan(None)  # no deliberated plan: the externality is absent
        done, success, steps = False, False, 0
        while not done:
            _, done, info = env.step({i: "act" for i in range(task.n_agents)})
            ledger.add_execution(info["sim_time"])
            success = info.get("success", False)
            steps += 1
        return EpisodeResult(
            task=task, arm=self.name, success=success,
            t_deliberation=ledger.t_deliberation, t_execution=ledger.t_execution,
            steps=steps,
        )


@dataclass
class L0Deliberation:
    """Full inter-robot LLM dialogue before execution (multi-round)."""

    llm: DeliberationModel
    dialogue_rounds: int = 3
    name: str = "L0-deliberation"

    def run_episode(self, env: Environment, task: TaskInstance) -> EpisodeResult:
        ledger = TimingLedger()
        env.reset(task)
        plan, latency = self.llm.deliberate(task, rounds=self.dialogue_rounds)
        ledger.add_deliberation(latency)
        env.install_plan(plan)
        done, success, steps = False, False, 0
        while not done:
            _, done, info = env.step({i: "act" for i in range(task.n_agents)})
            ledger.add_execution(info["sim_time"])
            success = info.get("success", False)
            steps += 1
        return EpisodeResult(
            task=task, arm=self.name, success=success,
            t_deliberation=ledger.t_deliberation, t_execution=ledger.t_execution,
            steps=steps, info={"rounds": self.dialogue_rounds},
        )


@dataclass
class L1Hybrid:
    """One-shot LLM structuring + policy execution (single dialogue round)."""

    llm: DeliberationModel
    name: str = "L1-hybrid"

    def run_episode(self, env: Environment, task: TaskInstance) -> EpisodeResult:
        ledger = TimingLedger()
        env.reset(task)
        plan, latency = self.llm.deliberate(task, rounds=1)
        ledger.add_deliberation(latency)
        env.install_plan(plan)
        done, success, steps = False, False, 0
        while not done:
            _, done, info = env.step({i: "act" for i in range(task.n_agents)})
            ledger.add_execution(info["sim_time"])
            success = info.get("success", False)
            steps += 1
        return EpisodeResult(
            task=task, arm=self.name, success=success,
            t_deliberation=ledger.t_deliberation, t_execution=ledger.t_execution,
            steps=steps,
        )


def default_arms(seed: int = 0) -> list:
    """The three fixed-mechanism arms of the Phase-0 experiment."""
    llm = SimulatedLLM(seed=seed)
    return [L2ReactivePolicy(), L1Hybrid(llm=llm), L0Deliberation(llm=llm)]
