import apiClient from './client';

export const systemApi = {
  // Comprobar estado operativo de PostgreSQL, ChromaDB, Ollama y hardware
  getStatus: () => apiClient.get('/system/status'),

  // Obtener estadísticas agregadas para el dashboard
  getDashboardStats: () => apiClient.get('/dashboard/stats'),
};
