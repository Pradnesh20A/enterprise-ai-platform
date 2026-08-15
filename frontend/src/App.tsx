import React, { useEffect, useState } from 'react';
import { DocumentManager } from './components/DocumentManager';
import { ChatInterface } from './components/ChatInterface';
import { api, Document } from './api/client';
import { Database } from 'lucide-react';

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);

  const fetchDocuments = async () => {
    try {
      const docs = await api.listDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  useEffect(() => {
    fetchDocuments();
    // Poll for status updates (if processing takes time)
    const interval = setInterval(fetchDocuments, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="flex items-center space-x-3 mb-8 px-2">
          <div className="w-10 h-10 rounded-xl bg-accent-gradient flex items-center justify-center shadow-lg shadow-accent-primary/20">
            <Database size={20} color="white" />
          </div>
          <div>
            <h1 className="text-lg font-bold leading-tight">Enterprise AI</h1>
            <p className="text-xs text-accent-primary font-medium tracking-wide uppercase mt-0.5">Platform</p>
          </div>
        </div>
        
        <DocumentManager 
          documents={documents} 
          onDocumentsChanged={fetchDocuments} 
        />
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <ChatInterface />
      </main>
    </div>
  );
}

export default App;
