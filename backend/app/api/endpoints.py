# file: app/api/endpoints.py (Corrected for Reasoning Graph)
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
from app.services import llm_service

router = APIRouter()
logger = logging.getLogger("tes_backend")

OLLAMA_CLIENT = AsyncClient()
OLLAMA_MODEL = "gemma:2b"

async def collect_ollama_stream(prompt: str) -> str:
    """Helper function to call the Ollama API and collect the full streaming response."""
    try:
        stream = await OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=prompt, stream=True)
        return "".join([chunk["response"] async for chunk in stream])
    except Exception as e:
        logger.error(f"Ollama stream collection failed: {e}")
        return f"Error generating response: {str(e)}"

# --- API Endpoints ---

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
    Stream the conversation advancement process to the frontend based on the new graph logic.
    """
    return StreamingResponse(
        stream_response_generator(experiment_id, user_input, db),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# --- Core Logic Functions ---

async def stream_response_generator(
    experiment_id: int,
    user_input: api_schemas.UserInput,
    db: AsyncSession
) -> AsyncGenerator[str, None]:
    try:
        db_experiment = await crud.get_experiment(db, experiment_id)
        if not db_experiment:
            yield json.dumps({"event": "error", "data": "Experiment not found"}) + "\n"
            return
        
        current_data = api_schemas.ExperimentData(**db_experiment.data)
        current_graph = current_data.graph
        
        # Create a new user node for the current input
        user_node = api_schemas.Node(
            id=str(uuid.uuid4()),
            type="user_input",
            content=user_input.message,
            metadata=api_schemas.NodeMetadata(depth=len(current_graph.nodes), timestamp=datetime.utcnow().isoformat())
        )
        current_graph.nodes.append(user_node)
        
        # Here we hardcode the `ai_expansion` for simplicity as per the MVP plan
        next_node_type = "ai_expansion"
        
        # Use LLM Service to generate the content for the new node
        prompt = llm_service.get_master_prompt_for_node(
            graph=current_graph,
            node_type=next_node_type
        )
        
        full_content = ""
        try:
            stream = await OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=prompt, stream=True)
            async for chunk in stream:
                chunk_text = chunk["response"]
                full_content += chunk_text
                # Stream the content back to the frontend
                yield json.dumps({"event": "stream_chunk", "data": chunk_text}) + "\n"
        except Exception as e:
            logger.error(f"Node content streaming failed: {e}")
            full_content = "Internal processing encountered an issue."
            yield json.dumps({"event": "stream_chunk", "data": full_content}) + "\n"
        
        # Create the new AI node and the connecting edge
        ai_node = api_schemas.Node(
            id=str(uuid.uuid4()),
            type=next_node_type,
            content=full_content.strip(),
            metadata=api_schemas.NodeMetadata(
                depth=len(current_graph.nodes),
                timestamp=datetime.utcnow().isoformat()
            )
        )
        edge = api_schemas.Edge(
            source=user_node.id,
            target=ai_node.id,
            relation="expands"
        )

        # Update the graph
        current_graph.nodes.append(ai_node)
        current_graph.edges.append(edge)
        
        # Save the updated graph to the database
        await crud.update_experiment_data(db=db, db_obj=db_experiment, data_in=current_data)
        logger.info(f"Successfully saved new nodes and edges for Experiment ID: {experiment_id}")
        
    except Exception as e:
        logger.error(f"Stream generation error: {e}")
        yield json.dumps({"event": "error", "data": f"Stream processing failed: {str(e)}"}) + "\n"