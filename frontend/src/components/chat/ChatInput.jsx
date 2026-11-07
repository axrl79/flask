import { useState } from 'react';
import { Send, Filter, Loader2, Sparkles } from 'lucide-react';

export default function ChatInput({
  onSendMessage,
  loading,
  documents = [],
  selectedDocId,
  onSelectDocId,
}) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!query.trim() || loading) return;
    onSendMessage(query.trim());
    setQuery('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const indexedDocs = documents.filter((d) => d.status === 'indexed');

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--border-medium)',
        borderRadius: 'var(--radius-lg)',
        padding: '12px 16px',
        boxShadow: '0 8px 30px rgba(0, 0, 0, 0.4)',
      }}
    >
      {/* Selector de Manual Filtro */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-muted)' }}>
          <Filter size={13} color="var(--accent-purple)" />
          <span>Consultar en:</span>
          <select
            value={selectedDocId || ''}
            onChange={(e) => onSelectDocId(e.target.value || null)}
            className="input-field"
            style={{
              padding: '3px 8px',
              fontSize: '11px',
              backgroundColor: 'var(--bg-card)',
              maxWidth: '260px',
            }}
          >
            <option value="">Todos los manuales ({indexedDocs.length} indexados)</option>
            {indexedDocs.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.original_filename}
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--text-faint)' }}>
          <Sparkles size={12} color="var(--accent-purple)" />
          <span>Temperatura 0.0 (Cero Alucinaciones)</span>
        </div>
      </div>

      {/* Input de texto y Botón de Envío */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <textarea
          rows={1}
          placeholder="Escribe una consulta técnica (ej: ¿Cuál es el torque para los pernos M12 o cómo resolver el código E-205?)..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          className="input-field"
          style={{
            flex: 1,
            resize: 'none',
            minHeight: '40px',
            maxHeight: '120px',
            border: 'none',
            backgroundColor: 'transparent',
            padding: '8px 0',
          }}
        />

        <button
          onClick={handleSubmit}
          disabled={!query.trim() || loading}
          className="btn btn-primary"
          style={{
            padding: '8px 14px',
            borderRadius: 'var(--radius-md)',
            flexShrink: 0,
          }}
        >
          {loading ? (
            <Loader2 size={16} className="spin" />
          ) : (
            <>
              <span>Consultar</span>
              <Send size={14} />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
