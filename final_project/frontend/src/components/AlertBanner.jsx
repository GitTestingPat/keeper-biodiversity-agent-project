/**
 * Componente para mostrar alertas de biodiversidad en tiempo real.
 * Soporta diferentes niveles de severidad con estilos visuales distintivos.
 * 
 * @param {Object} props
 * @param {Object|null} props.alert - Objeto de alerta con estructura del backend
 * @param {Function} props.onDismiss - Callback para cerrar la alerta
 * @param {boolean} props.autoHide - Si la alerta se oculta automáticamente (default: true)
 */
import { useState, useEffect } from 'react';

const AlertBanner = ({ alert, onDismiss, autoHide = true }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  // Configurar auto-ocultamiento para alertas de baja severidad
  useEffect(() => {
    if (alert && autoHide && alert.severity !== 'critical' && alert.severity !== 'high') {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onDismiss?.();
      }, 8000);
      return () => clearTimeout(timer);
    }
    setIsVisible(!!alert);
  }, [alert, autoHide, onDismiss]);

  if (!alert || !isVisible) return null;

  // Mapeo de severidad a estilos
  const severityStyles = {
    low: {
      bg: 'bg-blue-50 border-blue-200',
      text: 'text-blue-800',
      icon: '🔵',
      label: 'Informativo'
    },
    medium: {
      bg: 'bg-yellow-50 border-yellow-200',
      text: 'text-yellow-800',
      icon: '🟡',
      label: 'Atención'
    },
    high: {
      bg: 'bg-orange-50 border-orange-200',
      text: 'text-orange-800',
      icon: '🟠',
      label: 'Advertencia'
    },
    critical: {
      bg: 'bg-red-50 border-red-200 animate-pulse',
      text: 'text-red-800',
      icon: '🔴',
      label: 'CRÍTICO'
    }
  };

  const style = severityStyles[alert.severity] || severityStyles.medium;

  // Formatear ubicación para display
  const formatLocation = (location) => {
    if (!location) return 'Ubicación desconocida';
    if (location.name) return location.name;
    if (location.coordinates) {
      const { latitude, longitude } = location.coordinates;
      return `Lat: ${latitude?.toFixed(2)}, Lon: ${longitude?.toFixed(2)}`;
    }
    return 'Ubicación sin especificar';
  };

  // Formatear timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  return (
    <div 
      className={`fixed top-4 right-4 z-50 max-w-md border-l-4 shadow-lg rounded-r-lg transition-all duration-300 ${style.bg} ${style.text}`}
      role="alert"
      aria-live="polite"
    >
      {/* Header de la alerta */}
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <span className="text-xl shrink-0" aria-hidden="true">{style.icon}</span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-semibold">{style.label}</span>
                <span className="text-xs opacity-75 uppercase tracking-wide">
                  {alert.type?.replace(/_/g, ' ')}
                </span>
              </div>
              <p className="text-sm mt-1 break-words">
                {alert.description}
              </p>
              <p className="text-xs opacity-75 mt-1">
                📍 {formatLocation(alert.location)} • 🕐 {formatTime(alert.timestamp)}
              </p>
            </div>
          </div>
          
          {/* Botones de acción */}
          <div className="flex items-center gap-1 shrink-0">
            {alert.severity === 'critical' && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-1 hover:bg-black/5 rounded transition-colors"
                aria-label={isExpanded ? 'Contraer detalles' : 'Expandir detalles'}
                title="Ver detalles"
              >
                {isExpanded ? '▲' : '▼'}
              </button>
            )}
            <button
              onClick={() => {
                setIsVisible(false);
                onDismiss?.();
              }}
              className="p-1 hover:bg-black/5 rounded transition-colors"
              aria-label="Cerrar alerta"
              title="Cerrar"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Detalles expandibles (solo para críticas) */}
        {isExpanded && alert.metadata && Object.keys(alert.metadata).length > 0 && (
          <div className="mt-3 pt-3 border-t border-current/20">
            <p className="text-xs font-medium mb-2">Detalles técnicos:</p>
            <pre className="text-xs bg-black/5 rounded p-2 overflow-x-auto max-h-32">
              {JSON.stringify(alert.metadata, null, 2).slice(0, 500)}
              {JSON.stringify(alert.metadata).length > 500 ? '...' : ''}
            </pre>
            {alert.metadata?.recommendations && (
              <div className="mt-2">
                <p className="text-xs font-medium">Recomendaciones:</p>
                <ul className="text-xs list-disc list-inside mt-1 space-y-1">
                  {Array.isArray(alert.metadata.recommendations) 
                    ? alert.metadata.recommendations.map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))
                    : <li>{alert.metadata.recommendations}</li>
                  }
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Barra de progreso para auto-ocultamiento */}
      {autoHide && alert.severity !== 'critical' && alert.severity !== 'high' && (
        <div className="h-1 bg-current/10">
          <div 
            className="h-full bg-current/50 transition-all duration-300 ease-linear"
            style={{ animation: 'shrink 8s linear forwards' }}
          />
        </div>
      )}
    </div>
  );
};

// Agregar keyframes para la animación de la barra de progreso
const style = document.createElement('style');
style.textContent = `
  @keyframes shrink {
    from { width: 100%; }
    to { width: 0%; }
  }
`;
document.head.appendChild(style);

export default AlertBanner;