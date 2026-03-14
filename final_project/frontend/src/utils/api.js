/**
 * Utilidades para conexión con la API del backend.
 * Maneja errores, timeouts y formateo de respuestas.
 */

// Configurar base URL desde variables de entorno
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Realiza una petición fetch con configuración predeterminada.
 * @param {string} endpoint - Ruta relativa del endpoint
 * @param {Object} options - Opciones de fetch
 * @returns {Promise<any>} Respuesta parseada como JSON
 */
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    // Timeout de 30 segundos por defecto
    signal: AbortSignal.timeout(30000),
    ...options
  };

  try {
    const response = await fetch(url, config);
    
    // Manejar errores HTTP
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    // Respuestas sin contenido (204)
    if (response.status === 204) {
      return null;
    }
    
    return await response.json();
    
  } catch (error) {
    // Manejar errores de red/timeout
    if (error.name === 'TimeoutError' || error.message.includes('timeout')) {
      throw new Error('Tiempo de espera agotado. El servidor tarda demasiado en responder.');
    }
    
    if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
      throw new Error('No se pudo conectar con el servidor. Verifica que el backend esté ejecutándose.');
    }
    
    // Re-lanzar errores ya formateados
    throw error;
  }
};

/**
 * GET simplificado
 */
export const apiGet = (endpoint, params = {}) => {
  const queryString = new URLSearchParams(params).toString();
  const url = queryString ? `${endpoint}?${queryString}` : endpoint;
  return apiRequest(url, { method: 'GET' });
};

/**
 * POST simplificado
 */
export const apiPost = (endpoint, data = {}) => {
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  });
};

/**
 * Health check del backend
 */
export const checkBackendHealth = async () => {
  try {
    const response = await apiGet('/health');
    return {
      healthy: response.status === 'healthy',
      details: response
    };
  } catch (error) {
    return {
      healthy: false,
      error: error.message
    };
  }
};

/**
 * Obtener configuración pública del backend
 */
export const getBackendConfig = async () => {
  return apiGet('/api/config');
};

/**
 * Enviar alerta de prueba (solo desarrollo)
 */
export const sendTestAlert = async () => {
  return apiPost('/api/alerts/test');
};

/**
 * Hook helper para usar con React (exportar para usar en componentes)
 * Ejemplo: const { data, loading, error } = useApi('/endpoint');
 */
export const createApiHook = (defaultEndpoint) => {
  return function useApi(endpoint = defaultEndpoint, options = {}) {
    // Nota: Este es un helper conceptual. 
    // Para implementación real con useState/useEffect, 
    // crear un custom hook en un archivo separado.
    return {
      fetch: async (params) => apiRequest(endpoint, { ...options, params }),
      get: (params) => apiGet(endpoint, params),
      post: (data) => apiPost(endpoint, data)
    };
  };
};

// Exportar constante con endpoints comunes para evitar hardcoding
export const ENDPOINTS = {
  HEALTH: '/health',
  CONFIG: '/api/config',
  ALERTS_TEST: '/api/alerts/test',
  // CopilotKit se maneja automáticamente por la librería
};

export default {
  request: apiRequest,
  get: apiGet,
  post: apiPost,
  checkHealth: checkBackendHealth,
  getConfig: getBackendConfig,
  ENDPOINTS
};