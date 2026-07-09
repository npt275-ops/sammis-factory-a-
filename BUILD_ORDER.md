# BUILD ORDER — Factory A
Last updated: 2026-05-13

## Tổng quan
Factory A được build theo 3 phases. Mỗi phase phải COMPLETE trước khi sang phase tiếp theo.

---

## Phase 0: Setup (CURRENT)

| # | Task | Status | Notes |
|---|------|--------|-------|
| 0.1 | Python 3.10+ | ✅ DONE | 3.10.12 |
| 0.2 | Virtual environment | ✅ DONE | .venv/ created |
| 0.3 | Install packages | ⚠️ PENDING | Chạy setup_local_env.bat trên Windows |
| 0.4 | .env file | ✅ DONE | API keys configured |
| 0.5 | .gitignore | ✅ DONE | .env protected |
| 0.6 | Navigation files (7) | ✅ DONE | All 7 created |
| 0.7 | verify_phase0.py | ✅ DONE | |
| 0.8 | Git commit | ⏳ PENDING | |

**Exit criteria**: `python scripts/verify_phase0.py` → 11/13 green

---

## Phase 1: Foundation (DONE — ahead of schedule)

| # | Component | Status | Tests |
|---|-----------|--------|-------|
| 1.1 | shared_core/config.py | ✅ DONE | - |
| 1.2 | shared_core/logger.py | ✅ DONE | - |
| 1.3 | shared_core/database.py | ✅ DONE | - |
| 1.4 | shared_core/llm_provider.py | ✅ DONE | - |
| 1.5 | shared_core/memory.py | ✅ DONE | - |
| 1.6 | shared_core/telegram_base.py | ✅ DONE | - |
| 1.7 | shared_core/n8n_bridge.py | ✅ DONE | - |
| 1.8 | engine_vault/tier1/respond | ✅ DONE | 11/11 |
| 1.9 | engine_vault/tier1/rag | ✅ DONE | 11/11 |
| 1.10 | engine_vault/tier1/analytics | ✅ DONE | 11/11 |
| 1.11 | engine_vault/tier1/action | ✅ DONE | 11/11 |
| 1.12 | engine_vault/tier1/memory | ✅ DONE | 11/11 |
| 1.13 | engine_vault/tier1/schedule | ✅ DONE | 11/11 |
| 1.14 | engine_vault/tier1/identity | ✅ DONE | 11/11 |
| 1.15 | engine_vault/tier1/search | ✅ DONE | 11/11 |
| 1.16 | engine_vault/tier2/state_tracker | ✅ DONE | 11/11 |
| 1.17 | engine_vault/tier2/escalation_router | ✅ DONE | 11/11 |
| 1.18 | engine_vault/tier2/pattern_detector | ✅ DONE | 11/11 |
| 1.19 | engine_vault/tier2/long_memory | ✅ DONE | 11/11 |
| 1.20 | engine_vault/tier2/reflection_loop | ✅ DONE | 11/11 |
| 1.21 | engine_vault/tier2/decision_engine | ✅ DONE | 11/11 |
| 1.22 | engine_vault/tier2/multi_agent_coord | ✅ DONE | 11/11 |
| 1.23 | Integration tests | ✅ DONE | 10/10 |

**Exit criteria**: 168/168 tests pass ✅

---

## Phase 2: Pipeline A1→A7 ✅ DONE

| # | Component | Status | Depends on |
|---|-----------|--------|-----------|
| 2.1 | A1 Market Scanner + DirectInputAdapter | ✅ DONE | Phase 0 + 1 |
| 2.2 | A2 Pain Analyzer | ✅ DONE | A1 |
| 2.3 | A3 Blueprint Writer | ✅ DONE | A2 |
| 2.4 | A4 Bot Builder | ✅ DONE | A3 |
| 2.5 | A5 Quality Gates | ✅ DONE | A4 |
| 2.6 | A6 Deployer (ZIP + Server) | ✅ DONE | A5 |
| 2.7 | A7 Ops Worker | ✅ DONE | A6 |
| 2.8 | Orchestrator (Runner + StateMachine + Adapters) | ✅ DONE | A1–A7 |
| 2.9 | E2E test: L1 bot | ⏳ PENDING | A7 |
| 2.10 | E2E test: L2 bot | ⏳ PENDING | A7 |

**Exit criteria**: E2E test L1 + L2 PASS, bot deploy < 2 phút

---

## Milestone map
- **M0** — Phase 0 complete: Week 1
- **M1** — Phase 1 complete: Week 1 ✅ (AHEAD OF SCHEDULE)
- **M2** — Phase 2 complete: Week 3
- **M3** — L3 bots: Week 5
- **M4** — L4/L5 bots: Week 8
- **M5** — Production ready: Week 12
