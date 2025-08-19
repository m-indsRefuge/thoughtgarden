# file: app/core/content.py

PERSONAS = {
    "guide_philosopher": {
        "name": "The Philosopher",
        "prompt_description": "An AI persona that speaks in clear, thoughtful, and philosophical terms, guiding the user through a classic thought experiment."
    },
    "guide_storyteller": {
        "name": "The Storyteller",
        "prompt_description": "An AI persona that frames thought experiments as engaging narratives, focusing on characters and immersive descriptions."
    }
}

JOURNEYS = {
    "ship_of_theseus": {
        "title": "The Ship of Theseus's Mind",
        "description": "An exploration of identity and persistence through a classic paradox.",
        "script": {
            "guide_philosopher": [
                "Welcome. Let us consider the Ship of Theseus. If a ship has all its planks replaced over time, is it still the same ship? Now, what if we apply this to a mind?",
                "Imagine a person whose memories are slowly replaced, one by one, with new, fabricated ones. At what point, if any, do they cease to be the same person?",
                "Consider this: Is personal identity defined by the continuity of memory, the physical brain, or something else entirely? The paradox forces us to question the very foundation of self.",
                "There is no easy answer. The journey through this question is the destination. Thank you for pondering with me."
            ],
            "guide_storyteller": [
                "Gather 'round and listen to a tale. Old Captain Eva sailed the 'Wanderer' for fifty years, replacing every worn plank and mended sail until no original timber remained. Was it still the Wanderer? Now, imagine Eva's own mind is that ship.",
                "A mischievous sea spirit begins swapping Eva's memories of home with tales of a city of glass she's never seen. When she no longer remembers her childhood port, is she still Eva?",
                "What makes Eva, Eva? Is it the logbook of her past, written in the ink of memory? Or is it the steadfast captain standing at the helm, regardless of the charts she reads?",
                "The 'Wanderer' sails on, a mystery on the waves, just as Eva continues her journey, a paradox of the self. The story, like identity, is ever-changing."
            ]
        }
    }
    # We can easily add more journeys here in the future
}

# Add these to app/core/content.py

# Weights for our Weighted Sum equation. This allows us to tune the CAM's "personality".
# w_k: keyword/reasoning score, w_s: sentiment score, w_c: complexity score
CAM_WEIGHTS = {"w_k": 0.6, "w_s": 0.2, "w_c": 0.2}

# The Affinity Matrix now includes abstract reasoning cues.
KEYWORD_AFFINITIES = {
    # Reasoning Cues (high value)
    'causal':      {"Pragmatic Engineer": 30, "Critical Risk Analyst": 20, "Visionary Optimist": 10},
    'conditional': {"Critical Risk Analyst": 30, "Pragmatic Engineer": 20, "Visionary Optimist": 10},
    'comparative': {"Pragmatic Engineer": 25, "Critical Risk Analyst": 25, "Visionary Optimist": 10},
    'uncertainty': {"Visionary Optimist": 30, "Critical Risk Analyst": 20, "Pragmatic Engineer": 5},
    'evidential':  {"Critical Risk Analyst": 40, "Pragmatic Engineer": 20, "Visionary Optimist": -10},
    'emphasis':    {"Visionary Optimist": 25, "Pragmatic Engineer": 15, "Critical Risk Analyst": 10},

    # Thematic Keywords
    "risk":        {"Critical Risk Analyst": 50, "Pragmatic Engineer": 10, "Visionary Optimist": -20},
    "failure":     {"Critical Risk Analyst": 50, "Pragmatic Engineer": 5, "Visionary Optimist": -10},
    "opportunity": {"Visionary Optimist": 40, "Pragmatic Engineer": 10, "Critical Risk Analyst": -10},
    "growth":      {"Visionary Optimist": 40, "Pragmatic Engineer": 15, "Critical Risk Analyst": 0},
    "solution":    {"Pragmatic Engineer": 40, "Visionary Optimist": 10, "Critical Risk Analyst": 5},
    "plan":        {"Pragmatic Engineer": 50, "Visionary Optimist": 0, "Critical Risk Analyst": 10},
    "ethics":      {"Visionary Optimist": 30, "Critical Risk Analyst": 15, "Pragmatic Engineer": 0},
    "power":       {"Critical Risk Analyst": 30, "Pragmatic Engineer": 10, "Visionary Optimist": 0},
}