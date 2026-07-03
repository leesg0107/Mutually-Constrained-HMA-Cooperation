"""Coupling estimators: predict a subtask's coupling chi from its DESCRIPTION,
before running it — the gating signal of the architecture ([1]-[2] layers).

Three designs (problem-statement.md §4), each returning (chi_hat, latency_s):

  * RuleGate     — iTax-grounded keyword/structure rules. Zero latency,
                   interpretable; the auditable baseline any reviewer can read.
  * LearnedGate  — tiny linear model on extracted features, trained on labeled
                   task descriptions. Microsecond latency, better accuracy.
  * ProbeGate    — one cheap LLM classification call. Highest accuracy, but
                   its latency is REAL and must be charged against the savings
                   (a probe that costs more than the deliberation it routes
                   around defeats the thesis).

Ground-truth chi buckets follow the PARTNR-style ladder (benchmark-feasibility
§4 — the axis must be reasoning/allocation complexity, not congestion):

  ND  constraint-free    chi=0.10   independent deliveries
  SP  spatial            chi=0.35   shared targets/relations
  ID  temporal           chi=0.60   ordering constraints
  XD  heterogeneous      chi=0.80   capability-restricted / multi-robot lifts
  CD  ambiguous/complex  chi=0.95   divergent goals, "split it as makes sense"

The synthetic description generator below exists to develop and unit-test the
estimators; the real evaluation re-runs them on PARTNR's NL instructions.
"""

from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Protocol, Sequence, Tuple

BUCKETS: Dict[str, float] = {
    "ND": 0.10, "SP": 0.35, "ID": 0.60, "XD": 0.80, "CD": 0.95,
}
BUCKET_ORDER = ["ND", "SP", "ID", "XD", "CD"]


@dataclass(frozen=True)
class TaskDescription:
    text: str
    n_agents: int = 3
    true_bucket: Optional[str] = None  # ground truth when known (synthetic/PARTNR labels)

    @property
    def true_chi(self) -> Optional[float]:
        return BUCKETS.get(self.true_bucket) if self.true_bucket else None


class CouplingEstimator(Protocol):
    name: str

    def estimate(self, task: TaskDescription) -> Tuple[float, float]:
        """Returns (chi_hat, latency_seconds)."""
        ...


# --------------------------------------------------------------------------- #
# Marker lexicons (shared by RuleGate and LearnedGate features)
# --------------------------------------------------------------------------- #
_MARKERS: Dict[str, List[str]] = {
    # CD: divergent/ambiguous allocation — deliberation territory
    "ambiguity": [
        "as makes sense", "appropriately", "as needed", "however you",
        "wherever", "somehow", "tidy", "organize", "decide among",
        "split the work", "figure out",
    ],
    # XD: capability restrictions / forced multi-robot coupling
    "capability": [
        "only the", "requires two", "requires both", "together with the",
        "must be carried by", "cannot reach", "too heavy for one",
        "needs the drone", "needs the arm",
    ],
    # ID: temporal ordering
    "ordering": [
        "first", "then", "after", "before", "once", "finally",
        "in this order", "followed by",
    ],
    # SP: shared spatial relations
    "spatial": [
        "same shelf", "same room", "next to", "on top of", "beside",
        "same table", "close to", "aligned with",
    ],
}


def _count_markers(text: str) -> Dict[str, int]:
    low = text.lower()
    return {
        cls: sum(1 for m in phrases if m in low)
        for cls, phrases in _MARKERS.items()
    }


# --------------------------------------------------------------------------- #
# 1. RuleGate — iTax-grounded priority rules, zero latency
# --------------------------------------------------------------------------- #
@dataclass
class RuleGate:
    name: str = "rule-gate"

    def classify(self, task: TaskDescription) -> str:
        c = _count_markers(task.text)
        if c["ambiguity"]:
            return "CD"
        if c["capability"]:
            return "XD"
        if c["ordering"]:
            return "ID"
        if c["spatial"]:
            return "SP"
        return "ND"

    def estimate(self, task: TaskDescription) -> Tuple[float, float]:
        t0 = time.perf_counter()
        chi = BUCKETS[self.classify(task)]
        return chi, time.perf_counter() - t0


# --------------------------------------------------------------------------- #
# 2. LearnedGate — linear regression on marker features (numpy lstsq)
# --------------------------------------------------------------------------- #
@dataclass
class LearnedGate:
    name: str = "learned-gate"
    weights: Optional[List[float]] = None  # set by fit()

    @staticmethod
    def features(task: TaskDescription) -> List[float]:
        c = _count_markers(task.text)
        n_sentences = max(1, task.text.count(".") + task.text.count(";"))
        return [
            1.0,
            float(c["ambiguity"]),
            float(c["capability"]),
            float(c["ordering"]),
            float(c["spatial"]),
            float(task.n_agents),
            float(n_sentences),
            float(len(task.text.split())) / 20.0,
        ]

    def fit(self, tasks: Sequence[TaskDescription]) -> "LearnedGate":
        import numpy as np

        X = np.array([self.features(t) for t in tasks])
        y = np.array([t.true_chi for t in tasks], dtype=float)
        w, *_ = np.linalg.lstsq(X, y, rcond=None)
        self.weights = w.tolist()
        return self

    def estimate(self, task: TaskDescription) -> Tuple[float, float]:
        if self.weights is None:
            raise RuntimeError("call fit() first")
        t0 = time.perf_counter()
        chi = sum(w * f for w, f in zip(self.weights, self.features(task)))
        chi = min(1.0, max(0.0, chi))
        return chi, time.perf_counter() - t0


# --------------------------------------------------------------------------- #
# 3. ProbeGate — one cheap LLM classification call (latency is the point)
# --------------------------------------------------------------------------- #
@dataclass
class ProbeGate:
    """Simulated by default (accuracy/latency model); pass `client` to use a
    real LLM: client(text) -> bucket string."""

    latency_s: float = 2.5
    accuracy: float = 0.92  # P(correct bucket); errors land on a neighbor
    seed: int = 0
    client: Optional[Callable[[str], str]] = None
    name: str = "llm-probe"
    _rule: RuleGate = field(default_factory=RuleGate)

    def estimate(self, task: TaskDescription) -> Tuple[float, float]:
        if self.client is not None:
            t0 = time.perf_counter()
            bucket = self.client(task.text)
            return BUCKETS.get(bucket, 0.5), time.perf_counter() - t0
        # simulated: near-oracle bucket with neighbor errors + fixed latency
        rng = random.Random((hash(task.text) & 0xFFFF) ^ self.seed)
        true = task.true_bucket or self._rule.classify(task)
        idx = BUCKET_ORDER.index(true)
        if rng.random() > self.accuracy:
            idx = min(len(BUCKET_ORDER) - 1, max(0, idx + rng.choice((-1, 1))))
        latency = self.latency_s * (1.0 + rng.gauss(0.0, 0.1))
        return BUCKETS[BUCKET_ORDER[idx]], max(latency, 0.2)


# --------------------------------------------------------------------------- #
# 4. FallbackGate — value-of-computation at the gate level itself
# --------------------------------------------------------------------------- #
@dataclass
class FallbackGate:
    """Rule first; pay the probe's latency ONLY when the rules are not
    confident (no marker fired). The gate applies the paper's own thesis to
    itself: deliberate (probe) only where it pays.

    Caveat by construction: marker-free text is indistinguishable from a
    genuine ND task, so ND tasks also trigger the probe — the fallback's
    canonical-set overhead is exactly the ND fraction times the probe latency.
    """

    probe: ProbeGate = field(default_factory=ProbeGate)
    name: str = "fallback-gate"
    _rule: RuleGate = field(default_factory=RuleGate)

    def estimate(self, task: TaskDescription) -> Tuple[float, float]:
        t0 = time.perf_counter()
        counts = _count_markers(task.text)
        if any(counts.values()):
            chi = BUCKETS[self._rule.classify(task)]
            return chi, time.perf_counter() - t0
        chi, probe_latency = self.probe.estimate(task)
        return chi, (time.perf_counter() - t0) + probe_latency


# --------------------------------------------------------------------------- #
# Synthetic labeled task-description generator (dev/test only)
# --------------------------------------------------------------------------- #
_TEMPLATES: Dict[str, List[str]] = {
    "ND": [
        "Move the {a} to the kitchen. Move the {b} to the garage.",
        "Deliver the {a} to room 1. Deliver the {b} to room 2. Water the plant.",
        "Pick up the {a} and place it in the bin. Sweep the hallway.",
    ],
    "SP": [
        "Place the {a} on the same shelf as the {b}.",
        "Put the {a} next to the {b} in the living room.",
        "Arrange the {a} beside the {b}, close to the window.",
    ],
    "ID": [
        "First clear the table, then wipe it, and finally place the {a} on it.",
        "Wash the {a} before storing it. Once stored, charge the {b}.",
        "Collect the {a}, then the {b}, in this order, followed by a sweep.",
    ],
    "XD": [
        "Only the drone can inspect the roof; the ground robot must bring the {a}.",
        "The {a} is too heavy for one robot and requires two to carry it.",
        "Fetch the {b} from the top shelf — only the arm robot cannot reach it, so it needs the drone.",
    ],
    "CD": [
        "Tidy the workshop appropriately, splitting the work however you see fit.",
        "Organize the storage room as makes sense; decide among yourselves who does what.",
        "Prepare the site for the crew — figure out the priorities and split the work.",
    ],
}
_OBJECTS = ["red box", "toolkit", "ladder", "blue crate", "sensor rig", "cable spool"]

# Same semantics, DIFFERENT wording — deliberately avoids the marker lexicon.
# This is the honest test: keyword rules are evaluated on their own vocabulary
# in the canonical set (circular); the paraphrase set measures what happens on
# real, unseen phrasings (the PARTNR situation).
_PARAPHRASE_TEMPLATES: Dict[str, List[str]] = {
    "ND": [
        "Take the {a} over to the kitchen; the {b} goes to the garage.",
        "The {a} belongs in room 1 and the {b} in room 2. The plant needs water.",
        "Drop the {a} in the bin and give the hallway a quick sweep.",
    ],
    "SP": [
        "The {a} and the {b} should end up sharing a shelf.",
        "Position the {a} right by the {b} in the living room.",
        "The {a} goes directly under the window, with the {b} adjacent.",
    ],
    "ID": [
        "Clear the table; wiping comes next, and setting the {a} happens last.",
        "The {a} gets washed, and storing it precedes charging the {b}.",
        "Collect the {a}, moving on to the {b} when that is complete.",
    ],
    "XD": [
        "Roof inspection is drone-exclusive work; the ground unit handles the {a}.",
        "Lifting the {a} is a two-robot job — no single unit manages it.",
        "The top-shelf {b} is out of the arm robot's envelope; aerial support is essential.",
    ],
    "CD": [
        "Get the workshop into shape — you three work out the division of labor.",
        "Make the storage room presentable; the team can settle who covers what.",
        "Ready the site for the crew, allocating duties among yourselves.",
    ],
}


def generate_dataset(
    n_per_bucket: int = 40, seed: int = 0, style: str = "canonical"
) -> List[TaskDescription]:
    templates = {
        "canonical": _TEMPLATES, "paraphrase": _PARAPHRASE_TEMPLATES
    }[style]
    rng = random.Random(seed)
    out: List[TaskDescription] = []
    for bucket, tpls in templates.items():
        for i in range(n_per_bucket):
            tpl = rng.choice(tpls)
            a, b = rng.sample(_OBJECTS, 2)
            out.append(
                TaskDescription(
                    text=tpl.format(a=a, b=b),
                    n_agents=rng.choice((2, 3, 4)),
                    true_bucket=bucket,
                )
            )
    rng.shuffle(out)
    return out
