# file: backend/app/api/endpoints.py (Final Corrected Version to resolve AttributeError)
import asyncio
import json
import uuid
from typing import List, Dict, Any, AsyncGenerator
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from ollama import AsyncClient

from app.core.database import get_session
from app.crud import crud
from app.schemas import schemas as api_schemas
from app.models import Experiment
from app.services import llm_service, analysis_service
from app.services.memory_service import memory_service

router = APIRouter()
logger = logging.getLogger("tes_backend")

OLLAMA_CLIENT = AsyncClient()
OLLAMA_MODEL = "praxis-v1" 

@router.post("/experiments/", response_model=Experiment)
async def create_experiment(
    *,
    db: AsyncSession = Depends(get_session),
    experiment_in: api_schemas.ExperimentCreate,
):
    """Creates a new experiment with an initial user input node."""
    return await crud.create_experiment(db=db, experiment_in=experiment_in)

@router.get("/experiments/{experiment_id}", response_model=Experiment)
async def get_experiment_details(experiment_id: int, db: AsyncSession = Depends(get_session)):
    """Retrieves the full data for a single thought experiment."""
    experiment = await crud.get_experiment(db, experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment

@router.post("/experiments/{experiment_id}/advance")
async def advance_conversation_streaming(
    experiment_id: int,
    *,
    user_input: api_schemas.UserInput,
    db: AsyncSession = Depends(get_session)
):
    """
    Stream the conversation advancement process.
    """
    async def stream_response_generator() -> AsyncGenerator[str, None]:
        try:
            db_experiment = await crud.get_experiment(db, experiment_id)
            if not db_experiment:
                yield json.dumps({"event": "error", "data": "Experiment not found"}) + "\n"
                return
            
            current_data = api_schemas.ExperimentData(**db_experiment.data)
            current_graph = current_data.graph
            
            user_node = api_schemas.Node(
                id=str(uuid.uuid4()),
                type="user_input",
                content=user_input.message,
                metadata=api_schemas.NodeMetadata(depth=len(current_graph.nodes), timestamp=datetime.utcnow().isoformat())
            )
            current_graph.nodes.append(user_node)
            
            prompt_data = await llm_service.get_master_prompt_for_node(
                graph=current_graph
            )
            prompt = prompt_data["prompt"]
            winning_strategy = prompt_data["winning_strategy"]
            
            full_content = ""
            try:
                stream = await OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=prompt, stream=True)
                async for chunk in stream:
                    chunk_text = chunk["response"]
                    full_content += chunk_text
                    yield json.dumps({"event": "stream_chunk", "data": chunk_text}) + "\n"
            except Exception as e:
                logger.error(f"Node content streaming failed: {e}")
                full_content = "Internal processing encountered an issue."
                yield json.dumps({"event": "stream_chunk", "data": full_content}) + "\n"
            
            ai_node = api_schemas.Node(
                id=str(uuid.uuid4()),
                type="ai_expansion",
                content=full_content.strip(),
                metadata=api_schemas.NodeMetadata(
                    depth=len(current_graph.nodes),
                    timestamp=datetime.utcnow().isoformat(),
                    winning_strategy=winning_strategy
                )
            )
            edge = api_schemas.Edge(
                source=user_node.id,
                target=ai_node.id,
                relation="expands"
            )

            current_graph.nodes.append(ai_node)
            current_graph.edges.append(edge)
            
            await crud.update_experiment_data(db=db, db_obj=db_experiment, data_in=current_data)
            logger.info(f"Successfully saved new nodes and edges for Experiment ID: {experiment_id}")
            
        except Exception as e:
            logger.error(f"Stream generation error: {e}")
            yield json.dumps({"event": "error", "data": f"Stream processing failed: {str(e)}"}) + "\n"

    return StreamingResponse(
        stream_response_generator(),
        media_type="application/x-ndjson"
    )

@router.post("/experiments/{experiment_id}/conclude", status_code=202)
async def conclude_experiment(
    experiment_id: int,
    db: AsyncSession = Depends(get_session)
):
    """
    Concludes an experiment, triggering analysis and storage in long-term memory.
    """
    logger.info(f"Received request to conclude experiment ID: {experiment_id}")
    db_experiment = await crud.get_experiment(db, experiment_id)
    if not db_experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    graph = api_schemas.ReasoningGraph(**db_experiment.data['graph'])
    
    analysis_results = analysis_service.analyze_experiment_outcome(graph)
    summary_data = await analysis_service.generate_experiment_summary(graph)

    full_metadata = {
        **analysis_results,
        "keywords": summary_data.get("keywords", [])
    }

    memory_service.store_experiment_summary(
        experiment_id=str(experiment_id),
        summary_text=summary_data.get("summary_text", "No summary generated."),
        metadata=full_metadata
    )

    return {"message": "Experiment analysis and memory storage initiated."}