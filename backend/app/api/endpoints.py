# file: app/api/endpoints.py (Fixed Version)
import asyncio
import json
import re
from typing import List, Dict, Any, AsyncGenerator
import logging
import random

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from ollama import AsyncClient

from app.core.database import get_session
from app.crud import crud
from app.schemas import schemas as api_schemas
from app.models import Experiment
from app.services import llm_service
from app.services.analysis_service import analyze_user_input 
from app.core import content

router = APIRouter()
logger = logging.getLogger("tes_backend")

OLLAMA_CLIENT = AsyncClient()
OLLAMA_MODEL = "gemma:2b"

async def collect_ollama_stream(prompt: str) -> str:
    try:
        stream = await OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=prompt, stream=True)
        return "".join([chunk["response"] async for chunk in stream])
    except Exception as e:
        logger.error(f"Ollama stream collection failed: {e}")
        return f"Error generating response: {str(e)}"

@router.post("/experiments/", response_model=Experiment)
async def create_experiment(*,db: AsyncSession = Depends(get_session),experiment_in: api_schemas.ExperimentCreate,):
    return await crud.create_experiment(db=db, experiment_in=experiment_in)

@router.get("/experiments/", response_model=List[Experiment])
async def get_all_experiments(db: AsyncSession = Depends(get_session)):
    return await crud.get_all_experiments(db=db)

@router.get("/experiments/{experiment_id}", response_model=Experiment)
async def get_experiment_details(experiment_id: int, db: AsyncSession = Depends(get_session)):
    experiment = await crud.get_experiment(db, experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment

@router.post("/journeys/{journey_name}/start", response_model=api_schemas.JourneymanTurn)
async def start_journeyman_journey(journey_name: str,db: AsyncSession = Depends(get_session)):
    if journey_name not in content.JOURNEYS:
        raise HTTPException(status_code=404, detail="Journey not found")
    journey = content.JOURNEYS[journey_name]
    persona_options = ", ".join(content.PERSONAS.keys())
    prompt = f"Given a thought experiment titled '{journey['title']}', which persona would be a better guide: {persona_options}? Respond with only the persona's ID."
    locked_in_persona = (await collect_ollama_stream(prompt)).strip()
    if locked_in_persona not in content.PERSONAS:
        locked_in_persona = "guide_philosopher"
    logger.info(f"Locked in persona '{locked_in_persona}' for journey '{journey_name}'")
    initial_state = api_schemas.JourneymanState(journey_id=journey_name, locked_in_persona=locked_in_persona, current_step=0)
    db_experiment = Experiment(title=journey['title'], data=initial_state.model_dump())
    db.add(db_experiment)
    await db.commit()
    await db.refresh(db_experiment)
    script = journey["script"][locked_in_persona]
    return api_schemas.JourneymanTurn(narrative=script[0], is_complete=False, experiment_id=db_experiment.id)

@router.get("/journeys/{experiment_id}/next", response_model=api_schemas.JourneymanTurn)
async def next_journeyman_step(experiment_id: int,db: AsyncSession = Depends(get_session)):
    db_experiment = await crud.get_experiment(db, experiment_id)
    if not db_experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    state = api_schemas.JourneymanState(**db_experiment.data)
    state.current_step += 1
    journey = content.JOURNEYS[state.journey_id]
    script = journey["script"][state.locked_in_persona]
    is_complete = state.current_step >= len(script) - 1
    step_index = min(state.current_step, len(script) - 1)
    narrative = script[step_index]
    await crud.update_experiment_data(db=db, db_obj=db_experiment, data_in=state)
    return api_schemas.JourneymanTurn(narrative=narrative, is_complete=is_complete, experiment_id=experiment_id)

def run_cam(analysis: Dict[str, Any]) -> Dict[str, Any]:
    persona_scores = {"Visionary Optimist": 0.0, "Critical Risk Analyst": 0.0, "Pragmatic Engineer": 0.0}
    all_cues = analysis.get("keywords", []) + analysis.get("reasoning_cues", [])
    for cue in all_cues:
        if cue in content.KEYWORD_AFFINITIES:
            for persona, score in content.KEYWORD_AFFINITIES[cue].items():
                if persona in persona_scores: persona_scores[persona] += score
    sentiment = analysis.get("sentiment")
    if sentiment == "Positive": persona_scores["Visionary Optimist"] += 30
    elif sentiment == "Negative": persona_scores["Critical Risk Analyst"] += 30
    else: persona_scores["Pragmatic Engineer"] += 15
    complexity = analysis.get("complexity_score", 0)
    if complexity > 0.6:
        persona_scores["Critical Risk Analyst"] += 25
        persona_scores["Pragmatic Engineer"] += 10
    elif complexity > 0.3: persona_scores["Pragmatic Engineer"] += 15
    for p in persona_scores: persona_scores[p] += random.uniform(0, 5)
    winner = max(persona_scores, key=persona_scores.get)
    
    # Fix: Create debate arguments with correct structure matching frontend expectations
    debate_results = [
        api_schemas.DebateArgument(
            persona=p, 
            argument=f"From a {p.lower()} perspective: {generate_argument_for_persona(p)}", 
            score=round(s)
        ) 
        for p, s in persona_scores.items()
    ]
    debate_results.sort(key=lambda x: x.score, reverse=True)
    return {"winner": winner, "debate": debate_results}

def generate_argument_for_persona(persona: str) -> str:
    """Generate appropriate arguments for each persona type"""
    arguments = {
        "Visionary Optimist": [
            "This opens up exciting possibilities for emergent intelligence and creativity.",
            "We should embrace the transformative potential of this approach.",
            "The innovative aspects could lead to breakthrough discoveries.",
        ],
        "Critical Risk Analyst": [
            "We must carefully consider potential failure modes and edge cases.",
            "The computational complexity and resource requirements need thorough analysis.",
            "Risk mitigation strategies should be prioritized from the outset.",
        ],
        "Pragmatic Engineer": [
            "Let's focus on building a minimal viable implementation first.",
            "We need clear metrics and testable milestones for this approach.",
            "The practical constraints and real-world applicability are key factors.",
        ]
    }
    return random.choice(arguments.get(persona, ["This requires careful consideration."]))

async def stream_response_generator(experiment_id: int, user_input: api_schemas.UserInput, db: AsyncSession) -> AsyncGenerator[str, None]:
    try:
        db_experiment = await crud.get_experiment(db, experiment_id)
        if not db_experiment: 
            yield json.dumps({"event": "error", "data": "Experiment not found"}) + "\n"
            return 
        
        # Initialize conversation data if it doesn't exist
        conversation_data = db_experiment.data if db_experiment.data else {"history": []}
        conversation = api_schemas.ConversationData(**conversation_data)
        
        analysis = analyze_user_input(user_input.message)
        cam_result = run_cam(analysis)
        winning_persona = cam_result["winner"]
        debate_arguments = cam_result["debate"]
        
        logger.info(f"CAM Winner: {winning_persona}")
        
        # Send debate results immediately
        yield json.dumps({
            "event": "debate_complete", 
            "data": [arg.model_dump() for arg in debate_arguments]
        }) + "\n"
        
        logger.info("Streaming monologue...")
        monologue_prompt = llm_service.get_monologue_prompt_for_turn(
            conversation.history, 
            user_input.message, 
            winning_persona
        )
        
        full_monologue = ""
        try:
            async for chunk in await OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=monologue_prompt, stream=True):
                chunk_text = chunk["response"]
                full_monologue += chunk_text
                yield json.dumps({"event": "monologue_chunk", "data": chunk_text}) + "\n"
        except Exception as e:
            logger.error(f"Monologue streaming failed: {e}")
            full_monologue = "Internal processing encountered an issue..."
            yield json.dumps({"event": "monologue_chunk", "data": full_monologue}) + "\n"
        
        logger.info("Generating final question with multi-layer prompt...")
        question_prompt = llm_service.get_final_response_prompt(
            conversation.history, 
            full_monologue, 
            winning_persona
        )
        
        try:
            final_question = await collect_ollama_stream(question_prompt)
        except Exception as e:
            logger.error(f"Final question generation failed: {e}")
            final_question = "What aspect of this topic would you like to explore further?"
        
        yield json.dumps({"event": "question_complete", "data": final_question.strip()}) + "\n"

        logger.info("Saving full turn to database...")
        new_turn = api_schemas.Turn(
            turn_number=len(conversation.history) + 1,
            user_message=user_input.message,
            debate=debate_arguments,
            internal_monologue=full_monologue.strip(),
            ai_question_to_user=final_question.strip(),
        )
        conversation.history.append(new_turn)
        await crud.update_experiment_data(db=db, db_obj=db_experiment, data_in=conversation)
        logger.info(f"Successfully saved turn {new_turn.turn_number} for Experiment ID: {experiment_id}")
        
    except Exception as e:
        logger.error(f"Stream generation error: {e}")
        yield json.dumps({"event": "error", "data": f"Stream processing failed: {str(e)}"}) + "\n"

@router.post("/experiments/{experiment_id}/advance")
async def advance_conversation_streaming(
    experiment_id: int, 
    *, 
    user_input: api_schemas.UserInput, 
    db: AsyncSession = Depends(get_session)
):
    """
    Stream the conversation advancement process to the frontend
    """
    return StreamingResponse(
        stream_response_generator(experiment_id, user_input, db), 
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )