# file: app/api/endpoints.py
import asyncio
import json
import re
from typing import List, AsyncGenerator
import logging

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from ollama import AsyncClient

from app.core.database import get_session
from app.crud import crud
from app.schemas import schemas as api_schemas
from app.models import Experiment
from app.services import llm_service

router = APIRouter()
logger = logging.getLogger("tes_backend")

# --- Globals ---
OLLAMA_CLIENT = AsyncClient()
OLLAMA_MODEL = "gemma:2b"

async def collect_ollama_stream(prompt: str) -> str:
    """Helper function to call the Ollama API and collect the full streaming response."""
    stream = await OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=prompt, stream=True)
    return "".join([chunk["response"] async for chunk in stream])

@router.post("/experiments/", response_model=Experiment)
async def create_experiment(
    *,
    db: AsyncSession = Depends(get_session),
    experiment_in: api_schemas.ExperimentCreate,
):
    """Creates a new, empty thought experiment."""
    return await crud.create_experiment(db=db, experiment_in=experiment_in)

@router.get("/experiments/", response_model=List[Experiment])
async def get_all_experiments(db: AsyncSession = Depends(get_session)):
    """Retrieves a list of all thought experiments."""
    return await crud.get_all_experiments(db=db)

@router.get("/experiments/{experiment_id}", response_model=Experiment)
async def get_experiment_details(experiment_id: int, db: AsyncSession = Depends(get_session)):
    """Retrieves the full data for a single thought experiment."""
    experiment = await crud.get_experiment(db, experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment

async def run_simulation_generator(experiment_id: int, db: AsyncSession) -> AsyncGenerator[str, None]:
    """The core logic generator for running the simulation and streaming events."""
    logger.info(f"Starting Simulation for Experiment ID: {experiment_id}")
    db_experiment = await crud.get_experiment(db, experiment_id)
    if not db_experiment:
        yield json.dumps({"event": "error", "data": {"message": "Experiment not found."}}) + "\n"
        return
    
    experiment_data = api_schemas.ExperimentData(**db_experiment.data)
    
    try:
        # --- 1. Perspective Generation ---
        yield json.dumps({"event": "status", "data": {"message": "Generating perspectives..."}}) + "\n"
        prompt = llm_service.get_perspective_prompt(db_experiment.title, experiment_data.description)
        full_response = await collect_ollama_stream(prompt)
        
        perspectives_raw = []
        for line in full_response.strip().split('\n'):
            if ":" in line:
                parts = line.split(":", 1)
                perspectives_raw.append({"viewpoint_name": parts[0].strip(), "viewpoint_text": parts[1].strip()})
        
        if not perspectives_raw:
             raise ValueError("Failed to parse any perspectives from the LLM response.")

        for i, p_data in enumerate(perspectives_raw):
            p_obj = api_schemas.Perspective(id=i+1, **p_data)
            experiment_data.perspectives.append(p_obj)
            yield json.dumps({"event": "perspective_generated", "data": p_obj.model_dump()}) + "\n"
            await asyncio.sleep(0.1)

        # --- 2. Internal Debate Cycle ---
        yield json.dumps({"event": "status", "data": {"message": "Running internal debate..."}}) + "\n"
        for p1 in experiment_data.perspectives:
            for p2 in experiment_data.perspectives:
                if p1.id == p2.id: continue
                critique_response = await collect_ollama_stream(llm_service.get_debate_prompt(p1.viewpoint_name, p2.viewpoint_name, p2.viewpoint_text))
                
                critique_match = re.search(r"Critique:(.*?)(Question:|$)", critique_response, re.DOTALL)
                question_match = re.search(r"Question:(.*)", critique_response, re.DOTALL)
                critique = critique_match.group(1).strip() if critique_match else "Critique could not be parsed."
                question = question_match.group(1).strip() if question_match else "Question could not be parsed."

                response_text = await collect_ollama_stream(llm_service.get_response_prompt(p2.viewpoint_name, critique, question, p2.viewpoint_text))
                
                turn_obj = api_schemas.DebateTurn(
                    questioning_perspective_id=p1.id, critiqued_perspective_id=p2.id,
                    questioner_name=p1.viewpoint_name, critiqued_name=p2.viewpoint_name,
                    cross_question_text=critique, response_text=response_text
                )
                experiment_data.debate_turns.append(turn_obj)
                yield json.dumps({"event": "debate_turn", "data": turn_obj.model_dump()}) + "\n"
                await asyncio.sleep(0.1)

        # --- 3. Synthesis ---
        yield json.dumps({"event": "status", "data": {"message": "Generating synthesis..."}}) + "\n"
        prompt = llm_service.get_synthesis_prompt(db_experiment.title, experiment_data.description, experiment_data.perspectives, experiment_data.debate_turns)
        synthesis_text = await collect_ollama_stream(prompt)
        
        synthesis_obj = api_schemas.Synthesis(synthesis_text=synthesis_text)
        experiment_data.synthesis = synthesis_obj
        yield json.dumps({"event": "synthesis_generated", "data": synthesis_obj.model_dump()}) + "\n"

        # --- 4. Final Save ---
        yield json.dumps({"event": "status", "data": {"message": "Saving results..."}}) + "\n"
        await crud.update_experiment_data(db=db, db_obj=db_experiment, data_in=experiment_data)
        
        yield json.dumps({"event": "completion", "data": {"message": "Simulation complete."}}) + "\n"
        logger.info(f"Finished Simulation for Experiment ID: {experiment_id}")

    except Exception as e:
        logger.error(f"ERROR during simulation for Experiment ID {experiment_id}: {e}")
        yield json.dumps({"event": "error", "data": {"message": str(e)}}) + "\n"

@router.post("/experiments/{experiment_id}/run")
async def run_simulation(
    experiment_id: int, 
    db: AsyncSession = Depends(get_session)
):
    """Initiates the thought experiment simulation for a given experiment ID."""
    return StreamingResponse(run_simulation_generator(experiment_id, db), media_type="application/x-ndjson")