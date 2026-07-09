# SYSTEM STATUS - Factory A
Last updated: 2026-06-03

## Current state
- Active product path: A1-A9.
- Production entrypoint: CEO Bot `/resume`.
- Runtime direction: automation-only queue path.
- Manual `/build`: disabled in production.

## Director A
- [x] `DirectorLoop` continuous loop: 60-second interval, max 1 job per tick.
- [x] `FactoryScheduler`: radar scans every 6 hours and enqueue-only into `DirectorLoop`.
- [x] `DirectorJobStore`: durable JSON queue at `data/director_a_jobs.json`.
- [x] Stage checkpoint observability: A1-A9 checkpoint events stored per job.
- [x] Queue dashboard/status/report: `/factory`, `/status`, `/report <job_id>`.
- [x] Automation intelligence path: pre-build experiment/history hints and post-build learning hooks run through queued automation.
- [x] Failure policy: retryable queue failures are rescheduled; exhausted/unrecoverable jobs go to `dead_letter`.

## Pipeline
- [x] A1 market scanner/direct input.
- [x] A2 pain analyzer.
- [x] A3 blueprint writer.
- [x] A4 bot builder.
- [x] A5 quality gates.
- [x] A6 deployer / ZIP delivery.
- [x] A7 ops worker.
- [x] A8 packager.
- [x] A9 marketplace publisher.

## Verification
- Director A production tests: 14 passed.
- Full pytest suite: 656 passed, 1 skipped, 1 warning.
- Known warning: pytest cannot collect `tools/test_rig/modes/base.py::TestResult`
  because it is a dataclass with an `__init__`; this is unrelated to Director A.

## Runtime Map
```text
/resume
  -> set FactoryState RUNNING
  -> recover interrupted durable jobs
  -> scheduler radar enqueue
  -> DirectorLoop tick
  -> DirectorJobStore claim_next
  -> DirectorA.build
  -> PipelineRunner A1-A9
  -> A8 ZIP/product package
  -> A9 publish/skip result
  -> queue report/status
```
