# file: backend/app/services/analysis_service.py (Updated)
from typing import List, Dict, Any
from app.schemas.schemas import ReasoningGraph, Node
import logging
from ollama import AsyncClient
import json

logger = logging.getLogger("tes_backend")
OLLAMA_CLIENT = AsyncClient()
OLLAMA_MODEL = "praxis-v1" 

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

    ### RULES
    1. The output must be valid JSON with a 'summary' key and a 'keywords' key.
    2. The 'summary' value should be a single paragraph of text.
    3. The 'keywords' value must be a list of 5 to 10 relevant terms.
    4. The summary MUST NOT contain conversational filler or preambles.
    5. Be succinct and focused.

    ### TRANSCRIPT
    {full_history}

    ### RESPONSE FORMAT
    ```json
    {{
        "summary": "...",
        "keywords": ["...", "..."]
    }}
    ```
    """
    
    logger.info("ANALYSIS SERVICE: Generating experiment summary with LLM...")

    try:
        response = await OLLAMA_CLIENT.generate(
            model=OLLAMA_MODEL,
            prompt=summary_prompt,
            format="json"
        )
        summary_response = json.loads(response['response'])
        logger.info("ANALYSIS SERVICE: Summary generated successfully.")
        return summary_response
    except Exception as e:
        logger.error(f"Failed to generate summary with LLM: {e}")
        return {"summary": "Summary generation failed.", "keywords": []}


def analyze_experiment_outcome(graph: ReasoningGraph) -> Dict[str, Any]:
    """Analyzes the outcome of an experiment based on user engagement."""
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

    logger.info(f"ANALYSIS SERVICE: Analysis complete. Results: {analysis_summary}")
    return analysis_summary