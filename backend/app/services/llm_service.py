# file: backend/app/services/llm_service.py (Corrected for MCTS Architecture)
import json
from typing import List, Dict, Any
from app.schemas.schemas import Node, ReasoningGraph
import logging
from ollama import AsyncClient

# Import all our intelligence services
from app.services import creativity_service
from app.services import mcts_service
from app.services.memory_service import memory_service

logger = logging.getLogger("tes_backend")
OLLAMA_CLIENT = AsyncClient()
OLLAMA_MODEL = "praxis-v1" 

async def generate_oracle_strategies(graph: ReasoningGraph, memories: List[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    """The "Oracle": Generates a list of coherent, contextually relevant strategies."""
    context_summary = summarize_graph_context(graph)
    memory_str = "\n".join([f"- {m['document']}" for m in memories]) if memories else "None"
    
    strategist_prompt = f"""
    You are a Reasoning Strategist. Your task is to analyze a thought experiment's history and relevant memories to generate a list of 3 distinct, logical strategies to guide it forward.

    ### RELEVANT PAST MEMORIES
    {memory_str}

    ### CURRENT CONVERSATION HISTORY
    {context_summary}

    ### YOUR TASK
    Based on the memories and the current history, generate a JSON array of 3 potential strategies. Each strategy must be an object with two keys: "name" and "description".
    """
    try:
        response = await OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=strategist_prompt, format="json")
        strategies = json.loads(response['response'])
        return strategies if isinstance(strategies, list) else []
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
    creator_strategy = creativity_service.generate_wildcard_strategy()
    candidate_strategies = oracle_strategies + [creator_strategy]
    best_strategy = await mcts_service.find_best_strategy(graph, candidate_strategies)
    
    context_summary = summarize_graph_context(graph, retrieved_memories)
    
    context_section = f"### CONTEXT\n{context_summary}"
    
    task_description = (
        "Your task is to advance a thought experiment by generating a compelling \"ai_expansion\" node.\n\n"
        f'The user has just stated: "{last_user_input}"\n\n'
        "To do this, you must adopt the following dynamically selected reasoning strategy:\n"
        f'**Strategy Name:** {best_strategy.get("name", "N/A")}\n'
        f'**Strategy Description:** {best_strategy.get("description", "N/A")}\n\n'
        "Your response must synthesize this strategy into a cohesive narrative. Conclude with a clear, open-ended question."
    )

    task_section = f"### TASK\n{task_description}"

    final_prompt = "\n\n".join([context_section, task_section])
    
    logger.info(f"--- MCTS-SELECTED PROMPT --- \nWINNING STRATEGY: {best_strategy.get('name', 'N/A')}\n---\n{final_prompt}\n--- END OF PROMPT ---")
    
    return {
        "prompt": final_prompt,
        "winning_strategy": best_strategy.get("name", "Unknown")
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