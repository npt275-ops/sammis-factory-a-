# Factory A — PROJECT MAP
Last updated: 2026-05-13

## Cấu trúc thư mục

```
factory_a/
├── .env                          ← KHÔNG commit (gitignore)
├── .env.template                 ← Template để khách điền
├── .gitignore
├── requirements.txt
│
├── PROJECT_BIBLE.md              ← Navigation file 1
├── FACTORY_A_NAVIGATION.md       ← Navigation file 2
├── PROJECT_MAP.md                ← Navigation file 3 (FILE NÀY)
├── BUILD_ORDER.md                ← Navigation file 4
├── SYSTEM_STATUS.md              ← Navigation file 5
├── TODO.md                       ← Navigation file 6
├── FILE_INDEX.md                 ← Navigation file 7
│
├── shared_core/                  ← Shared modules (Phase 1 DONE)
│   ├── __init__.py
│   ├── config.py
│   ├── logger.py
│   ├── database.py
│   ├── llm_provider.py
│   ├── memory.py
│   ├── telegram_base.py
│   └── n8n_bridge.py
│
├── engine_vault/                 ← Engine library (Phase 1 DONE)
│   ├── tier1_foundation/
│   │   ├── respond/
│   │   ├── rag/
│   │   ├── analytics/
│   │   ├── action/
│   │   ├── memory/
│   │   ├── schedule/
│   │   ├── identity/
│   │   └── search/
│   └── tier2_director/
│       ├── state_tracker/
│       ├── escalation_router/
│       ├── pattern_detector/
│       ├── long_memory/
│       ├── reflection_loop/
│       ├── decision_engine/
│       └── multi_agent_coord/
│
├── pipeline/                     ← A1→A7 workers + orchestrator ✅ DONE
│   ├── a1_market_scanner/        ← PainSignal discovery + PII scrubbing
│   ├── a2_pain_analyzer/         ← Scoring → ScoredPain
│   ├── a3_blueprint_writer/      ← Bot design → Blueprint
│   ├── a4_bot_builder/           ← Code generation → BotPackage
│   ├── a5_quality_gates/         ← QA → QualityBundle
│   ├── a6_deployer/              ← ZIP / server deploy → DeploymentReport
│   ├── a7_ops_worker/            ← Monitoring daemon (server-hosted)
│   └── orchestrator/             ← Runner, StateMachine, Adapters, Validator
│
├── config/                       ← Configuration files
├── scripts/                      ← Utility scripts
├── database/                     ← DB migrations
├── tests/                        ← All tests
├── output/                       ← Bot packages (gitignore)
└── tools/                        ← Tool clients
```

## Ghi chú
- `output/bot_packages/` — gitignore'd
- `logs/` — gitignore'd
- `.env` — gitignore'd, KHÔNG push lên GitHub
- `.venv/` — gitignore'd, mỗi dev tự tạo local
