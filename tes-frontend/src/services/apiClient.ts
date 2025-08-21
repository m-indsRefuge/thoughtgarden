// file: src/services/apiClient.ts
import {
  UserInput,
  ExperimentCreate,
  ExperimentData,
} from "../schemas";

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// --- API Functions ---
export const createExperiment = async (
  experimentIn: ExperimentCreate
): Promise<ExperimentData> => {
  console.log(`[API] Creating experiment: ${experimentIn.title}`);

  try {
    const response = await fetch(`${API_BASE_URL}/experiments/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(experimentIn),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        `HTTP error! status: ${response.status}, detail: ${JSON.stringify(
          errorData
        )}`
      );
    }

    const experiment = await response.json();
    console.log(`[API] Created experiment with ID: ${experiment.id}`);
    return experiment;
  } catch (error) {
    console.error("[API] Failed to create experiment:", error);
    throw error;
  }
};

export const advanceConversationStream = async (
  experimentId: number,
  message: string,
  callbacks: {
    onStreamChunk: (chunk: string) => void;
    onError: (error: string) => void;
    onClose: () => void;
  }
) => {
  console.log(
    `[API] Streaming conversation for experiment ${experimentId} with message: ${message}`
  );

  try {
    const userInput: UserInput = { message: message };
    const response = await fetch(
      `${API_BASE_URL}/experiments/${experimentId}/advance`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userInput),
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, detail: ${errorText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("Failed to get response reader");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          console.log("[API] Stream completed");
          callbacks.onClose();
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.trim()) {
            try {
              const event = JSON.parse(line);
              console.log("[API] Received event:", event);

              switch (event.event) {
                case "stream_chunk":
                  if (typeof event.data === "string") {
                    callbacks.onStreamChunk(event.data);
                  }
                  break;
                case "error":
                  callbacks.onError(event.data);
                  break;
                default:
                  console.warn("[API] Unknown event type:", event.event);
              }
            } catch (parseError) {
              console.error("[API] Failed to parse event:", parseError, "Line:", line);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  } catch (error) {
    console.error("Backend streaming failed:", error);
    const errorMessage = error instanceof Error ? error.message : String(error);
    callbacks.onError(errorMessage);
  }
};

export const getExperiment = async (
  experimentId: number
): Promise<ExperimentData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/experiments/${experimentId}`);
    if (!response.ok) {
      throw new Error(
        `HTTP error! status: ${response.status}, detail: ${await response.text()}`
      );
    }
    return await response.json();
  } catch (error) {
    console.error(`[API] Failed to get experiment ${experimentId}:`, error);
    throw error;
  }
};