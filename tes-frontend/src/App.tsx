import React, { createContext, useContext, useEffect, useState, ReactNode, useRef, useCallback } from 'react';
import { ChevronDown, ChevronRight, Plus, Send, User, Bot, MessageSquare, Circle, BrainCircuit } from 'lucide-react';

// Simple toast notification system
const toast = {
  success: (message: string) => console.log('✓', message),
  error: (message: string) => console.log('✗', message),
};

// Simple time formatting utility
const formatDistanceToNow = (date: Date) => {
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInMinutes = Math.floor(diffInMs / 60000);
  
  if (diffInMinutes < 1) return 'now';
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}h ago`;
  const diffInDays = Math.floor(diffInHours / 24);
  return `${diffInDays}d ago`;
};

// ==============================================================================
// 1. TYPES & INTERFACES
// ==============================================================================

interface PersonaDebate {
  persona: string;
  score: number;
  isWinner: boolean;
  reasoning: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  content: string | {
    debate: PersonaDebate[];
    responseText: string;
    leadPersona: string;
    internal_monologue?: string;
  };
}

interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  lastMessage: Date;
  type: 'user_driven' | 'journeyman';
  journeymanId?: string;
}

// ==============================================================================
// 2. MODERN MINIMALIST UI COMPONENTS
// ==============================================================================

const Button: React.FC<{
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  className?: string;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
}> = ({ children, onClick, variant = 'primary', className = '', disabled = false, size = 'md' }) => {
  const variantStyles = {
    primary: 'bg-pink-500 text-black hover:bg-pink-400 focus:ring-pink-500 font-medium',
    secondary: 'bg-gray-700 text-gray-300 hover:bg-gray-600 border border-gray-600 hover:border-gray-500', 
    ghost: 'bg-transparent text-gray-400 hover:text-pink-400 hover:bg-gray-900/50',
  };

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  return (
    <button
      className={`
        rounded transition-all duration-200 transform hover:scale-102 active:scale-98
        focus:outline-none focus:ring-1 focus:ring-offset-1 focus:ring-offset-black
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variantStyles[variant]} ${sizeStyles[size]} ${className}
      `}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

// ==============================================================================
// 3. MINIMALIST SIDEBAR COMPONENT
// ==============================================================================

const Sidebar: React.FC<{
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: (type: 'user_driven' | 'journeyman') => void;
}> = ({ conversations, activeConversationId, onSelectConversation, onNewConversation }) => {
  const [showNewMenu, setShowNewMenu] = useState(false);

  return (
    <div className="w-72 bg-black border-r border-gray-800 flex flex-col h-full">
      {/* Header */}
      <div className="p-6 border-b border-gray-800">
        <div className="mb-6">
          <h1 className="text-pink-400 text-lg font-light tracking-wide">THOUGHT GARDEN</h1>
          <p className="text-gray-500 text-xs mt-1 font-mono">PERSONA AI SYSTEM</p>
        </div>
        
        <div className="relative">
          <Button 
            variant="primary" 
            onClick={() => setShowNewMenu(!showNewMenu)}
            className="w-full flex items-center justify-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>NEW SESSION</span>
          </Button>
          
          {showNewMenu && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-gray-900 border border-gray-700 rounded shadow-xl z-50 animate-in fade-in duration-200">
              <button
                onClick={() => {
                  onNewConversation('user_driven');
                  setShowNewMenu(false);
                }}
                className="w-full px-4 py-3 text-left text-sm text-gray-300 hover:bg-gray-800 hover:text-pink-400 transition-colors border-b border-gray-700"
              >
                <div className="font-medium">USER-DRIVEN</div>
                <div className="text-xs text-gray-500 mt-1">Free exploration</div>
              </button>
              <button
                onClick={() => {
                  onNewConversation('journeyman');
                  setShowNewMenu(false);
                }}
                className="w-full px-4 py-3 text-left text-sm text-gray-300 hover:bg-gray-800 hover:text-pink-400 transition-colors"
              >
                <div className="font-medium">JOURNEYMAN</div>
                <div className="text-xs text-gray-500 mt-1">Guided exploration</div>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <div className="text-gray-600 text-xs font-mono mb-4 uppercase tracking-widest">
            ACTIVE SESSIONS
          </div>
          
          {conversations.length === 0 ? (
            <div className="text-gray-600 text-sm py-12 text-center">
              <div className="w-8 h-8 border border-gray-700 rounded mx-auto mb-4 flex items-center justify-center">
                <MessageSquare className="w-4 h-4" />
              </div>
              <div className="text-xs font-mono">NO ACTIVE SESSIONS</div>
            </div>
          ) : (
            <div className="space-y-2">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`p-3 cursor-pointer transition-all duration-200 border-l-2 hover:bg-gray-900/50 animate-in slide-in-from-left duration-300 ${
                    activeConversationId === conv.id 
                      ? 'bg-gray-900/80 border-l-pink-400 text-pink-400' 
                      : 'border-l-gray-800 text-gray-400 hover:border-l-gray-600'
                  }`}
                  onClick={() => onSelectConversation(conv.id)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-sm font-mono truncate flex-1">{conv.title}</div>
                    <Circle 
                      className={`w-2 h-2 ${
                        conv.type === 'journeyman' ? 'text-purple-500' : 'text-green-500'
                      }`} 
                      fill="currentColor"
                    />
                  </div>
                  <div className="text-xs opacity-70 font-mono">
                    {conv.messages.length} MSG
                  </div>
                  <div className="text-xs opacity-50 mt-1 font-mono">
                    {formatDistanceToNow(conv.lastMessage)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ==============================================================================
// 4. MINIMALIST MESSAGE COMPONENTS
// ==============================================================================

const UserMessage: React.FC<{ message: ChatMessage }> = ({ message }) => {
  return (
    <div className="flex justify-end mb-6 animate-in slide-in-from-right duration-300">
      <div className="max-w-2xl">
        <div className="bg-gray-900 border border-gray-700 p-4 text-gray-300">
          <div className="text-sm leading-relaxed whitespace-pre-wrap font-mono">
            {message.content as string}
          </div>
        </div>
        <div className="text-xs text-gray-600 mt-2 text-right font-mono">
          {formatDistanceToNow(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

const AssistantMessage: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const [showDebate, setShowDebate] = useState(false);
  const [showMonologue, setShowMonologue] = useState(false);

  const content = message.content as {
    debate: PersonaDebate[];
    responseText: string;
    leadPersona: string;
    internal_monologue?: string;
  };

  useEffect(() => {
    setDisplayedText('');
    setIsComplete(false);
    
    let index = 0;
    const interval = setInterval(() => {
      if (index < content.responseText.length) {
        setDisplayedText(content.responseText.slice(0, index + 1));
        index++;
      } else {
        setIsComplete(true);
        clearInterval(interval);
      }
    }, 20);

    return () => clearInterval(interval);
  }, [content.responseText]);

  return (
    <div className="flex justify-start mb-6 animate-in slide-in-from-left duration-300">
      <div className="max-w-2xl w-full">
        <div className="bg-black border border-gray-800 overflow-hidden">
          {/* Persona Debate Section */}
          <div className="border-b border-gray-800">
            <button
              onClick={() => setShowDebate(!showDebate)}
              className="w-full px-4 py-3 flex items-center justify-between text-left transition-colors hover:bg-gray-900/50"
            >
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 border border-gray-700 flex items-center justify-center">
                  <Bot className="w-3 h-3 text-pink-400" />
                </div>
                <span className="text-sm font-mono text-gray-400">INTERNAL PROCESS</span>
              </div>
              <ChevronRight className={`w-4 h-4 text-gray-600 transition-transform duration-200 ${showDebate ? 'rotate-90' : ''}`} />
            </button>
            
            {showDebate && (
              <div className="animate-in slide-in-from-top duration-300">
                <div className="px-4 pb-4">
                  <div className="space-y-2">
                    {content.debate.map((persona, index) => (
                      <div
                        key={index}
                        className={`flex items-center justify-between p-3 border animate-in fade-in duration-200 ${
                          persona.isWinner 
                            ? 'border-pink-500/30 bg-pink-500/5' 
                            : 'border-gray-700 bg-gray-900/30'
                        }`}
                        style={{ animationDelay: `${index * 100}ms` }}
                      >
                        <div className="flex items-center space-x-3">
                          <div className={`text-sm font-mono ${
                            persona.isWinner ? 'text-pink-400' : 'text-gray-500'
                          }`}>
                            {persona.persona.toUpperCase()}
                          </div>
                          {persona.isWinner && (
                            <span className="text-xs bg-pink-500 text-black px-2 py-1 font-mono">
                              LEAD
                            </span>
                          )}
                        </div>
                        <div className={`text-sm font-mono ${
                          persona.isWinner ? 'text-pink-400' : 'text-gray-600'
                        }`}>
                          {persona.score}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {content.internal_monologue && (
            <div className="border-b border-gray-800">
              <button
                onClick={() => setShowMonologue(!showMonologue)}
                className="w-full px-4 py-3 flex items-center justify-between text-left transition-colors hover:bg-gray-900/50"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-6 h-6 border border-gray-700 flex items-center justify-center">
                    <BrainCircuit className="w-3 h-3 text-gray-400" />
                  </div>
                  <span className="text-sm font-mono text-gray-400">INTERNAL MONOLOGUE</span>
                </div>
                <ChevronRight className={`w-4 h-4 text-gray-600 transition-transform duration-200 ${showMonologue ? 'rotate-90' : ''}`} />
              </button>
              
              {showMonologue && (
                <div className="animate-in slide-in-from-top duration-300">
                  <div className="p-4 text-xs font-mono text-gray-500 italic border-l-2 border-gray-700 ml-6 pl-4 leading-relaxed">
                    {content.internal_monologue}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Response Section */}
          <div className="p-4">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-6 h-6 bg-pink-500 flex items-center justify-center">
                <Bot className="w-3 h-3 text-black" />
              </div>
              <span className="text-sm font-mono text-pink-400">{content.leadPersona.toUpperCase()}</span>
            </div>
            <div className="text-sm leading-relaxed text-gray-300 whitespace-pre-wrap font-mono">
              {displayedText}
              {!isComplete && (
                <span className="text-pink-400 animate-pulse">▌</span>
              )}
            </div>
          </div>
        </div>
        
        <div className="text-xs text-gray-600 mt-2 font-mono">
          {formatDistanceToNow(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

// ==============================================================================
// 5. MINIMALIST CHAT AREA
// ==============================================================================

const ChatArea: React.FC<{
  activeConversation: Conversation | null;
  onSendMessage: (content: string) => void;
  isLoading: boolean;
}> = ({ activeConversation, onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeConversation?.messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!activeConversation) {
    return (
      <div className="flex-1 flex items-center justify-center bg-black">
        <div className="text-center max-w-md animate-in fade-in duration-500">
          <div className="w-16 h-16 border border-gray-800 mx-auto mb-6 flex items-center justify-center">
            <MessageSquare className="w-6 h-6 text-pink-400" />
          </div>
          <h2 className="text-xl font-light text-pink-400 mb-3 font-mono tracking-wide">
            THOUGHT GARDEN
          </h2>
          <p className="text-gray-500 text-sm font-mono leading-relaxed">
            Select a session from the sidebar or initialize<br />
            a new conversation to begin exploration
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-black">
      {/* Chat Header */}
      <div className="bg-gray-900/50 border-b border-gray-800 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-pink-400 text-lg font-mono tracking-wide">
              {activeConversation.title.toUpperCase()}
            </h1>
            <p className="text-sm text-gray-600 flex items-center space-x-4 mt-1 font-mono">
              <span>{activeConversation.messages.length} MESSAGES</span>
              <span className="flex items-center space-x-2">
                <Circle 
                  className={`w-2 h-2 ${
                    activeConversation.type === 'journeyman' ? 'text-purple-500' : 'text-green-500'
                  }`}
                  fill="currentColor"
                />
                <span>{activeConversation.type.toUpperCase().replace('_', '-')}</span>
              </span>
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-pink-400 rounded-full animate-pulse" />
            <span className="text-xs text-gray-500 font-mono">CONNECTED</span>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          {activeConversation.messages.map((message) => {
            if (message.role === 'user') {
              return <UserMessage key={message.id} message={message} />;
            } else {
              return <AssistantMessage key={message.id} message={message} />;
            }
          })}
          
          {isLoading && (
            <div className="flex justify-start mb-6 animate-in fade-in duration-300">
              <div className="max-w-2xl">
                <div className="bg-black border border-gray-800 p-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-6 h-6 border border-gray-700 flex items-center justify-center">
                      <Bot className="w-3 h-3 text-pink-400" />
                    </div>
                    <span className="text-sm text-gray-500 font-mono">PROCESSING</span>
                    <div className="flex space-x-1">
                      {[0, 1, 2].map((i) => (
                        <div
                          key={i}
                          className="w-1 h-1 bg-pink-400 animate-pulse"
                          style={{ animationDelay: `${i * 200}ms` }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-800 bg-gray-900/30 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-4">
            <div className="flex-1">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter your query..."
                className="w-full bg-black text-gray-300 border border-gray-800 p-4 focus:outline-none focus:ring-1 focus:ring-pink-500 focus:border-pink-500 resize-none font-mono text-sm"
                rows={1}
                disabled={isLoading}
                style={{ minHeight: '52px', maxHeight: '120px' }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = '52px';
                  target.style.height = Math.min(target.scrollHeight, 120) + 'px';
                }}
              />
            </div>
            <Button 
              onClick={handleSendMessage} 
              disabled={isLoading || !input.trim()}
              variant="primary"
              className="flex items-center space-x-2 h-[52px]"
            >
              <Send className="w-4 h-4" />
              <span className="font-mono">SEND</span>
            </Button>
          </div>
          
          <div className="mt-3 text-xs text-gray-600 flex justify-between font-mono">
            <span>ENTER TO SEND / SHIFT+ENTER FOR NEW LINE</span>
            <span>PERSONA AI SYSTEM V1.0</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==============================================================================
// 6. MAIN APP COMPONENT
// ==============================================================================

export default function ThoughtGardenApp() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const API_URL = "http://127.0.0.1:8000/api";

  const createNewConversation = async (type: 'user_driven' | 'journeyman') => {
    setIsLoading(true);
    let newExperimentId: string | null = null;
    
    try {
      console.log(`Starting new ${type} conversation...`);
      // Step 1: Create the experiment record on the backend
      const createResponse = await fetch(`${API_URL}/experiments/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: type === 'journeyman' ? 'New Journeyman Journey' : 'New User-Driven Session',
          description: "Session created from frontend" 
        }),
      });

      if (!createResponse.ok) {
        throw new Error('Failed to create experiment on the backend');
      }
      const newExperiment = await createResponse.json();
      newExperimentId = newExperiment.id.toString();
      console.log(`Experiment created with ID: ${newExperimentId}`);

      let secondApiResponse;
      let initialPrompt: string | undefined;
      let title: string = newExperiment.title;

      // Step 2: Make the second API call to start the journey and get the first message
      if (type === 'user_driven') {
        initialPrompt = "What if sleep was no longer biologically necessary for humans?";
        console.log(`Calling backend to start user-driven journey with prompt: "${initialPrompt}"`);
        secondApiResponse = await fetch(`${API_URL}/experiments/${newExperimentId}/start_user_driven`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_input: initialPrompt })
        });
        title = initialPrompt.slice(0, 30) + (initialPrompt.length > 30 ? '...' : '');

      } else { // Journeyman
        const journeymanScriptName = 'ship_of_theseus';
        console.log(`Calling backend to start journeyman journey with script: "${journeymanScriptName}"`);
        secondApiResponse = await fetch(`${API_URL}/experiments/${newExperimentId}/start_interactive`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ script_name: journeymanScriptName })
        });
      }

      if (!secondApiResponse.ok) {
        const errorText = await secondApiResponse.text();
        console.error("Backend error response:", errorText);
        throw new Error(`Failed to start the journey on the backend. Status: ${secondApiResponse.status}. Details: ${errorText}`);
      }

      const updatedExperiment = await secondApiResponse.json();
      const journey = updatedExperiment.data.journey || [];
      const firstJourneyStep = journey[journey.length - 1];

      if (!firstJourneyStep || !firstJourneyStep.cam_result) {
        throw new Error("Invalid response structure from backend");
      }
      console.log("Successfully received first turn data:", firstJourneyStep);

      const debateData = Object.entries(firstJourneyStep.cam_result.scores).map(([name, score]) => ({
          persona: name,
          score: score as number,
          isWinner: name === firstJourneyStep.cam_result.winner,
          reasoning: name === firstJourneyStep.cam_result.winner ? 'Primary alignment' : 'Supporting vector'
      }));

      // Construct the complete message list for the new conversation
      const messages: ChatMessage[] = [];
      if (initialPrompt) {
        messages.push({
          id: Date.now().toString(),
          role: 'user',
          content: initialPrompt,
          timestamp: new Date()
        });
      }

      messages.push({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        timestamp: new Date(),
        content: {
          debate: debateData,
          responseText: firstJourneyStep.dilemma_text,
          leadPersona: firstJourneyStep.cam_result.winner,
          internal_monologue: firstJourneyStep.internal_monologue
        }
      });
      
      // Step 3: Update state with the final, complete conversation object
      const newConv: Conversation = {
        id: newExperimentId,
        title: title,
        type,
        messages: messages,
        lastMessage: new Date(),
        journeymanId: type === 'journeyman' ? 'ship_of_theseus' : undefined,
      };

      setConversations(prev => [newConv, ...prev]);
      setActiveConversationId(newExperimentId);
      toast.success(`${type === 'journeyman' ? 'Journeyman' : 'User-Driven'} session started`);

    } catch (error) {
      console.error("Failed to create new conversation:", error);
      toast.error('Could not start a new session. Is the backend server running? Check console for details.');
      if (newExperimentId) {
        setConversations(prev => prev.filter(c => c.id !== newExperimentId));
      }
      setActiveConversationId(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!activeConversationId) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    
    const activeConv = conversations.find(c => c.id === activeConversationId);
    if (!activeConv) return;

    setConversations(prev => prev.map(conv => {
      if (conv.id === activeConversationId) {
        return {
          ...conv,
          messages: [...conv.messages, userMessage],
          lastMessage: new Date(),
          title: conv.messages.length === 1 ? content.slice(0, 30) + (content.length > 30 ? '...' : '') : conv.title
        };
      }
      return conv;
    }));

    setIsLoading(true);

    try {
      const endpoint = `${API_URL}/experiments/${activeConversationId}/advance`;
      
      const payload = {
        step_id: activeConv.messages.length,
        choice_id: 1, 
        user_input: content
      };
      
      console.log("Sending advance request with payload:", payload);

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const err = await response.json();
        console.error("Backend advance error response:", err);
        throw new Error(err.detail || 'API request failed');
      }

      const updatedExperiment = await response.json();
      const journey = updatedExperiment.data.journey || [];
      const lastJourneyStep = journey[journey.length - 1];

      if (!lastJourneyStep || !lastJourneyStep.cam_result) {
        throw new Error("Invalid response structure from backend");
      }
      console.log("Successfully received next turn data:", lastJourneyStep);

      const debateData = Object.entries(lastJourneyStep.cam_result.scores).map(([name, score]) => ({
          persona: name,
          score: score as number,
          isWinner: name === lastJourneyStep.cam_result.winner,
          reasoning: name === lastJourneyStep.cam_result.winner ? 'Primary alignment' : 'Supporting vector'
      }));

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        timestamp: new Date(),
        content: {
          debate: debateData,
          responseText: lastJourneyStep.dilemma_text,
          leadPersona: lastJourneyStep.cam_result.winner,
          internal_monologue: lastJourneyStep.internal_monologue
        }
      };
      
      setConversations(prev => prev.map(conv => {
        if (conv.id === activeConversationId) {
          return { ...conv, messages: [...conv.messages, assistantMessage] };
        }
        return conv;
      }));

    } catch (error) {
      console.error("Failed to send message:", error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        timestamp: new Date(),
        content: {
          debate: [],
          responseText: `Error: Could not get a response from the engine.\n\n${(error as Error).message}`,
          leadPersona: 'System'
        }
      };
       setConversations(prev => prev.map(conv => {
        if (conv.id === activeConversationId) {
          return { ...conv, messages: [...conv.messages, errorMessage] };
        }
        return conv;
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const activeConversation = conversations.find(c => c.id === activeConversationId) || null;

  return (
    <div className="bg-black min-h-screen flex font-mono antialiased">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={setActiveConversationId}
        onNewConversation={createNewConversation}
      />
      
      <ChatArea
        activeConversation={activeConversation}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
      />
    </div>
  );
}