# ThoughtGarden V2 Refoundation Design

## Product purpose

ThoughtGarden is a persistent dialectical reasoning environment designed to help a user examine, challenge, and evolve philosophical beliefs through bounded deliberation between contrasting intellectual frameworks.

Praxis is not a fourth philosopher. Praxis is the collective result of governed deliberation between exactly three initial minds: Platonic, Nietzschean, and Faustian.

The orchestrator governs procedure. It must not choose a philosophically preferred answer.

## User-facing Praxis response

Every completed deliberation attempts to produce:

1. **Consensus Core** — what all three perspectives can defend.
2. **Remaining Tensions** — qualifications, disagreement, and unresolved assumptions.
3. **Critical Question** — the strongest next question the user should confront.

Consensus must never be fabricated. If no complete candidate is unanimously ratifiable, the engine returns an unresolved outcome rather than manufacturing agreement.

## Initial bounded protocol

The initial engine uses five phases:

1. Independent Thesis
2. Challenge
3. Revision
4. Consensus Proposal
5. Ratification

Each phase requires one submission from each governed mind before the orchestrator advances. Duplicate or out-of-phase submissions are invalid.

## Constitutional rules

- Historical claims must be grounded in an approved corpus.
- Source-grounded claims and philosophical extrapolation must be distinguishable.
- Minds are governed reasoning lenses, not historical-person roleplay personas.
- The system must not request, persist, or expose hidden chain-of-thought.
- Observable reasoning is represented as claims, evidence references, objections, revisions, proposals, ratifications, and final outputs.
- Minds must represent opposing arguments charitably before criticism.
- Revision and concession are valid outcomes.
- Genuine disagreement is preserved.

## Backend architecture

The V2 backend is split into four boundaries:

### Praxis domain

Pure typed contracts, a deterministic five-phase state machine, and deterministic consensus resolution. It has no dependency on Ollama, Chroma, model weights, or HTTP.

### Model/corpus ports

Protocol interfaces define future mind-generation and corpus-retrieval adapters. No concrete model provider is part of the refoundation slice.

### Persistence

Async SQLite stores inquiries and serialized Praxis state. Persistence does not decide reasoning policy.

### API

FastAPI exposes health, inquiry creation/retrieval, and submission recording. It is a thin transport layer over the domain and persistence boundaries.

## Persistence model

An Inquiry contains:

- id
- title
- user question
- created/updated timestamps
- serialized DeliberationState

A DeliberationState contains the current phase, all structured submissions, completion state, and optional Praxis response.

## Consensus procedure

In the consensus-proposal phase each mind proposes one complete candidate Praxis response.

In ratification each mind evaluates all three candidates using categorical decisions:

- ratify
- ratify_with_reservation
- reject

A candidate is unanimously admissible when no mind rejects it. If multiple candidates are unanimously admissible, the orchestrator may apply a deterministic procedural tie-break among already-admissible candidates; this is not a philosophical score or winner model.

If no candidate is unanimously admissible, the engine returns an unresolved response with no fabricated Consensus Core and a meta-level Critical Question directing the user toward the unresolved tension.

## Explicit removals from the V2 critical path

The following V1 mechanisms are removed rather than repaired:

- MCTS selector
- reward neural network
- planning neural network
- random reward learning loop
- trainer/checkpoint machinery
- randomized strategy scoring as a reasoning authority
- global Chroma initialization
- monolithic llm_service orchestration
- single Praxis Modelfile persona
- committed generated Chroma database
- backup model files and stale debug/test artifacts

The ideas of memory, creativity, and reasoning graphs may return later behind explicit interfaces and evidence-backed acceptance criteria.

## Frontend boundary

The active React/Tauri application is not redesigned in this pass. Obvious backup/generated/empty files may be removed, but active UI code remains intact. The API transport continues to use port 8000 and `/api` as the future integration seam.

## Verification

The first local gate after sync is:

```powershell
cd backend
python -m pytest -q
```

Then:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

No runtime-green claim is made until these commands are executed locally.
