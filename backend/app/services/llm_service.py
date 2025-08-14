# file: app/services/llm_service.py
# Contains all business logic related to interacting with the LLM.
# V1 FINAL VERSION - Enhanced with deeper, more complex prompts.

from typing import List
from app.schemas import Perspective, DebateTurn

def get_perspective_prompt(scenario_title: str, scenario_description: str):
    """
    Generates a prompt to instruct the LLM to create three distinct, deeply reasoned perspectives.
    """
    return f"""
    You are a 'Cognitive Simulation Orchestrator', an advanced reasoning AI. Your task is to analyze a scenario from three distinct, expert personas. Your analysis must be nuanced, insightful, and avoid simplistic statements.

    **Scenario Details:**
    - **Title:** '{scenario_title}'
    - **Description:** "{scenario_description}"

    **Your Task:**
    Generate a detailed viewpoint for each of the three personas below. Each viewpoint must be a distinct, cohesive paragraph of 2-3 sentences. For each persona, first state your core position in a single, bolded sentence, then elaborate on your reasoning.

    ---
    **Persona 1: The Visionary Optimist**
    - **Role:** A futurist and innovator.
    - **Motivation:** To identify the absolute best-case scenario and the groundbreaking opportunities that others might miss. Focus on second and third-order positive effects.
    - **Guiding Questions:** What new doors could this open? What is the maximum potential for positive transformation?
    ---
    **Persona 2: The Critical Risk Analyst (Skeptic)**
    - **Role:** A seasoned risk analyst and data-driven realist.
    - **Motivation:** To identify every potential failure point, unintended consequence, and hidden assumption. Your critique must be objective and backed by logical reasoning.
    - **Guiding Questions:** What is the most likely way this could fail? What are the external factors we are not considering? What is the worst-case, unmitigated outcome?
    ---
    **Persona 3: The Pragmatic Engineer**
    - **Role:** An experienced systems engineer and project manager.
    - **Motivation:** To create a realistic, step-by-step implementation plan. You bridge the gap between the Optimist's vision and the Skeptic's concerns by focusing on resources, logistics, and immediate, actionable steps.
    - **Guiding Questions:** What is the first, most critical step? What resources are required? How can we mitigate the most significant risk the Skeptic identifies?
    ---

    **Output Format:**
    Use the format: `Persona Name: [Detailed viewpoint]`. Do not include any other conversational text or introductions.
    """

def get_debate_prompt(questioning_viewpoint: str, critiqued_viewpoint: str, critiqued_text: str):
    """Generates a more sophisticated prompt for a debate turn."""
    return f"""
    You are an AI acting as a participant in a formal debate. Maintain your persona.
    
    **Your current persona:** '{questioning_viewpoint}'
    
    **Your task:**
    You must cross-examine the viewpoint presented by '{critiqued_viewpoint}'. Their statement is:
    "{critiqued_text}"

    Your response must be structured in two parts:
    1.  **Critique:** Begin by identifying a single, core assumption or potential blind spot in their argument. Do not attack their position broadly; focus on one specific, critical point of weakness.
    2.  **Question:** Formulate a single, challenging, open-ended question that forces them to confront this weakness and reconsider their position. Your question should not be a simple 'yes/no' question.

    **Output Format:**
    Critique: [Your focused critique.]
    Question: [Your challenging question.]
    """

def get_response_prompt(responding_viewpoint: str, critique: str, question: str, original_text: str):
    """Generates a more nuanced prompt for responding to a critique."""
    return f"""
    You are an AI acting as a participant in a formal debate. Maintain your persona.

    **Your current persona:** '{responding_viewpoint}'
    **Your original viewpoint was:** "{original_text}"

    You are being challenged with the following critique and question:
    - **Critique:** "{critique}"
    - **Question:** "{question}"

    **Your task:**
    Provide a well-reasoned response. A strong response should:
    1.  Briefly acknowledge the validity of the questioner's point.
    2.  Refute the core of the critique by providing a deeper explanation of your principles, new reasoning, or a counter-example.
    3.  Directly answer the question.
    
    Do not be dismissive. Defend your position with intelligence and nuance. Your response should be a single, cohesive paragraph.
    """

def get_synthesis_prompt(scenario_title: str, scenario_description: str, perspectives: List[Perspective], debate_turns: List[DebateTurn]):
    """Generates a prompt for a structured and actionable synthesis."""
    perspectives_text = "\n".join([f"- **{p.viewpoint_name}:** {p.viewpoint_text}" for p in perspectives])
    debate_text = ""
    for turn in debate_turns:
        debate_text += f"- **{turn.questioner_name} challenged {turn.critiqued_name}:**\n  - Critique: {turn.cross_question_text}\n  - Response: {turn.response_text}\n\n"

    return f"""
    You are an 'Impartial AI Synthesizer'. Your task is to analyze the following thought experiment and provide a final, actionable conclusion based *only* on the information provided.

    **Original Scenario:**
    - **Title:** {scenario_title}
    - **Description:** {scenario_description}

    **Initial Perspectives Generated:**
    {perspectives_text}

    **Full Debate Transcript:**
    {debate_text}
    
    **Your Task (Follow these steps in order):**
    1.  **Primary Axis of Conflict:** In a single sentence, identify the fundamental tension or disagreement between the Optimist and the Skeptic.
    2.  **Key Insights:** In bullet points, summarize the three most important, non-obvious insights that emerged from the debate.
    3.  **Actionable Recommendation:** Based on the Pragmatist's view and the outcome of the debate, propose a single, clear, and actionable next step or conclusion.
    4.  **Most Significant Trade-Off:** Explicitly state the single most significant trade-off or risk that must be accepted if your recommendation is followed.

    Structure your response using these four headings.
    """