import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import DashboardPage from './pages/DashboardPage';
import DocumentsPage from './pages/DocumentsPage';
import ChatPage from './pages/ChatPage';
import SystemPage from './pages/SystemPage';
import PDFViewerModal from './components/viewer/PDFViewerModal';

function AppContent() {
  const location = useLocation();

  // Estado global para el visor de PDF accesible desde cualquier pantalla
  const [viewerState, setViewerState] = useState({
    isOpen: false,
    documentId: null,
    documentName: '',
    initialPage: 1,
    highlightSnippet: null,
  });

  const openViewer = (documentId, documentName, page = 1, snippet = null) => {
    setViewerState({
      isOpen: true,
      documentId,
      documentName,
      initialPage: page,
      highlightSnippet: snippet,
    });
  };

  const closeViewer = () => {
    setViewerState((prev) => ({ ...prev, isOpen: false }));
  };

  const getPageTitle = (pathname) => {
    switch (pathname) {
      case '/':
        return 'Panel de Control';
      case '/documents':
        return 'Gestión de Manuales Técnicos';
      case '/chat':
        return 'Asistente Técnico RAG';
      case '/system':
        return 'Salud y Diagnóstico de Servicios';
      default:
        return 'Plataforma RAG Industrial';
    }
  };

  return (
    <div className="app-container">
      {/* Navegación Lateral */}
      <Sidebar />

      {/* Contenido Principal */}
      <div className="main-content">
        <Header title={getPageTitle(location.pathname)} />

        <main className="page-body">
          <Routes>
            <Route path="/" element={<DashboardPage onOpenViewer={openViewer} />} />
            <Route path="/documents" element={<DocumentsPage onOpenViewer={openViewer} />} />
            <Route path="/chat" element={<ChatPage onOpenViewer={openViewer} />} />
            <Route path="/system" element={<SystemPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>

      {/* Visor Modal de PDF con Salto a Página y Snippet de Referencia */}
      <PDFViewerModal
        isOpen={viewerState.isOpen}
        onClose={closeViewer}
        documentId={viewerState.documentId}
        documentName={viewerState.documentName}
        initialPage={viewerState.initialPage}
        highlightSnippet={viewerState.highlightSnippet}
      />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
