# file: backend/app/services/llm_service.py (Updated to produce AI response)
import json
from typing import List, Dict, Any
from app.schemas.schemas import Node, ReasoningGraph
from app.schemas.dsl import Strategy
import logging
from ollama import AsyncClient
import asyncio
from pydantic import ValidationError

# Import all our intelligence services
from app.services import creativity_service
from app.services import mcts_service
from app.services.memory_service import memory_service
from app.services.learning_loop import learning_loop

logger = logging.getLogger("tes_backend")
OLLAMA_CLIENT = AsyncClient()
OLLAMA_MODEL = "praxis-v1" 

async def generate_oracle_strategies(graph: ReasoningGraph, memories: List[Dict[str, Any]] = None) -> List[Strategy]:
    """The "Oracle": Generates a list of coherent, contextually relevant strategies in the DSL format."""
    context_summary = summarize_graph_context(graph)
    memory_str = "\n".join([f"- Past Insight: {m['document']}" for m in memories]) if memories else "None"
    
    strategist_prompt = f"""
    You are a Reasoning Strategist. Your task is to analyze a thought experiment's history and relevant memories to generate a list of 3 distinct, logical strategies to guide it forward. Each strategy must be a full, valid JSON object that strictly adheres to the provided Strategy DSL schema.

    ### RELEVANT PAST MEMORIES
    {memory_str}

    ### CURRENT CONVERSATION HISTORY
    {context_summary}

    ### STRATEGY DSL SCHEMA
    {{
        "id": "A unique identifier for the strategy (UUID).",
        "goal": "The high-level objective of the strategy.",
        "priority": "The priority of this strategy, from 0.0 (low) to 1.0 (high).",
        "constraints": "List of structured constraints. Each constraint is an object with 'type', 'value', 'unit', and 'description'.",
        "lenses": "List of perspectives or filters to apply.",
        "mutators": "List of algorithmic mutators to use.",
        "actions": "A sequence of actions to execute the strategy. Each action must have a 'type', 'step_description', and optional 'input_data'."
    }}

    ### YOUR TASK
    Based on the memories and the current history, generate a JSON array of 3 potential strategies. Ensure your output is ONLY the JSON array.
    """
    
    try:
        response = await OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=strategist_prompt, format="json")
        strategies_data = json.loads(response['response'])
        
        strategies = []
        for s_data in strategies_data:
            try:
                strategies.append(Strategy.model_validate(s_data))
            except ValidationError as ve:
                logger.error(f"Strategy validation failed: {ve}")
                continue
        return strategies
    except Exception as e:
        logger.error(f"Oracle strategy generation failed: {e}")
        return []

async def get_master_prompt_for_node(graph: ReasoningGraph) -> Dict[str, Any]:
    """Orchestrates the pipeline and returns both the prompt and the winning strategy."""
    last_user_input = get_last_user_input(graph)
    
    retrieved_memories = []
    if len(graph.nodes) <= 1:
        logger.info("First turn detected. Querying long-term memory.")
        retrieved_memories = memory_service.retrieve_similar_memories(query_text=last_user_input)
        if retrieved_memories:
            logger.info(f"Retrieved {len(retrieved_memories)} similar memories from the past.")

    oracle_strategies = await generate_oracle_strategies(graph, retrieved_memories)
    # Correctly call the new function name from the creativity_service
    creator_strategy = creativity_service.generate_hybrid_strategy(context=last_user_input)
    candidate_strategies = oracle_strategies + [creator_strategy]
    
    best_strategy = await mcts_service.find_best_strategy(graph, candidate_strategies)
    
    # --- Integration with Learning Loop ---
    await learning_loop.collect_experience(graph, candidate_strategies)
    await learning_loop.train_if_ready()
    # --- End of Integration ---

    context_summary = summarize_graph_context(graph, retrieved_memories)
    
    context_section = f"### CONTEXT\n{context_summary}"
    
    # Use the new structured strategy object to format the prompt
    task_description = (
        "Your task is to advance a thought experiment by generating a compelling \"ai_expansion\" node.\n\n"
        f'The user has just stated: "{last_user_input}"\n\n'
        "To do this, you must adopt the following dynamically selected reasoning strategy:\n"
        f'**Strategy Goal:** {best_strategy.goal}\n'
        f'**Strategy Constraints:** {", ".join([c.description for c in best_strategy.constraints])}\n'
        f'**Strategy Lenses:** {", ".join(best_strategy.lenses)}\n'
        f'**Actions:**\n' + "\n".join([f' - {action.step_description}' for action in best_strategy.actions]) + "\n\n"
        "Your response must synthesize this strategy into a cohesive narrative. Conclude with a clear, open-ended question."
    )

    task_section = f"### TASK\n{task_description}"

    final_prompt = "\n\n".join([context_section, task_section])
    
    logger.info(f"--- MCTS-SELECTED PROMPT --- \nWINNING STRATEGY: {best_strategy.goal}\n---\n{final_prompt}\n--- END OF PROMPT ---")
    
    # Send the final prompt to the LLM to get the response
    try:
        final_response = await OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=final_prompt)
        return {
            "prompt": final_prompt,
            "winning_strategy": best_strategy.goal,
            "response": final_response.get("response", "")
        }
    except Exception as e:
        logger.error(f"Final response generation failed: {e}")
        return {
            "prompt": final_prompt,
            "winning_strategy": best_strategy.goal,
            "response": "An internal error occurred."
        }


def summarize_graph_context(graph: ReasoningGraph, memories: List[Dict[str, Any]] = None) -> str:
    summary = ""
    if memories:
        summary += "Based on a review of relevant past experiments, the following insights were retrieved:\n"
        for mem in memories:
            summary += f"- Past Insight: {mem['document']}\n"
        summary += "\n---\n\n"
        
    if not graph.nodes:
        summary += "The current experiment has just begun."
        return summary

    seed_node = ""
    for node in graph.nodes:
        if node.type == 'user_input':
            seed_node = node.content
            break
    if not seed_node:
        summary += "The user has started a new session but has not provided a premise."
        return summary

    recent_nodes = graph.nodes[-4:]
    summary += f"- The initial premise of the current experiment is: '{seed_node}'\n"
    if len(recent_nodes) > 1:
        summary += "- The most recent turns in the current conversation are:\n"
        for node in recent_nodes:
            content_str = str(node.content) if node.content is not None else ""
            summary += f"  - [{node.type.upper()}]: {content_str.strip()}\n"
    return summary.strip()

def get_last_user_input(graph: ReasoningGraph) -> str:
    for node in reversed(graph.nodes):
        if node.type == 'user_input':
            return str(node.content) if node.content is not None else ""
    return "[No user input found]"