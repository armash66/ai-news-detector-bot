import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, Search, Bell, BarChart2, Settings, HelpCircle, ShieldCheck } from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { name: 'Event Feed', path: '/feed', icon: Home },
    { name: 'Intelligence', path: '/intelligence', icon: Search },
    { name: 'Alerts', path: '/alerts', icon: Bell },
    { name: 'Analytics', path: '/analytics', icon: BarChart2 },
    { name: 'Analyze Article', path: '/analyze', icon: ShieldCheck },
  ];

  return (
    <aside style={{
      width: 'var(--sidebar-width)',
      backgroundColor: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-light)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      padding: '1.5rem 1rem',
    }}>
      {/* Logo Block */}
      <div style={{ padding: '0 0.75rem', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{
          width: '32px', height: '32px', borderRadius: '8px',
          background: 'linear-gradient(135deg, var(--primary), #6366f1)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'white', fontWeight: 'bold', fontSize: '0.875rem',
          boxShadow: '0 2px 8px rgba(67,56,202,0.3)',
        }}>
          TL
        </div>
        <div>
          <h2 style={{ fontSize: '1rem', margin: 0, fontWeight: 700 }}>TruthLens</h2>
          <div style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)', letterSpacing: '0.08em', textTransform: 'uppercase', fontWeight: 600 }}>Intelligence</div>
        </div>
      </div>

      {/* Primary Navigation */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', flex: 1 }}>
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            end={item.path === '/'}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.7rem 0.75rem',
              borderRadius: '8px',
              textDecoration: 'none',
              color: isActive ? 'var(--primary)' : 'var(--text-secondary)',
              backgroundColor: isActive ? 'var(--primary-light)' : 'transparent',
              fontWeight: isActive ? 600 : 500,
              fontSize: '0.875rem',
              transition: 'all 0.15s',
            })}
          >
            <item.icon size={18} />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* Footer Settings */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
        <a href="#" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.7rem 0.75rem', textDecoration: 'none', color: 'var(--text-secondary)', fontSize: '0.875rem', fontWeight: 500, borderRadius: '8px' }}>
          <Settings size={18} /> Settings
        </a>
        <a href="#" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.7rem 0.75rem', textDecoration: 'none', color: 'var(--text-secondary)', fontSize: '0.875rem', fontWeight: 500, borderRadius: '8px' }}>
          <HelpCircle size={18} /> Support
        </a>

        {/* User Profile */}
        <div style={{ marginTop: '0.75rem', padding: '0.75rem', backgroundColor: 'var(--bg-app)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: '34px', height: '34px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--primary), #6366f1)', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 700, fontSize: '0.75rem' }}>IU</div>
          <div>
            <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-primary)' }}>Intelligence Unit</div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>Global Feed • Live</div>
          </div>
        </div>
      </div>
    </aside>
  );
};
