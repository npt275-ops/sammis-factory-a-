# FILE INDEX â€” Factory A
Last updated: 2026-05-13

## Quick lookup

| File | MÃ´ táº£ | Phase |
|------|-------|-------|
| **Navigation** | | |
| PROJECT_BIBLE.md | Mission, principles, tech stack | 0 |
| FACTORY_A_NAVIGATION.md | HÆ°á»›ng dáº«n sá»­ dá»¥ng, anti-patterns, troubleshoot | 0 |
| PROJECT_MAP.md | Cáº¥u trÃºc thÆ° má»¥c chi tiáº¿t | 0 |
| BUILD_ORDER.md | Thá»© tá»± build, milestone map | 0 |
| SYSTEM_STATUS.md | Tráº¡ng thÃ¡i hiá»‡n táº¡i, test pass rate | 0 |
| TODO.md | Viá»‡c cáº§n lÃ m hÃ´m nay / tuáº§n nÃ y | 0 |
| FILE_INDEX.md | File nÃ y â€” tra cá»©u nhanh | 0 |
| **Setup** | | |
| .env | API keys (KHÃ”NG commit) | 0 |
| .env.template | Template cho .env | 0 |
| .gitignore | Git ignore rules | 0 |
| requirements.txt | Python dependencies | 0 |
| scripts/verify_phase0.py | Phase 0 verification script | 0 |
| scripts/setup_local_env.bat | Windows setup + pip install script | 0 |
| .aider.conf.yml | Aider AI config (ollama/deepseek-r1:7b) | 0 |
| **Shared Core** | | |
| shared_core/config.py | Config loader, pydantic BaseSettings | 1 |
| shared_core/logger.py | Loguru logger, notify_error | 1 |
| shared_core/database.py | SQLite + Supabase adapter | 1 |
| shared_core/llm_provider.py | LLM fallback chain | 1 |
| shared_core/memory.py | Conversation + episode memory | 1 |
| shared_core/telegram_base.py | Base bot, polling + webhook | 1 |
| shared_core/n8n_bridge.py | n8n workflow trigger | 1 |
| **Engine Vault â€” Tier 1** | | |
| engine_vault/tier1_foundation/respond/ | Response + button handling | 1 |
| engine_vault/tier1_foundation/rag/ | RAG with SQLite FTS5 | 1 |
| engine_vault/tier1_foundation/analytics/ | Event tracking + metrics | 1 |
| engine_vault/tier1_foundation/action/ | API calls + KiotViet | 1 |
| engine_vault/tier1_foundation/memory/ | TTL memory engine | 1 |
| engine_vault/tier1_foundation/schedule/ | APScheduler engine | 1 |
| engine_vault/tier1_foundation/identity/ | RBAC roles | 1 |
| engine_vault/tier1_foundation/search/ | Internal + DDG search | 1 |
| **Engine Vault â€” Tier 2** | | |
| engine_vault/tier2_director/state_tracker/ | Multi-source state | 1 |
| engine_vault/tier2_director/escalation_router/ | Urgency routing | 1 |
| engine_vault/tier2_director/pattern_detector/ | Z-score anomaly | 1 |
| engine_vault/tier2_director/long_memory/ | SQLite long memory | 1 |
| engine_vault/tier2_director/reflection_loop/ | Self-critique | 1 |
| engine_vault/tier2_director/decision_engine/ | Confidence routing | 1 |
| engine_vault/tier2_director/multi_agent_coord/ | Agent coordination | 1 |
| **Database** | | |
| database/migrations/001_initial_schema.sql | DB schema | 1 |
| **Tests** | | |
| tests/integration/test_shared_core.py | 10 integration tests (10/10 PASS) | 1 |
| tests/integration/test_engine_vault.py | Engine vault tests | 1 |
| **Pipeline A1-A9** DONE | | |
| pipeline/a1_market_scanner/ | A1 â€” Market Scanner, PII scrubber, DirectInputAdapter | 2 |
| pipeline/a2_pain_analyzer/ | A2 â€” Pain scoring â†’ ScoredPain | 2 |
| pipeline/a3_blueprint_writer/ | A3 â€” Bot design â†’ Blueprint | 2 |
| pipeline/a4_bot_builder/ | A4 â€” Code generation â†’ BotPackage | 2 |
| pipeline/a5_quality_gates/ | A5 â€” QA gates â†’ QualityBundle | 2 |
| pipeline/a6_deployer/ | A6 â€” ZIP / server deploy â†’ DeploymentReport | 2 |
| pipeline/a7_ops_worker/ | A7 â€” Monitoring daemon | 2 |
| pipeline/orchestrator/ | Runner, StateMachine, Adapters, OutputValidator | 2 |
| **Orchestration** âœ… DONE | | |
| orchestration/director_a/director.py | DirectorA - internal A1-A9 executor used by DirectorLoop | 2 |
| orchestration/director_a/director_loop.py | DirectorLoop - continuous durable queue loop, checkpoint, retry/dead-letter | 2 |
| orchestration/director_a/job_store.py | DirectorJobStore - durable resume queue and status/report source | 2 |
| orchestration/director_a/factory_state.py | FactoryState â€” RUNNING/PAUSED/TEST/STOPPED | 2 |
| orchestration/director_a/scheduler.py | FactoryScheduler â€” radar every 6h | 2 |
| orchestration/ceo_bot/bot.py | CEO Telegram Bot â€” automation-only /resume /factory /pause /test /stop | 2 |
