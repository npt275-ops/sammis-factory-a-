# Factory A — MANIFEST
Version: V2 | Standard: Operator Autonomous OS Agent Standard V2

This file is the source of truth for the active Factory A runtime.
If docs, comments, or scripts disagree with this manifest, this manifest wins.

---

## Project Map

```
factory_a/
├── pipeline/                  # A1→A9 stage workers
│   ├── a1_market_scanner/     # Scan & ingest pain signals
│   ├── a2_pain_analyzer/      # Score and rank pain signals
│   ├── a3_blueprint_writer/   # Generate bot blueprint from scored pain
│   ├── a4_bot_builder/        # Build bot code from blueprint
│   ├── a5_quality_gates/      # Run quality checks on bot package (ACTIVE)
│   ├── a6_deployer/           # Deploy bot to target environment (ACTIVE)
│   ├── a7_ops_worker/         # Monitor and self-heal deployed bots (ACTIVE)
│   ├── a8_packager/           # Package bot for marketplace
│   ├── a9_marketplace/        # Publish to marketplace
│   ├── orchestrator/          # PipelineRunner — wires A1→A9 sequence
├── orchestration/
│   ├── director_a/            # Director: job scheduling, monitoring, B2 bridge
│   └── ceo_bot/               # Telegram CEO Bot: command interface, LLM brain
├── shared_core/               # Shared utilities: DB, LLM provider, logger, Telegram
├── tests/
│   ├── unit/                  # Unit tests (isolated, mocked)
│   ├── integration/           # Integration tests (adjacent stages, mock APIs)
│   ├── e2e/                   # End-to-end golden path tests
│   └── fixtures/              # Shared test data
├── specs/                     # Formal specs (9-section format)
├── docs/                      # Internal documentation
├── scripts/                   # Operational scripts (golden test runner, etc.)
├── config/                    # Per-stage YAML config files
├── pyproject.toml             # Package metadata + pytest path config (pip install -e .)
├── MANIFEST.md                # This file — source of truth
├── CONTEXT.md                 # Interface contracts, coding rules, architecture decisions
├── .env.example               # Environment variable template
└── protected_checksums        # MD5 hashes of stable files
```

---

## File Status Table

| File / Module | Status | Stage / Owner | Notes |
|---|---|---|---|
| `pipeline/a1_market_scanner/scanner.py` | active | A1 | MarketScanner entrypoint |
| `pipeline/a2_pain_analyzer/analyzer.py` | active | A2 | PainAnalyzer entrypoint |
| `pipeline/a3_blueprint_writer/writer.py` | active | A3 | BlueprintWriter entrypoint |
| `pipeline/a4_bot_builder/builder.py` | active | A4 | BotBuilder entrypoint |
| `pipeline/a5_quality_gates/` | active | A5 | GateOrchestrator |
| `pipeline/a6_deployer/` | active | A6 | A6Deployer |
| `pipeline/a7_ops_worker/` | active | A7 | A7OpsWorker |
| `pipeline/a8_packager/packager.py` | active | A8 | A8Packager entrypoint |
| `pipeline/a9_marketplace/` | active | A9 | A9Publisher |
| `pipeline/orchestrator/runner.py` | active | orchestrator | PipelineRunner.WORKERS_SEQUENCE |
| `pipeline/a5_engine_assembler/` | removed | — | Deleted 2026-06-23, was 0-byte skeleton |
| `pipeline/a6_sandbox_tester/` | removed | — | Deleted 2026-06-23, was 0-byte skeleton |
| `pipeline/a7_quality_gate/` | removed | — | Deleted 2026-06-23, was 0-byte skeleton |
| `shared_core/database.py` | stable | all stages | Supabase client |
| `shared_core/llm_provider.py` | stable | A2, A3, A4 | LLM abstraction |
| `shared_core/logger.py` | stable | all stages | Structured logging |
| `orchestration/director_a/director.py` | active | Director A | Job orchestration |
| `orchestration/director_a/b2_bridge.py` | active | Director A | Factory B integration |
| `orchestration/ceo_bot/bot.py` | active | CEO Bot | Telegram handler |
| `orchestration/ceo_bot/ceo_brain.py` | active | CEO Bot | LLM reasoning layer |
| `pyproject.toml` | stable | project root | Package install + pytest path config |

---

## Golden Runtime Path

Factory A currently runs the product line from A1 to A9:

```text
Pain input
  -> A1 Market Scanner / Direct Input
  -> A2 Pain Analyzer
  -> A3 Blueprint Writer
  -> A4 Bot Builder
  -> A5 Quality Gates
  -> A6 Deployer
  -> A7 Ops Worker
  -> A8 Packager
  -> A9 Marketplace Publisher
```

The active sequence is declared in:

```text
pipeline/orchestrator/runner.py::PipelineRunner.WORKERS_SEQUENCE
```

---

## Active Worker Map

| Stage | Active module | Runtime entry | Contract |
| --- | --- | --- | --- |
| A1 | `pipeline/a1_market_scanner` | `A1DirectInputAdapter` / `MarketScanner` | pain input -> `PainSignal` |
| A2 | `pipeline/a2_pain_analyzer` | `PainAnalyzer` | `PainSignal` -> `ScoredPain` |
| A3 | `pipeline/a3_blueprint_writer` | `BlueprintWriter` | `ScoredPain` -> `Blueprint` |
| A4 | `pipeline/a4_bot_builder` | `A4BotBuilderAdapter` -> `BotBuilder` | `Blueprint` -> `BotPackage` |
| A5 | `pipeline/a5_quality_gates` | `A5QualityGatesAdapter` -> `GateOrchestrator` | `BotPackage` -> `QualityBundle` |
| A6 | `pipeline/a6_deployer` | `A6DeployerAdapter` -> `A6Deployer` | `QualityBundle` -> `DeploymentReport` |
| A7 | `pipeline/a7_ops_worker` | `A7OpsAdapter` -> `A7OpsWorker` | monitor server-hosted, pass through zip delivery |
| A8 | `pipeline/a8_packager` | `A8PackagerAdapter` -> `A8Packager` | `DeploymentReport` -> `MarketablePackage` |
| A9 | `pipeline/a9_marketplace` | `A9MarketplaceAdapter` -> `A9Publisher` | `MarketablePackage` -> `PublishResult` |

---

## Legacy / Alternate Modules

The following folders were removed in V2 hardening (2026-06-23).
All were 0-byte skeleton stubs with no active imports.

| Removed | Replaced by |
|---|---|
| `pipeline/a5_engine_assembler/` | `pipeline/a5_quality_gates/` |
| `pipeline/a6_sandbox_tester/` | `pipeline/a6_deployer/` |
| `pipeline/a7_quality_gate/` | `pipeline/a5_quality_gates/` |

See `pipeline/LEGACY.md` for removal audit trail.

---

## Golden Tests

Required checks before changing runtime wiring:

```powershell
$env:PYTHONPATH='<path-to-your-workspace>'
.\.venv\Scripts\python.exe -m pytest pipeline\a1_market_scanner\tests.py pipeline\a2_pain_analyzer\tests.py pipeline\a3_blueprint_writer\tests.py pipeline\a4_bot_builder\tests pipeline\a5_quality_gates\tests pipeline\a6_deployer\tests pipeline\a7_ops_worker\tests pipeline\a8_packager\tests.py pipeline\a9_marketplace\tests.py pipeline\orchestrator\tests.py -q
.\.venv\Scripts\python.exe scripts\run_a1_a6_golden.py --full-level-matrix --include-a9
```

`scripts/run_a1_a6_golden.py` is historically named. Functionally it now tests
A1-A9 when `--include-a9` is passed.

---

## Noise Rules

Generated runtime output belongs under ignored output/log/cache paths.
Do not commit generated zip packages, listing files, temp README/TODO files,
pytest cache, logs, or product probe artifacts unless they are deliberately
promoted into `tests/fixtures` or `docs/examples`.
