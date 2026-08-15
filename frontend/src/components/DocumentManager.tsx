import React, { useRef, useState } from 'react';
import { Upload, FileText, Trash2, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { api, Document } from '../api/client';

interface Props {
  documents: Document[];
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
        return <span className="badge badge-success"><CheckCircle size={12} className="mr-1" /> Ready</span>;
      case 'FAILED':
        return <span className="badge badge-danger"><AlertCircle size={12} className="mr-1" /> Failed</span>;
      default:
        return <span className="badge badge-warning"><Clock size={12} className="mr-1" /> {status}</span>;
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-1">Knowledge Base</h2>
        <p className="text-sm text-secondary">Manage your enterprise documents</p>
      </div>

      <button 
        onClick={handleUploadClick}
        disabled={isUploading}
        className="btn-primary w-full mb-6 py-3"
      >
        <Upload size={18} />
        {isUploading ? 'Uploading...' : 'Upload Document'}
      </button>
      
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        className="hidden" 
        accept=".pdf,.txt,.docx"
      />

      <div className="flex-1 overflow-y-auto pr-2">
        {documents.length === 0 ? (
          <div className="text-center py-10 text-muted">
            <FileText size={48} className="mx-auto mb-3 opacity-20" />
            <p>No documents uploaded yet.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div key={doc.id} className="glass-panel group relative">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 overflow-hidden">
                    <div className="mt-1 flex-shrink-0 text-accent-primary">
                      <FileText size={20} />
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-sm font-medium truncate" title={doc.filename}>
                        {doc.filename}
                      </h4>
                      <div className="text-xs text-muted mt-1 flex items-center space-x-2">
                        <span>{formatFileSize(doc.file_size)}</span>
                        <span>•</span>
                        {renderStatus(doc.status)}
                      </div>
                    </div>
                  </div>
                  <button 
                    onClick={() => handleDelete(doc.id)}
                    className="text-muted hover:text-danger opacity-0 group-hover:opacity-100 transition-opacity p-1"
                    title="Delete document"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
