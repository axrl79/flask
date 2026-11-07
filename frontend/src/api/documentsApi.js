import apiClient from './client';

export const documentsApi = {
  // Listar documentos con filtros opcionales
  list: (params = {}) => apiClient.get('/documents', { params }),

  // Obtener detalle de un documento
  getById: (id) => apiClient.get(`/documents/${id}`),

  // Subir manual técnico PDF mediante multipart
  upload: (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress,
    });
  },

  // Disparar indexación de documento
  index: (id) => apiClient.post(`/documents/${id}/index`),

  // Eliminar documento
  delete: (id) => apiClient.delete(`/documents/${id}`),

  // URL directa para descargar o visualizar en el visor de PDF
  getDownloadUrl: (id) => `/api/documents/${id}/download`,
};
