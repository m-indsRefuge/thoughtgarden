# file: backend/app/services/creativity_service.py (Expanded with New Strategies)
import random
from typing import Dict, List, Callable

# --- Strategy Components ---

ANALOGICAL_CONCEPTS = [
    "the principles of ancient Roman aqueduct design", "the decentralized nature of a mycelial network",
    "the dramatic structure of a three-act play", "the rules of a game of chess",
    "the process of biological evolution by natural selection", "the economic theory of supply and demand",
    "the social structure of a beehive", "the transmission of information in Morse code",
    "the principles of jazz improvisation", "the philosophical concept of the Ship of Theseus",
    "the life cycle of a star", "the rules of a constitutional legal system",
    "the artistic process of pointillism", "the physics of quantum entanglement",
    "the logic of a circuit board", "the migration patterns of monarch butterflies",
    "the psychological phenomenon of confirmation bias"
]

CONSTRAINTS = [
    "must be accomplished with zero energy cost", "must be explained to a child from the 15th century",
    "must function without the use of language", "must operate on a timescale of a single second",
    "must operate on a timescale of a billion years", "cannot involve any technology invented after 1900",
    "must be achieved with a budget of only $100", "must be achieved without violating the laws of thermodynamics"
]

PERSPECTIVES = [
    "a geologist who thinks in terms of deep time", "a colony of ants", "a future AI historian",
    "a single photon of light", "a skeptical child", "a cynical marketing executive",
    "a philosopher specializing in ethics", "the last surviving member of a long-dead alien species"
]

# --- Core Creative Strategy Functions ---

def _generate_analogical_leap() -> Dict[str, str]:
    """Generates a strategy that forces a connection between two disparate concepts."""
    random_concept = random.choice(ANALOGICAL_CONCEPTS)
    return {
        "name": "Perform an Analogical Leap",
        "description": f"Force a creative connection between the user's idea and the seemingly unrelated concept of '{random_concept}'. Explore what new insights this surprising parallel might reveal."
    }

def _generate_constraint_injection() -> Dict[str, str]:
    """Generates a strategy that adds a new, unexpected rule to the problem."""
    random_constraint = random.choice(CONSTRAINTS)
    return {
        "name": "Inject a New Constraint",
        "description": f"Re-evaluate the user's last statement, but under the new and surprising constraint that it '{random_constraint}'. How does this new rule change the entire problem?"
    }

def _generate_perspective_shift() -> Dict[str, str]:
    """Generates a strategy that forces a change in viewpoint."""
    random_perspective = random.choice(PERSPECTIVES)
    return {
        "name": "Shift the Perspective",
        "description": f"Analyze the user's idea, but from the completely different point of view of '{random_perspective}'. What new priorities, fears, or opportunities would this new perspective reveal?"
    }

def _generate_scale_inversion() -> Dict[str, str]:
    """Generates a strategy that dramatically alters the scale of the problem."""
    inversion_type = random.choice(["micro", "macro"])
    if inversion_type == "micro":
        description = "Zoom all the way in. How does the user's idea affect a single, specific individual on a personal and emotional level? Create a brief narrative vignette about this person."
    else: # macro
        description = "Zoom all the way out. How does the user's idea affect the entire planet, galaxy, or the fabric of spacetime over a million years? Explore the largest possible consequences."
    
    return {
        "name": f"Invert the Scale (to {inversion_type})",
        "description": description
    }

# --- Main Service Function ---

# A list of all available creative strategy functions
CREATIVE_STRATEGIES: List[Callable[[], Dict[str, str]]] = [
    _generate_analogical_leap,
    _generate_constraint_injection,
    _generate_perspective_shift,
    _generate_scale_inversion,
]

def generate_wildcard_strategy() -> Dict[str, str]:
    """
    Randomly selects and executes one of the available creative strategy functions.
    This is the main entry point for the "Creator" service.
    
    Returns:
        A dictionary representing a single, creative "wildcard" strategy.
    """
    # Randomly choose which creative strategy to use this turn
    chosen_strategy_func = random.choice(CREATIVE_STRATEGIES)
    
    # Execute the chosen function to get the strategy dictionary
    return chosen_strategy_func()