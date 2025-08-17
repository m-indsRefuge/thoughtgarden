// ==============================================================================
// 1. FIXED DebateView.tsx
// ==============================================================================

import React, { useState } from 'react';

interface DebateMessage {
  id: string;
  speaker: string;
  message: string;
  timestamp: Date;
  side: 'pro' | 'con';
}

interface DebateViewProps {
  topic?: string;
  onClose?: () => void;
}

const DebateView: React.FC<DebateViewProps> = ({ 
  topic = "The Nature of Consciousness", 
  onClose 
}) => {
  const [messages, setMessages] = useState<DebateMessage[]>([
    {
      id: '1',
      speaker: 'Materialist',
      message: 'Consciousness is nothing more than the result of complex neural processes in the brain.',
      timestamp: new Date(),
      side: 'pro'
    },
    {
      id: '2', 
      speaker: 'Dualist',
      message: 'But how can subjective experience emerge from mere matter? There must be something beyond the physical.',
      timestamp: new Date(),
      side: 'con'
    }
  ]);

  const [newMessage, setNewMessage] = useState('');
  const [selectedSide, setSelectedSide] = useState<'pro' | 'con'>('pro');

  const handleAddMessage = () => {
    if (!newMessage.trim()) return;

    const message: DebateMessage = {
      id: Date.now().toString(),
      speaker: selectedSide === 'pro' ? 'Supporter' : 'Opponent',
      message: newMessage,
      timestamp: new Date(),
      side: selectedSide
    };

    setMessages(prev => [...prev, message]);
    setNewMessage('');
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Debate: {topic}</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ✕
          </button>
        )}
      </div>

      {/* Debate Messages */}
      <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.side === 'pro' ? 'justify-start' : 'justify-end'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                msg.side === 'pro'
                  ? 'bg-blue-100 text-blue-900'
                  : 'bg-red-100 text-red-900'
              }`}
            >
              <div className="font-semibold text-sm mb-1">{msg.speaker}</div>
              <div className="text-sm">{msg.message}</div>
              <div className="text-xs opacity-60 mt-1">
                {msg.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Add Message Form */}
      <div className="border-t pt-4">
        <div className="flex gap-2 mb-3">
          <button
            onClick={() => setSelectedSide('pro')}
            className={`px-3 py-1 rounded text-sm ${
              selectedSide === 'pro'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Pro Side
          </button>
          <button
            onClick={() => setSelectedSide('con')}
            className={`px-3 py-1 rounded text-sm ${
              selectedSide === 'con'
                ? 'bg-red-500 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Con Side
          </button>
        </div>
        
        <div className="flex gap-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Add your argument..."
            className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:border-blue-500"
            onKeyPress={(e) => e.key === 'Enter' && handleAddMessage()}
          />
          <button
            onClick={handleAddMessage}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Add
          </button>
        </div>
      </div>
    </div>
  );
};

export default DebateView;