/*
================================================================================
File: frontend/src/components/organisms/HistorySidebar.tsx
Purpose: The left sidebar component. It displays the "Thought Garden" title,
         a button to create a new experiment, and a list of past experiments.
================================================================================
*/
import React from 'react';
import Button from '../atoms/Button';

// Define the shape of our experiment data for type safety
type Experiment = {
  id: number;
  title: string;
};

type HistorySidebarProps = {
  experiments: Experiment[];
  selectedExperimentId: number | null;
  onSelectExperiment: (id: number) => void;
  onNewExperiment: () => void;
};

// A simple SVG icon for the "New Thought" button
const PlusIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
);

const HistorySidebar: React.FC<HistorySidebarProps> = ({
  experiments,
  selectedExperimentId,
  onSelectExperiment,
  onNewExperiment,
}) => {
  return (
    <aside className="w-80 bg-slate-800/50 p-6 flex flex-col border-r border-slate-700">
      <div className="flex items-center mb-8">
        {/* Placeholder for a logo */}
        <div className="w-8 h-8 bg-fuchsia-500 rounded-lg mr-3"></div>
        <h1 className="text-xl font-bold text-white">Thought Garden</h1>
      </div>

      <Button onClick={onNewExperiment} className="w-full flex items-center justify-center">
        <PlusIcon />
        New Thought
      </Button>

      <div className="mt-8 flex-grow overflow-y-auto">
        <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          Your Garden
        </h2>
        <nav className="flex flex-col gap-1">
          {experiments.map((exp) => (
            <a
              key={exp.id}
              href="#"
              onClick={(e) => {
                e.preventDefault();
                onSelectExperiment(exp.id);
              }}
              className={`
                px-3 py-2 rounded-md text-sm font-medium transition-colors duration-150
                truncate
                ${
                  selectedExperimentId === exp.id
                    ? 'bg-fuchsia-600/20 text-fuchsia-400'
                    : 'text-slate-300 hover:bg-slate-700/50'
                }
              `}
            >
              {exp.title}
            </a>
          ))}
        </nav>
      </div>
    </aside>
  );
};

export default HistorySidebar;
