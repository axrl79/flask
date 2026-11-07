import { BookOpen, ExternalLink, Table } from 'lucide-react';

export default function SourceCard({ source, onOpenViewer }) {
  const {
    document_id,
    document_name,
    page_number,
    similarity_score,
    snippet,
    is_table,
  } = source;

  const scorePercent = similarity_score ? Math.round(similarity_score * 100) : null;

  return (
    <div
      className="glass-card"
      style={{
        padding: '12px 14px',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        transition: 'all 0.15s ease',
      }}
    >
      {/* Cabecera de la Fuente */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', minWidth: 0 }}>
          {is_table ? <Table size={14} color="#38bdf8" /> : <BookOpen size={14} color="var(--accent-purple)" />}
          <span
            style={{
              fontSize: '12px',
              fontWeight: 600,
              color: 'var(--text-main)',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
            title={document_name}
          >
            {document_name}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
          {scorePercent !== null && (
            <span
              style={{
                fontSize: '11px',
                color: scorePercent > 75 ? 'var(--status-success)' : 'var(--text-muted)',
                backgroundColor: 'rgba(255, 255, 255, 0.04)',
                padding: '2px 6px',
                borderRadius: '4px',
              }}
              title="Similitud semántica con la consulta"
            >
              {scorePercent}%
            </span>
          )}

          <button
            className="btn btn-secondary"
            onClick={() => onOpenViewer(document_id, document_name, page_number, snippet)}
            style={{
              padding: '3px 8px',
              fontSize: '11px',
              color: 'var(--accent-purple)',
              borderColor: 'var(--border-subtle)',
            }}
          >
            <span>Pág. {page_number}</span>
            <ExternalLink size={11} />
          </button>
        </div>
      </div>

      {/* Snippet de Evidencia */}
      {snippet && (
        <div
          style={{
            fontSize: '12px',
            color: 'var(--text-muted)',
            lineHeight: '1.5',
            backgroundColor: 'rgba(0, 0, 0, 0.25)',
            padding: '8px 10px',
            borderRadius: 'var(--radius-sm)',
            fontFamily: 'var(--font-mono)',
            maxHeight: '80px',
            overflowY: 'auto',
          }}
        >
          {snippet}
        </div>
      )}
    </div>
  );
}
