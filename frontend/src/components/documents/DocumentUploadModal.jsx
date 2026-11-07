import { useState, useRef } from 'react';
import Modal from '../common/Modal';
import { UploadCloud, AlertCircle, Loader2 } from 'lucide-react';
import { documentsApi } from '../../api/documentsApi';

export default function DocumentUploadModal({ isOpen, onClose, onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const resetState = () => {
    setFile(null);
    setUploading(false);
    setProgress(0);
    setError(null);
  };

  const handleClose = () => {
    if (!uploading) {
      resetState();
      onClose();
    }
  };

  const validateAndSetFile = (selectedFile) => {
    setError(null);
    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setError('Únicamente se admiten manuales en formato PDF (.pdf).');
      return;
    }

    if (selectedFile.size > 50 * 1024 * 1024) {
      setError('El tamaño del archivo no puede exceder 50 MB.');
      return;
    }

    setFile(selectedFile);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const doc = await documentsApi.upload(file, (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setProgress(percent);
      });
      resetState();
      onUploadSuccess(doc);
      onClose();
    } catch (err) {
      setError(err.message || 'Error al subir el manual.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Cargar Manual Técnico">
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Zona Drag & Drop */}
        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: `2px dashed ${isDragOver ? 'var(--accent-purple)' : 'var(--border-medium)'}`,
            borderRadius: 'var(--radius-lg)',
            padding: '36px 20px',
            textAlign: 'center',
            backgroundColor: isDragOver ? 'rgba(168, 85, 247, 0.05)' : 'var(--bg-secondary)',
            cursor: uploading ? 'not-allowed' : 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => validateAndSetFile(e.target.files?.[0])}
            accept=".pdf"
            style={{ display: 'none' }}
            disabled={uploading}
          />

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '46px',
                height: '46px',
                borderRadius: '50%',
                backgroundColor: 'rgba(168, 85, 247, 0.12)',
                color: 'var(--accent-purple)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <UploadCloud size={24} />
            </div>
            <div>
              <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '14px' }}>
                {file ? file.name : 'Arrastra un manual PDF aquí o haz clic para explorar'}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-faint)', marginTop: '4px' }}>
                {file
                  ? `${(file.size / (1024 * 1024)).toFixed(2)} MB`
                  : 'Soporta manuales técnicos de maquinaria, catálogos y especificaciones (Máx 50 MB)'}
              </div>
            </div>
          </div>
        </div>

        {/* Barra de progreso */}
        {uploading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Subiendo y validando integridad...</span>
              <span style={{ color: 'var(--accent-purple)', fontWeight: 600 }}>{progress}%</span>
            </div>
            <div style={{ width: '100%', height: '6px', backgroundColor: 'var(--bg-secondary)', borderRadius: '3px', overflow: 'hidden' }}>
              <div
                style={{
                  width: `${progress}%`,
                  height: '100%',
                  background: 'linear-gradient(90deg, #9333ea, #c084fc)',
                  transition: 'width 0.2s ease',
                }}
              />
            </div>
          </div>
        )}

        {/* Mensaje de error */}
        {error && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 14px',
              backgroundColor: 'var(--status-error-bg)',
              color: 'var(--status-error)',
              borderRadius: 'var(--radius-md)',
              fontSize: '12px',
            }}
          >
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Botones de acción */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <button type="button" className="btn btn-secondary" onClick={handleClose} disabled={uploading}>
            Cancelar
          </button>
          <button type="submit" className="btn btn-primary" disabled={!file || uploading}>
            {uploading ? (
              <>
                <Loader2 size={16} className="spin" />
                Subiendo...
              </>
            ) : (
              'Cargar Manual'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
}
