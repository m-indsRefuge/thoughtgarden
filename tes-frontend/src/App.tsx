import React, { useState, useEffect, useRef, useCallback } from 'react';
import { toast, Toaster } from 'react-hot-toast';
import * as apiClient from './services/apiClient';

// --- Inline SVG Icons ---
const MenuIcon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <line x1="4" x2="20" y1="12" y2="12" />
    <line x1="4" x2="20" y1="6" y2="6" />
    <line x1="4" x2="20" y1="18" y2="18" />
  </svg>
);
const XIcon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M18 6L6 18" />
    <path d="M6 6L18 18" />
  </svg>
);
const SendIcon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M22 2L11 13" />
    <path d="M22 2L15 22L11 13L2 9L22 2Z" />
  </svg>
);
const LoaderIcon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M21 12a9 9 0 1 1-6.219-8.56" />
  </svg>
);
const PlusIcon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M5 12h14" />
    <path d="M12 5v14" />
  </svg>
);
const WrenchIcon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94-7.94l-3.77 3.77a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0z" />
    <path d="M10.6 2.2a1 1 0 0 0-1.4 0L2.2 9.2a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1 7.94-7.94l-3.77 3.77z" />
    <path d="M18.5 12.5L12.5 18.5" />
    <path d="M17.7 18.3l-1.6-1.6" />
  </svg>
);
const SparklesIcon = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M14.5 4.5L21 11m-4-7l-7 7m10 0L14 14m0-7l7 7" />
    <path d="M12 2L8.5 8.5L2 12l6.5 3.5L12 22l3.5-6.5L22 12l-6.5-3.5L12 2Z" />
  </svg>
);
const BrainIcon = (props) => (
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
const GardenPathMenu = ({ onSelectExperiment, onClose }) => {
  return (
    <div className="fixed inset-0 bg-gray-950 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-black p-8 rounded-xl shadow-2xl max-w-sm w-full relative border border-gray-700">
        <button onClick={onClose} className="absolute top-3 right-3 text-gray-400 hover:text-white transition-colors">
          <XIcon size={24} />
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
const ChatSidebar = ({ conversations, activeConversationId, onSelectConversation, onNewConversation, onOpenGuidedMenu, isSidebarOpen, setIsSidebarOpen }) => {
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
          <XIcon size={24} />
        </button>
      </div>
      <div className="space-y-2 mb-4">
        <div className="relative">
          <button 
            onClick={() => setShowNewMenu(!showNewMenu)}
            className="flex items-center justify-center w-full px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors duration-200"
          >
            <PlusIcon size={20} className="mr-2" /> New Session
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
            <WrenchIcon size={20} className="mr-2" /> The Garden Path
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

const UserMessage = ({ message }) => {
  return (
    <div className="flex justify-end mb-4">
      <div className="bg-gray-800 text-white p-4 rounded-lg max-w-lg shadow-lg">
        {typeof message.content === 'string' && <p>{message.content}</p>}
      </div>
    </div>
  );
};

const AssistantMessage = ({ message, isStreaming = false, streamingContent }) => {
  const content = isStreaming ? streamingContent : (message.content);

  if (!content) return null;

  return (
    <div className="flex justify-start mb-6">
      <div className="bg-gray-900 text-white p-6 rounded-lg max-w-3xl shadow-lg relative border border-gray-800">
        <div className="absolute top-0 right-0 p-2 opacity-50">
          {isStreaming ? (
            <SparklesIcon className="animate-pulse text-fuchsia-400" size={18} />
          ) : (
            <SparklesIcon className="text-fuchsia-400" size={18} />
          )}
        </div>
        
        {/* Internal Monologue Section */}
        <div className="bg-gray-800 p-4 rounded-lg mb-4 text-gray-300 border border-gray-700 shadow-inner">
          <h4 className="font-bold text-sm text-gray-400 mb-2 flex items-center"><BrainIcon className="mr-2 text-gray-500" />Mind's Eye..</h4>
          {content.monologue ? (
            <p className="text-sm italic">{content.monologue}</p>
          ) : (
            <p className="text-sm italic animate-pulse">Thinking..</p>
          )}
        </div>

        {/* Debate Section */}
        <div className="mb-4">
          <h4 className="font-bold text-sm text-gray-400 mb-2 flex items-center"><WrenchIcon className="mr-2 text-gray-500" />The Internal Struggle..</h4>
          {content.debate.length > 0 ? (
            <div className="space-y-2">
              {content.debate.map((arg, index) => (
                <div key={index} className="bg-gray-950 p-3 rounded-lg border border-gray-800">
                  <div className="flex justify-between items-start mb-1">
                    <p className="font-semibold text-xs text-fuchsia-400">{arg.persona || arg.persona_id}:</p>
                    {arg.score && <span className="text-xs text-gray-500">({arg.score})</span>}
                  </div>
                  <p className="text-sm text-gray-300">{arg.argument || arg.argument_text}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500 italic">The Internal Struggle...</p>
          )}
        </div>

        {/* Final Question/Response Section */}
        <div className="border-t pt-4 border-gray-700">
          <h4 className="font-bold text-sm text-gray-400 mb-2">Consider This..</h4>
          {content.question || content.ai_question_to_user ? (
            <p className="font-semibold text-lg">{content.question || content.ai_question_to_user}</p>
          ) : (
            <p className="text-lg text-gray-500 italic animate-pulse">Talking...</p>
          )}
        </div>
      </div>
    </div>
  );
};

const ChatArea = ({ activeConversation, streamingTurn }) => {
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [activeConversation, streamingTurn]);

  if (!activeConversation) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 text-center text-gray-500">
        <p>Start a new session to begin a thought experiment.</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-y-auto p-4 space-y-6">
      {activeConversation.messages.map((message, index) => {
        const isLastMessage = index === activeConversation.messages.length - 1;
        if (message.role === 'user') {
          return <UserMessage key={message.id} message={message} />;
        }
        if (isLastMessage && streamingTurn.monologue) {
          return <AssistantMessage key={message.id} message={message} isStreaming={true} streamingContent={streamingTurn} />;
        }
        return <AssistantMessage key={message.id} message={message} />;
      })}
      <div ref={chatEndRef} />
    </div>
  );
};

const ChatInput = ({ onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');

  const handleKeyPress = (e) => {
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
        {isLoading ? <LoaderIcon size={24} className="animate-spin text-white" /> : <SendIcon size={24} />}
      </button>
    </div>
  );
};

const ThoughtGardenApp = () => {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 1024);
  const [showGardenPathMenu, setShowGardenPathMenu] = useState(false);
  const streamingContentRef = useRef({ debate: [], monologue: '', question: '' });

  useEffect(() => {
    const handleResize = () => {
      setIsDesktop(window.innerWidth >= 1024);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const [streamingTurn, setStreamingTurn] = useState({
    debate: [],
    monologue: '',
    question: ''
  });

  const handleNewConversation = useCallback(() => {
    const newId = `temp-${Date.now()}`;
    const newConversation = {
      id: newId,
      title: 'New Session',
      messages: [],
      createdAt: new Date(),
      lastUpdatedAt: new Date(),
    };
    setConversations(prev => [newConversation, ...prev]);
    setActiveConversationId(newId);
    setIsSidebarOpen(false);
  }, []);

  const handleNewGuidedSession = useCallback(async (scriptName) => {
    console.log(`Starting a new Guided session with script: ${scriptName}...`);
    toast.success(`Starting a new Guided Session!`);
    
    try {
      const journeyTurn = await apiClient.startGardenPath(scriptName);
      const newId = journeyTurn.experiment_id.toString();
      const newConversation = {
        id: newId,
        title: scriptName.split('_').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' '),
        messages: [
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: { question: journeyTurn.narrative, debate: [], monologue: 'Journey initialized...' },
            timestamp: new Date()
          }
        ],
        createdAt: new Date(),
        lastUpdatedAt: new Date(),
      };
      setConversations(prev => [newConversation, ...prev]);
      setActiveConversationId(newId);
      setIsSidebarOpen(false);
      setShowGardenPathMenu(false); // Close the menu
    } catch (error) {
      console.error("Failed to start Guided session:", error);
      toast.error("Failed to start Guided session");
    }
  }, []);

  const handleSendMessage = async (content) => {
    const currentConvoId = activeConversationId;
    if (!currentConvoId) return;

    const userMessage = { id: Date.now().toString(), role: 'user', content, timestamp: new Date() };
    const assistantPlaceholder = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      timestamp: new Date(),
      content: { turn_number: 0, user_message: content, debate: [], internal_monologue: '', ai_question_to_user: '' }
    };

    setConversations(prev =>
      prev.map(conv =>
        conv.id === currentConvoId
          ? { ...conv, messages: [...conv.messages, userMessage, assistantPlaceholder] }
          : conv
      )
    );

    setIsLoading(true);
    setStreamingTurn({ debate: [], monologue: '', question: '' });
    streamingContentRef.current = { debate: [], monologue: '', question: '' };

    try {
      let finalConvoId = currentConvoId;
      let experimentId = null;

      if (currentConvoId.startsWith('temp-')) {
        const newExperiment = await apiClient.createExperiment("User-Driven Session", content);
        finalConvoId = newExperiment.id.toString();
        experimentId = newExperiment.id;

        setConversations(prev =>
          prev.map(c =>
            c.id === currentConvoId
              ? { ...c, id: finalConvoId, title: content.slice(0, 30) + '...' }
              : c
          )
        );
        setActiveConversationId(finalConvoId);
      } else {
        experimentId = parseInt(currentConvoId, 10);
      }

      await apiClient.advanceConversationStream(experimentId, content, {
        onDebate: (debate) => {
          streamingContentRef.current.debate = debate;
          setStreamingTurn(prev => ({ ...prev, debate }));
        },
        onMonologueChunk: (chunk) => {
          streamingContentRef.current.monologue += chunk;
          setStreamingTurn(prev => ({ ...prev, monologue: streamingContentRef.current.monologue }));
        },
        onQuestion: (question) => {
          streamingContentRef.current.question = question;
          setStreamingTurn(prev => ({ ...prev, question }));
        },
        onError: (error) => {
          toast.error(error);
          setIsLoading(false);
        },
        onClose: () => {
          const finalTurnData = {
            turn_number: 0,
            user_message: content,
            debate: streamingContentRef.current.debate,
            internal_monologue: streamingContentRef.current.monologue,
            ai_question_to_user: streamingContentRef.current.question,
          };

          setConversations(prev =>
            prev.map(conv =>
              conv.id === finalConvoId
                ? { ...conv, messages: [...conv.messages.slice(0, -1), { ...assistantPlaceholder, content: finalTurnData }] }
                : conv
            )
          );
          setIsLoading(false);
        },
      });

    } catch (e) {
      const error = e;
      toast.error(error.message);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (conversations.length === 0) {
      handleNewConversation();
    }
  }, [conversations, handleNewConversation]);

  const activeConversation = conversations.find(c => c.id === activeConversationId) || null;

  return (
    <div className="flex h-screen text-white font-sans">
      <Toaster position="bottom-right" reverseOrder={false} />
      
      {showGardenPathMenu && (
        <GardenPathMenu
          onSelectExperiment={handleNewGuidedSession}
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
            <MenuIcon size={24} />
          </button>
        )}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          <ChatArea
            activeConversation={activeConversation}
            streamingTurn={streamingTurn}
          />
        </div>
        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default ThoughtGardenApp;