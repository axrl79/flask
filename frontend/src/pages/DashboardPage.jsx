import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  CheckCircle2,
  MessageSquare,
  Bot,
  Activity,
  Upload,
  Layers,
} from 'lucide-react';
import { systemApi } from '../api/systemApi';
import { documentsApi } from '../api/documentsApi';
import StatusBadge from '../components/common/StatusBadge';
import DocumentUploadModal from '../components/documents/DocumentUploadModal';

export default function DashboardPage({ onOpenViewer }) {
  const [stats, setStats] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [recentDocs, setRecentDocs] = useState([]);
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  useEffect(() => {
    let isMounted = true;
    Promise.all([
      systemApi.getDashboardStats().catch(() => null),
      systemApi.getStatus().catch(() => null),
      documentsApi.list().catch(() => []),
    ]).then(([statsData, sysData, docsData]) => {
      if (isMounted) {
        setStats(statsData);
        setSystemStatus(sysData);
        setRecentDocs(docsData.slice(0, 4));
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  const loadData = async () => {
    try {
      const [statsData, sysData, docsData] = await Promise.all([
        systemApi.getDashboardStats().catch(() => null),
        systemApi.getStatus().catch(() => null),
        documentsApi.list().catch(() => []),
      ]);
      setStats(statsData);
      setSystemStatus(sysData);
      setRecentDocs(docsData.slice(0, 4));
    } catch {
      // Ignorar errores de carga inicial
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* Banner de Bienvenida y Acciones Rápidas */}
      <div
        className="glass-card"
        style={{
          background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.12), rgba(59, 130, 246, 0.08))',
          borderColor: 'var(--border-accent)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '20px',
          flexWrap: 'wrap',
          padding: '28px 32px',
        }}
      >
        <div style={{ maxWidth: '640px' }}>
          <h1 style={{ fontSize: '24px', margin: '0 0 8px 0' }}>
            Plataforma RAG de Manuales Industriales
          </h1>
          <p style={{ fontSize: '14px', lineHeight: '1.6' }}>
            Asistente inteligente con recuperación fundamentada y cero alucinaciones. Realiza consultas operativas sobre maquinaria con referencias directas al número de página del manual.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-secondary" onClick={() => setIsUploadOpen(true)}>
            <Upload size={16} /> Cargar Manual
          </button>
          <Link to="/chat" className="btn btn-primary" style={{ textDecoration: 'none' }}>
            <Bot size={16} /> Abrir Asistente
          </Link>
        </div>
      </div>

      {/* Tarjetas de Métricas Clave */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '10px', backgroundColor: 'rgba(59, 130, 246, 0.12)', color: '#60a5fa' }}>
            <FileText size={24} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Manuales Registrados
            </div>
            <div style={{ fontSize: '26px', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>
              {stats?.documents?.total ?? 0}
            </div>
          </div>
        </div>

        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '10px', backgroundColor: 'rgba(16, 185, 129, 0.12)', color: '#34d399' }}>
            <CheckCircle2 size={24} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Documentos Indexados
            </div>
            <div style={{ fontSize: '26px', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>
              {stats?.documents?.indexed ?? 0}
            </div>
          </div>
        </div>

        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '10px', backgroundColor: 'rgba(168, 85, 247, 0.12)', color: '#c084fc' }}>
            <Layers size={24} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Páginas Analizadas
            </div>
            <div style={{ fontSize: '26px', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>
              {stats?.documents?.total_pages ?? 0}
            </div>
          </div>
        </div>

        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ padding: '12px', borderRadius: '10px', backgroundColor: 'rgba(245, 158, 11, 0.12)', color: '#fbbf24' }}>
            <MessageSquare size={24} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Consultas Técnicas
            </div>
            <div style={{ fontSize: '26px', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>
              {stats?.chat?.total_queries ?? 0}
            </div>
          </div>
        </div>
      </div>

      {/* Grid: Estado de Servicios IA + Actividad Reciente */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px' }}>
        {/* Panel de Estado de Componentes IA */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Activity size={18} color="var(--accent-purple)" />
              <h3 style={{ fontSize: '15px' }}>Salud del Sistema Local</h3>
            </div>
            <Link to="/system" style={{ fontSize: '12px', color: 'var(--accent-purple)', textDecoration: 'none' }}>
              Ver detalles →
            </Link>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {/* PostgreSQL */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: '13px' }}>PostgreSQL 16</div>
                <div style={{ fontSize: '11px', color: 'var(--text-faint)' }}>Base relacional de metadatos y jobs</div>
              </div>
              <StatusBadge status={systemStatus?.components?.postgresql?.status} />
            </div>

            {/* ChromaDB */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: '13px' }}>ChromaDB</div>
                <div style={{ fontSize: '11px', color: 'var(--text-faint)' }}>Persistencia vectorial HNSW (Coseno)</div>
              </div>
              <StatusBadge status={systemStatus?.components?.chromadb?.status} />
            </div>

            {/* Ollama */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: '13px' }}>Ollama Local</div>
                <div style={{ fontSize: '11px', color: 'var(--text-faint)' }}>Embeddings (nomic-embed) + LLM</div>
              </div>
              <StatusBadge status={systemStatus?.components?.ollama?.status} />
            </div>
          </div>
        </div>

        {/* Panel de Manuales Recientes */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={18} color="var(--accent-blue)" />
              <h3 style={{ fontSize: '15px' }}>Manuales Recientes</h3>
            </div>
            <Link to="/documents" style={{ fontSize: '12px', color: 'var(--accent-purple)', textDecoration: 'none' }}>
              Ver todos →
            </Link>
          </div>

          {recentDocs.length === 0 ? (
            <div style={{ padding: '24px 0', textAlign: 'center', color: 'var(--text-faint)', fontSize: '13px' }}>
              No hay manuales cargados aún.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {recentDocs.map((doc) => (
                <div
                  key={doc.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 12px',
                    backgroundColor: 'var(--bg-secondary)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
                    <FileText size={16} color="#60a5fa" />
                    <span
                      style={{
                        fontSize: '13px',
                        color: 'var(--text-main)',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                      title={doc.original_filename}
                    >
                      {doc.original_filename}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
                    <StatusBadge status={doc.status} />
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '4px 8px', fontSize: '11px' }}
                      onClick={() => onOpenViewer(doc.id, doc.original_filename, 1)}
                    >
                      Ver
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Modal de Carga de Documentos */}
      <DocumentUploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={() => loadData()}
      />
    </div>
  );
}
