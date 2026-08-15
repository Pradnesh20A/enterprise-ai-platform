import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../api/client';
import type { Citation } from '../api/client';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { exportConversationToMarkdown } from '../utils/export';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
}

interface Props {
  activeConversationId: string | null;
  onNewConversation: (id: string) => void;
  onStartNewChat: () => void;
}

export function ChatInterface({ activeConversationId, onNewConversation, onStartNewChat }: Props) {
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

  useEffect(() => {
    if (activeConversationId) {
      loadConversation(activeConversationId);
    } else {
      setMessages([]);
      setInput('');
    }
  }, [activeConversationId]);

  const loadConversation = async (id: string) => {
    try {
      setIsLoading(true);
      const data = await api.getConversationMessages(id);
      const loadedMessages = data.messages.map((m: any) => ({
        id: m.id,
        role: m.role,
        content: m.content,
        citations: m.sources && Array.isArray(m.sources) ? m.sources.map((s: any) => ({
          document_id: s.document_id || '',
          filename: s.filename || 'Unknown Document',
          snippet: s.content_snippet || ''
        })) : []
      }));
      setMessages(loadedMessages);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    onStartNewChat();
  };

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
      const storedPrompt = localStorage.getItem('systemPrompt');
      const storedTemp = localStorage.getItem('temperature');
      
      const systemPrompt = storedPrompt || undefined;
      const temperature = storedTemp ? parseFloat(storedTemp) : undefined;

      const response = await api.askQuestion(
        userMessage.content, 
        activeConversationId || undefined,
        systemPrompt,
        temperature
      );
      
      if (response.conversation_id && !activeConversationId) {
        onNewConversation(response.conversation_id);
      }
      
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

  const handleExport = () => {
    if (messages.length === 0) return;
    exportConversationToMarkdown(messages);
  };

  return (
    <div className="chat-container">
      {/* Chat Header */}
      <div style={{
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        padding: '1rem', 
        borderBottom: '1px solid rgba(255,255,255,0.05)',
        backgroundColor: 'rgba(0,0,0,0.2)'
      }}>
        <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
          Enterprise AI Assistant
        </h3>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button 
            onClick={handleExport}
            disabled={messages.length === 0}
            className="btn"
            style={{
              padding: '0.4rem 0.8rem',
              fontSize: '0.85rem',
              backgroundColor: 'transparent',
              border: '1px solid rgba(255,255,255,0.1)',
              color: messages.length === 0 ? 'var(--text-muted)' : 'var(--text-primary)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              borderRadius: '6px',
              cursor: messages.length === 0 ? 'not-allowed' : 'pointer'
            }}
            title="Export conversation as Markdown"
          >
            Export
          </button>
          <button 
            onClick={handleNewChat}
            className="btn"
            style={{
              padding: '0.4rem 0.8rem',
              fontSize: '0.85rem',
              backgroundColor: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(255,255,255,0.1)',
              color: 'var(--text-primary)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              borderRadius: '6px'
            }}
          >
            <Bot size={14} /> New Chat
          </button>
        </div>
      </div>
      
      {/* Chat History */}
      <div className="chat-history">
        {messages.length === 0 ? (
          <div className="chat-empty animate-fade-in">
            <div className="chat-empty-icon">
              <Bot size={32} />
            </div>
            <h2 style={{color: 'var(--text-primary)', marginBottom: '8px'}}>Enterprise AI Assistant</h2>
            <p style={{maxWidth: '400px', margin: '0 auto', fontSize: '0.875rem'}}>
              Ask me anything about your uploaded documents. I will search the knowledge base and provide answers with direct citations.
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`chat-message ${msg.role}`}>
              {/* Avatar */}
              <div className={`chat-avatar ${msg.role}`}>
                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
              </div>
              
              {/* Message Content */}
              <div className="chat-content">
                <div className="chat-bubble animate-fade-in markdown-body">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                </div>

                {/* Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="citations-wrapper animate-fade-in">
                    <div className="citations-title">Sources:</div>
                    <div className="citations-list">
                      {msg.citations.map((citation, idx) => (
                        <div key={`${msg.id}-cite-${idx}`} className="citation-item">
                          <button
                            onClick={() => toggleCitation(`${msg.id}-cite-${idx}`)}
                            className="citation-btn"
                          >
                            <FileText size={12} className="icon" />
                            <span style={{maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>
                              {citation.filename}
                            </span>
                            {expandedCitation === `${msg.id}-cite-${idx}` ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                          </button>
                          
                          <AnimatePresence>
                            {expandedCitation === `${msg.id}-cite-${idx}` && (
                              <motion.div
                                initial={{ opacity: 0, y: 5 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: 5 }}
                                className="citation-dropdown glass-panel shadow-lg"
                              >
                                "{citation.snippet}"
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
          <div className="chat-message bot animate-fade-in">
            <div className="chat-avatar bot">
              <Bot size={20} />
            </div>
            <div className="chat-content">
              <div className="loading-indicator">
                <div className="dot"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="chat-input-area">
        <form onSubmit={handleSubmit} className="chat-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="chat-input"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="chat-submit-btn"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
