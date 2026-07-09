# Factory A — NAVIGATION GUIDE
Version: 1.0.0 | Date: 2026-05-13

## Section 1: Bắt đầu nhanh

### Đọc theo thứ tự này:
1. `PROJECT_BIBLE.md` — Mission, principles, tech stack
2. `PROJECT_MAP.md` — Cấu trúc thư mục chi tiết
3. `BUILD_ORDER.md` — Thứ tự build các component
4. `SYSTEM_STATUS.md` — Trạng thái hiện tại
5. `TODO.md` — Việc cần làm hôm nay
6. `FILE_INDEX.md` — Tra cứu file nhanh

## Section 2: Cách chạy Factory A

### Local development
```bash
# 1. Activate venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac

# 2. Verify environment
python scripts/verify_phase0.py

# 3. Run tests
pytest tests/ -v

# 4. Run pipeline (khi Phase 2 done)
python -m pipeline.run --level L1
```

### Yêu cầu hệ thống
- Python 3.10+
- Ollama running trên localhost:11434
- Model: deepseek-r1:7b (primary), deepseek-coder:6.7b (code gen)
- RAM: 8GB+ (cho Ollama)
- Storage: 10GB+ (cho models + outputs)

## Section 3: Quy trình làm việc

### Thêm engine mới
1. Tạo thư mục trong `engine_vault/tier1_foundation/<name>/` hoặc `tier2_director/`
2. Tạo 4 files: `engine.py`, `contract.json`, `tests.py`, `VERSION`
3. Viết tests trước (TDD)
4. Implement engine
5. Chạy `pytest engine_vault/<path>/tests.py -v`
6. Update `FILE_INDEX.md`

### Thêm pipeline worker
1. Tạo thư mục trong `pipeline/a<N>_<name>/`
2. Implement `worker.py` với interface chuẩn
3. Viết integration tests
4. Update `BUILD_ORDER.md` và `SYSTEM_STATUS.md`

### Commit convention
```
feat: <description>      — tính năng mới
fix: <description>       — bug fix
test: <description>      — thêm/sửa test
chore: <description>     — maintenance, setup
docs: <description>      — documentation
refactor: <description>  — code refactor
```

## Section 4: LLM Routing

### Provider priority
1. **Ollama** (local, free, primary) — deepseek-r1:7b
2. **Groq** (cloud, fast, fallback 1) — llama3-70b
3. **Gemini** (cloud, fallback 2) — gemini-pro
4. **Claude** (cloud, fallback 3) — claude-3-haiku (khi có key)

### Khi nào dùng provider nào
- Analysis tasks → Ollama (deepseek-r1)
- Code generation → Ollama (deepseek-coder)
- Fast inference → Groq
- Long context → Gemini
- Complex reasoning → Claude (nếu có key)

## Section 5: Database

### Local SQLite (primary)
- Path: `factory_a.db` (auto-created)
- Migration: `database/migrations/001_initial_schema.sql`
- Access: qua `shared_core/database.py`

### Supabase (cloud backup)
- URL: xem `.env`
- Dùng cho: persistent storage, remote access
- Access: qua `shared_core/database.py` adapter

## Section 6: Anti-patterns (KHÔNG làm)

1. **Không** hard-code API keys trong source code
2. **Không** commit `.env` file
3. **Không** ship code không có tests
4. **Không** skip quality gate (A7)
5. **Không** implement "later" — nếu cần thì build ngay hoặc không build
6. **Không** dùng `print()` cho logging — dùng `loguru` qua `shared_core/logger.py`
7. **Không** access database trực tiếp — luôn qua `shared_core/database.py`
8. **Không** call LLM trực tiếp — luôn qua `shared_core/llm_provider.py`

## Section 7: Troubleshooting

### Ollama không chạy
```bash
# Start Ollama
ollama serve

# Pull models nếu chưa có
ollama pull deepseek-r1:7b
ollama pull deepseek-coder:6.7b
```

### Test fail
```bash
# Xem chi tiết lỗi
pytest tests/ -v --tb=short

# Chạy 1 test cụ thể
pytest tests/integration/test_shared_core.py::test_config -v
```

### .env không load
```bash
# Verify .env tồn tại
ls -la .env

# Verify format
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('FACTORY_ENV'))"
```
