/*
================================================================================
File: frontend/src/components/layout/MainLayout.tsx
Purpose: Defines the core two-column layout for the entire application.
         It creates the main container and background.
================================================================================
*/
import React from 'react';

type MainLayoutProps = {
  children: React.ReactNode;
};

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    // Main container with a dark background and flex layout
    <div className="bg-slate-900 text-slate-200 min-h-screen flex antialiased">
      {/* This is where the two main children components (Sidebar and ContentView)
        will be rendered side-by-side.
      */}
      {children}
    </div>
  );
};

export default MainLayout;
