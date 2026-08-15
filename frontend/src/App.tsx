import React, { useEffect, useState } from 'react';
import { DocumentManager } from './components/DocumentManager';
import { ChatInterface } from './components/ChatInterface';
import { ConversationList } from './components/ConversationList';
import { AdminDashboard } from './components/AdminDashboard';
import { AuthScreen } from './components/AuthScreen';
import { SettingsModal } from './components/SettingsModal';
import { api } from './api/client';
import { Settings } from 'lucide-react';
import type { DocumentItem } from './api/client';
import { Database, LogOut } from 'lucide-react';
import './index.css';

function App() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState<string>('user');
  const [isAdminView, setIsAdminView] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [chatRefreshTrigger, setChatRefreshTrigger] = useState(0);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      handleInitialLoad();
    }
  }, []);

  const handleInitialLoad = async () => {
    try {
      const user = await api.getMe();
      setUserRole(user.role);
      setIsAuthenticated(true);
      fetchDocuments();
    } catch (error) {
      handleLogout();
    }
  };

  const fetchDocuments = async () => {
    try {
      const docs = await api.listDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Error fetching documents:', error);
      // If unauthorized, log out
      if ((error as any).response?.status === 401) {
        handleLogout();
      }
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      const interval = setInterval(fetchDocuments, 5000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  const handleLogin = (token: string) => {
    localStorage.setItem('token', token);
    handleInitialLoad();
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setUserRole('user');
    setIsAdminView(false);
    setDocuments([]);
    setActiveConversationId(null);
  };

  if (!isAuthenticated) {
    return <AuthScreen onLogin={handleLogin} />;
  }

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div className="logo-icon">
              <Database size={20} color="white" />
            </div>
            <div>
              <h1>Enterprise AI</h1>
              <p className="brand-sub">Platform</p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button 
              onClick={() => setIsSettingsOpen(true)}
              title="Settings"
              style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '0.25rem' }}
            >
              <Settings size={18} />
            </button>
            {userRole === 'admin' && (
              <button 
                onClick={() => setIsAdminView(!isAdminView)} 
                title={isAdminView ? "Back to Chat" : "Admin Dashboard"}
                style={{ background: 'none', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.8rem' }}
              >
                {isAdminView ? "Chat" : "Admin"}
              </button>
            )}
            <button 
              onClick={handleLogout} 
              title="Log out"
              style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: '0.25rem' }}
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
        
        <DocumentManager 
          documents={documents} 
          onDocumentsChanged={fetchDocuments} 
        />
        <ConversationList 
          activeConversationId={activeConversationId}
          onSelectConversation={setActiveConversationId}
          refreshTrigger={chatRefreshTrigger}
        />
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        {isAdminView ? (
          <AdminDashboard />
        ) : (
          <ChatInterface 
            activeConversationId={activeConversationId}
            onNewConversation={(id) => {
              setActiveConversationId(id);
              setChatRefreshTrigger(prev => prev + 1);
            }}
            onStartNewChat={() => setActiveConversationId(null)}
          />
        )}
      </main>

      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </div>
  );
}

export default App;
