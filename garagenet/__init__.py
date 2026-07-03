"""GarageNet Phase-0 measurement harness.

Wall-clock completion time (deliberation + execution + routing) per
coordination mechanism (L0 LLM-deliberation / L1 hybrid / L2 learned policy)
across a controllable coupling axis, with a congestion negative-control axis.

See docs/idea-verdict-and-architecture.md for the staged plan this implements.
"""

from garagenet.interfaces import EpisodeResult, TaskInstance
from garagenet.timing import TimingLedger

__all__ = ["EpisodeResult", "TaskInstance", "TimingLedger"]
