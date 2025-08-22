# file: backend/app/services/analysis_service.py (Updated with Timeouts)
from typing import List, Dict, Any
from app.schemas.schemas import ReasoningGraph, Node
import logging
from ollama import AsyncClient
import json
import asyncio

logger = logging.getLogger("tes_backend")
OLLAMA_CLIENT = AsyncClient()
OLLAMA_MODEL = "praxis-v1" 

# Define a reasonable timeout for LLM calls
LLM_TIMEOUT = 60.0  # 60 seconds

# --- Core Analysis Functions ---

def calculate_engagement_score(user_node: Node) -> float:
    """Calculates a simple engagement score based on response length."""
    if not user_node or not user_node.content:
        return 0.0
    score = min(len(user_node.content) / 250.0, 1.0)
    return score

async def generate_experiment_summary(graph: ReasoningGraph) -> Dict[str, Any]:
    """Uses the LLM to generate a semantic summary and keywords for an experiment."""
    full_history = "\n".join([f"[{n.type.upper()}]: {n.content}" for n in graph.nodes])
    
    summary_prompt = f"""
    You are an analyst. Your task is to read the full transcript of a thought experiment and generate a concise, high-level summary. The summary should capture the initial premise, the key ideas explored, and the final state or conclusion.

    ### EXPERIMENT TRANSCRIPT
    {full_history}

    ### YOUR TASK
    Generate a concise summary (1-2 paragraphs) of the experiment.
    """
    try:
        # Generate summary with timeout
        summary_task = OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=summary_prompt)
        response = await asyncio.wait_for(summary_task, timeout=LLM_TIMEOUT)
        summary_text = response.get('response', 'Summary generation timed out.')

        keywords_prompt = f"""
        You are an analyst. Your task is to read the following summary and extract 5-7 key keywords that describe the main topics.

        ### SUMMARY
        {summary_text}

        ### YOUR TASK
        Generate a JSON list of these keywords.
        """
        # Generate keywords with timeout
        keywords_task = OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=keywords_prompt, format="json")
        keywords_response = await asyncio.wait_for(keywords_task, timeout=LLM_TIMEOUT)
        keywords = json.loads(keywords_response['response'])
        
        return {"summary_text": summary_text, "keywords": keywords}
        
    except asyncio.TimeoutError:
        logger.error("LLM call timed out during experiment summary generation.")
        return {"summary_text": "Failed to generate summary due to timeout.", "keywords": ["error", "timeout"]}
    except Exception as e:
        logger.error(f"Failed to generate experiment summary or keywords: {e}")
        return {"summary_text": "Failed to generate summary.", "keywords": ["error"]}

def analyze_experiment_outcome(graph: ReasoningGraph) -> Dict[str, Any]:
    """
    Analyzes a completed thought experiment to correlate strategies with outcomes.
    """
    logger.info("ANALYSIS SERVICE: Beginning post-experiment analysis with real logic.")
    
    total_engagement = 0
    turn_count = 0
    strategy_performance: Dict[str, List[float]] = {}

    for i, current_node in enumerate(graph.nodes):
        if current_node.type == 'ai_expansion' and (i + 1) < len(graph.nodes):
            next_node = graph.nodes[i+1]
            if next_node.type == 'user_input':
                strategy_used = current_node.metadata.winning_strategy
                engagement_score = calculate_engagement_score(next_node)
                
                if strategy_used:
                    if strategy_used not in strategy_performance:
                        strategy_performance[strategy_used] = []
                    strategy_performance[strategy_used].append(engagement_score)
                
                total_engagement += engagement_score
                turn_count += 1

    final_strategy_scores = {
        strategy: sum(scores) / len(scores) if scores else 0
        for strategy, scores in strategy_performance.items()
    }

    average_engagement = total_engagement / turn_count if turn_count > 0 else 0

    analysis_summary = {
        "average_engagement": round(average_engagement, 2),
        "total_turns": turn_count,
        "strategy_performance": final_strategy_scores
    }

    logger.info(f"ANALYSIS SERVICE: Post-experiment analysis complete. Results: {analysis_summary}")
    
    return analysis_summary