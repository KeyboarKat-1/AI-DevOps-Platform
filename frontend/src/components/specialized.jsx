import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle, X } from 'lucide-react';
import { Card, Button, LoadingSpinner } from './common';
import { insightsService } from '../services/api';

export const AIAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'Hello! I\'m your AI DevOps Assistant. How can I help you today?',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEnd = useRef(null);

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      text: input,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await insightsService.getAISuggestions(input);
      const botMessage = {
        id: messages.length + 2,
        text: response.data?.suggestion || 'I\'m processing your request...',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: messages.length + 2,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-primary-600 to-primary-500 rounded-full shadow-glow-lg hover:shadow-glow flex items-center justify-center z-40 hover:scale-110 transition-transform"
      >
        <MessageCircle className="w-6 h-6 text-white" />
      </button>
    );
  }

  return (
    <Card className="fixed bottom-6 right-6 w-96 max-w-[calc(100vw-24px)] h-screen max-h-[600px] flex flex-col z-50 shadow-glow-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <h3 className="font-semibold text-white">AI Assistant</h3>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="btn-icon text-dark-400 hover:text-white"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                msg.sender === 'user'
                  ? 'bg-primary-600/30 text-primary-200'
                  : 'bg-dark-700/50 text-white'
              }`}
            >
              <p className="text-sm">{msg.text}</p>
              <span className="text-xs opacity-50 mt-1 block">
                {msg.timestamp.toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-dark-700/50 px-4 py-3 rounded-lg">
              <LoadingSpinner size="sm" />
            </div>
          </div>
        )}
        <div ref={messagesEnd} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask me anything..."
            className="flex-1 input-field text-sm"
            disabled={loading}
          />
          <button
            onClick={handleSendMessage}
            disabled={loading || !input.trim()}
            className="btn-primary p-2 disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </Card>
  );
};

export const SuggestionPanel = ({ suggestions }) => {
  return (
    <Card className="p-6 animate-fade-in">
      <h3 className="text-lg font-semibold mb-4 text-white">
        AI Suggestions & Insights
      </h3>
      <div className="space-y-3">
        {suggestions && suggestions.map((suggestion, idx) => (
          <div key={idx} className="p-3 bg-primary-900/20 border border-primary-700/30 rounded-lg">
            <p className="text-sm text-primary-200">{suggestion.text}</p>
            {suggestion.action && (
              <Button size="sm" className="mt-2">
                {suggestion.action}
              </Button>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
};

export const HealthIndicator = ({ status, label }) => {
  const statusConfig = {
    healthy: {
      color: 'bg-green-500',
      label: 'Healthy',
      pulse: true,
    },
    warning: {
      color: 'bg-yellow-500',
      label: 'Warning',
      pulse: false,
    },
    critical: {
      color: 'bg-red-500',
      label: 'Critical',
      pulse: true,
    },
  };

  const config = statusConfig[status] || statusConfig.healthy;

  return (
    <div className="flex items-center gap-3">
      <div
        className={`w-3 h-3 rounded-full ${config.color} ${
          config.pulse ? 'animate-pulse' : ''
        }`}
      />
      <span className="text-sm text-white">{label}</span>
    </div>
  );
};
