// file: tes-frontend/src/App.tsx (Corrected and Refactored from User's File)
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
            <PlusIcon /> Entrance
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
                Follow Me
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

  return (
    <div className={`mb-4 flex ${isUserInput ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`p-4 rounded-lg shadow-lg max-w-lg ${
          isUserInput ? 'bg-fuchsia-600 text-black' : 'bg-gray-900 text-white border border-gray-800'
        }`}
      >
        <p>{node.content}</p>
      </div>
    </div>
  );
};

const ChatArea = ({ activeConversation }: { activeConversation: ExperimentData | null }) => {
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [activeConversation]);

  if (!activeConversation) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 text-center text-gray-500">
        <p>Select "Entrance" to begin a new thought experiment.</p>
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

  useEffect(() => {
    const handleResize = () => {
      setIsDesktop(window.innerWidth >= 1024);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleNewConversation = useCallback(async () => {
    setIsLoading(true);
    setActiveConversationId(null);
    try {
      const experimentIn: ExperimentCreate = {
        title: "New Thought Experiment",
        description: "A new session initiated by the user.",
      };
      const newExperiment = await apiClient.createExperiment(experimentIn);

      // Add an initial greeting from Praxis
      const greetingNode: Node = {
        id: `ai-${Date.now()}`,
        type: 'ai_expansion',
        content: "Welcome. How shall we begin our shared thought experiment?",
        metadata: {
          timestamp: new Date().toISOString(),
          depth: 0,
        }
      };

      const updatedExperiment = {
        ...newExperiment,
        data: {
          ...newExperiment.data,
          graph: {
            nodes: [greetingNode],
            edges: [],
          }
        }
      };

      setConversations(prev => [updatedExperiment, ...prev]);
      setActiveConversationId(newExperiment.id);
      setIsSidebarOpen(false);
    } catch (e) {
      toast.error('Failed to start new conversation.');
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleSendMessage = async (content: string) => {
    let currentConvo = conversations.find(c => c.id === activeConversationId);
    
    if (!currentConvo) {
      toast.error('No active conversation selected.');
      return;
    }

    setIsLoading(true);

    const newUserNode: Node = {
      id: `user-${Date.now()}`,
      type: 'user_input',
      content: content,
      metadata: {
        timestamp: new Date().toISOString(),
        depth: currentConvo.data.graph?.nodes.length || 0,
      }
    };
    
    const tempAiNode: Node = {
        id: `ai-${Date.now()}`,
        type: 'ai_expansion',
        content: '',
        metadata: {
            timestamp: new Date().toISOString(),
            depth: (currentConvo.data.graph?.nodes.length || 0) + 1,
        }
    };

    const optimisticNodes = [...(currentConvo.data.graph?.nodes || []), newUserNode, tempAiNode];

    setConversations(prev =>
      prev.map(conv =>
        conv.id === activeConversationId
          ? {
            ...conv,
            data: {
              ...conv.data,
              graph: {
                ...(conv.data.graph || { nodes: [], edges: [] }),
                nodes: optimisticNodes,
              }
            }
          }
          : conv
      )
    );

    try {
      await apiClient.advanceConversationStream(currentConvo.id, content, {
        onStreamChunk: (chunk: string) => {
          setConversations(prev =>
            prev.map(conv => {
              if (conv.id !== activeConversationId) return conv;
              
              const updatedNodes = conv.data.graph.nodes.map(node => 
                node.id === tempAiNode.id 
                  ? { ...node, content: node.content + chunk } 
                  : node
              );

              return { ...conv, data: { ...conv.data, graph: { ...conv.data.graph, nodes: updatedNodes, edges: conv.data.graph.edges ?? [], } } };
            })
          );
        },
        onError: (error: string) => {
          toast.error(`Error: ${error}`);
          setIsLoading(false);
        },
        onClose: async () => {
          try {
            const finalExperiment = await apiClient.getExperiment(currentConvo!.id);
            setConversations(prev =>
              prev.map(conv =>
                conv.id === activeConversationId ? finalExperiment : conv
              )
            );
          } catch (e) {
            toast.error('Failed to sync final conversation history.');
            console.error(e);
          } finally {
            setIsLoading(false);
          }
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
        onNewConversation={handleNewConversation}
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
          />
        </div>
        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default ThoughtGardenApp;