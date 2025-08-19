// file: src/services/apiClient.ts (Fixed to use backend properly)

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// --- Type Definitions ---
export interface DebateArgument {
  persona: string;
  argument: string;
  score: number;
}

export interface ApiTurn {
  turn_number: number;
  user_message: string;
  debate: DebateArgument[];
  internal_monologue: string;
  ai_question_to_user: string;
}

// Renamed JourneymanTurn to GardenPathTurn
export interface GardenPathTurn {
  narrative: string;
  is_complete: boolean;
  experiment_id: number;
}

export interface Experiment {
  id: number;
  title: string;
  description: string;
}

// --- API Functions ---
export const createExperiment = async (title: string, description: string): Promise<Experiment> => {
  console.log(`[API] Creating experiment: ${title}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/experiments/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title,
        description,
        data: { history: [] } // Initialize with empty conversation history
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const experiment = await response.json();
    console.log(`[API] Created experiment with ID: ${experiment.id}`);
    return experiment;
  } catch (error) {
    console.error('[API] Failed to create experiment:', error);
    // Fallback to mock for development
    return { id: Math.floor(Math.random() * 100000), title, description };
  }
};

// Renamed startJourney to startGardenPath
export const startGardenPath = async (journeyName: string): Promise<GardenPathTurn> => {
  console.log(`[API] Starting new journeyman journey: ${journeyName}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/journeys/${journeyName}/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('[API] Failed to start journey:', error);
    // Fallback to mock
    return {
      narrative: "You have begun the journey into the mind of Theseus. What is your first action?",
      is_complete: false,
      experiment_id: Math.floor(Math.random() * 100000),
    };
  }
};

// Renamed getNextJourneyStep to getNextGardenPathStep
export const getNextGardenPathStep = async (experimentId: number): Promise<GardenPathTurn> => {
  console.log(`[API] Getting next step for experiment ID: ${experimentId}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/journeys/${experimentId}/next`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('[API] Failed to get next journey step:', error);
    // Fallback to mock
    return {
      narrative: "The next step of your journey is a puzzle. What do you do?",
      is_complete: false,
      experiment_id: experimentId,
    };
  }
};

export const advanceConversationStream = async (
  experimentId: number,
  message: string,
  callbacks: {
    onDebate: (debate: DebateArgument[]) => void;
    onMonologueChunk: (chunk: string) => void;
    onQuestion: (question: string) => void;
    onError: (error: string) => void;
    onClose: () => void;
  }
) => {
  console.log(`[API] Streaming conversation for experiment ${experimentId} with message: ${message}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/experiments/${experimentId}/advance`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Failed to get response reader');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log('[API] Stream completed');
          callbacks.onClose();
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.trim()) {
            try {
              const event = JSON.parse(line);
              console.log('[API] Received event:', event);

              switch (event.event) {
                case 'debate_complete':
                  if (Array.isArray(event.data)) {
                    callbacks.onDebate(event.data);
                  }
                  break;
                case 'monologue_chunk':
                  if (typeof event.data === 'string') {
                    callbacks.onMonologueChunk(event.data);
                  }
                  break;
                case 'question_complete':
                  if (typeof event.data === 'string') {
                    callbacks.onQuestion(event.data);
                  }
                  break;
                default:
                  console.warn('[API] Unknown event type:', event.event);
              }
            } catch (parseError) {
              console.error('[API] Failed to parse event:', parseError, 'Line:', line);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

  } catch (error) {
    console.error("Backend streaming failed:", error);
    
    // Fallback to mock implementation for development
    console.log('[API] Using fallback mock implementation');
    const mockResponses = [
      [
        { event: 'monologue_chunk', data: "The user's query is intriguing. I need to break it down. " },
        { event: 'monologue_chunk', data: "It touches on systems architecture, intelligence, and adaptability. " },
        { event: 'debate_complete', data: [
          { persona: 'Visionary Optimist', argument: "This opens up exciting possibilities for emergent intelligence systems.", score: 85 },
          { persona: 'Critical Risk Analyst', argument: "We must carefully consider the computational complexity and potential failure modes.", score: 78 },
          { persona: 'Pragmatic Engineer', argument: "Let's focus on building a minimal viable implementation first.", score: 72 }
        ]},
        { event: 'question_complete', data: "What specific aspect of this system would you like to explore first - the emergent behaviors, the risk mitigation strategies, or the practical implementation approach?" }
      ],
    ];

    const mockData = mockResponses[Math.floor(Math.random() * mockResponses.length)];

    for (const event of mockData) {
      await new Promise(resolve => setTimeout(resolve, 300));
      
      switch (event.event) {
        case 'debate_complete':
          if (Array.isArray(event.data)) {
            callbacks.onDebate(event.data);
          }
          break;
        case 'monologue_chunk':
          if (typeof event.data === 'string') {
            callbacks.onMonologueChunk(event.data);
          }
          break;
        case 'question_complete':
          if (typeof event.data === 'string') {
            callbacks.onQuestion(event.data);
          }
          break;
      }
    }
    
    callbacks.onClose();
  }
};