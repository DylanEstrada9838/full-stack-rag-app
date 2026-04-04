/**
 * Header.jsx — App header with gradient background and branding.
 */

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <div className="header-logo">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
              <line x1="8" y1="7" x2="16" y2="7" />
              <line x1="8" y1="11" x2="14" y2="11" />
            </svg>
          </div>
          <div className="header-text">
            <h1>Reglamento Universidad</h1>
            <p>Asistente IA · Reglamento General de Estudiantes</p>
          </div>
        </div>
        <div className="header-badge">
          <span className="status-dot"></span>
          En línea
        </div>
      </div>
    </header>
  )
}

export default Header
