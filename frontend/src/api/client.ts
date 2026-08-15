import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface DocumentItem {
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
  conversation_id?: string;
}

export interface UserResponse {
  id: string;
  email: string;
  role: string;
}

export interface AdminStats {
  total_users: number;
  total_documents: number;
  total_chunks: number;
  total_conversations: number;
}

export interface AdminUser {
  id: string;
  email: string;
  role: string;
  created_at: string;
  document_count: number;
}

export const api = {
  // Auth
  login: async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    const response = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  },
  
  register: async (email: string, password: string) => {
    const response = await apiClient.post('/auth/register', { email, password });
    return response.data;
  },

  getMe: async (): Promise<UserResponse> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  searchDocuments: async (query: string, topK: number = 5) => {
    const response = await apiClient.get('/search', { params: { query, top_k: topK } });
    return response.data;
  },

  askQuestion: async (question: string, conversationId?: string, systemPrompt?: string, temperature?: number): Promise<QAResponse> => {
    const payload: any = { question, top_k: 5 };
    if (conversationId) payload.conversation_id = conversationId;
    if (systemPrompt) payload.system_prompt = systemPrompt;
    if (temperature !== undefined) payload.temperature = temperature;
    
    const response = await apiClient.post('/qa/ask', payload);
    return response.data;
  },
  
  getConversations: async () => {
    const response = await apiClient.get('/conversations');
    return response.data;
  },
  
  getConversationMessages: async (conversationId: string) => {
    const response = await apiClient.get(`/conversations/${conversationId}`);
    return response.data;
  },
  
  deleteConversation: async (conversationId: string) => {
    const response = await apiClient.delete(`/conversations/${conversationId}`);
    return response.data;
  },

  // Documents
  listDocuments: async (skip = 0, limit = 100): Promise<DocumentItem[]> => {
    const response = await apiClient.get(`/documents?skip=${skip}&limit=${limit}`);
    return response.data.documents;
  },
  
  uploadDocument: async (file: File): Promise<DocumentItem> => {
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

  // Admin
  getAdminStats: async (): Promise<AdminStats> => {
    const response = await apiClient.get('/admin/stats');
    return response.data;
  },

  getAdminUsers: async (skip = 0, limit = 100): Promise<AdminUser[]> => {
    const response = await apiClient.get(`/admin/users?skip=${skip}&limit=${limit}`);
    return response.data;
  }
};
