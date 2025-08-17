/*
================================================================================
File: frontend/src/services/apiClient.ts
Purpose: Centralizes all communication with the backend API. It provides
         typed functions for each endpoint, handling requests, responses,
         and error handling.
================================================================================
*/

// --- Configuration ---
// The base URL for our backend server.
const API_BASE_URL = 'http://127.0.0.1:8001/api';

// --- Type Definitions ---
// These types define the shape of the data we expect from the API,
// ensuring type safety throughout our frontend application.

export interface Experiment {
  id: number;
  title: string;
  created_at: string; // ISO date string
  data: ExperimentData;
}

export interface ExperimentData {
  description: string;
  perspectives: Perspective[];
  debate_turns: DebateTurn[];
  synthesis: Synthesis | null;
}

export interface Perspective {
  id: number;
  viewpoint_name: string;
  viewpoint_text: string;
}

export interface DebateTurn {
  questioning_perspective_id: number;
  critiqued_perspective_id: number;
  questioner_name: string;
  critiqued_name: string;
  cross_question_text: string;
  response_text: string;
}

export interface Synthesis {
  synthesis_text: string;
  reasoning_steps: string | null;
}

// --- API Functions ---

/**
 * Fetches a list of all experiments from the backend.
 * @returns A promise that resolves to an array of Experiment objects.
 */
export const getAllExperiments = async (): Promise<Experiment[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/experiments/`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to fetch experiments:", error);
    // In a real app, you might want to show a notification to the user
    return []; // Return an empty array on failure
  }
};

/**
 * Creates a new experiment.
 * @param title - The title of the new experiment.
 * @param description - The description of the new experiment.
 * @returns A promise that resolves to the newly created Experiment object.
 */
export const createExperiment = async (title: string, description: string): Promise<Experiment> => {
  const response = await fetch(`${API_BASE_URL}/experiments/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title, description }),
  });

  if (!response.ok) {
    // We can add more detailed error handling here later
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to create experiment');
  }
  return await response.json();
};

/**
 * Fetches the full details for a single experiment.
 * @param experimentId - The ID of the experiment to fetch.
 * @returns A promise that resolves to a single Experiment object.
 */
export const getExperimentById = async (experimentId: number): Promise<Experiment> => {
    const response = await fetch(`${API_BASE_URL}/experiments/${experimentId}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}


// The runSimulationStream function will be more complex as it handles
// the streaming response. We will build this in a later step when we
// implement the live simulation view.

