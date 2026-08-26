# ThoughtGarden

ThoughtGarden is a persistent dialectical reasoning environment designed to help a user examine, challenge, and evolve philosophical beliefs through bounded deliberation between contrasting intellectual frameworks.

## V2: Praxis

Praxis is the collective reasoning construct formed by three governed minds:

- **Platonic** — asks what a claim means, what must be true of it, and whether it is coherent.
- **Nietzschean** — interrogates perspective, genealogy, values, and hidden assumptions.
- **Faustian** — tests what follows when an idea is pursued, lived, or acted upon.

The orchestrator governs procedure; it is not a fourth philosopher and does not select a philosophically preferred answer.

A completed deliberation attempts to return:

1. **Consensus Core**
2. **Remaining Tensions**
3. **Critical Question**

See `docs/praxis/construct.md` for the constitutional contract.

## Current build status

`build/tg-v2-refoundation` is the clean V2 backend foundation. It deliberately does **not** yet call an LLM/SLM, perform retrieval, or persist semantic memory. The first goal is to prove the construct independently of model competence.

## Local setup

From the repository root on Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m uvicorn app.main:app --reload --port 8000
```

Then open the FastAPI docs at `/docs` and check `GET /api/health`.

## Historical V1

The original V1 implementation remains preserved in Git history and on `main`. V2 intentionally removes the pseudo-learning/MCTS/reward-model stack from the active critical path rather than attempting to repair it in place.
