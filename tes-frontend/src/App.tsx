// file: src/App.tsx (Corrected Version)

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { toast, Toaster } from 'react-hot-toast';
import * as apiClient from './services/apiClient';
import { ExperimentData, Node, Edge, ExperimentCreate, NodeType, EdgeRelation, NodeMetadata, ReasoningGraph } from "./schemas";


// --- Inline SVG Icons (with corrected types) ---
const MenuIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <line x1="4" x2="20" y1="12" y2="12" />
    <line x1="4" x2="20" y1="6" y2="6" />
    <line x1="4" x2="20" y1="18" y2="18" />
  </svg>
);
const XIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M18 6L6 18" />
    <path d="M6 6L18 18" />
  </svg>
);
const SendIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M22 2L11 13" />
    <path d="M22 2L15 22L11 13L2 9L22 2Z" />
  </svg>
);
const LoaderIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
  </svg>
);
const PlusIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M5 12h14" />
    <path d="M12 5v14" />
  </svg>
);
const WrenchIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94-7.94l-3.77 3.77a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0z" />
    <path d="M10.6 2.2a1 1 0 0 0-1.4 0L2.2 9.2a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1 7.94-7.94l-3.77 3.77z" />
    <path d="M18.5 12.5L12.5 18.5" />
    <path d="M17.7 18.3l-1.6-1.6" />
  </svg>
);
const SparklesIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M14.5 4.5L21 11m-4-7l-7 7m10 0L14 14m0-7l7 7" />
    <path d="M12 2L8.5 8.5L2 12l6.5 3.5L12 22l3.5-6.5L22 12l-6.5-3.5L12 2Z" />
  </svg>
);
const BrainIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M12 2a2.5 2.5 0 0 0-2.5 2.5v15a2.5 2.5 0 0 0 2.5 2.5v0" />
    <path d="M14 4.5A2.5 2.5 0 0 0 16.5 2V21a2.5 2.5 0 0 0-2.5-2.5v0" />
    <path d="M10 4.5A2.5 2.5 0 0 1 7.5 2V21a2.5 2.5 0 0 1 2.5-2.5v0" />
    <path d="M16 4.5a2.5 2.5 0 0 1 2.5-2.5v19a2.5 2.5 0 0 1-2.5-2.5v0" />
    <path d="M8 12.5H2a2 2 0 0 1-2-2v-1a2 2 0 0 1 2-2h6" />
    <path d="M16 12.5H22a2 2 0 0 0 2-2v-1a2 2 0 0 0-2-2h-6" />
  </svg>
);

// --- NEW COMPONENT: GardenPathMenu ---
const GardenPathMenu = ({ onSelectExperiment, onClose }: { onSelectExperiment: (name: string) => void, onClose: () => void }) => {
  return (
    <div className="fixed inset-0 bg-gray-950 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-black p-8 rounded-xl shadow-2xl max-w-sm w-full relative border border-gray-700">
        <button onClick={onClose} className="absolute top-3 right-3 text-gray-400 hover:text-white transition-colors">
          <XIcon />
        </button>
        <h3 className="text-xl font-bold mb-6 text-center text-white">Choose Your Thought Experiment</h3>
        <div className="space-y-4">
          <button
            onClick={() => onSelectExperiment("the_penrose_black_hole")}
            className="w-full text-center px-4 py-3 bg-fuchsia-600 hover:bg-fuchsia-500 rounded-lg transition-colors duration-200 text-lg font-semibold text-black"
          >
            The Penrose Black Hole
          </button>
          <button
            onClick={() => onSelectExperiment("the_turing_solution")}
            className="w-full text-center px-4 py-3 bg-fuchsia-600 hover:bg-fuchsia-500 rounded-lg transition-colors duration-200 text-lg font-semibold text-black"
          >
            The Turing Solution
          </button>
        </div>
      </div>
    </div>
  );
};

// --- MAIN COMPONENTS ---
const ChatSidebar = ({ conversations, activeConversationId, onSelectConversation, onNewConversation, onOpenGuidedMenu, isSidebarOpen, setIsSidebarOpen }: {
  conversations: ExperimentData[];
  activeConversationId: number | null;
  onSelectConversation: (id: number) => void;
  onNewConversation: () => void;
  onOpenGuidedMenu: () => void;
  isSidebarOpen: boolean;
  setIsSidebarOpen: (isOpen: boolean) => void;
}) => {
  const [showNewMenu, setShowNewMenu] = useState(false);

  return (
    <div
      className={`
        fixed inset-y-0 left-0 w-64 bg-gray-950 text-white z-40 transform transition-transform duration-300
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:h-screen
        p-4 flex flex-col
      `}
    >
      <div className="flex justify-between items-center mb-4 lg:mb-8">
        <h2 className="text-xl font-bold text-fuchsia-400">Thought Garden</h2>
        <button onClick={() => setIsSidebarOpen(false)} className="lg:hidden text-white hover:text-gray-300">
          <XIcon />
        </button>
      </div>
      <div className="space-y-2 mb-4">
        <div className="relative">
          <button
            onClick={() => setShowNewMenu(!showNewMenu)}
            className="flex items-center justify-center w-full px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors duration-200"
          >
            <PlusIcon /> New Session
          </button>
          {showNewMenu && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-gray-900 border border-gray-700 rounded-lg shadow-xl z-50">
              <button
                onClick={() => {
                  onNewConversation();
                  setShowNewMenu(false);
                }}
                className="w-full text-left px-4 py-3 text-sm text-gray-300 hover:bg-gray-700 transition-colors"
              >
                User-Driven
              </button>
            </div>
          )}
        </div>
        <div>
          <button
            onClick={onOpenGuidedMenu}
            className="flex items-center justify-center w-full px-4 py-2 bg-fuchsia-600 hover:bg-fuchsia-500 rounded-lg transition-colors duration-200 text-black font-semibold"
          >
            <WrenchIcon /> The Garden Path
          </button>
        </div>
      </div>
      <div className="flex-grow overflow-y-auto space-y-2">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            onClick={() => onSelectConversation(conv.id)}
            className={`
              p-3 rounded-lg cursor-pointer transition-colors duration-200
              ${conv.id === activeConversationId ? 'bg-fuchsia-600/20 text-fuchsia-400' : 'bg-gray-800 hover:bg-gray-700 text-gray-400'}
            `}
          >
            <p className="font-semibold">{conv.title}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

const NodeDisplay = ({ node }: { node: Node }) => {
  const isUserInput = node.type === 'user_input';
  const isAiExpansion = node.type === 'ai_expansion';

  return (
    <div className={`mb-4 flex ${isUserInput ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`p-4 rounded-lg shadow-lg max-w-lg ${
          isUserInput ? 'bg-fuchsia-600 text-black' : 'bg-gray-900 text-white border border-gray-800'
        }`}
      >
        <p className="font-bold text-sm text-gray-400 mb-2">{isUserInput ? 'User Input' : 'AI Expansion'}</p>
        <p>{node.content}</p>
      </div>
    </div>
  );
};

const ChatArea = ({ activeConversation, streamingNodeContent }: { activeConversation: ExperimentData | null, streamingNodeContent: string }) => {
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [activeConversation, streamingNodeContent]);

  if (!activeConversation) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 text-center text-gray-500">
        <p>Start a new session to begin a thought experiment.</p>
      </div>
    );
  }

  const nodesToDisplay = activeConversation.data.graph?.nodes || [];

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {nodesToDisplay.map((node) => (
          <NodeDisplay key={node.id} node={node} />
        ))}
        {streamingNodeContent && (
          <div className="flex justify-start mb-4">
            <div className="p-4 rounded-lg shadow-lg max-w-lg bg-gray-900 text-white border border-gray-800 animate-pulse">
              <p>{streamingNodeContent}</p>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>
    </div>
  );
};

const ChatInput = ({ onSendMessage, isLoading }: { onSendMessage: (content: string) => void, isLoading: boolean }) => {
  const [input, setInput] = useState('');

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <div className="p-4 bg-gray-900 border-t border-gray-700 flex items-center">
      <textarea
        id="chat-input"
        name="chat-input"
        className="flex-1 p-3 bg-gray-950 text-white rounded-lg resize-none placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-fuchsia-500 transition-shadow duration-200"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyPress}
        rows={1}
        placeholder={isLoading ? "Generating response..." : "What's on your mind?"}
        disabled={isLoading}
      />
      <button
        onClick={handleSubmit}
        disabled={isLoading}
        className={`
          ml-4 p-3 rounded-full text-black transition-colors duration-200
          ${isLoading ? 'bg-gray-700 cursor-not-allowed' : 'bg-fuchsia-600 hover:bg-fuchsia-500'}
        `}
      >
        {isLoading ? <LoaderIcon className="animate-spin text-white" /> : <SendIcon />}
      </button>
    </div>
  );
};

const ThoughtGardenApp = () => {
  const [conversations, setConversations] = useState<ExperimentData[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 1024);
  const [showGardenPathMenu, setShowGardenPathMenu] = useState(false);
  const [streamingNodeContent, setStreamingNodeContent] = useState('');

  useEffect(() => {
    const handleResize = () => {
      setIsDesktop(window.innerWidth >= 1024);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleNewConversation = useCallback(async (initialMessage: string = 'New Session') => {
    setIsLoading(true);
    try {
      const experimentIn: ExperimentCreate = {
        title: initialMessage.substring(0, 30) + '...',
        description: initialMessage,
      };
      const newExperiment = await apiClient.createExperiment(experimentIn);
      setConversations(prev => [newExperiment, ...prev]);
      setActiveConversationId(newExperiment.id);
      setIsSidebarOpen(false);
      setStreamingNodeContent('');
    } catch (e) {
      toast.error('Failed to start new conversation.');
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleSendMessage = async (content: string) => {
    let currentConvo = conversations.find(c => c.id === activeConversationId);
    
    // Logic to start a new conversation if one doesn't exist
    if (!currentConvo) {
      setIsLoading(true);
      try {
        const experimentIn: ExperimentCreate = {
          title: content.substring(0, 30) + '...',
          description: content,
        };
        const newExperiment = await apiClient.createExperiment(experimentIn);
        setConversations(prev => [newExperiment, ...prev]);
        setActiveConversationId(newExperiment.id);
        currentConvo = newExperiment;
      } catch (e) {
        toast.error('Failed to start new conversation.');
        console.error(e);
        setIsLoading(false);
        return;
      } finally {
        setIsLoading(false);
      }
    }

    // Optimistically update UI with user's message
    const newUserNode: Node = {
      id: `user-${Date.now()}`,
      type: 'user_input',
      content: content,
      metadata: {
        timestamp: new Date().toISOString(),
        depth: currentConvo.data.graph?.nodes.length || 0,
      }
    };

    const newGraphNodes = [...(currentConvo.data.graph?.nodes || []), newUserNode];

    setConversations(prev =>
      prev.map(conv =>
        conv.id === activeConversationId
          ? {
            ...conv,
            data: {
              ...conv.data,
              graph: {
                ...(conv.data.graph || { nodes: [], edges: [] }),
                nodes: newGraphNodes,
              }
            }
          }
          : conv
      )
    );

    setIsLoading(true);
    setStreamingNodeContent('');

    try {
      await apiClient.advanceConversationStream(currentConvo.id, content, {
        onStreamChunk: (chunk: string) => {
          setStreamingNodeContent(prev => prev + chunk);
        },
        onError: (error: string) => {
          toast.error(`Error: ${error}`);
          setIsLoading(false);
        },
        onClose: async () => {
          setIsLoading(false);
          // Fetch the final, updated experiment data from the database
          try {
            const finalExperiment = await apiClient.getExperiment(currentConvo.id);
            setConversations(prev =>
              prev.map(conv =>
                conv.id === activeConversationId ? finalExperiment : conv
              )
            );
          } catch (e) {
            toast.error('Failed to sync conversation history.');
            console.error(e);
          }
          setStreamingNodeContent('');
        },
      });
    } catch (e) {
      const error = e;
      if (typeof error === 'object' && error !== null && 'message' in error) {
        toast.error((error as { message: string }).message);
      } else {
        toast.error('An unknown error occurred.');
      }
      setIsLoading(false);
      setStreamingNodeContent('');
    }
  };

  const activeConversation = conversations.find(c => c.id === activeConversationId) || null;

  return (
    <div className="flex h-screen text-white font-sans">
      <Toaster position="bottom-right" reverseOrder={false} />

      {showGardenPathMenu && (
        <GardenPathMenu
          onSelectExperiment={() => {}}
          onClose={() => setShowGardenPathMenu(false)}
        />
      )}

      <ChatSidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={setActiveConversationId}
        onNewConversation={() => handleNewConversation()}
        onOpenGuidedMenu={() => setShowGardenPathMenu(true)}
        isSidebarOpen={isSidebarOpen}
        setIsSidebarOpen={setIsSidebarOpen}
      />

      <div className="flex-1 flex flex-col overflow-hidden relative">
        {!isDesktop && (
          <button onClick={() => setIsSidebarOpen(true)} className="p-4 text-white z-50 fixed top-0 left-0">
            <MenuIcon />
          </button>
        )}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          <ChatArea
            activeConversation={activeConversation}
            streamingNodeContent={streamingNodeContent}
          />
        </div>
        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default ThoughtGardenApp;