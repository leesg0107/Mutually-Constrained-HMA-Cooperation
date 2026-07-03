"""Wall-clock instrumentation with a deliberation/execution/routing split.

Two accounting modes, one ledger:
  * real time  — context managers wrap actual calls (LLM inference, Habitat
    stepping); used by the PARTNR adapter and any live-LLM arm.
  * simulated  — `add_*(seconds)` records environment-reported costs; used by
    the mock environment so results are machine-independent.

Both modes may be mixed in one episode (e.g., real LLM latency + simulated
execution), which is exactly the Phase-0 configuration.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, Iterator

_CLOCKS = ("deliberation", "execution", "routing")


@dataclass
class TimingLedger:
    seconds: Dict[str, float] = field(
        default_factory=lambda: {c: 0.0 for c in _CLOCKS}
    )

    def _check(self, clock: str) -> None:
        if clock not in self.seconds:
            raise KeyError(f"unknown clock {clock!r}; expected one of {_CLOCKS}")

    # -- simulated accounting -------------------------------------------------
    def add(self, clock: str, seconds: float) -> None:
        self._check(clock)
        if seconds < 0:
            raise ValueError("negative duration")
        self.seconds[clock] += seconds

    def add_deliberation(self, seconds: float) -> None:
        self.add("deliberation", seconds)

    def add_execution(self, seconds: float) -> None:
        self.add("execution", seconds)

    def add_routing(self, seconds: float) -> None:
        self.add("routing", seconds)

    # -- real-time accounting -------------------------------------------------
    @contextmanager
    def measure(self, clock: str) -> Iterator[None]:
        self._check(clock)
        t0 = time.perf_counter()
        try:
            yield
        finally:
            self.seconds[clock] += time.perf_counter() - t0

    def deliberation(self) -> "_Ctx":
        return _Ctx(self, "deliberation")

    def execution(self) -> "_Ctx":
        return _Ctx(self, "execution")

    def routing(self) -> "_Ctx":
        return _Ctx(self, "routing")

    # -- readout ----------------------------------------------------------------
    @property
    def t_deliberation(self) -> float:
        return self.seconds["deliberation"]

    @property
    def t_execution(self) -> float:
        return self.seconds["execution"]

    @property
    def t_routing(self) -> float:
        return self.seconds["routing"]

    @property
    def t_total(self) -> float:
        return sum(self.seconds.values())


class _Ctx:
    """Reusable context-manager handle (`with ledger.deliberation(): ...`)."""

    def __init__(self, ledger: TimingLedger, clock: str) -> None:
        self._ledger, self._clock = ledger, clock

    def __enter__(self) -> None:
        self._t0 = time.perf_counter()

    def __exit__(self, *exc: object) -> None:
        self._ledger.seconds[self._clock] += time.perf_counter() - self._t0
