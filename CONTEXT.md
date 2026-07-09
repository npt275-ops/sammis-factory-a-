# Factory A — CONTEXT
Version: V2 | Standard: Operator Autonomous OS Agent Standard V2

Interface contracts, coding rules, and architecture decisions.
See MANIFEST.md for runtime file map and golden test commands.

---

## 1. Interface Contracts (Stage Data Flow)

Each stage receives one typed object and emits one typed object.
The orchestrator (`pipeline/orchestrator/runner.py`) enforces this boundary.

```
A1 MarketScanner / A1DirectInputAdapter
   output → PainSignal
              ↓
A2 PainAnalyzer
   input  ← PainSignal
   output → ScoredPain
              ↓
A3 BlueprintWriter
   input  ← ScoredPain
   output → Blueprint
              ↓
A4 BotBuilder  (via A4BotBuilderAdapter)
   input  ← Blueprint
   output → BotPackage
              ↓
A5 GateOrchestrator  (via A5QualityGatesAdapter)
   input  ← BotPackage
   output → QualityBundle
              ↓
A6 A6Deployer  (via A6DeployerAdapter)
   input  ← QualityBundle
   output → DeploymentReport
              ↓
A7 A7OpsWorker  (via A7OpsAdapter)
   input  ← DeploymentReport
   output → DeploymentReport  (pass-through, adds ops metadata)
              ↓
A8 A8Packager  (via A8PackagerAdapter)
   input  ← DeploymentReport
   output → MarketablePackage
              ↓
A9 A9Publisher  (via A9MarketplaceAdapter)
   input  ← MarketablePackage
   output → PublishResult
```

### Contract definitions by module

| Contract type | Defined in |
|---|---|
| `PainSignal` | `pipeline/a1_market_scanner/` |
| `ScoredPain` | `pipeline/a2_pain_analyzer/` |
| `Blueprint` | `pipeline/a3_blueprint_writer/` |
| `BotPackage` | `pipeline/a4_bot_builder/` |
| `QualityBundle` | `pipeline/a5_quality_gates/` |
| `DeploymentReport` | `pipeline/a6_deployer/` |
| `MarketablePackage` | `pipeline/a8_packager/` |
| `PublishResult` | `pipeline/a9_marketplace/` |

---

## 2. Coding Rules (Project-Specific)

### Import paths
Always use absolute imports from the repo root `<path-to-your-workspace>`.
Set `PYTHONPATH=<path-to-your-workspace>` before running any script or test.

```python
# correct
from factory_a.shared_core.logger import get_logger
from pipeline.a2_pain_analyzer.analyzer import PainAnalyzer

# wrong
from ..shared_core.logger import get_logger
```

### Environment variables
Use `os.environ.get("KEY", default)` pattern. Default values are for local dev
only — production must have the var set explicitly.

```python
import os
base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
```

**Rule:** env var names in code must exactly match names in `.env.example`.
No aliases, no duplicates.

### Logging
Use `shared_core/logger.py`. Never use `print()` in production code.

```python
from shared_core.logger import get_logger
logger = get_logger(__name__)
logger.info("Stage A3 started", extra={"blueprint_id": bp.id})
```

### Adapter pattern
Every stage `aX` must expose an adapter class as its public entrypoint.
The orchestrator calls the adapter — never the internal class directly.

```
pipeline/aX/
├── adapter.py     ← AXAdapter (orchestrator calls this)
├── worker.py      ← internal logic
└── __init__.py
```

### Immutability
Stage output objects must be treated as read-only once emitted.
Do not mutate a contract object received from an upstream stage.

---

## 3. Architecture Decisions (ADR)

### ADR-001: Adapter pattern for each stage
**Decision:** Each pipeline stage exposes an adapter class, not its internal
class, to the orchestrator.
**Reason:** Decouples orchestrator from internal stage implementation. Allows
a stage to be replaced or A/B-tested by swapping its adapter without touching
`runner.py`.
**Consequence:** Every new stage must implement the adapter interface defined
in `pipeline/orchestrator/adapters.py`.

### ADR-002: Single orchestrator (`pipeline/orchestrator/runner.py`)
**Decision:** Only `PipelineRunner` is allowed to sequence stage calls.
**Reason:** Centralising sequence logic prevents race conditions, simplifies
telemetry, and gives the Director a single control point for pause/resume.
**Consequence:** Director A calls `PipelineRunner`, not individual stages.

### ADR-003: Legacy modules removed (V2 hardening)
**Decision:** `pipeline/a5_engine_assembler`, `pipeline/a6_sandbox_tester`,
`pipeline/a7_quality_gate` were deleted on 2026-06-23.
**Reason:** All three were 0-byte skeleton stubs with no active imports and no
engineering content. Retaining them added noise without value.
**Audit:** Pre-deletion grep confirmed zero imports from any of the three
folders across the entire codebase. See `pipeline/LEGACY.md`.

### ADR-004: CEO Bot LLM env var name
**Decision:** Standardised on `OLLAMA_BASE_URL` (matching `.env.example`).
**Reason:** `ceo_brain.py` previously read `OLLAMA_URL` — name mismatch caused
silent misconfiguration in new deployments.
**Fixed in:** `orchestration/ceo_bot/ceo_brain.py` (Step 7 of V2 hardening).

---

## 4. Known Deviations

| Deviation | Status | Tracking |
|---|---|---|
| `OLLAMA_URL` vs `OLLAMA_BASE_URL` name mismatch | Fixed — V2 hardening Step 7 | ceo_brain.py:65 |
| `B2_RECEIVER_URL` missing from env template | Fixed — V2 hardening Step 8 | .env.example |
| `tests/unit/` directory missing | Fixed — V2 hardening Step 9 | tests/unit/ |
| `scripts/run_a1_a6_golden.py` historical name | Documented — name misleading but functional | MANIFEST.md |
