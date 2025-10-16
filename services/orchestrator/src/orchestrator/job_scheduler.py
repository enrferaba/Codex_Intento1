"""GPU/MIG aware job scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Mapping, MutableMapping, Sequence


@dataclass
class Slice:
    """Represents a MIG slice or logical partition in a GPU."""

    id: str
    profile: str
    capacity: int
    running: int = 0

    def has_capacity(self) -> bool:
        return self.running < self.capacity


@dataclass
class Gpu:
    """GPU instance with utilisation and thermal state."""

    id: str
    utilisation: float
    temperature: float
    slices: MutableMapping[str, Slice] = field(default_factory=dict)

    def compatible_slices(self, profile: str) -> Iterator[Slice]:
        sl = self.slices.get(profile)
        if sl:
            yield sl


@dataclass(frozen=True)
class Job:
    id: str
    profile: str


@dataclass(frozen=True)
class Allocation:
    job_id: str
    gpu_id: str
    slice_id: str


@dataclass
class SchedulerConfig:
    max_temperature: float = 82.0
    max_utilisation: float = 0.92


class JobScheduler:
    """Assigns jobs to GPUs honouring MIG profiles and headroom policies."""

    def __init__(self, gpus: Sequence[Gpu], config: SchedulerConfig | None = None) -> None:
        if not gpus:
            raise ValueError("At least one GPU must be declared")
        self._gpus: List[Gpu] = list(gpus)
        self._config = config or SchedulerConfig()

    def schedule(self, jobs: Iterable[Job]) -> List[Allocation]:
        assignments: List[Allocation] = []
        for job in jobs:
            allocation = self._allocate(job)
            if allocation:
                assignments.append(allocation)
        return assignments

    def _allocate(self, job: Job) -> Allocation | None:
        candidates: list[tuple[float, float, Gpu, Slice]] = []
        for gpu in self._gpus:
            if gpu.temperature >= self._config.max_temperature:
                continue
            if gpu.utilisation >= self._config.max_utilisation:
                continue
            for sl in gpu.compatible_slices(job.profile):
                if not sl.has_capacity():
                    continue
                load = sl.running / sl.capacity if sl.capacity else 1.0
                candidates.append((load, gpu.utilisation, gpu, sl))
        if not candidates:
            return None
        candidates.sort(key=lambda item: (item[0], item[1]))
        _, _, gpu, slice_ = candidates[0]
        slice_.running += 1
        gpu.utilisation = min(1.0, gpu.utilisation + (1.0 / max(slice_.capacity, 1)))
        return Allocation(job.id, gpu.id, slice_.id)


def build_gpu_fleet(config: Mapping[str, Mapping[str, int]]) -> list[Gpu]:
    """Helper to construct a GPU fleet from a nested mapping.

    Example input::

        {
            "gpu0": {"fast": 2, "verify": 1},
            "gpu1": {"expert": 1},
        }
    """

    fleet: list[Gpu] = []
    for gpu_id, slices in config.items():
        gpu_slices = {
            profile: Slice(id=f"{gpu_id}:{profile}", profile=profile, capacity=capacity)
            for profile, capacity in slices.items()
        }
        fleet.append(Gpu(id=gpu_id, utilisation=0.0, temperature=60.0, slices=gpu_slices))
    return fleet


__all__ = [
    "Allocation",
    "Gpu",
    "Job",
    "JobScheduler",
    "SchedulerConfig",
    "Slice",
    "build_gpu_fleet",
]
