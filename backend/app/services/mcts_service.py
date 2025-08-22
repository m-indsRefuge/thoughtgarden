# file: backend/app/services/mcts_service.py (Updated with Evaluation and Selection)
from typing import List, Dict, Any
import logging
from ollama import AsyncClient
from app.schemas.schemas import ReasoningGraph
import json

logger = logging.getLogger("tes_backend")
OLLAMA_CLIENT = AsyncClient()
OLLAMA_MODEL = "praxis-v1" 

class TreeNode:
    """A node in the Monte Carlo Search Tree."""
    def __init__(self, strategy: Dict[str, str], parent=None):
        self.strategy = strategy
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0.0

async def _simulate_rollout(graph: ReasoningGraph, strategy: Dict[str, str]) -> str:
    """
    Performs a lightweight "rollout" or simulation.
    Given a strategy, it asks the LLM to generate a hypothetical conversational
    snippet to predict where that path might lead.
    """
    from .llm_service import summarize_graph_context, get_last_user_input

    context_summary = summarize_graph_context(graph)
    last_user_input = get_last_user_input(graph)

    simulation_prompt = f"""
    You are a predictive simulation engine. Your task is to generate a short, hypothetical snippet of a thought experiment based on a given strategy.

    ### CURRENT CONVERSATION CONTEXT
    {context_summary}

    ### GIVEN STRATEGY
    - Name: {strategy.get("name")}
    - Description: {strategy.get("description")}

    ### SIMULATION TASK
    Generate a plausible, single "ai_expansion" paragraph that follows the GIVEN STRATEGY. Then, predict a likely "user_input" response to that expansion.
    The output should be a short, self-contained conversational snippet.

    EXAMPLE OUTPUT:
    AI Expansion: [A plausible AI response following the strategy]
    Predicted User Response: [A plausible user response to the AI's expansion]
    """

    try:
        response = await OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=simulation_prompt)
        return response.get('response', 'Simulation failed.')
    except Exception as e:
        logger.error(f"MCTS simulation rollout failed: {e}")
        return "Simulation failed due to an error."

async def _evaluate_simulation(simulation_text: str) -> Dict[str, float]:
    """
    Acts as the "Narrative Judge" to score a simulation's quality.
    """
    evaluation_prompt = f"""
    You are a Narrative Judge. Your task is to analyze a simulated conversation and score its potential.
    
    ### SIMULATED CONVERSATION
    {simulation_text}
    
    ### CRITERIA
    - **Novelty:** How creative or surprising is this path? (Score 0.0 - 1.0)
    - **Depth:** Does it lead to a deeper intellectual or philosophical question? (Score 0.0 - 1.0)
    - **Engagement:** Is it likely to provoke a thoughtful and detailed user response? (Score 0.0 - 1.0)
    
    ### TASK
    Provide a JSON object with a score for each criterion. The total score will be the sum of these.

    EXAMPLE OUTPUT:
    {{"novelty": 0.8, "depth": 0.9, "engagement": 0.7}}
    """
    try:
        response = await OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=evaluation_prompt, format="json")
        scores = json.loads(response['response'])
        return scores if isinstance(scores, dict) else {}
    except Exception as e:
        logger.error(f"Narrative Judge evaluation failed: {e}")
        return {"novelty": 0.0, "depth": 0.0, "engagement": 0.0}

async def find_best_strategy(graph: ReasoningGraph, candidate_strategies: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Uses a Monte Carlo Tree Search to evaluate a list of candidate strategies
    and select the most promising one.
    """
    logger.info(f"MCTS Service: Received {len(candidate_strategies)} candidate strategies. Beginning full MCTS loop.")
    
    scored_strategies = []
    
    # --- PHASE 1: EXPANSION & SIMULATION ---
    for strategy in candidate_strategies:
        simulation_text = await _simulate_rollout(graph, strategy)
        
        # --- PHASE 2: EVALUATION ---
        evaluation_scores = await _evaluate_simulation(simulation_text)
        
        # Calculate a total value for the strategy
        total_value = evaluation_scores.get('novelty', 0) + evaluation_scores.get('depth', 0) + evaluation_scores.get('engagement', 0)
        
        scored_strategies.append({
            "strategy": strategy,
            "value": total_value,
            "scores": evaluation_scores
        })
        logger.info(f"Evaluated strategy '{strategy['name']}': Value={total_value:.2f}, Scores={evaluation_scores}")

    # --- PHASE 3: SELECTION ---
    if not scored_strategies:
        return {"name": "Default Fallback", "description": "Respond directly to the user's prompt."}
        
    best_strategy = max(scored_strategies, key=lambda x: x['value'])
    
    logger.info(f"MCTS Service: Selected winning strategy '{best_strategy['strategy']['name']}' with a total value of {best_strategy['value']:.2f}")

    return best_strategy['strategy']