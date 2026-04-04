/**
 * ThinkingIndicator.jsx — Animated dots shown while the bot is processing.
 */

function ThinkingIndicator() {
  return (
    <div className="message bot">
      <div className="avatar bot-avatar">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z" />
          <path d="M16 14H8a4 4 0 0 0-4 4v2h16v-2a4 4 0 0 0-4-4z" />
        </svg>
      </div>
      <div className="message-content">
        <span className="message-label">Asistente</span>
        <div className="message-bubble bot-bubble thinking-bubble">
          <div className="thinking">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <span className="thinking-text">Analizando el reglamento...</span>
        </div>
      </div>
    </div>
  )
}

export default ThinkingIndicator
