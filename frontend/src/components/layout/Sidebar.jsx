import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Bot,
  Activity,
  Cpu,
  ShieldCheck,
} from 'lucide-react';

export default function Sidebar() {
  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/documents', label: 'Manuales Técnicos', icon: FileText },
    { to: '/chat', label: 'Asistente RAG', icon: Bot },
    { to: '/system', label: 'Estado del Sistema', icon: Activity },
  ];

  return (
    <aside
      style={{
        width: 'var(--sidebar-width)',
        backgroundColor: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '24px 16px',
        flexShrink: 0,
      }}
    >
      <div>
        {/* Brand / Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '0 8px 28px 8px' }}>
          <div
            style={{
              width: '34px',
              height: '34px',
              borderRadius: '9px',
              background: 'linear-gradient(135deg, #a855f7, #3b82f6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              boxShadow: '0 0 15px rgba(168, 85, 247, 0.4)',
            }}
          >
            <Cpu size={20} />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '15px', color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
              RAG Industrial
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-faint)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Plataforma Local
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  textDecoration: 'none',
                  fontSize: '13px',
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? '#fff' : 'var(--text-muted)',
                  backgroundColor: isActive ? 'var(--bg-card)' : 'transparent',
                  border: isActive ? '1px solid var(--border-medium)' : '1px solid transparent',
                  transition: 'all 0.15s ease',
                })}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div
        className="glass-card"
        style={{
          padding: '12px 14px',
          fontSize: '11px',
          backgroundColor: 'rgba(255, 255, 255, 0.02)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        <ShieldCheck size={16} color="var(--status-success)" />
        <div>
          <div style={{ color: 'var(--text-main)', fontWeight: 600 }}>100% Local & Privado</div>
          <div style={{ color: 'var(--text-faint)' }}>Sin salida a APIs en la nube</div>
        </div>
      </div>
    </aside>
  );
}
