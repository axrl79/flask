import { useState, useEffect } from 'react';
import { systemApi } from '../api/systemApi';
import StatusBadge from '../components/common/StatusBadge';
import {
  Database,
  Cpu,
  Layers,
  HardDrive,
  RefreshCw,
  Server,
  Sparkles,
} from 'lucide-react';

export default function SystemPage() {
  const [statusData, setStatusData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    systemApi
      .getStatus()
      .then((data) => {
        if (isMounted) {
          setStatusData(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          if (err.details || err.status === 503) {
            setStatusData({
              status: 'degraded',
              components: {
                postgresql: { status: 'disconnected', error: err.message },
                chromadb: { status: 'ready' },
                ollama: { status: 'offline', error: err.message },
              },
            });
          }
          setLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const data = await systemApi.getStatus();
      setStatusData(data);
    } catch (err) {
      if (err.details || err.status === 503) {
        setStatusData({
          status: 'degraded',
          components: {
            postgresql: { status: 'disconnected', error: err.message },
            chromadb: { status: 'ready' },
            ollama: { status: 'offline', error: err.message },
          },
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const components = statusData?.components || {};
  const hardware = statusData?.hardware || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Cabecera */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '22px', margin: 0 }}>Diagnóstico de Servicios de IA y Base de Datos</h1>
          <p style={{ fontSize: '13px', marginTop: '4px' }}>
            Monitorización en tiempo real de los servicios locales y recursos de hardware.
          </p>
        </div>

        <button className="btn btn-secondary" onClick={fetchStatus} disabled={loading}>
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
          {loading ? 'Comprobando...' : 'Comprobar Ahora'}
        </button>
      </div>

      {/* Grid de Componentes Principales */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
        {/* Backend Flask */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Server size={20} color="var(--accent-purple)" />
              <h3 style={{ fontSize: '15px' }}>Backend Flask API</h3>
            </div>
            <StatusBadge status="online" />
          </div>
          <p style={{ fontSize: '13px', lineHeight: '1.5' }}>
            Servidor REST modular con Application Factory, SQLAlchemy y Flask-Migrate.
          </p>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', borderTop: '1px solid var(--border-subtle)', paddingTop: '8px' }}>
            Puerto: 5000 • CORS Habilitado
          </div>
        </div>

        {/* PostgreSQL */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Database size={20} color="#38bdf8" />
              <h3 style={{ fontSize: '15px' }}>PostgreSQL 16</h3>
            </div>
            <StatusBadge status={components.postgresql?.status} />
          </div>
          <p style={{ fontSize: '13px', lineHeight: '1.5' }}>
            {components.postgresql?.message || 'Conexión a la base de datos relacional de metadatos y jobs.'}
          </p>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', borderTop: '1px solid var(--border-subtle)', paddingTop: '8px' }}>
            Base de datos: <code>flask_db</code> • Driver: Psycopg 3
          </div>
        </div>

        {/* ChromaDB */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Layers size={20} color="#34d399" />
              <h3 style={{ fontSize: '15px' }}>ChromaDB Vector Store</h3>
            </div>
            <StatusBadge status={components.chromadb?.status} />
          </div>
          <p style={{ fontSize: '13px', lineHeight: '1.5' }}>
            Índice vectorial HNSW con distancia coseno para recuperación semántica.
          </p>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', borderTop: '1px solid var(--border-subtle)', paddingTop: '8px' }}>
            Directorio: <code>{components.chromadb?.persist_directory || 'storage/chroma'}</code>
          </div>
        </div>

        {/* Ollama Local Daemon */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Cpu size={20} color="#f59e0b" />
              <h3 style={{ fontSize: '15px' }}>Ollama Local Daemon</h3>
            </div>
            <StatusBadge status={components.ollama?.status} />
          </div>
          <p style={{ fontSize: '13px', lineHeight: '1.5' }}>
            Motor de inferencia local ejecutándose en el puerto 11434.
          </p>
          <div style={{ fontSize: '11px', color: 'var(--text-faint)', borderTop: '1px solid var(--border-subtle)', paddingTop: '8px' }}>
            Modelos instalados: {components.ollama?.available_models?.join(', ') || 'Ninguno'}
          </div>
        </div>
      </div>

      {/* Tarjetas de Modelos Activos y Hardware */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
        {/* Modelos de IA Configurados */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Sparkles size={18} color="var(--accent-purple)" />
            <h3 style={{ fontSize: '15px' }}>Modelos Asignados al Pipeline</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ padding: '10px 12px', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>Modelo de Embeddings</div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)', marginTop: '2px' }}>
                {components.ollama?.configured_embed_model || 'nomic-embed-text'} (768 dim)
              </div>
            </div>

            <div style={{ padding: '10px 12px', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>Modelo de Generación (LLM)</div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)', marginTop: '2px' }}>
                {components.ollama?.configured_llm_model || 'llama3.1:8b'} (Temp: 0.0)
              </div>
            </div>
          </div>
        </div>

        {/* Recursos del Host */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <HardDrive size={18} color="#60a5fa" />
            <h3 style={{ fontSize: '15px' }}>Recursos de la Máquina</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 12px', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Núcleos de CPU</span>
              <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{hardware.cpu_cores || 'N/A'} Cores</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 12px', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Memoria RAM Total</span>
              <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{hardware.ram_total_mb ? `${hardware.ram_total_mb} MB` : 'N/A'}</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 12px', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>RAM Disponible</span>
              <span style={{ fontWeight: 600, color: 'var(--status-success)' }}>{hardware.ram_available_mb ? `${hardware.ram_available_mb} MB` : 'N/A'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
