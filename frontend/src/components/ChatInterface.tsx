import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { api, Citation } from '../api/client';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedCitation, setExpandedCitation] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.askQuestion(userMessage.content);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        citations: response.citations,
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to get answer:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error while searching the documents.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleCitation = (id: string) => {
    setExpandedCitation(expandedCitation === id ? null : id);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-muted animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-panel flex items-center justify-center mb-4 shadow-lg border border-border">
              <Bot size={32} className="text-accent-primary" />
            </div>
            <h2 className="text-2xl font-semibold text-primary mb-2">Enterprise AI Assistant</h2>
            <p className="max-w-md text-center text-sm">
              Ask me anything about your uploaded documents. I will search the knowledge base and provide answers with direct citations.
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`flex gap-4 max-w-4xl mx-auto ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              {/* Avatar */}
              <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                msg.role === 'user' 
                  ? 'bg-gradient-to-tr from-accent-primary to-accent-secondary' 
                  : 'bg-surface border border-border'
              }`}>
                {msg.role === 'user' ? <User size={20} color="white" /> : <Bot size={20} className="text-accent-primary" />}
              </div>
              
              {/* Message Content */}
              <div className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} max-w-[80%]`}>
                <div className={`px-5 py-3.5 rounded-2xl ${
                  msg.role === 'user' 
                    ? 'bg-panel border border-border/50 text-primary' 
                    : 'bg-transparent text-primary'
                }`}>
                  <div className="prose prose-invert max-w-none text-sm leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </div>
                </div>

                {/* Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 w-full space-y-2">
                    <p className="text-xs font-semibold text-muted ml-1 uppercase tracking-wider">Sources:</p>
                    <div className="flex flex-wrap gap-2">
                      {msg.citations.map((citation, idx) => (
                        <div key={`${msg.id}-cite-${idx}`} className="relative">
                          <button
                            onClick={() => toggleCitation(`${msg.id}-cite-${idx}`)}
                            className="flex items-center gap-1.5 px-3 py-1.5 bg-panel border border-border rounded-full text-xs text-secondary hover:text-primary hover:border-accent-primary transition-colors"
                          >
                            <FileText size={12} className="text-accent-primary" />
                            <span className="truncate max-w-[150px]">{citation.filename}</span>
                            {expandedCitation === `${msg.id}-cite-${idx}` ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                          </button>
                          
                          <AnimatePresence>
                            {expandedCitation === `${msg.id}-cite-${idx}` && (
                              <motion.div
                                initial={{ opacity: 0, y: 5 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: 5 }}
                                className="absolute left-0 top-full mt-2 w-80 z-20 glass-panel shadow-lg p-4"
                              >
                                <p className="text-xs text-muted leading-relaxed font-mono">
                                  "{citation.snippet}"
                                </p>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="flex gap-4 max-w-4xl mx-auto">
            <div className="w-10 h-10 rounded-full bg-surface border border-border flex items-center justify-center">
              <Bot size={20} className="text-accent-primary animate-pulse" />
            </div>
            <div className="px-5 py-3.5 flex space-x-2 items-center">
              <div className="w-2 h-2 rounded-full bg-accent-primary animate-bounce"></div>
              <div className="w-2 h-2 rounded-full bg-accent-primary animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 rounded-full bg-accent-primary animate-bounce" style={{ animationDelay: '0.4s' }}></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 bg-surface/50 backdrop-blur-md border-t border-border">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="input-base pr-12 py-4 rounded-xl shadow-sm bg-panel border-border/60"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-accent-gradient rounded-lg text-white hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
