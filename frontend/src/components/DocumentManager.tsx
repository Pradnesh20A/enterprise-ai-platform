import React, { useRef, useState } from 'react';
import { Upload, FileText, Trash2, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { api } from '../api/client';
import type { DocumentItem } from '../api/client';

interface Props {
  documents: DocumentItem[];
  onDocumentsChanged: () => void;
}

export function DocumentManager({ documents, onDocumentsChanged }: Props) {
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsUploading(true);
      await api.uploadDocument(file);
      onDocumentsChanged();
    } catch (error) {
      console.error('Failed to upload document:', error);
      alert('Failed to upload document.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.deleteDocument(id);
      onDocumentsChanged();
    } catch (error) {
      console.error('Failed to delete document:', error);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const renderStatus = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="badge badge-success"><CheckCircle size={12} style={{marginRight: '4px'}} /> Ready</span>;
      case 'FAILED':
        return <span className="badge badge-danger"><AlertCircle size={12} style={{marginRight: '4px'}} /> Failed</span>;
      default:
        return <span className="badge badge-warning"><Clock size={12} style={{marginRight: '4px'}} /> {status}</span>;
    }
  };

  return (
    <div className="doc-section">
      <div>
        <h2>Knowledge Base</h2>
        <p className="subtitle">Manage your enterprise documents</p>
      </div>

      <button 
        onClick={handleUploadClick}
        disabled={isUploading}
        className="btn-primary"
      >
        <Upload size={18} />
        {isUploading ? 'Uploading...' : 'Upload Document'}
      </button>
      
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        className="hidden-input" 
        accept=".pdf,.txt,.docx"
      />

      <div className="doc-list">
        {documents.length === 0 ? (
          <div style={{textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)'}}>
            <FileText size={48} style={{margin: '0 auto 12px auto', opacity: 0.2}} />
            <p>No documents uploaded yet.</p>
          </div>
        ) : (
          documents.map((doc) => (
            <div key={doc.id} className="glass-panel">
              <div className="doc-item-header">
                <div className="doc-item-info">
                  <div className="doc-icon">
                    <FileText size={20} />
                  </div>
                  <div className="doc-meta">
                    <div className="doc-filename" title={doc.filename}>
                      {doc.filename}
                    </div>
                    <div className="doc-details">
                      <span>{formatFileSize(doc.file_size)}</span>
                      <span>•</span>
                      {renderStatus(doc.status)}
                    </div>
                  </div>
                </div>
                <button 
                  onClick={() => handleDelete(doc.id)}
                  className="btn-delete"
                  title="Delete document"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
