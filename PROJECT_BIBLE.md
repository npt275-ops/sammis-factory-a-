# Factory A — PROJECT BIBLE
Version: 1.0.0 | Date: 2026-05-13

## Mission
Factory A sản xuất AI agent Telegram từ pain signal. Output chuẩn = 1 bot_package với 9 artifacts, deploy được trong < 2 phút.

## Core Principles
1. **Deterministic over clever** — Pipeline A1→A7 không được "sáng tạo" ngoài spec
2. **Test everything** — Không có code không có test
3. **Local-first** — Chạy hoàn toàn local với Ollama, cloud chỉ là optional
4. **No anti-patterns** — Xem FACTORY_A_NAVIGATION.md Section 6
5. **Ship real products** — Không ảo, không vibe code, không implement-later

## Tech Stack
- Python 3.10+
- Ollama (DeepSeek-R1:7b primary LLM)
- Supabase (database cloud backup)
- SQLite (local database primary)
- python-telegram-bot 20+
- Jinja2 (template engine cho A4)
- pytest + pytest-asyncio (testing)

## Pipeline Overview
A1 (Market Scanner / Direct Input) → A2 (Pain Analyzer) → A3 (Blueprint Writer) → A4 (Bot Builder) → A5 (Quality Gates) → A6 (Deployer) → A7 (Ops Worker)

## Output Levels
- L1: Basic FAQ bot (linear menu)
- L2: CRUD bot (state machine)
- L3: Context bot (event-driven)
- L4: Director bot (reasoning DAG)
- L5: Conductor bot (hierarchical agent)

## Repository
GitHub: sammis-factory-a (private)
Branch strategy: main (stable), dev (development)
