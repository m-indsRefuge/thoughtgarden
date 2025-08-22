# file: backend/app/services/mcts_service.py (Refactored for Neural-Assisted MCTS)
import math
import random
from typing import List, Dict, Any
import logging
import asyncio

from app.schemas.schemas import ReasoningGraph, Node
from app.schemas.dsl import Strategy, Action
from app.services.reward_model import score_strategy
from ollama import AsyncClient
from app.schemas.dsl import Strategy, Action, Constraint, Mutator
from app.schemas.schemas import ReasoningGraph, Node, NodeMetadata, NodeType, Edge, EdgeRelation

logger = logging.getLogger("tes_backend")
OLLAMA_CLIENT = AsyncClient()
OLLAMA_MODEL = "praxis-v1"

# --- MCTS Node and Core Logic ---
class TreeNode:
    """A node in the Monte Carlo Search Tree."""
    def __init__(self, strategy: Strategy, parent: 'TreeNode' = None, state: Any = None):
        self.strategy = strategy
        self.parent = parent
        self.children: Dict[str, 'TreeNode'] = {}
        self.visits = 0
        self.value = 0.0
        self.state = state
        self.is_terminal = False

async def simulate_action(state: Dict[str, Any], action: Action) -> str:
    """
    Simulates a single, lightweight step by calling the LLM with a highly constrained prompt.
    This replaces expensive, multi-turn rollouts.
    """
    # A highly constrained prompt to generate a concise, single-turn simulation.
    prompt = f"""
    You are a simulator. Given the user's last input and a chosen action, generate a brief, realistic single-turn AI response to that action.
    
    ### CONVERSATION CONTEXT
    The user's last input was: "{state['graph'].nodes[-1].content}"
    
    ### ACTION TO SIMULATE
    Action Type: {action.type}
    Action Description: {action.step_description}

    ### YOUR TASK
    Based on this action, generate ONLY the AI's hypothetical response for the next turn. Do not add any extra conversation.
    """
    try:
        response = await asyncio.wait_for(
            OLLAMA_CLIENT.generate(model=OLLAMA_MODEL, prompt=prompt, options={"num_predict": 100}), # Limit response length for speed
            timeout=10.0 # Strict timeout for simulation
        )
        return response['response'].strip()
    except Exception as e:
        logger.error(f"Failed to simulate action with LLM: {e}")
        return "Simulation failed."

async def find_best_strategy(graph: ReasoningGraph, candidate_strategies: List[Strategy]) -> Strategy:
    """
    Uses a simplified Monte Carlo Tree Search to evaluate candidate strategies.
    This version replaces expensive LLM rollouts with a single simulated action
    and a call to our reward model.
    """
    logger.info("MCTS Service: Beginning simplified neural-assisted MCTS loop.")

    # A single root node to start the search
    root_state = {"graph": graph, "candidates": candidate_strategies}
    root = TreeNode(strategy=Strategy(goal="root", priority=0.0, constraints=[], lenses=[], mutators=[], actions=[]), state=root_state)

    # Initialize the tree with all candidate strategies as children of the root
    for strategy in candidate_strategies:
        child_state = {"graph": graph, "strategy": strategy}
        root.children[strategy.id] = TreeNode(strategy=strategy, parent=root, state=child_state)

    # MCTS loop with a fixed number of iterations for now
    iterations = 5 
    cpuct = 1.0  # Exploration constant

    for _ in range(iterations):
        node = root
        path = []
        
        # 1. SELECTION: Traverse the tree to find the best leaf node to expand
        while node.children:
            total_visits = sum(child.visits for child in node.children.values())
            
            # Using the PUCT formula for selection
            def puct_score(child_node: TreeNode):
                # We use strategy.priority as our initial policy prior (P)
                prior = child_node.strategy.priority
                # Q(s,a) = child_node.value
                # N(s,a) = child_node.visits
                # N(s,b) = total_visits
                # P(a|s) = prior
                if child_node.visits == 0:
                    return float('inf') # Prioritize unvisited nodes
                return child_node.value / child_node.visits + cpuct * prior * (math.sqrt(total_visits) / (1 + child_node.visits))

            action_id, node = max(
                node.children.items(),
                key=lambda item: puct_score(item[1])
            )
            path.append(node)
            
        # 2. EXPANSION & EVALUATION: A "leaf" node is selected. Simulate and score its value.
        simulated_response = await simulate_action(node.state, node.strategy.actions[0])

        # Score the simulated response using the reward model
        value = await score_strategy(node.state['graph'], node.strategy, simulated_response)
        
        # 3. BACKUP: Propagate the value back up the tree
        for visited_node in reversed(path):
            visited_node.visits += 1
            visited_node.value += value
            
    # 4. SELECTION: Choose the best strategy based on the most-visited node at the root level
    if not root.children:
        logger.error("MCTS failed to expand any nodes. Returning default.")
        return Strategy(
            goal="Default Fallback",
            priority=0.0,
            constraints=[],
            lenses=[],
            mutators=[],
            actions=[Action(type="generate_text", step_description="Respond directly to the user's input.")]
        )

    best_child = max(root.children.values(), key=lambda node: node.visits)
    
    logger.info(f"MCTS Service: Selected winning strategy '{best_child.strategy.goal}' with {best_child.visits} visits.")

    return best_child.strategy