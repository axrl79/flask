import { useState, useEffect, useRef } from 'react';
import { chatApi } from '../api/chatApi';
import { documentsApi } from '../api/documentsApi';
import ChatMessage from '../components/chat/ChatMessage';
import ChatInput from '../components/chat/ChatInput';
import { Bot, Plus, MessageSquare, Trash2, AlertCircle, Loader2 } from 'lucide-react';

export default function ChatPage({ onOpenViewer }) {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const loadSession = async (sessionId) => {
    try {
      setActiveSessionId(sessionId);
      const data = await chatApi.getSession(sessionId);
      setMessages(data.messages || []);
    } catch (err) {
      setError(err.message || 'Error cargando sesión.');
    }
  };

  // Cargar lista de sesiones y manuales indexados al inicio
  useEffect(() => {
    let mounted = true;
    const initialize = async () => {
      try {
        const [sessionsData, docsData] = await Promise.all([
          chatApi.listSessions().catch(() => []),
          documentsApi.list().catch(() => []),
        ]);
        if (!mounted) return;
        setSessions(sessionsData);
        setDocuments(docsData);

        if (sessionsData.length > 0) {
          loadSession(sessionsData[0].id);
        }
      } catch (err) {
        if (mounted) setError(err.message || 'Error inicializando el asistente.');
      }
    };
    initialize();
    return () => { mounted = false; };
  }, []);

  const handleNewSession = async () => {
    try {
      const newSession = await chatApi.createSession('Nueva Consulta Técnica');
      setSessions((prev) => [newSession, ...prev]);
      setActiveSessionId(newSession.id);
      setMessages([]);
    } catch (err) {
      setError(err.message || 'Error al crear sesión.');
    }
  };

  const handleDeleteSession = async (sessionId, e) => {
    e.stopPropagation();
    try {
      await chatApi.deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        setActiveSessionId(null);
        setMessages([]);
      }
    } catch (err) {
      setError(err.message || 'Error al eliminar sesión.');
    }
  };

  const handleSendMessage = async (queryText) => {
    setError(null);
    setLoading(true);

    // Agregar mensaje local del usuario inmediatamente para fluidez
    const userMsg = {
      role: 'user',
      content: queryText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const response = await chatApi.query(
        queryText,
        activeSessionId,
        selectedDocId,
        4
      );

      // Si la sesión era nueva, actualizar ID de sesión activa y lista
      if (!activeSessionId && response.session_id) {
        setActiveSessionId(response.session_id);
        chatApi.listSessions().then(setSessions);
      }

      // Agregar respuesta estructurada del asistente
      const assistantMsg = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources || [],
        evidence_sufficient: response.evidence_sufficient,
        latency_seconds: response.latency_seconds,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setError(err.message || 'Error al consultar el motor RAG.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        gap: '20px',
        height: 'calc(100vh - var(--header-height) - 56px)',
        minHeight: '500px',
      }}
    >
      {/* Panel Lateral: Historial de Sesiones */}
      <div
        className="glass-card"
        style={{
          width: '260px',
          padding: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          flexShrink: 0,
        }}
      >
        <button className="btn btn-primary" onClick={handleNewSession} style={{ width: '100%' }}>
          <Plus size={16} /> Nueva Consulta
        </button>

        <div style={{ fontSize: '11px', color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: '0.04em', marginTop: '6px' }}>
          Historial de Sesiones
        </div>

        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {sessions.length === 0 ? (
            <div style={{ fontSize: '12px', color: 'var(--text-faint)', padding: '12px 4px' }}>
              No hay sesiones previas
            </div>
          ) : (
            sessions.map((s) => (
              <div
                key={s.id}
                onClick={() => loadSession(s.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '9px 12px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: activeSessionId === s.id ? 'var(--bg-card-hover)' : 'transparent',
                  border: `1px solid ${activeSessionId === s.id ? 'var(--border-medium)' : 'transparent'}`,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  fontSize: '13px',
                  color: activeSessionId === s.id ? 'var(--text-main)' : 'var(--text-muted)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                  <MessageSquare size={14} color={activeSessionId === s.id ? 'var(--accent-purple)' : 'var(--text-faint)'} />
                  <span style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                    {s.title}
                  </span>
                </div>
                <button
                  onClick={(e) => handleDeleteSession(s.id, e)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--text-faint)',
                    cursor: 'pointer',
                    padding: '2px',
                    display: 'flex',
                  }}
                  title="Eliminar sesión"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Área Principal de Conversación */}
      <div
        className="glass-card"
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          padding: '20px',
          gap: '16px',
          minWidth: 0,
        }}
      >
        {/* Mensajes del Chat */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
            paddingRight: '6px',
          }}
        >
          {messages.length === 0 ? (
            <div
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '14px',
                color: 'var(--text-faint)',
                textAlign: 'center',
                padding: '40px 20px',
              }}
            >
              <div
                style={{
                  width: '54px',
                  height: '54px',
                  borderRadius: '14px',
                  backgroundColor: 'rgba(168, 85, 247, 0.12)',
                  color: 'var(--accent-purple)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Bot size={28} />
              </div>
              <div>
                <h3 style={{ fontSize: '17px', color: 'var(--text-main)', marginBottom: '6px' }}>
                  Asistente Técnico Especializado
                </h3>
                <p style={{ fontSize: '13px', maxWidth: '460px', lineHeight: '1.6' }}>
                  Formula preguntas sobre parámetros, códigos de falla, presiones o procedimientos de mantenimiento. Las respuestas se fundamentarán exclusivamente en los manuales indexados.
                </p>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <ChatMessage
                key={msg.id || idx}
                message={msg}
                onOpenViewer={onOpenViewer}
              />
            ))
          )}

          {/* Estado de Pensamiento / Generación */}
          {loading && (
            <div
              className="animate-fade-in"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '14px 18px',
                borderRadius: 'var(--radius-lg)',
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--accent-purple)',
                fontSize: '13px',
              }}
            >
              <Loader2 size={16} className="spin" />
              <span>Consultando fragmentos en ChromaDB e infiriendo respuesta con Ollama...</span>
            </div>
          )}

          {/* Mensaje de Error si ocurre */}
          {error && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 16px',
                backgroundColor: 'var(--status-error-bg)',
                color: 'var(--status-error)',
                borderRadius: 'var(--radius-md)',
                fontSize: '13px',
              }}
            >
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input de Consulta */}
        <ChatInput
          onSendMessage={handleSendMessage}
          loading={loading}
          documents={documents}
          selectedDocId={selectedDocId}
          onSelectDocId={setSelectedDocId}
        />
      </div>
    </div>
  );
}
