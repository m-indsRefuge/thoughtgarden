# file: app/services/cognitive_matrix.py

import random
from typing import List, Dict, Any
from app.schemas import schemas as api_schemas # Import our new schemas

# Define the persona affinities. In a real app, this could be more complex.
PERSONA_AFFINITIES = {
    'analyst': {'logic': 40, 'data': 30, 'ethics': -10},
    'idealist': {'ethics': 50, 'hope': 25, 'practicality': -20},
    'pragmatist': {'survival': 40, 'practicality': 40, 'abstract': -15}
}

def calculate_affinity(persona_id: str, tags: List[str]) -> float:
    """Calculates a persona's affinity score based on tags."""
    score = 0.0
    affinities = PERSONA_AFFINITIES.get(persona_id, {})
    for tag in tags:
        score += affinities.get(tag, 0)
    return score

def arbitrate(
    personas: List[api_schemas.Persona],
    current_step: api_schemas.JourneyStep,
    user_history: List[Any]
) -> api_schemas.CAMResult:
    """
    The Core CAM function.
    Determines which persona "speaks" next.
    """
    scores = {}
    max_score = -1
    winner_id = ""

    # This is a simple implementation of the formula: Score(p) = (Wp * Ap(St)) + R
    for p in personas:
        affinity_score = calculate_affinity(p.id, current_step.thematic_tags)
        # We can add more complex logic here based on user_history later
        
        final_score = (p.base_weight * affinity_score) + random.uniform(0, 15)
        
        scores[p.id] = round(final_score, 2)
        if final_score > max_score:
            max_score = final_score
            winner_id = p.id
            
    return api_schemas.CAMResult(scores=scores, winner=winner_id)