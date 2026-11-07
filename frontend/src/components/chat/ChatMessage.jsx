import { User, Bot, Layers, Clock, ShieldAlert } from 'lucide-react';
import SourceCard from './SourceCard';

export default function ChatMessage({ message, onOpenViewer }) {
  const isUser = message.role === 'user';
  const sources = message.citations || message.sources || [];
  const evidenceSufficient = message.evidence_sufficient !== false;

  return (
    <div
      className="animate-fade-in"
      style={{
        display: 'flex',
        gap: '14px',
        padding: '16px 20px',
        borderRadius: 'var(--radius-lg)',
        backgroundColor: isUser ? 'rgba(255, 255, 255, 0.02)' : 'var(--bg-card)',
        border: `1px solid ${isUser ? 'transparent' : 'var(--border-subtle)'}`,
      }}
    >
      {/* Avatar */}
      <div
        style={{
          width: '32px',
          height: '32px',
          borderRadius: '8px',
          backgroundColor: isUser ? 'rgba(255, 255, 255, 0.08)' : 'rgba(168, 85, 247, 0.15)',
          color: isUser ? 'var(--text-main)' : 'var(--accent-purple)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      {/* Contenido del Mensaje */}
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {/* Cabecera del Mensaje */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
          <span style={{ fontSize: '13px', fontWeight: 600, color: isUser ? 'var(--text-main)' : 'var(--accent-purple)' }}>
            {isUser ? 'Técnico' : 'Asistente RAG Industrial'}
          </span>

          {!isUser && message.latency_seconds && (
            <span
              style={{
                fontSize: '11px',
                color: 'var(--text-faint)',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <Clock size={11} /> {message.latency_seconds}s
            </span>
          )}
        </div>

        {/* Advertencia si la evidencia no fue suficiente en los manuales */}
        {!isUser && !evidenceSufficient && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 12px',
              backgroundColor: 'var(--status-warning-bg)',
              color: 'var(--status-warning)',
              borderRadius: 'var(--radius-sm)',
              fontSize: '12px',
            }}
          >
            <ShieldAlert size={16} />
            <span>Información no documentada con certeza en los manuales indexados.</span>
          </div>
        )}

        {/* Texto de la Respuesta con salto de línea preservado */}
        <div
          style={{
            color: 'var(--text-main)',
            fontSize: '14px',
            lineHeight: '1.65',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
        >
          {message.content}
        </div>

        {/* Fuentes Documentales Citadas */}
        {!isUser && sources.length > 0 && (
          <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '12px',
                fontWeight: 600,
                color: 'var(--text-muted)',
                borderTop: '1px solid var(--border-subtle)',
                paddingTop: '10px',
              }}
            >
              <Layers size={14} color="var(--accent-purple)" />
              <span>Fuentes Técnicas Citadas ({sources.length}):</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '8px' }}>
              {sources.map((src, idx) => (
                <SourceCard
                  key={src.chunk_id || idx}
                  source={src}
                  onOpenViewer={onOpenViewer}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
