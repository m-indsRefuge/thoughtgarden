/*
================================================================================
File: frontend/src/components/organisms/ContentView.tsx
Purpose: The main content area on the right. It will display the details
         of the selected experiment or the live simulation.
================================================================================
*/
import React from 'react';

type ContentViewProps = {
  title?: string;
  content?: string;
};

const ContentView: React.FC<ContentViewProps> = ({
  title = "Welcome to your Thought Garden",
  content = "Select a thought from your garden on the left, or plant a new seed by clicking 'New Thought'."
}) => {
  return (
    <main className="flex-1 p-12 overflow-y-auto">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white border-b border-slate-700 pb-4 mb-8">
          {title}
        </h1>
        <div className="prose prose-invert prose-lg max-w-none text-slate-300">
          {/* The 'prose' classes from Tailwind provide beautiful default styling 
            for blocks of text, which will be perfect for displaying the AI's output.
          */}
          <p>{content}</p>
        </div>
      </div>
    </main>
  );
};

export default ContentView;
