import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

// ==============================================================================
// 1. DATA MODELS & TYPES
// ==============================================================================
// These types are taken directly from the provided apiClient.ts file
// to ensure consistency and type safety.

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

// ==============================================================================
// 2. API CLIENT (INLINE FOR SELF-CONTAINED DEMO)
// ==============================================================================
// The functions from apiClient.ts are included here to make the immersive
// code block self-contained and resolve the import path issue.

const API_BASE_URL = 'http://127.0.0.1:8001/api';

const getAllExperiments = async (): Promise<Experiment[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/experiments/`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to fetch experiments:", error);
    return [];
  }
};

const createExperiment = async (title: string, description: string): Promise<Experiment> => {
  const response = await fetch(`${API_BASE_URL}/experiments/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title, description }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to create experiment');
  }
  return await response.json();
};

const getExperimentById = async (experimentId: number): Promise<Experiment> => {
  const response = await fetch(`${API_BASE_URL}/experiments/${experimentId}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
};

// ==============================================================================
// 3. CONTEXT SETUP
// ==============================================================================

// Define the shape of the context value
type AppContextType = {
  // State
  scenarios: Experiment[];
  selectedScenarioId: number | null;
  selectedScenarioData: Experiment | null;
  isLoadingScenarios: boolean;
  isLoadingDetails: boolean;
  isSimulating: boolean;
  simulationLog: string[];
  error: string | null;

  // Actions
  selectScenario: (id: number) => void;
  createNewScenario: (title: string, description: string) => Promise<void>;
  runSimulation: () => Promise<void>;
};

// Create the context with a default undefined value
const AppContext = createContext<AppContextType | undefined>(undefined);

// ==============================================================================
// 4. PROVIDER COMPONENT
// ==============================================================================

type AppProviderProps = {
  children: ReactNode;
};

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  // Application State
  const [scenarios, setScenarios] = useState<Experiment[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<number | null>(null);
  const [selectedScenarioData, setSelectedScenarioData] = useState<Experiment | null>(null);
  const [isLoadingScenarios, setIsLoadingScenarios] = useState(true);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationLog, setSimulationLog] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Function to fetch the list of all scenarios
  const fetchAllScenarios = async () => {
    setIsLoadingScenarios(true);
    setError(null);
    try {
      const fetchedScenarios = await getAllExperiments();
      setScenarios(fetchedScenarios);
    } catch (e: any) {
      setError(e.message || "Failed to fetch scenarios.");
      console.error(e);
    } finally {
      setIsLoadingScenarios(false);
    }
  };

  // Effect to fetch scenarios on initial load
  useEffect(() => {
    fetchAllScenarios();
  }, []);

  // Effect to fetch full scenario details when a scenario is selected
  useEffect(() => {
    const fetchScenarioDetails = async () => {
      if (selectedScenarioId === null) {
        setSelectedScenarioData(null);
        return;
      }
      setIsLoadingDetails(true);
      setError(null);
      try {
        const details = await getExperimentById(selectedScenarioId);
        setSelectedScenarioData(details);
      } catch (e: any) {
        setError(e.message || "Failed to fetch scenario details.");
        console.error(e);
        setSelectedScenarioData(null);
      } finally {
        setIsLoadingDetails(false);
      }
    };
    fetchScenarioDetails();
  }, [selectedScenarioId]);

  // Handler for selecting a scenario from the sidebar
  const selectScenario = (id: number) => {
    setSelectedScenarioId(id);
    // Reset simulation data when a new scenario is selected
    setSimulationLog([]);
    setIsSimulating(false);
  };

  // Handler for creating a new scenario
  const createNewScenario = async (title: string, description: string) => {
    try {
      const newScenario = await createExperiment(title, description);
      // Add the new scenario to the list and select it
      setScenarios(prev => [newScenario, ...prev]);
      selectScenario(newScenario.id);
    } catch (e: any) {
      setError(e.message || "Failed to create new scenario.");
      console.error(e);
    }
  };

  // Handler for running the simulation
  const runSimulation = async () => {
    if (selectedScenarioId === null) {
      setError("Please select a scenario to run.");
      return;
    }
    
    setIsSimulating(true);
    setSimulationLog([]);
    setError(null);

    try {
      // Get the reader for the streaming response
      const response = await fetch(`${API_BASE_URL}/scenarios/${selectedScenarioId}/run`, { method: 'POST' });
      if (!response.ok || !response.body) {
        throw new Error('Failed to start simulation stream.');
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      // Read the stream chunk by chunk
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        // The API sends newline-separated JSON objects
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.trim() === '') continue;
          try {
            const event = JSON.parse(line);
            setSimulationLog(prev => [...prev, JSON.stringify(event, null, 2)]);
            
            // Handle different event types from the backend
            if (event.event === "perspective_generated" || event.event === "debate_turn" || event.event === "synthesis_generated" || event.event === "completion") {
              // Re-fetch the full scenario details to update the UI
              const updatedDetails = await getExperimentById(selectedScenarioId);
              setSelectedScenarioData(updatedDetails);
            }
          } catch (e: any) {
            console.error("Failed to parse JSON from stream:", e, line);
          }
        }
      }
    } catch (e: any) {
      setError(e.message || "An error occurred during the simulation.");
      console.error("Simulation error:", e);
    } finally {
      setIsSimulating(false);
    }
  };

  // Value provided by the context
  const contextValue = {
    scenarios,
    selectedScenarioId,
    selectedScenarioData,
    isLoadingScenarios,
    isLoadingDetails,
    isSimulating,
    simulationLog,
    error,
    selectScenario,
    createNewScenario,
    runSimulation,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};

// ==============================================================================
// 5. CUSTOM HOOK
// ==============================================================================

/**
 * A custom hook to easily consume the AppContext.
 * @returns {AppContextType} The context value.
 */
export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};
