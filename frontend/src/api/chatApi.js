import apiClient from './client';

export const chatApi = {
  // Crear nueva sesión de chat
  createSession: (title) => apiClient.post('/chat/sessions', { title }),

  // Listar historial de sesiones
  listSessions: (limit = 50) => apiClient.get('/chat/sessions', { params: { limit } }),

  // Obtener mensajes de una sesión
  getSession: (sessionId) => apiClient.get(`/chat/sessions/${sessionId}`),

  // Eliminar sesión
  deleteSession: (sessionId) => apiClient.delete(`/chat/sessions/${sessionId}`),

  // Enviar consulta técnica al motor RAG
  query: (query, sessionId = null, documentId = null, topK = 4) => {
    const payload = {
      query,
      top_k: topK,
    };
    if (sessionId) payload.session_id = sessionId;
    if (documentId) payload.document_id = documentId;
    return apiClient.post('/chat/query', payload);
  },
};
