import { useState, useEffect } from 'react';
import { systemApi } from '../../api/systemApi';
import { Circle } from 'lucide-react';

export default function Header({ title }) {
  const [systemHealthy, setSystemHealthy] = useState(null);

  useEffect(() => {
    let mounted = true;
    systemApi.getStatus()
      .then((data) => {
        if (mounted) setSystemHealthy(data.status === 'healthy');
      })
      .catch(() => {
        if (mounted) setSystemHealthy(false);
      });
    return () => { mounted = false; };
  }, []);

  return (
    <header
      style={{
        height: 'var(--header-height)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 36px',
        backgroundColor: 'rgba(10, 12, 16, 0.75)',
        backdropFilter: 'blur(10px)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}
    >
      <h2 style={{ fontSize: '17px', fontWeight: 600 }}>{title}</h2>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '12px',
            color: 'var(--text-muted)',
            padding: '6px 12px',
            borderRadius: '20px',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <Circle
            size={8}
            fill={systemHealthy === null ? '#94a3b8' : systemHealthy ? '#10b981' : '#f43f5e'}
            color="transparent"
          />
          <span>
            {systemHealthy === null
              ? 'Verificando...'
              : systemHealthy
              ? 'Servicios IA Activos'
              : 'Atención Requerida'}
          </span>
        </div>
      </div>
    </header>
  );
}
