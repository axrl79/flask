import { useState, useEffect } from 'react';
import { documentsApi } from '../api/documentsApi';
import DocumentList from '../components/documents/DocumentList';
import DocumentUploadModal from '../components/documents/DocumentUploadModal';
import { Upload, RefreshCw, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function DocumentsPage({ onOpenViewer }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [notification, setNotification] = useState(null);

  const showNotification = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  useEffect(() => {
    let isMounted = true;
    documentsApi
      .list()
      .then((docs) => {
        if (isMounted) {
          setDocuments(docs);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          showNotification(err.message || 'Error al obtener manuales.', 'error');
          setLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const docs = await documentsApi.list();
      setDocuments(docs);
    } catch (err) {
      showNotification(err.message || 'Error al obtener manuales.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleIndex = async (id) => {
    try {
      showNotification('Iniciando extracción y generación de embeddings en ChromaDB...', 'info');
      await documentsApi.index(id);
      showNotification('Manual indexado exitosamente en ChromaDB.', 'success');
      loadDocuments();
    } catch (err) {
      showNotification(err.message || 'Fallo durante la indexación.', 'error');
      loadDocuments();
    }
  };

  const handleDelete = async (id) => {
    try {
      await documentsApi.delete(id);
      showNotification('Manual y vectores asociados eliminados.', 'success');
      loadDocuments();
    } catch (err) {
      showNotification(err.message || 'Error al eliminar manual.', 'error');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Cabecera de la Página */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', flexWrap: 'wrap' }}>
        <div>
          <h1 style={{ fontSize: '22px', margin: 0 }}>Gestión de Manuales Técnicos</h1>
          <p style={{ fontSize: '13px', marginTop: '4px' }}>
            Repositorio de documentación PDF, planos de mantenimiento e indexación semántica.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-secondary" onClick={loadDocuments} title="Actualizar lista">
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
            Actualizar
          </button>
          <button className="btn btn-primary" onClick={() => setIsUploadOpen(true)}>
            <Upload size={14} />
            Cargar Manual
          </button>
        </div>
      </div>

      {/* Banner de Notificación */}
      {notification && (
        <div
          className="animate-fade-in"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '12px 18px',
            borderRadius: 'var(--radius-md)',
            fontSize: '13px',
            backgroundColor:
              notification.type === 'error'
                ? 'var(--status-error-bg)'
                : notification.type === 'info'
                ? 'var(--status-info-bg)'
                : 'var(--status-success-bg)',
            color:
              notification.type === 'error'
                ? 'var(--status-error)'
                : notification.type === 'info'
                ? 'var(--status-info)'
                : 'var(--status-success)',
            border: '1px solid currentColor',
          }}
        >
          {notification.type === 'error' ? <AlertCircle size={16} /> : <CheckCircle2 size={16} />}
          <span>{notification.msg}</span>
        </div>
      )}

      {/* Lista de Documentos con Búsqueda y Filtros */}
      <DocumentList
        documents={documents}
        loading={loading}
        onIndex={handleIndex}
        onDelete={handleDelete}
        onOpenViewer={onOpenViewer}
      />

      {/* Modal de Carga de Manuales */}
      <DocumentUploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={(newDoc) => {
          showNotification(`Manual '${newDoc.original_filename}' subido exitosamente.`);
          loadDocuments();
        }}
      />
    </div>
  );
}
