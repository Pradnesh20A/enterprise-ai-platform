import React, { useEffect, useState } from 'react';
import { MessageSquare, Trash2, Clock } from 'lucide-react';
import { api } from '../api/client';

interface ConversationItem {
  id: string;
  title: string;
  created_at: string;
}

interface Props {
  activeConversationId: string | null;
  onSelectConversation: (id: string | null) => void;
  refreshTrigger: number;
}

export function ConversationList({ activeConversationId, onSelectConversation, refreshTrigger }: Props) {
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchConversations = async () => {
    try {
      setIsLoading(true);
      const data = await api.getConversations();
      setConversations(data);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, [refreshTrigger]);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await api.deleteConversation(id);
      if (activeConversationId === id) {
        onSelectConversation(null);
      }
      fetchConversations();
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  return (
    <div className="doc-section" style={{ marginTop: '2rem', flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <div>
        <h2>Recent Chats</h2>
      </div>

      <div className="doc-list" style={{ flex: 1, overflowY: 'auto' }}>
        {isLoading && conversations.length === 0 ? (
          <div style={{textAlign: 'center', padding: '20px 0', color: 'var(--text-muted)'}}>
            <p>Loading...</p>
          </div>
        ) : conversations.length === 0 ? (
          <div style={{textAlign: 'center', padding: '20px 0', color: 'var(--text-muted)'}}>
            <MessageSquare size={32} style={{margin: '0 auto 12px auto', opacity: 0.2}} />
            <p>No recent chats.</p>
          </div>
        ) : (
          conversations.map((conv) => (
            <div 
              key={conv.id} 
              className={`glass-panel ${activeConversationId === conv.id ? 'active' : ''}`}
              style={{ 
                cursor: 'pointer',
                borderColor: activeConversationId === conv.id ? 'var(--primary-color)' : 'transparent',
                backgroundColor: activeConversationId === conv.id ? 'rgba(99, 102, 241, 0.1)' : 'rgba(255, 255, 255, 0.03)'
              }}
              onClick={() => onSelectConversation(conv.id)}
            >
              <div className="doc-item-header">
                <div className="doc-item-info">
                  <div className="doc-icon">
                    <MessageSquare size={16} color={activeConversationId === conv.id ? 'var(--primary-color)' : 'var(--text-secondary)'} />
                  </div>
                  <div className="doc-meta" style={{ width: '130px' }}>
                    <div className="doc-filename" title={conv.title} style={{ fontSize: '0.9rem', color: activeConversationId === conv.id ? 'var(--primary-color)' : 'var(--text-primary)'}}>
                      {conv.title}
                    </div>
                    <div className="doc-details">
                      <Clock size={10} style={{marginRight: '2px'}} />
                      <span>{formatDate(conv.created_at)}</span>
                    </div>
                  </div>
                </div>
                <button 
                  onClick={(e) => handleDelete(e, conv.id)}
                  className="btn-delete"
                  title="Delete chat"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
