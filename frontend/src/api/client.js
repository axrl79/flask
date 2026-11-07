import axios from 'axios';

// Utiliza la URL de Vite o el proxy por defecto a /api
const baseURL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL,
  timeout: 120000, // 2 minutos para inferencia en CPU si es requerida
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de respuesta para manejo consistente de errores
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    let message = 'Error inesperado de comunicación con el servidor.';
    let code = 'NETWORK_ERROR';
    let details = {};

    if (error.response && error.response.data) {
      const errorData = error.response.data.error || error.response.data;
      message = errorData.message || error.response.statusText || message;
      code = errorData.code || `HTTP_${error.response.status}`;
      details = errorData.details || {};
    } else if (error.message) {
      message = error.message;
    }

    const customError = new Error(message);
    customError.code = code;
    customError.details = details;
    customError.status = error.response ? error.response.status : 0;
    return Promise.reject(customError);
  }
);

export default apiClient;
