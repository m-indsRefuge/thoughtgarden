# file: backend/app/services/cognitive_matrix.py (New File)
import random
from typing import Dict, List, Any

"""
This service defines the "Cognitive Matrix," a structured set of reasoning lenses and directives.
It uses a weighted random search algorithm to select a dynamic "reasoning lens" for the LLM 
at each turn, ensuring variety and depth in the AI's responses.
"""

# The Cognitive Matrix: A dictionary of different reasoning approaches.
# Each lens has a 'weight' to control its frequency of selection.
COGNITIVE_MATRIX = {
    "lenses": [
        {"name": "Historical Perspective", "weight": 10, "description": "Analyze the user's idea through the lens of historical precedent and past events."},
        {"name": "Ethical Implications", "weight": 15, "description": "Focus on the moral and ethical consequences of the user's idea."},
        {"name": "Technological Impact", "weight": 15, "description": "Explore the technological ramifications, both immediate and long-term."},
        {"name": "Economic Analysis", "weight": 10, "description": "Examine the economic costs, benefits, and externalities."},
        {"name": "Psychological Motivation", "weight": 10, "description": "Consider the underlying psychological drivers and human behavior related to the idea."},
        {"name": "Socratic Questioning", "weight": 20, "description": "Challenge the user's core assumptions by asking probing, foundational questions."},
        {"name": "Contrarian Viewpoint", "weight": 20, "description": "Take a deliberately opposite or unpopular stance to test the strength of the user's idea."},
    ],
    "mutators": [
        {"name": "Increase Abstraction", "weight": 10, "description": "Elevate the concept to a more philosophical or abstract level."},
        {"name": "Force a Concrete Example", "weight": 15, "description": "Demand a specific, real-world example of the user's abstract idea."},
        {"name": "Introduce a Constraint", "weight": 15, "description": "Add a new limitation or scarcity to the scenario and ask how it changes things."},
    ]
}

def select_dynamic_lens(conversation_depth: int) -> Dict[str, Any]:
    """
    Selects a reasoning lens and a mutator from the Cognitive Matrix using a 
    weighted random selection algorithm.
    
    Args:
        conversation_depth: The number of nodes in the graph, used to adjust selection logic.

    Returns:
        A dictionary containing the selected 'lens' and 'mutator'.
    """
    # Simple algorithm: As the conversation gets deeper, we favor more challenging lenses.
    if conversation_depth > 6:
        # Increase the weight of more "advanced" lenses like Socratic and Contrarian
        for lens in COGNITIVE_MATRIX["lenses"]:
            if lens["name"] in ["Socratic Questioning", "Contrarian Viewpoint"]:
                lens["weight"] += 10

    # Weighted random selection for the main lens
    lenses = COGNITIVE_MATRIX["lenses"]
    total_weight_lenses = sum(l['weight'] for l in lenses)
    chosen_lens_val = random.uniform(0, total_weight_lenses)
    
    cumulative_weight = 0
    selected_lens = None
    for lens in lenses:
        cumulative_weight += lens['weight']
        if chosen_lens_val <= cumulative_weight:
            selected_lens = lens
            break
            
    # Weighted random selection for the mutator (with a 50% chance of no mutator)
    mutators = COGNITIVE_MATRIX["mutators"] + [{"name": "None", "weight": 100, "description": "No mutator."}]
    total_weight_mutators = sum(m['weight'] for m in mutators)
    chosen_mutator_val = random.uniform(0, total_weight_mutators)

    cumulative_weight = 0
    selected_mutator = None
    for mutator in mutators:
        cumulative_weight += mutator['weight']
        if chosen_mutator_val <= cumulative_weight:
            selected_mutator = mutator
            break

    return {
        "lens": selected_lens,
        "mutator": selected_mutator if selected_mutator and selected_mutator['name'] != "None" else None
    }