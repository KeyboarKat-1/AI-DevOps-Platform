import React, { useState } from 'react';
import { MessageCircle, Send, Zap } from 'lucide-react';
import { Card, Button, Input } from '../components';
import { insightsService } from '../services/api';

export const AIAssistantPage = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'Hello! I\'m your AI DevOps Assistant. I can help you with system monitoring, troubleshooting, and optimization. What would you like to know?',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const suggestedQuestions = [
    'What containers are using the most CPU?',
    'How is the system health looking?',
    'Show me recent deployment issues',
    'Optimize my Docker setup',
  ];

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      text: input,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await insightsService.getAISuggestions(input);
      const suggestion = response.data?.suggestion || 'I\'m analyzing your request now.';
      const botMessage = {
        id: messages.length + 2,
        text: suggestion,
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error fetching AI suggestion:', error);
      const botMessage = {
        id: messages.length + 2,
        text: 'Sorry, I could not fetch an answer from the AI service. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestedQuestion = (question) => {
    setInput(question);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">AI Assistant</h1>
        <p className="text-dark-400 mt-1">Get intelligent insights and recommendations</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chat */}
        <div className="lg:col-span-2">
          <Card className="p-6 h-96 lg:h-full flex flex-col">
            <div className="flex-1 overflow-y-auto space-y-4 mb-6">
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
                    <div className="flex gap-2">
                      <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce delay-100" />
                      <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce delay-200" />
                    </div>
                  </div>
                </div>
              )}
            </div>

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
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <Card className="p-6">
            <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-primary-400" />
              Suggested Questions
            </h3>
            <div className="space-y-3">
              {suggestedQuestions.map((question, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSuggestedQuestion(question)}
                  className="w-full p-3 text-left text-sm text-dark-300 hover:text-white hover:bg-dark-700/30 rounded-lg transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="font-semibold text-white mb-4">AI Capabilities</h3>
            <ul className="space-y-2 text-sm text-dark-400">
              <li>✓ Real-time system analysis</li>
              <li>✓ Performance optimization</li>
              <li>✓ Incident diagnosis</li>
              <li>✓ Deployment recommendations</li>
              <li>✓ Cost optimization</li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
};
