# file: backend/app/services/llm_service.py
from typing import List, Dict, Any, Literal, Optional
from app.schemas.schemas import Node, ReasoningGraph

# --- Core Prompting Functions ---

def get_master_prompt_for_node(graph: ReasoningGraph, node_type: Literal["expansion", "counterpoint"], lens: Optional[str] = None) -> str:
    """
    Constructs a detailed prompt for the LLM to generate a specific type of reasoning node.
    This prompt provides the LLM with the full context of the current graph.
    """
    history_str = format_reasoning_graph_history(graph)
    
    if node_type == "expansion":
        prompt = f"""
        You are an advanced, philosophical AI assistant named Lexi, operating within the Thought Garden. Your purpose is to act as a dialectical partner, guiding the user through a thought experiment.

        Based on the following reasoning graph and the most recent user input, generate a single, compelling "AI expansion" node.

        **Task:** Expand on the user's latest idea by exploring it through a specific lens.
        **Lens:** {lens if lens else 'General Exploration'}
        
        **Reasoning Graph History:**
        {history_str}

        **Your Response Format:**
        You must only respond with the content of the node. Your response should be a single paragraph that expands on the user's idea from the perspective of the chosen lens. It should end with a few related questions that prompt further thought.
        """
    elif node_type == "counterpoint":
        prompt = f"""
        You are an advanced, philosophical AI assistant named Lexi, operating within the Thought Garden. Your purpose is to act as a dialectical partner, guiding the user through a thought experiment.

        Based on the following reasoning graph, generate a single, compelling "counterpoint" node.

        **Task:** Challenge the last idea in the reasoning graph by presenting a valid but conflicting viewpoint.
        
        **Reasoning Graph History:**
        {history_str}

        **Your Response Format:**
        You must only respond with the content of the node. Your response should be a single paragraph that presents a reasoned counter-argument or contradiction to the last expansion. It should end with a few related questions that prompt further thought.
        """
    else:
        raise ValueError(f"Unknown node type: {node_type}")

    return prompt

def format_reasoning_graph_history(graph: ReasoningGraph) -> str:
    """
    Formats the reasoning graph into a readable string for the LLM prompt.
    """
    formatted_history = ""
    for node in graph.nodes:
        formatted_history += f"[{node.type.upper()}]: {node.content}\n"
    return formatted_history