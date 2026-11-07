import { useState } from 'react';
import StatusBadge from '../common/StatusBadge';
import {
  FileText,
  Search,
  Trash2,
  Play,
  RotateCw,
  BookOpen,
  Calendar,
  Layers,
  HardDrive,
} from 'lucide-react';

export default function DocumentList({
  documents,
  loading,
  onIndex,
  onDelete,
  onOpenViewer,
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [deletingId, setDeletingId] = useState(null);

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch = doc.original_filename.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || doc.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  const formatDate = (isoStr) => {
    if (!isoStr) return 'N/A';
    const date = new Date(isoStr);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Barra de Filtros y Búsqueda */}
      <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ position: 'relative', minWidth: '280px', flex: 1, maxWidth: '450px' }}>
          <Search
            size={16}
            style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-faint)',
            }}
          />
          <input
            type="text"
            placeholder="Buscar por nombre de manual o modelo..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field"
            style={{ width: '100%', paddingLeft: '36px' }}
          />
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          {['all', 'indexed', 'uploaded', 'failed'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className="btn btn-secondary"
              style={{
                padding: '6px 12px',
                fontSize: '12px',
                borderColor: statusFilter === st ? 'var(--accent-purple)' : 'var(--border-subtle)',
                backgroundColor: statusFilter === st ? 'rgba(168, 85, 247, 0.1)' : 'var(--bg-secondary)',
                color: statusFilter === st ? '#fff' : 'var(--text-muted)',
              }}
            >
              {st === 'all' && 'Todos'}
              {st === 'indexed' && 'Indexados'}
              {st === 'uploaded' && 'Pendientes'}
              {st === 'failed' && 'Con Error'}
            </button>
          ))}
        </div>
      </div>

      {/* Lista de Documentos en Tabla / Cards */}
      {loading ? (
        <div className="glass-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-faint)' }}>
          Cargando manuales técnicos...
        </div>
      ) : filteredDocs.length === 0 ? (
        <div
          className="glass-card"
          style={{
            padding: '48px 20px',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <FileText size={40} color="var(--text-faint)" />
          <div style={{ fontWeight: 600, color: 'var(--text-muted)', fontSize: '15px' }}>
            No se encontraron manuales registrados
          </div>
          <div style={{ fontSize: '13px', color: 'var(--text-faint)', maxWidth: '400px' }}>
            Sube manuales PDF de compresores, bombas o maquinaria industrial para comenzar a realizar consultas RAG.
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {filteredDocs.map((doc) => (
            <div
              key={doc.id}
              className="glass-card"
              style={{
                padding: '16px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '16px',
                flexWrap: 'wrap',
              }}
            >
              {/* Información Primaria */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flex: 2, minWidth: '240px' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '8px',
                    backgroundColor: 'rgba(59, 130, 246, 0.12)',
                    color: '#60a5fa',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  <FileText size={20} />
                </div>
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '14px' }}>
                    {doc.original_filename}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px', color: 'var(--text-faint)', marginTop: '3px' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <HardDrive size={13} /> {formatBytes(doc.file_size_bytes)}
                    </span>
                    <span>•</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Layers size={13} /> {doc.total_pages} Páginas
                    </span>
                    <span>•</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Calendar size={13} /> {formatDate(doc.created_at)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Estado de Indexación */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <StatusBadge status={doc.status} />
                {doc.status === 'indexed' && (
                  <span style={{ fontSize: '12px', color: 'var(--text-faint)' }}>
                    {doc.chunks_count || 0} fragmentos en ChromaDB
                  </span>
                )}
              </div>

              {/* Acciones */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {/* Abrir en Visor de PDF */}
                <button
                  className="btn btn-secondary"
                  title="Abrir en Visor PDF"
                  onClick={() => onOpenViewer(doc.id, doc.original_filename, 1)}
                  style={{ padding: '6px 10px' }}
                >
                  <BookOpen size={15} />
                  <span style={{ fontSize: '12px' }}>Ver PDF</span>
                </button>

                {/* Indexar / Reintentar */}
                {doc.status === 'uploaded' && (
                  <button
                    className="btn btn-primary"
                    onClick={() => onIndex(doc.id)}
                    style={{ padding: '6px 12px', fontSize: '12px' }}
                  >
                    <Play size={14} /> Indexar
                  </button>
                )}

                {doc.status === 'failed' && (
                  <button
                    className="btn btn-secondary"
                    onClick={() => onIndex(doc.id)}
                    style={{ padding: '6px 12px', fontSize: '12px', color: 'var(--status-warning)' }}
                  >
                    <RotateCw size={14} /> Reintentar
                  </button>
                )}

                {/* Eliminar con confirmación */}
                {deletingId === doc.id ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <button
                      className="btn btn-danger"
                      style={{ padding: '5px 10px', fontSize: '11px' }}
                      onClick={() => {
                        onDelete(doc.id);
                        setDeletingId(null);
                      }}
                    >
                      Confirmar
                    </button>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '5px 8px', fontSize: '11px' }}
                      onClick={() => setDeletingId(null)}
                    >
                      Cancelar
                    </button>
                  </div>
                ) : (
                  <button
                    className="btn btn-secondary"
                    title="Eliminar Manual"
                    onClick={() => setDeletingId(doc.id)}
                    style={{ padding: '6px 8px', color: 'var(--text-faint)' }}
                  >
                    <Trash2 size={15} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
