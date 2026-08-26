# ThoughtGarden V2 Refoundation Implementation Plan

**Goal:** Replace the speculative V1 reasoning stack with a small, governed, testable Praxis domain while preserving the repository history and active frontend shell.

**Architecture:** A pure Pydantic Praxis domain owns contracts, five-phase deliberation, and consensus. FastAPI and SQLite sit outside the domain. Future SLM and corpus integrations attach through protocols rather than being embedded in orchestration.

**Tech Stack:** Python 3.12+, Pydantic 2, FastAPI, SQLModel/SQLAlchemy async SQLite, pytest.

**Spec:** `docs/superpowers/specs/2026-08-26-thoughtgarden-v2-refoundation-design.md`

## Global Constraints

- Work only on `build/tg-v2-refoundation`; preserve `main`.
- Exactly three governed minds: Platonic, Nietzschean, Faustian.
- Exactly five bounded deliberation phases.
- Orchestrator governs procedure, not philosophical preference.
- Consensus is ratification-based, never numeric model scoring.
- No LLM/SLM calls, RAG, Chroma, fine-tuning, MCTS, reward model, or trainer in this slice.
- Preserve active React/Tauri source for a later UI integration slice.

### Task 1: Define RED domain tests

Create focused tests for contracts, phase progression, invalid submissions, consensus ratification, and soul-document presence. The tests intentionally fail until `app.praxis` exists.

### Task 2: Replace backend dependency surface

Reduce `backend/requirements.txt` to the dependencies required by the deterministic V2 backend and tests. Remove generated Chroma state and speculative ML/model dependencies.

### Task 3: Implement Praxis contracts

Create typed enums and phase-specific submissions. Define `DeliberationState`, `PraxisResponse`, and ratification ballot models.

### Task 4: Implement deterministic state machine

Record exactly one submission per mind per phase. Reject duplicates and out-of-phase submissions. Advance only after all three governed minds submit. Mark complete after ratification.

### Task 5: Implement consensus resolver

Accept only candidates with no rejection. Preserve reservations as tensions. Return an unresolved response if no candidate is unanimously admissible.

### Task 6: Add constitutional soul documents

Add construct documentation plus Platonic, Nietzschean, and Faustian `soul.md` contracts defining reasoning obligations and prohibiting historical-person impersonation.

### Task 7: Rebuild persistence and API shell

Replace V1 experiment CRUD with Inquiry persistence. Add health, create inquiry, get inquiry, list inquiries, and submit phase endpoints under `/api`.

### Task 8: Repository cleanup

Delete V1 MCTS, reward/planning/learning/trainer, Chroma memory implementation and data, stale model backups, old Modelfile, debug artifacts, and obvious frontend backup/generated/empty files.

### Task 9: Local verification after sync

Run from `backend`:

```powershell
python -m pytest -q
python -m uvicorn app.main:app --reload --port 8000
```

Then inspect `/api/health` and create an inquiry through the OpenAPI docs or curl. Do not call the branch runtime verified until these gates pass locally.
