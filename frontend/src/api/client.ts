import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Document {
  id: string;
  filename: string;
  file_size: number;
  upload_date: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
}

export interface Citation {
  document_id: string;
  filename: string;
  snippet: string;
}

export interface QAResponse {
  answer: string;
  citations: Citation[];
}

export const api = {
  // Documents
  listDocuments: async (skip = 0, limit = 100): Promise<Document[]> => {
    const response = await apiClient.get(`/documents?skip=${skip}&limit=${limit}`);
    return response.data;
  },
  
  uploadDocument: async (file: File): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  deleteDocument: async (id: string): Promise<void> => {
    await apiClient.delete(`/documents/${id}`);
  },
  
  // QA
  askQuestion: async (question: string, top_k = 5): Promise<QAResponse> => {
    const response = await apiClient.post('/qa/ask', {
      question,
      top_k,
    });
    return response.data;
  },
};
