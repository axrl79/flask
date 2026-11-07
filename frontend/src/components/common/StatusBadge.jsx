import { CheckCircle2, Clock, AlertTriangle, XCircle, RefreshCw } from 'lucide-react';

export default function StatusBadge({ status }) {
  const configs = {
    indexed: {
      label: 'Indexado',
      className: 'badge-success',
      icon: CheckCircle2,
    },
    processing: {
      label: 'Procesando',
      className: 'badge-info',
      icon: RefreshCw,
      spin: true,
    },
    uploaded: {
      label: 'Pendiente',
      className: 'badge-warning',
      icon: Clock,
    },
    failed: {
      label: 'Error',
      className: 'badge-error',
      icon: XCircle,
    },
    connected: {
      label: 'Conectado',
      className: 'badge-success',
      icon: CheckCircle2,
    },
    online: {
      label: 'En Línea',
      className: 'badge-success',
      icon: CheckCircle2,
    },
    offline: {
      label: 'Desconectado',
      className: 'badge-error',
      icon: AlertTriangle,
    },
    ready: {
      label: 'Listo',
      className: 'badge-success',
      icon: CheckCircle2,
    },
  };

  const config = configs[status] || {
    label: status || 'Desconocido',
    className: 'badge-info',
    icon: Clock,
  };

  const Icon = config.icon;

  return (
    <span className={`badge ${config.className}`}>
      <Icon size={12} className={config.spin ? 'spin' : ''} />
      {config.label}
    </span>
  );
}
