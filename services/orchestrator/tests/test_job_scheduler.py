from __future__ import annotations

from orchestrator import (
    Allocation,
    Job,
    JobScheduler,
    SchedulerConfig,
    build_gpu_fleet,
)


def test_scheduler_assigns_jobs_to_matching_profiles() -> None:
    fleet = build_gpu_fleet({"gpu0": {"fast": 2, "verify": 1}})
    scheduler = JobScheduler(fleet)
    jobs = [Job(id="job-fast-1", profile="fast"), Job(id="job-fast-2", profile="fast")]
    assignments = scheduler.schedule(jobs)
    assert {(alloc.job_id, alloc.gpu_id) for alloc in assignments} == {
        ("job-fast-1", "gpu0"),
        ("job-fast-2", "gpu0"),
    }


def test_scheduler_respects_capacity() -> None:
    fleet = build_gpu_fleet({"gpu0": {"fast": 1}})
    scheduler = JobScheduler(fleet)
    jobs = [Job(id="job-1", profile="fast"), Job(id="job-2", profile="fast")]
    assignments = scheduler.schedule(jobs)
    assert len(assignments) == 1
    assert assignments[0] == Allocation(job_id="job-1", gpu_id="gpu0", slice_id="gpu0:fast")


def test_scheduler_skips_hot_gpu() -> None:
    fleet = build_gpu_fleet({"gpu0": {"fast": 1}, "gpu1": {"fast": 1}})
    fleet[0].temperature = 90.0
    scheduler = JobScheduler(fleet, SchedulerConfig(max_temperature=80.0))
    assignments = scheduler.schedule([Job(id="job-1", profile="fast")])
    assert len(assignments) == 1
    assert assignments[0].gpu_id == "gpu1"
