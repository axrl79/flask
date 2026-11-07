import { useState } from 'react';
import Modal from '../common/Modal';
import { ExternalLink, ChevronLeft, ChevronRight, Quote } from 'lucide-react';
import { documentsApi } from '../../api/documentsApi';

export default function PDFViewerModal({
  isOpen,
  onClose,
  documentId,
  documentName,
  initialPage = 1,
  highlightSnippet = null,
}) {
  const [currentPage, setCurrentPage] = useState(initialPage);
  const pdfUrl = documentId ? `${documentsApi.getDownloadUrl(documentId)}#page=${currentPage}` : '';

  if (!isOpen || !documentId) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Visor Técnico: ${documentName || 'Manual PDF'}`}
      maxWidth="1100px"
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', height: '78vh' }}>
        {/* Barra superior de herramientas del visor */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 14px',
            backgroundColor: 'var(--bg-secondary)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Página actual:</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <button
                className="btn btn-secondary"
                style={{ padding: '4px 8px' }}
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              >
                <ChevronLeft size={16} />
              </button>
              <input
                type="number"
                min="1"
                value={currentPage}
                onChange={(e) => setCurrentPage(parseInt(e.target.value) || 1)}
                className="input-field"
                style={{ width: '60px', padding: '4px 8px', textAlign: 'center' }}
              />
              <button
                className="btn btn-secondary"
                style={{ padding: '4px 8px' }}
                onClick={() => setCurrentPage((p) => p + 1)}
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <a
              href={documentsApi.getDownloadUrl(documentId)}
              target="_blank"
              rel="noreferrer"
              className="btn btn-secondary"
              style={{ padding: '6px 12px', fontSize: '12px' }}
            >
              <ExternalLink size={14} />
              Abrir en nueva pestaña
            </a>
          </div>
        </div>

        {/* Contenedor dividido: Visor PDF + Panel de Referencia/Cita */}
        <div style={{ display: 'flex', gap: '16px', flex: 1, minHeight: 0 }}>
          {/* Iframe del visor nativo con navegación #page= */}
          <div
            style={{
              flex: highlightSnippet ? 2.8 : 1,
              backgroundColor: '#050608',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)',
              overflow: 'hidden',
            }}
          >
            <iframe
              key={`${documentId}-${currentPage}`}
              src={pdfUrl}
              title="Visor PDF"
              style={{
                width: '100%',
                height: '100%',
                border: 'none',
              }}
            />
          </div>

          {/* Panel lateral con el fragmento citado */}
          {highlightSnippet && (
            <div
              style={{
                flex: 1.2,
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                overflowY: 'auto',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-purple)' }}>
                <Quote size={18} />
                <h4 style={{ fontSize: '14px', fontWeight: 600 }}>Fragmento de Evidencia</h4>
              </div>
              <div
                style={{
                  fontSize: '11px',
                  color: 'var(--text-faint)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                }}
              >
                Cita extraída de la Página {currentPage}
              </div>
              <div
                style={{
                  backgroundColor: 'var(--bg-card)',
                  padding: '14px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-subtle)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '12px',
                  lineHeight: '1.6',
                  color: 'var(--text-main)',
                  whiteSpace: 'pre-wrap',
                }}
              >
                {highlightSnippet}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: 'auto' }}>
                💡 <em>Usa el visor para examinar diagramas, esquemas o especificaciones circundantes en la página citada.</em>
              </div>
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
}
