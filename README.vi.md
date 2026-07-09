# Factory A

Factory A lÃ  má»™t "nhÃ  mÃ¡y" tá»± Ä‘á»™ng sáº£n xuáº¥t Telegram bot. Há»‡ thá»‘ng nháº­n má»™t pain signal, biáº¿n nÃ³ thÃ nh cÆ¡ há»™i sáº£n pháº©m Ä‘Ã£ Ä‘Æ°á»£c cháº¥m Ä‘iá»ƒm, viáº¿t blueprint cho bot, sinh gÃ³i Telegram bot, cháº¡y quality gate, deploy hoáº·c Ä‘Ã³ng gÃ³i ZIP, Ä‘Äƒng kÃ½ monitoring váº­n hÃ nh, lÃ m giÃ u thÃ nh sáº£n pháº©m cÃ³ thá»ƒ bÃ¡n, rá»“i tÃ¹y cáº¥u hÃ¬nh sáº½ publish lÃªn marketplace.

Luong code hien tai la **A1 -> A9**. Source of truth la `pipeline/orchestrator/runner.py`.

## Luá»“ng Runtime

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

Director A production automation chay theo queue:

- `/resume` la entrypoint production duy nhat.
- `FactoryScheduler` quet radar moi 6 gio va chi enqueue job.
- `DirectorLoop` chay lien tuc moi 60 giay, moi tick claim toi da 1 job durable,
  va co the tick ngay khi go `/resume`.
- `DirectorJobStore` luu durable queue trong `data/director_a_jobs.json`, gom
  attempts, max attempts, priority, `next_run_at`, stage checkpoint events,
  failure type va dead-letter reason.
- Theo doi queue qua `/factory`, `/status`, va `/report <job_id>`.
- Manual `/build` da tat trong production de factory chi con mot ban do
  automation.

Tráº¡ng thÃ¡i factory Ä‘Æ°á»£c lÆ°u trong `data/factory_state.json` vÃ  Ä‘iá»u khiá»ƒn qua CEO Bot:

| State | Radar | Queue | DirectorLoop | Má»¥c Ä‘Ã­ch |
| --- | --- | --- | --- | --- |
| `RUNNING` | Báº­t | Cho phÃ©p enqueue | Xá»­ lÃ½ job | Cháº¿ Ä‘á»™ automation production |
| `PAUSED` | Táº¯t | Giá»¯ nguyÃªn | Cháº·n | Táº¡m dá»«ng automation, khÃ´ng máº¥t queue |
| `TEST` | Táº¯t | Ná»™i bá»™ | Ná»™i bá»™ | Cháº¿ Ä‘á»™ an toÃ n Ä‘á»ƒ test |
| `STOPPED` | Táº¯t | Cháº·n | Cháº·n | Dá»«ng toÃ n bá»™ production |

## Pipeline ChÃ­nh

Pipeline active Ä‘Æ°á»£c khai bÃ¡o trong `PipelineRunner.WORKERS_SEQUENCE`.

| Stage | Module | Class/adapter chÃ­nh | Input | Output | Vai trÃ² |
| --- | --- | --- | --- | --- | --- |
| A1 | `pipeline/a1_market_scanner` | `A1DirectInputAdapter` hoáº·c `MarketScanner` | pain text, seed hoáº·c radar signal | `PainSignal` | Chuáº©n hÃ³a pain input, scrub PII, deduplicate ná»™i dung nguá»“n |
| A2 | `pipeline/a2_pain_analyzer` | `PainAnalyzer` | `PainSignal` | `ScoredPain` | Cháº¥m Ä‘iá»ƒm impact/frequency/buildability/profitability, phÃ¢n loáº¡i segment, bot type, tier vÃ  level |
| A3 | `pipeline/a3_blueprint_writer` | `BlueprintWriter` | `ScoredPain` | `Blueprint` | Chá»n engine, topology, template, DAG, data schema, quality layers |
| A4 | `pipeline/a4_bot_builder` | `A4BotBuilderAdapter` -> `BotBuilder` | A3 `Blueprint` | `BotPackage` | Chuyá»ƒn blueprint sang schema A4, render template, cháº¡y codegen, táº¡o file bot |
| A5 | `pipeline/a5_quality_gates` | `A5QualityGatesAdapter` -> `GateOrchestrator` | `BotPackage` | `QualityBundle` | Cháº¡y structure, security, dependency, smoke, container vÃ  integration gates |
| A6 | `pipeline/a6_deployer` | `A6DeployerAdapter` -> `A6Deployer` | `QualityBundle` | `DeploymentReport` | Máº·c Ä‘á»‹nh ZIP delivery, hoáº·c deploy server-hosted |
| A7 | `pipeline/a7_ops_worker` | `A7OpsAdapter` -> `A7OpsWorker` | `DeploymentReport` | pass-through `DeploymentReport` | ÄÄƒng kÃ½ monitoring cho server-hosted bot; bá» qua bot chá»‰ giao ZIP |
| A8 | `pipeline/a8_packager` | `A8PackagerAdapter` -> `A8Packager` | `DeploymentReport` | `MarketablePackage` | ThÃªm metadata sáº£n pháº©m, pricing, tags, `PRODUCT.md`, `listing.json` |
| A9 | `pipeline/a9_marketplace` | `A9MarketplaceAdapter` -> `A9Publisher` | `MarketablePackage` | `PublishResult` | Publish/skip/dry-run Gumroad, Payhip, Lemon Squeezy adapters |

Chi tiáº¿t implementation quan trá»ng:

- `pipeline/orchestrator/adapters.py` lÃ  lá»›p tÆ°Æ¡ng thÃ­ch giá»¯a cÃ¡c API stage. A4, A5, A6, A7, A8 vÃ  A9 khÃ´ng dÃ¹ng cÃ¹ng má»™t method signature, nÃªn runner gá»i adapter thay vÃ¬ gá»i trá»±c tiáº¿p worker thÃ´.
- `pipeline/orchestrator/output_validator.py` hiá»‡n validate handoff tá»« A1 Ä‘áº¿n A7. A7 -> A8 vÃ  A8 -> A9 Ä‘ang dá»±a vÃ o contract cá»§a adapter, chÆ°a cÃ³ schema validator riÃªng.
- A1 cÃ³ hai dáº¡ng cháº¡y: `MarketScanner` lÃ  batch radar crawler, cÃ²n `A1DirectInputAdapter` chuáº©n hÃ³a má»™t pain Ä‘Æ°á»£c `DirectorLoop` claim tá»« queue.
- A7 lÃ  module dáº¡ng daemon váº­n hÃ nh. á»ž cháº¿ Ä‘á»™ ZIP delivery, nÃ³ cá»‘ Ã½ khÃ´ng monitor gÃ¬ vÃ  chá»‰ pass-through deployment report.

## Orchestration

`orchestration/ceo_bot/`

- Giao diá»‡n Ä‘iá»u khiá»ƒn qua Telegram cho Sammis.
- Entrypoint: `orchestration/ceo_bot/bot.py`.
- DÃ¹ng `CEO_BOT_TOKEN` vÃ  `CEO_CHAT_ID`.
- Tá»± khá»Ÿi Ä‘á»™ng `FactoryScheduler` trá»« khi `FACTORY_SCHEDULER=0`.
- CÃ¡c command chÃ­nh:
  - `/resume` Ä‘á»ƒ cháº¡y Ä‘Æ°á»ng automation
  - `/status`
  - `/report <job_id>`
  - `/factory`
  - `/pause`, `/test`, `/stop`
  - `/selfmodel`, `/experiments`, `/optimize`, `/ask`

`orchestration/director_a/`

- `director.py`: build director náº±m giá»¯a CEO Bot/radar vÃ  `PipelineRunner`.
- `director_loop.py`: continuous queue loop, stage checkpoint writer,
  automation intelligence hook runner, va queue-level retry/dead-letter policy.
- `job_store.py`: durable JSON queue cho resume, retry timing, dashboard status
  va dead-letter diagnostics.
- `factory_state.py`: state machine bá»n vá»¯ng cho RUNNING/PAUSED/TEST/STOPPED.
- `scheduler.py`: vÃ²ng radar Ä‘á»‹nh ká»³, máº·c Ä‘á»‹nh 6 giá», tá»‘i Ä‘a 5 signal má»—i láº§n.
- `retry_engine.py`: phÃ¢n loáº¡i lá»—i vÃ  quyáº¿t Ä‘á»‹nh retry hay give-up.
- `quality_gate.py`: gate A2 cho human override vá»›i signal lÆ°ng chá»«ng.
- `feedback_memory.py`: ghi outcome build vÃ  inject hint tá»« lá»‹ch sá»­.
- `blueprint_dedup.py`: cache blueprint exact/draft Ä‘á»ƒ reuse.
- `blueprint_race.py`: cháº¡y song song nhiá»u á»©ng viÃªn A3 cho signal Ä‘iá»ƒm cao.
- `b2_bridge.py`: gá»­i context build hoÃ n táº¥t sang downstream ghostwriter flow.

`orchestration/n8n_workflows/`

- CÃ¡c thÆ° má»¥c placeholder cho n8n workflow, nhÃ³m theo customer ops, intelligence, maintenance vÃ  pipeline.

## Báº£n Äá»“ Repo

```text
factory_a/
|-- orchestration/          Telegram CEO Bot, DirectorA, scheduler, n8n placeholders
|-- pipeline/               Pipeline sáº£n pháº©m A1-A9, adapters vÃ  module legacy
|-- engine_vault/           ThÆ° viá»‡n engine tÃ¡i sá»­ dá»¥ng cho bot Ä‘Æ°á»£c sinh ra
|-- shared_core/            Config, logger, database, memory, Telegram base, LLM router
|-- tools/                  LLM clients, deployment helpers, scraping, test rig, storage
|-- intelligence/           VÃ²ng intelligence A0 evolution vÃ  A9 telemetry
|-- maintenance/            Self-heal, patch, rollback, feature request, verification
|-- security/               Static analysis vÃ  kiá»ƒm tra luáº­t dá»¯ liá»‡u Viá»‡t Nam
|-- privacy/                PII scrubber vÃ  patterns
|-- cost_guard/             Monitor API quota, infra cost vÃ  LLM cost
|-- adversarial/            Bá»™ red-team attack arsenal
|-- database/               SQLite/Supabase schema vÃ  migrations
|-- config/                 YAML runtime config cho A1/A2/A3/orchestrator/LLM/etc.
|-- docs/                   Design docs vÃ  policy dÃ i hÆ¡n
|-- scripts/                Verification, calibration, seed mining vÃ  E2E scripts
|-- tests/                  Integration vÃ  E2E tests
|-- output/                 Bot packages vÃ  artifact delivery Ä‘Æ°á»£c sinh ra
```

## Chi Tiáº¿t ThÆ° Má»¥c Pipeline

`pipeline/a1_market_scanner/`

- Public API: `MarketScanner`, `PainSignal`, `RawPain`, `ExtractedPain`.
- Sources gá»“m Hacker News, Indie Hackers, Product Hunt, YC public content, Reddit SaaS/startups/Vietnam, RSS Vietnam, SME forums, Twitter/X stubs, seed loader vÃ  direct input.
- Module há»— trá»£: extractor, deduplicator, PII scrubber, config, source base class vÃ  tests.

`pipeline/a2_pain_analyzer/`

- Public API: `PainAnalyzer`, `ScoredPain`, `Score`.
- Scorers: impact, frequency, buildability, profitability.
- Detectors: segment, bot type, integrations, similarity grouping.
- Map cÆ¡ há»™i thÃ nh tiers vÃ  levels L1-L5.

`pipeline/a3_blueprint_writer/`

- Public API: `BlueprintWriter`, `Blueprint`, `DataSchema`, `EngineRef`, `TopologyConfig`.
- Topologies gá»“m linear menus, callback menus, CRUD state machines, forms, wizards, event-driven bots, reasoning DAGs vÃ  hierarchical agents.
- CÃ³ DAG templates cho founder, builder vÃ  SME use cases.
- Sinh customer data schema cho flow setup/onboarding cá»§a bot Ä‘Æ°á»£c generate.

`pipeline/a3_5_data_collector/`

- ThÆ° má»¥c tá»“n táº¡i nhÆ°ng hiá»‡n chÆ°a cÃ³ Python implementation.
- A3 Ä‘Ã£ emit `DataSchema`, vÃ  A4 consume schema Ä‘Ã³ Ä‘á»ƒ generate logic setup/onboarding.

`pipeline/a4_bot_builder/`

- Public schemas: A4 `Blueprint`, `BotPackage`, `BotPackageFile`, `BotPackageMetadata`, `BotBuilderOptions`.
- CÃ¡c file báº¯t buá»™c Ä‘Æ°á»£c generate gá»“m `bot.py`, `requirements.txt`, `Dockerfile`, `.env.example`, README sinh ra, smoke test, `setup.py` vÃ  `run.sh`.
- DÃ¹ng template loading/rendering vÃ  optional codegen cho state machines, DAGs, decision routers vÃ  async loops.

`pipeline/a5_quality_gates/`

- Stage quality gate active Ä‘ang Ä‘Æ°á»£c runner dÃ¹ng.
- Gates: structure, security, dependency, smoke test, container build vÃ  integration.
- Tráº£ vá» immutable `QualityReport`; adapter wrap report vá»›i `BotPackage` gá»‘c thÃ nh `QualityBundle`.

`pipeline/a6_deployer/`

- Deployment modes:
  - `zip_delivery`: máº·c Ä‘á»‹nh, ghi ZIP output local.
  - `server_hosted`: deploy cloud/server qua adapters.
- Targets gá»“m Oracle Cloud, Fly.io, Render, local Docker vÃ  generic VPS.
- ThÆ° má»¥c ZIP output Ä‘Æ°á»£c Ä‘iá»u khiá»ƒn bá»Ÿi `PIPELINE_ZIP_OUTPUT_DIR`.

`pipeline/a7_ops_worker/`

- Monitoring vÃ  healing daemon cho server-hosted bots.
- Theo dÃµi health, metrics, log scrape data, heal events vÃ  stability window 24 giá».
- Healing strategies gá»“m container restart, image rollback, full redeploy vÃ  human alert.

`pipeline/a8_packager/`

- Chuyá»ƒn deployment output thÃ nh product package.
- ThÃªm pricing, product copy, tags, listing metadata vÃ  marketplace-ready JSON cáº¡nh deliverable.

`pipeline/a9_marketplace/`

- Publish `MarketablePackage` qua adapters.
- Adapter hiá»‡n cÃ³: Gumroad, Payhip vÃ  Lemon Squeezy.
- Thiáº¿u token thÃ¬ skip an toÃ n; `A9_DRY_RUN=true` sáº½ giáº£ láº­p publish.

`pipeline/orchestrator/`

- `runner.py`: cháº¡y tuáº§n tá»± A1-A9 vá»›i timeout, retry vÃ  validation.
- `state_machine.py`: lÆ°u pipeline run status vÃ  timings.
- `output_validator.py`: validate handoff giá»¯a cÃ¡c stage.
- `failure_handler.py`: phÃ¢n loáº¡i lá»—i transient/permanent/validation.
- `notifier.py`: Telegram notifications.
- `adapters.py`: bridge API stage thá»±c táº¿ vÃ o calling convention cá»§a runner.

CÃ¡c thÆ° má»¥c legacy (`a5_engine_assembler/`, `a6_sandbox_tester/`,
`a7_quality_gate/`) Ä'Ã£ bá»‹ xÃ³a trong V2 hardening (2026-06-23) — toÃ n bá»™
lÃ skeleton stub 0-byte, khÃ´ng cÃ³ import nÃ o tá»« codebase active.
Xem `pipeline/LEGACY.md` Ä'á»ƒ biáº¿t audit trail.

## Engine Vault

`engine_vault/` chá»©a cÃ¡c reusable engine Ä‘á»ƒ A3 chá»n vÃ  A4 wire vÃ o bot Ä‘Æ°á»£c generate.

Tier 1 foundation engines:

- `respond`: hÃ nh vi response cho command/FAQ.
- `rag`: retrieval augmented generation trÃªn knowledge base nhá».
- `analytics`: tracking event vÃ  metric.
- `action`: gá»i action/integration bÃªn ngoÃ i.
- `memory`: user/conversation memory.
- `schedule`: scheduled jobs/reminders.
- `identity`: identity/profile handling.
- `search`: hÃ nh vi search.

Tier 2 director engines:

- `state_tracker`: snapshot state vÃ  diff.
- `escalation_router`: urgency scoring vÃ  recipient routing.
- `pattern_detector`: phÃ¡t hiá»‡n signal/pattern láº·p láº¡i.
- `long_memory`: lÆ°u vÃ  retrieve memory dÃ i háº¡n.
- `reflection_loop`: reflection theo outcome vÃ  lessons.
- `decision_engine`: decision scoring.
- `multi_agent_coord`: Ä‘Äƒng kÃ½ sub-agent, tÃ¡ch task vÃ  aggregate káº¿t quáº£.

Má»—i engine folder Ä‘i theo contract local: `engine.py`, tests vÃ  metadata file náº¿u cÃ³. Xem thÃªm `engine_vault/ENGINE_CONTRACT.md`.

## Shared Core

`shared_core/` lÃ  runtime layer dÃ¹ng chung:

- `config.py`: Pydantic settings load tá»« `.env`.
- `logger.py`: structured logging dá»±a trÃªn Loguru.
- `database.py`: async SQLite adapter vÃ  Supabase adapter.
- `llm_provider.py`: provider fallback chain load tá»« `config/llm_routing.yaml`.
- `memory.py`: shared memory helpers.
- `telegram_base.py`: tiá»‡n Ã­ch ná»n cho Telegram bot.
- `n8n_bridge.py`: optional n8n integration.

LLM fallback order máº·c Ä‘á»‹nh lÃ  Ollama -> Groq -> Gemini -> Claude, trá»« khi Ä‘Æ°á»£c override trong `config/llm_routing.yaml`.

## Intelligence, Maintenance, Security VÃ  Ops

`intelligence/`

- `a0_evolution`: phÃ¢n tÃ­ch outcome, tá»‘i Æ°u prompt vÃ  version engines.
- `a9_telemetry`: collect telemetry, aggregate signals vÃ  detect anomalies, API failures, complaints, errors, silent death.

`maintenance/`

- `self_heal`: monitor, diagnose vÃ  cháº¥m confidence cho recovery.
- `strategies`: hot patch, cold patch, engine swap, regenerate vÃ  escalate.
- `strategy_selector`: chá»n recovery strategy.
- `patch_deployer`: HTTP/SSH/pull deployment helpers.
- `rollback`: quáº£n lÃ½ git revert vÃ  version rollback.
- `feature_request_handler`: parse, kiá»ƒm tra feasibility vÃ  route approval.
- `verification`: sanity tests vÃ  post-patch monitor.

`security/`

- `static_analysis`: secret scanner, dependency scanner vÃ  code scanner.
- `compliance`: kiá»ƒm tra luáº­t dá»¯ liá»‡u Viá»‡t Nam.

`privacy/`

- `pii_scrubber`: xÃ³a hoáº·c mask email, phone, CCCD/passport, bank account vÃ  address patterns.

`cost_guard/`

- Theo dÃµi LLM cost, infra cost vÃ  API quota usage.

`adversarial/`

- Bá»™ red-team attack arsenal bao gá»“m prompt injection, jailbreak, data exfil, cost attacks, privilege escalation, logic bombs vÃ  social engineering.

## Tools

`tools/llm/`

- Provider clients: Ollama, Groq, Gemini, Claude.

`tools/deployment/`

- Docker packaging cÃ¹ng Oracle Cloud, Fly.io vÃ  SSH deploy helpers.

`tools/scraping/`

- RSS reader, Playwright wrapper vÃ  OpenClaw client.

`tools/test_rig/`

- CLI test rig vá»›i smoke, integration vÃ  soak modes.
- CÃ³ Telegram client scenario runner, bot client, response judge, Docker runner, ZIP extractor, env loader vÃ  JSON/HTML reporters.

`tools/storage/`

- Supabase vÃ  GitHub storage clients.

## Configuration

CÃ¡c file config quan trá»ng:

| File | Má»¥c Ä‘Ã­ch |
| --- | --- |
| `config/a1_config.yaml` | Market scanner source vÃ  scan settings |
| `config/a2_config.yaml` | Pain analyzer weights vÃ  thresholds |
| `config/a3_config.yaml` | Blueprint writer settings |
| `config/engine_capabilities.yaml` | Capabilities available cho A2/A3 |
| `config/level_limits.yaml` | RÃ ng buá»™c L1-L5 |
| `config/market_knowledge.yaml` | Heuristic pricing/market cho scoring |
| `config/orchestrator_config.yaml` | Runner vÃ  orchestration settings |
| `config/llm_routing.yaml` | LLM providers, fallback vÃ  task overrides |

Má»™t sá»‘ config file hiá»‡n lÃ  placeholder rá»—ng vÃ  chÆ°a active: `cost_guard_thresholds.yaml`, `deployment_models.yaml`, `engine_registry.yaml`, `factory_config.yaml`, `maintenance_config.yaml`, `pricing_tiers.yaml`, `security_config.yaml`.

## Environment Variables

Code hiá»‡n cÃ³ hai nhÃ³m env Telegram:

- CEO Bot runtime dÃ¹ng `CEO_BOT_TOKEN` vÃ  `CEO_CHAT_ID`.
- `shared_core.config.Config` yÃªu cáº§u `TELEGRAM_BOT_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY` vÃ  `OLLAMA_BASE_URL`.

CÃ¡c biáº¿n chÃ­nh:

| Variable | DÃ¹ng bá»Ÿi | Required | Ghi chÃº |
| --- | --- | --- | --- |
| `CEO_BOT_TOKEN` | CEO Bot | CÃ³ vá»›i CEO Bot | Token Telegram control bot riÃªng |
| `CEO_CHAT_ID` | CEO Bot | CÃ³ vá»›i CEO Bot | Chat ID operator Ä‘Æ°á»£c phÃ©p Ä‘iá»u khiá»ƒn |
| `TELEGRAM_BOT_TOKEN` | shared core/generated bots | CÃ³ vá»›i shared config | Bot token mÃ  shared config ká»³ vá»ng |
| `TELEGRAM_ERROR_CHAT_ID` | notifications | KhÃ´ng báº¯t buá»™c | Chat nháº­n error notification |
| `SUPABASE_URL` | shared core | CÃ³ vá»›i shared config | Cloud backup/remote storage |
| `SUPABASE_KEY` | shared core | CÃ³ vá»›i shared config | Supabase API key |
| `OLLAMA_BASE_URL` | LLM provider | CÃ³ vá»›i shared config | ThÆ°á»ng lÃ  `http://localhost:11434` |
| `GROQ_API_KEY` | LLM fallback | KhÃ´ng báº¯t buá»™c | Cloud fallback |
| `GEMINI_API_KEY` | LLM fallback | KhÃ´ng báº¯t buá»™c | Cloud fallback |
| `CLAUDE_API_KEY` / `ANTHROPIC_API_KEY` | LLM/codegen scripts | TÃ¹y flow | Naming trong repo chÆ°a thá»‘ng nháº¥t hoÃ n toÃ n |
| `FACTORY_SCHEDULER` | CEO Bot | KhÃ´ng báº¯t buá»™c | Set `0` Ä‘á»ƒ táº¯t background radar |
| `PIPELINE_DEPLOY_MODE` | A6 adapter | KhÃ´ng báº¯t buá»™c | Máº·c Ä‘á»‹nh `zip_delivery`, hoáº·c `server_hosted` |
| `PIPELINE_ZIP_OUTPUT_DIR` | A6 ZIP delivery | KhÃ´ng báº¯t buá»™c | Máº·c Ä‘á»‹nh `/tmp/factory_a_output` |
| `PIPELINE_BOT_ENV_*` | A6 server-hosted | KhÃ´ng báº¯t buá»™c | Inject vÃ o env cá»§a bot Ä‘Æ°á»£c deploy |
| `GUMROAD_ACCESS_TOKEN` | A9 | KhÃ´ng báº¯t buá»™c | Publish Gumroad |
| `PAYHIP_API_KEY` | A9 | KhÃ´ng báº¯t buá»™c | Publish Payhip |
| `LEMONSQUEEZY_API_KEY` | A9 | KhÃ´ng báº¯t buá»™c | Publish Lemon Squeezy |
| `LEMONSQUEEZY_STORE_ID` | A9 | KhÃ´ng báº¯t buá»™c | Báº¯t buá»™c náº¿u dÃ¹ng Lemon Squeezy key |
| `A9_DRY_RUN` | A9 | KhÃ´ng báº¯t buá»™c | Giáº£ láº­p marketplace publish |

## Chạy Local

Cài dependencies:

```bash
pip install -r requirements.txt
```

Tạo `.env`:

```bash
cp .env.template .env
```

Trên Windows, bật CEO Bot supervisor từ thư mục này:

```bat
start_ceo_bot.bat
```

`run_ceo_bot.bat` chỉ còn là alias tương thích cho ghi chú cũ.

Sau khi CEO Bot online, mở Telegram và bấm `▶️ Start / Resume` để bắt đầu
vòng loop của nhà máy. Loop sẽ chuyển FactoryState sang `RUNNING`, quét radar,
enqueue job, rồi để DirectorLoop xử lý A1 -> A9. ZIP bot được ghi vào
`output/bot_packages` và có thể xem từ Telegram bằng nút `📁 Latest ZIP`.

Nếu chạy module thủ công, hãy chạy từ parent directory của `factory_a` và giữ
`PYTHONPATH` trỏ về parent directory đó:

```bash
cd ..
python -m factory_a.orchestration.ceo_bot.bot
```

## Testing Và Verification

Verify phase/environment:

```bash
python scripts/verify_phase0.py
```

Cháº¡y toÃ n bá»™ test suite:

```bash
pytest tests/ -v
```

Smoke test nhanh A5 -> A7 khÃ´ng cáº§n DB/API:

```bash
python scripts/run_pipeline_e2e.py --from-a5
```

Full E2E script:

```bash
python scripts/run_pipeline_e2e.py --pain "Bot dat ban FnB" --segment founder
```

Full E2E phá»¥ thuá»™c vÃ o packages Ä‘Ã£ cÃ i, API keys Ä‘Ã£ cáº¥u hÃ¬nh vÃ  runtime services Ä‘ang cháº¡y. Smoke path lÃ  check an toÃ n hÆ¡n Ä‘á»ƒ cháº¡y trÆ°á»›c.

## Ghi ChÃº PhÃ¡t Triá»ƒn Hiá»‡n Táº¡i

- Runner active la A1-A9.
- `TODO.md` cÅ© hÆ¡n tráº¡ng thÃ¡i code hiá»‡n táº¡i vÃ  váº«n mÃ´ táº£ má»™t sá»‘ viá»‡c Phase 2 lÃ  pending.
- `SYSTEM_STATUS.md` vÃ  `BUILD_ORDER.md` gáº§n vá»›i tráº¡ng thÃ¡i má»›i hÆ¡n, nhÆ°ng `runner.py` lÃ  nguá»“n sá»± tháº­t cho cÃ¡c stage active.
- Repo hiá»‡n cÃ³ nhiá»u file modified/untracked trong workspace. LuÃ´n xem `git status` trÆ°á»›c khi commit.
- Má»™t sá»‘ markdown vÃ  source comments cÃ³ mojibake do lá»—i encoding trÆ°á»›c Ä‘Ã³. README nÃ y dÃ¹ng tiáº¿ng Viá»‡t cÃ³ dáº¥u vÃ¬ Ä‘Ã¢y lÃ  tÃ i liá»‡u Ä‘á»c chÃ­nh.

## License

Private. All rights reserved.
