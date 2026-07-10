# Factory A

Factory A is an autonomous Telegram-bot factory. It takes a pain signal,
turns it into a scored product opportunity, writes a bot blueprint, generates
the Telegram bot package, runs quality gates, deploys or zips the output,
registers ops monitoring, enriches it as a marketable product, and optionally
publishes it to marketplaces.

The current code path is **A1 -> A9**. The source of truth is
`pipeline/orchestrator/runner.py`.

## Runtime Flow

```text
CEO Bot /resume
        |
        v
FactoryState RUNNING
        |
        v
FactoryScheduler radar scan
        |
        v
DirectorJobStore queue
        |
        v
DirectorLoop claim job
        |
        v
DirectorA executor -> PipelineRunner A1 -> A9
        |
        v
A8 ZIP/product package + A9 listing
        |
        v
output/bot_packages
```

Director A production automation is queue-first:

- `/resume` is the single production entrypoint.
- `FactoryScheduler` scans radar on a 6-hour cadence and only enqueues jobs.
- `DirectorLoop` runs continuously every 60 seconds, claims at most one durable
  job per tick, and can be triggered immediately by `/resume`.
- `DirectorJobStore` persists queue jobs in `data/director_a_jobs.json`,
  including attempts, max attempts, priority, `next_run_at`, stage checkpoint
  events, failure type, and dead-letter reason.
- Queue visibility is exposed through `/factory`, `/status`, and
  `/report <job_id>`.
- Manual `/build` is disabled in production so the factory has one automation
  map.

Factory state is persisted in `data/factory_state.json` and controlled through
the CEO Bot:

| State | Radar | Queue | DirectorLoop | Purpose |
| --- | --- | --- | --- | --- |
| `RUNNING` | On | Enqueue enabled | Processes jobs | Automation production mode |
| `PAUSED` | Off | Preserved | Blocked | Pause automation without losing queue |
| `TEST` | Off | Internal only | Internal only | Safe mode for tests |
| `STOPPED` | Off | Blocked | Blocked | Stop all production |

## Main Pipeline

The active pipeline is declared in `PipelineRunner.WORKERS_SEQUENCE`.

| Stage | Module | Main class/adapter | Input | Output | Role |
| --- | --- | --- | --- | --- | --- |
| A1 | `pipeline/a1_market_scanner` | `A1DirectInputAdapter` or `MarketScanner` | pain text, seed, or radar signal | `PainSignal` | Normalize pain input, scrub PII, deduplicate source content |
| A2 | `pipeline/a2_pain_analyzer` | `PainAnalyzer` | `PainSignal` | `ScoredPain` | Score impact/frequency/buildability/profitability, classify segment, bot type, tier and level |
| A3 | `pipeline/a3_blueprint_writer` | `BlueprintWriter` | `ScoredPain` | `Blueprint` | Select engines, topology, template, DAG, data schema, quality layers |
| A4 | `pipeline/a4_bot_builder` | `A4BotBuilderAdapter` -> `BotBuilder` | A3 `Blueprint` | `BotPackage` | Convert blueprint to A4 schema, render templates, run codegen, produce bot files |
| A5 | `pipeline/a5_quality_gates` | `A5QualityGatesAdapter` -> `GateOrchestrator` | `BotPackage` | `QualityBundle` | Run structure, security, dependency, smoke, container and integration gates |
| A6 | `pipeline/a6_deployer` | `A6DeployerAdapter` -> `A6Deployer` | `QualityBundle` | `DeploymentReport` | ZIP delivery by default, or server-hosted deployment |
| A7 | `pipeline/a7_ops_worker` | `A7OpsAdapter` -> `A7OpsWorker` | `DeploymentReport` | `DeploymentReport` pass-through | Register server-hosted bots with monitoring; skip ZIP-only bots |
| A8 | `pipeline/a8_packager` | `A8PackagerAdapter` -> `A8Packager` | `DeploymentReport` | `MarketablePackage` | Add product metadata, pricing, tags, `PRODUCT.md`, `listing.json` |
| A9 | `pipeline/a9_marketplace` | `A9MarketplaceAdapter` -> `A9Publisher` | `MarketablePackage` | `PublishResult` | Publish/skip/dry-run Gumroad, Payhip, Lemon Squeezy adapters |

Important implementation details:

- `pipeline/orchestrator/adapters.py` is the compatibility layer between stage
  APIs. A4, A5, A6, A7, A8 and A9 do not all expose the same method signature,
  so the runner calls adapters instead of raw workers.
- `pipeline/orchestrator/output_validator.py` currently validates handoffs from
  A1 through A7. A7 -> A8 and A8 -> A9 are handled by adapter contracts, not by
  explicit validator schemas yet.
- A1 has two shapes: `MarketScanner` is batch radar crawling, while
  `A1DirectInputAdapter` normalizes one queued pain when `DirectorLoop`
  claims a job.
- A7 is a daemon-style ops module. In ZIP delivery mode it intentionally does
  not monitor anything and passes the deployment report through.

## Orchestration

`orchestration/ceo_bot/`

- Telegram control surface for Sammis.
- Entrypoint: `orchestration/ceo_bot/bot.py`.
- Uses `CEO_BOT_TOKEN` and `CEO_CHAT_ID`.
- Starts `FactoryScheduler` unless `FACTORY_SCHEDULER=0`.
- Commands include:
  - `/resume` to run the automation path
  - `/status`
  - `/report <job_id>`
  - `/factory`
  - `/pause`, `/test`, `/stop`
  - `/selfmodel`, `/experiments`, `/optimize`, `/ask`

`orchestration/director_a/`

- `director.py`: build director between CEO Bot/radar and `PipelineRunner`.
- `director_loop.py`: continuous queue loop, stage checkpoint writer,
  automation intelligence hook runner, and queue-level retry/dead-letter policy.
- `job_store.py`: durable JSON queue for resume, retry timing, dashboard status,
  and dead-letter diagnostics.
- `factory_state.py`: persistent state machine for RUNNING/PAUSED/TEST/STOPPED.
- `scheduler.py`: periodic radar loop, default 6 hours, max 5 signals per run.
- `retry_engine.py`: classifies failures and decides retry vs give-up.
- `quality_gate.py`: A2 human override gate for borderline signals.
- `feedback_memory.py`: records build outcomes and injects historical hints.
- `blueprint_dedup.py`: exact/draft blueprint reuse cache.
- `blueprint_race.py`: runs parallel A3 candidates for high-score signals.
- `b2_bridge.py`: posts completed build context to a downstream ghostwriter flow.

`orchestration/n8n_workflows/`

- Placeholder folders for n8n workflows grouped by customer ops, intelligence,
  maintenance and pipeline.

## Repository Map

```text
factory_a/
|-- orchestration/          Telegram CEO Bot, DirectorA, scheduler, n8n placeholders
|-- pipeline/               A1-A9 product pipeline plus adapters and legacy modules
|-- engine_vault/           Reusable engine library for generated bots
|-- shared_core/            Config, logger, database, memory, Telegram base, LLM router
|-- tools/                  LLM clients, deployment helpers, scraping, test rig, storage
|-- intelligence/           A0 evolution and A9 telemetry intelligence loops
|-- maintenance/            Self-heal, patch, rollback, feature request and verification logic
|-- security/               Static analysis and Vietnam data-law checks
|-- privacy/                PII scrubber and patterns
|-- cost_guard/             API quota, infra cost and LLM cost monitors
|-- adversarial/            Red-team attack arsenal
|-- database/               SQLite/Supabase schema and migrations
|-- config/                 Runtime YAML config for A1/A2/A3/orchestrator/LLM/etc.
|-- docs/                   Longer design docs and policies
|-- scripts/                Verification, calibration, seed mining and E2E scripts
|-- tests/                  Integration and E2E tests
|-- output/                 Generated bot packages and delivery artifacts
```

## Pipeline Directory Detail

`pipeline/a1_market_scanner/`

- Public API: `MarketScanner`, `PainSignal`, `RawPain`, `ExtractedPain`.
- Sources include Hacker News, Indie Hackers, Product Hunt, YC public content,
  Reddit SaaS/startups/Vietnam, RSS Vietnam, SME forums, Twitter/X stubs, seed
  loader and direct input.
- Supporting modules: extractor, deduplicator, PII scrubber, config,
  source base class and tests.

`pipeline/a2_pain_analyzer/`

- Public API: `PainAnalyzer`, `ScoredPain`, `Score`.
- Scorers: impact, frequency, buildability, profitability.
- Detectors: segment, bot type, integrations, similarity grouping.
- Maps opportunities to tiers and levels L1-L5.

`pipeline/a3_blueprint_writer/`

- Public API: `BlueprintWriter`, `Blueprint`, `DataSchema`, `EngineRef`,
  `TopologyConfig`.
- Topologies include linear menus, callback menus, CRUD state machines, forms,
  wizards, event-driven bots, reasoning DAGs and hierarchical agents.
- Contains DAG templates for founder, builder and SME use cases.
- Produces customer data schema for generated setup/onboarding flows.

`pipeline/a3_5_data_collector/`

- Directory exists but currently has no Python implementation.
- A3 already emits `DataSchema`, and A4 consumes that schema for generated
  setup/onboarding logic.

`pipeline/a4_bot_builder/`

- Public schemas: A4 `Blueprint`, `BotPackage`, `BotPackageFile`,
  `BotPackageMetadata`, `BotBuilderOptions`.
- Required generated files include `bot.py`, `requirements.txt`, `Dockerfile`,
  `.env.example`, generated README, smoke test, `setup.py` and `run.sh`.
- Uses template loading/rendering plus optional codegen for state machines,
  DAGs, decision routers and async loops.

`pipeline/a5_quality_gates/`

- Active quality gate stage used by the runner.
- Gates: structure, security, dependency, smoke test, container build and
  integration.
- Returns immutable `QualityReport`; adapter wraps it with the original
  `BotPackage` as `QualityBundle`.

`pipeline/a6_deployer/`

- Deployment modes:
  - `zip_delivery`: default, writes ZIP output locally.
  - `server_hosted`: cloud/server deployment using adapters.
- Targets include Oracle Cloud, Fly.io, Render, local Docker and generic VPS.
- ZIP output directory is controlled by `PIPELINE_ZIP_OUTPUT_DIR`.

`pipeline/a7_ops_worker/`

- Monitoring and healing daemon for server-hosted bots.
- Tracks health, metrics, log scrape data, heal events and 24-hour stability
  windows.
- Healing strategies include container restart, image rollback, full redeploy
  and human alert.

`pipeline/a8_packager/`

- Converts deployment output into a product package.
- Adds pricing, product copy, tags, listing metadata and marketplace-ready
  JSON beside the deliverable.

`pipeline/a9_marketplace/`

- Publishes `MarketablePackage` through adapters.
- Current adapters: Gumroad, Payhip and Lemon Squeezy.
- Missing tokens are skipped gracefully; `A9_DRY_RUN=true` simulates publishing.

`pipeline/orchestrator/`

- `runner.py`: sequential A1-A9 execution with timeout, retry and validation.
- `state_machine.py`: persists pipeline run status and timings.
- `output_validator.py`: validates stage handoffs.
- `failure_handler.py`: classifies transient/permanent/validation failures.
- `notifier.py`: Telegram notifications.
- `adapters.py`: bridges real stage APIs to the runner calling convention.

Legacy pipeline folders (`a5_engine_assembler/`, `a6_sandbox_tester/`,
`a7_quality_gate/`) were removed in V2 hardening (2026-06-23) — they were
0-byte skeleton stubs with no active imports. See `pipeline/LEGACY.md`.

## Engine Vault

`engine_vault/` contains reusable engines that A3 can select and A4 can wire
into generated bots.

Tier 1 foundation engines:

- `respond`: command/FAQ response behavior.
- `rag`: retrieval augmented generation over small knowledge bases.
- `analytics`: event and metric tracking.
- `action`: external action/integration calls.
- `memory`: user/conversation memory.
- `schedule`: scheduled jobs/reminders.
- `identity`: identity/profile handling.
- `search`: search behavior.

Tier 2 director engines:

- `state_tracker`: state snapshots and diffs.
- `escalation_router`: urgency scoring and recipient routing.
- `pattern_detector`: repeated signal/pattern detection.
- `long_memory`: longer-term memory storage and retrieval.
- `reflection_loop`: outcome reflection and lessons.
- `decision_engine`: decision scoring.
- `multi_agent_coord`: sub-agent registration, task decomposition and result
  aggregation.

Each engine folder follows the local contract style: `engine.py`, tests and
metadata files where present. See `engine_vault/ENGINE_CONTRACT.md`.

## Shared Core

`shared_core/` is the common runtime layer:

- `config.py`: Pydantic settings loaded from `.env`.
- `logger.py`: Loguru-based structured logging.
- `database.py`: async SQLite adapter plus Supabase adapter.
- `llm_provider.py`: provider fallback chain loaded from `config/llm_routing.yaml`.
- `memory.py`: shared memory helpers.
- `telegram_base.py`: Telegram bot base utilities.
- `n8n_bridge.py`: optional n8n integration.

LLM fallback order defaults to Ollama -> Groq -> Gemini -> Claude unless
overridden by `config/llm_routing.yaml`.

## Intelligence, Maintenance, Security and Ops

`intelligence/`

- `a0_evolution`: analyzes outcomes, optimizes prompts and versions engines.
- `a9_telemetry`: collects telemetry, aggregates signals and detects anomalies,
  API failures, complaints, errors and silent death.

`maintenance/`

- `self_heal`: monitor, diagnose and score confidence for recovery.
- `strategies`: hot patch, cold patch, engine swap, regenerate and escalate.
- `strategy_selector`: chooses a recovery strategy.
- `patch_deployer`: HTTP/SSH/pull deployment helpers.
- `rollback`: git revert and version rollback management.
- `feature_request_handler`: parse, check feasibility and route approvals.
- `verification`: sanity tests and post-patch monitor.

`security/`

- `static_analysis`: secret, dependency and code scanners.
- `compliance`: Vietnam data law checker.

`privacy/`

- `pii_scrubber`: removes or masks email, phone, CCCD/passport, bank account
  and address patterns.

`cost_guard/`

- Tracks LLM cost, infra cost and API quota usage.

`adversarial/`

- Red-team attack arsenal covering prompt injection, jailbreak, data exfil,
  cost attacks, privilege escalation, logic bombs and social engineering.

## Tools

`tools/llm/`

- Provider clients: Ollama, Groq, Gemini, Claude.

`tools/deployment/`

- Docker packaging plus Oracle Cloud, Fly.io and SSH deploy helpers.

`tools/scraping/`

- RSS reader, Playwright wrapper and OpenClaw client.

`tools/test_rig/`

- CLI test rig with smoke, integration and soak modes.
- Includes Telegram client scenario runner, bot client, response judge,
  Docker runner, ZIP extractor, env loader and JSON/HTML reporters.

`tools/storage/`

- Supabase and GitHub storage clients.

## Configuration

Important config files:

| File | Purpose |
| --- | --- |
| `config/a1_config.yaml` | Market scanner source and scan settings |
| `config/a2_config.yaml` | Pain analyzer weights and thresholds |
| `config/a3_config.yaml` | Blueprint writer settings |
| `config/engine_capabilities.yaml` | Capabilities available to A2/A3 |
| `config/level_limits.yaml` | L1-L5 constraints |
| `config/market_knowledge.yaml` | Pricing/market heuristics for scoring |
| `config/orchestrator_config.yaml` | Runner and orchestration settings |
| `config/llm_routing.yaml` | LLM providers, fallback and task overrides |

Some config files are placeholders with zero length and are not active yet:
`cost_guard_thresholds.yaml`, `deployment_models.yaml`,
`engine_registry.yaml`, `factory_config.yaml`, `maintenance_config.yaml`,
`pricing_tiers.yaml`, `security_config.yaml`.

## Environment Variables

There are two Telegram env groups in the current code:

- CEO Bot runtime uses `CEO_BOT_TOKEN` and `CEO_CHAT_ID`.
- `shared_core.config.Config` requires `TELEGRAM_BOT_TOKEN`,
  `SUPABASE_URL`, `SUPABASE_KEY` and `OLLAMA_BASE_URL`.

Core variables:

| Variable | Used by | Required | Notes |
| --- | --- | --- | --- |
| `CEO_BOT_TOKEN` | CEO Bot | Yes for CEO Bot | Private Telegram control bot token |
| `CEO_CHAT_ID` | CEO Bot | Yes for CEO Bot | Authorized operator chat ID |
| `TELEGRAM_BOT_TOKEN` | shared core/generated bots | Yes for shared config | Bot token expected by shared config |
| `TELEGRAM_ERROR_CHAT_ID` | notifications | Optional | Error notification chat |
| `SUPABASE_URL` | shared core | Yes for shared config | Cloud backup/remote storage |
| `SUPABASE_KEY` | shared core | Yes for shared config | Supabase API key |
| `OLLAMA_BASE_URL` | LLM provider | Yes for shared config | Usually `` |
| `GROQ_API_KEY` | LLM fallback | Optional | Cloud fallback |
| `GEMINI_API_KEY` | LLM fallback | Optional | Cloud fallback |
| `CLAUDE_API_KEY` / `ANTHROPIC_API_KEY` | LLM/codegen scripts | Optional/flow-dependent | Naming is not fully unified in the repo |
| `FACTORY_SCHEDULER` | CEO Bot | Optional | Set `0` to disable background radar |
| `PIPELINE_DEPLOY_MODE` | A6 adapter | Optional | `zip_delivery` default, or `server_hosted` |
| `PIPELINE_ZIP_OUTPUT_DIR` | A6 ZIP delivery | Optional | Default `/tmp/factory_a_output` |
| `PIPELINE_BOT_ENV_*` | A6 server-hosted | Optional | Injected into deployed bot env |
| `GUMROAD_ACCESS_TOKEN` | A9 | Optional | Gumroad publishing |
| `PAYHIP_API_KEY` | A9 | Optional | Payhip publishing |
| `LEMONSQUEEZY_API_KEY` | A9 | Optional | Lemon Squeezy publishing |
| `LEMONSQUEEZY_STORE_ID` | A9 | Optional | Required with Lemon Squeezy key |
| `A9_DRY_RUN` | A9 | Optional | Simulate marketplace publish |

## Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`:

```bash
cp .env.template .env
```

On Windows, start the CEO Bot supervisor from this directory:

```bat
start_ceo_bot.bat
```

`run_ceo_bot.bat` is kept only as a compatibility alias for older local notes.

After the CEO Bot is online, open Telegram and press `▶️ Start / Resume` to
start the factory loop. The loop sets FactoryState to `RUNNING`, scans radar,
enqueues jobs, and lets DirectorLoop process A1 -> A9. Generated ZIP packages
are written under `output/bot_packages` and can be checked from Telegram with
`📁 Latest ZIP`.

If running the module manually, run it from the parent directory of `factory_a`
and keep `PYTHONPATH` pointed at that parent directory:

```bash
cd ..
python -m factory_a.orchestration.ceo_bot.bot
```

## Testing and Verification

Phase/environment verification:

```bash
python scripts/verify_phase0.py
```

Full test suite:

```bash
pytest tests/ -v
```

Fast A5 -> A7 smoke test without DB/API:

```bash
python scripts/run_pipeline_e2e.py --from-a5
```

Full E2E script:

```bash
python scripts/run_pipeline_e2e.py --pain "Bot dat ban FnB" --segment founder
```

The full E2E path depends on installed packages, configured API keys and working
runtime services. The smoke path is the safer first check.

## Current Development Notes

- The active runner is A1-A9.
- `TODO.md` is older than the current code state and still describes some
  Phase 2 work as pending.
- `SYSTEM_STATUS.md` and `BUILD_ORDER.md` are closer to the recent state, but
  `runner.py` is the source of truth for active stages.
- The repo contains many untracked or modified files in the current workspace.
  Treat `git status` as the source of truth before committing.
- Some markdown and source comments contain mojibake from earlier encoding
  issues. This README intentionally uses ASCII to stay stable across shells.

## License

Private. All rights reserved.
