# file: backend/app/services/creativity_service.py
"""
Creativity Service v3: Hybrid Reasoning Engine
Combines structured strategies, wildcard perturbations, and meta-reasoning scoring.
Fully compatible with the Thought Garden Strategy DSL.
"""

import random
from typing import Dict, List, Callable, Optional
from uuid import uuid4

from app.schemas.dsl import Strategy, Action, Constraint

# --- Knowledge Pools ---
# Updated list with more closely related concepts (e.g., computational and data-driven analogies)
ANALOGICAL_CONCEPTS = [
    "the principles of a distributed ledger (blockchain)", "the flow of data in a pipeline architecture",
    "the structure of a binary search tree", "the rules of a compiler",
    "the process of a packet's journey through a network", "the optimization of an algorithm",
    "the self-organizing nature of a neural network", "the caching of information in memory",
    "the logic of a circuit board", "the version control of a software repository",
    "the parallel processing of a GPU", "the recursive nature of a fractal"
]

CONSTRAINTS = [
    {"type": "energy", "value": 0, "unit": "J", "description": "must be accomplished with zero energy cost"},
    {"type": "audience", "value": "child_15th_century", "description": "must be explained to a child from the 15th century"},
    {"type": "medium", "value": "language-free", "description": "must function without the use of language"},
    {"type": "timescale", "value": "single_second", "unit": "s", "description": "must operate on a timescale of a single second"},
    {"type": "timescale", "value": "billion_years", "unit": "years", "description": "must operate on a timescale of a billion years"},
    {"type": "technology", "value": "pre-1900", "description": "cannot involve any technology invented after 1900"},
    {"type": "budget", "value": 100, "unit": "$", "description": "must be achieved with a budget of only $100"},
    {"type": "physics", "value": "thermodynamics", "description": "must be achieved without violating the laws of thermodynamics"}
]

PERSPECTIVES = [
    "a geologist who thinks in terms of deep time", "a colony of ants", "a future AI historian",
    "a single photon of light", "a skeptical child", "a cynical marketing executive",
    "a philosopher specializing in ethics", "the last surviving member of a long-dead alien species"
]

# --- Strategy Registry ---
STRATEGY_REGISTRY = {}

def register_strategy(name: str):
    def decorator(func: Callable):
        STRATEGY_REGISTRY[name] = func
        return func
    return decorator

# --- Core Strategy Generators ---

@register_strategy("Analogical Leap")
def _generate_analogical_leap(context: Optional[str] = None) -> Strategy:
    """Generates a strategy that forces a connection between two disparate concepts."""
    random_concept = random.choice(ANALOGICAL_CONCEPTS)
    goal = f"Force a creative connection to the concept of '{random_concept}' to reveal new insights."
    actions = [
        Action(type="reflect", step_description=f"Analyze the user's input through the lens of '{random_concept}'."),
        Action(type="generate_text", step_description="Formulate a question that bridges the current topic and the new analogical concept.")
    ]
    return Strategy(
        id=str(uuid4()),
        goal=goal,
        priority=0.8,
        constraints=[],
        lenses=["analogical-thinking"],
        actions=actions
    )

@register_strategy("Constraint Injection")
def _generate_constraint_injection(context: Optional[str] = None) -> Strategy:
    """Generates a strategy that adds a new, unexpected rule to the problem."""
    random_constraint_dict = random.choice(CONSTRAINTS)
    random_constraint = Constraint(
        type=random_constraint_dict["type"],
        value=random_constraint_dict.get("value"),
        unit=random_constraint_dict.get("unit"),
        description=random_constraint_dict["description"]
    )
    goal = f"Re-evaluate the problem under the new constraint: '{random_constraint.description}'."
    actions = [
        Action(type="reflect", step_description="Analyze how the new constraint fundamentally changes the problem space."),
        Action(type="generate_text", step_description="Formulate a new question that incorporates the injected constraint.")
    ]
    return Strategy(
        id=str(uuid4()),
        goal=goal,
        priority=0.9,
        constraints=[random_constraint],
        lenses=["constrained-thinking"],
        actions=actions
    )

@register_strategy("Perspective Shift")
def _generate_perspective_shift(context: Optional[str] = None) -> Strategy:
    """Generates a strategy that forces a change in viewpoint."""
    random_perspective = random.choice(PERSPECTIVES)
    goal = f"Analyze the problem from the point of view of '{random_perspective}'."
    actions = [
        Action(type="reflect", step_description="Consider the core values and knowledge of the new perspective."),
        Action(type="generate_text", step_description="Synthesize the user's idea into a response from this new viewpoint, ending with a question.")
    ]
    return Strategy(
        id=str(uuid4()),
        goal=goal,
        priority=0.85,
        constraints=[],
        lenses=[random_perspective],
        actions=actions
    )

@register_strategy("Scale Inversion")
def _generate_scale_inversion(context: Optional[str] = None) -> Strategy:
    """Generates a strategy that dramatically alters the scale of the problem."""
    inversion_type = random.choice(["micro", "macro"])
    if inversion_type == "micro":
        goal = "Zoom in to explore the idea's impact on a single individual's experience."
        actions = [
            Action(type="generate_text", step_description="Create a short vignette of an individual affected by the idea."),
            Action(type="reflect", step_description="Analyze the emotional/personal consequences in the vignette.")
        ]
        lens = "scale-micro"
        priority = 0.92
    else: # macro
        goal = "Zoom out to explore the idea's impact on a global or cosmic scale."
        actions = [
            Action(type="generate_text", step_description="Describe the idea's consequences over millions/billions of years."),
            Action(type="reflect", step_description="Analyze systemic changes revealed at this scale.")
        ]
        lens = "scale-macro"
        priority = 0.95
    
    return Strategy(
        id=str(uuid4()),
        goal=goal,
        priority=priority,
        constraints=[],
        lenses=[lens],
        actions=actions
    )

# --- Scoring Functions ---
def score_strategy(strategy: Strategy, context: Optional[str] = None) -> float:
    """
    A conceptual function to score a strategy based on a simplified meta-reasoning for v3.
    """
    base = strategy.priority
    novelty_bonus = random.uniform(0.0, 0.05)
    relevance_bonus = 0.05 if context else 0
    return min(1.0, base + novelty_bonus + relevance_bonus)

# --- Hybrid Strategy Generator ---
def generate_hybrid_strategy(context: Optional[str] = None) -> Strategy:
    """
    Generates a reasoning strategy by combining structured and wildcard approaches.
    Includes meta-reasoning scoring and selection weighting.
    """
    # Step 1: Select a candidate strategy from registry
    name, generator = random.choice(list(STRATEGY_REGISTRY.items()))
    strategy = generator(context)

    # Step 2: Apply meta-reasoning scoring
    strategy.priority = score_strategy(strategy, context)

    # Step 3: Optional secondary wildcard perturbation
    if random.random() < 0.3:  # 30% chance to inject secondary perturbation
        perturb_name, perturb_fn = random.choice(list(STRATEGY_REGISTRY.items()))
        if perturb_name != name:
            perturb_strategy = perturb_fn(context)
            # Merge actions from perturbation
            strategy.actions.extend(perturb_strategy.actions)
            strategy.lenses.extend([l for l in perturb_strategy.lenses if l not in strategy.lenses])
            strategy.constraints.extend([c for c in perturb_strategy.constraints if c not in strategy.constraints])
            strategy.goal = f"Combine '{strategy.goal}' with '{perturb_strategy.goal}'"

    return strategy