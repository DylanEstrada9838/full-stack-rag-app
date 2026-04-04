/**
 * ChatMessage.jsx — A single message bubble (user or bot).
 *
 * Props:
 *   - role:    'user' | 'bot'
 *   - text:    The message content string
 *   - sources: (optional) Array of page numbers retrieved
 */

function ChatMessage({ role, text, sources }) {
  const isUser = role === 'user'

  return (
    <div className={`message ${role}`}>
      {/* Avatar */}
      {!isUser && (
        <div className="avatar bot-avatar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z" />
            <path d="M16 14H8a4 4 0 0 0-4 4v2h16v-2a4 4 0 0 0-4-4z" />
          </svg>
        </div>
      )}

      <div className="message-content">
        {/* Role label */}
        <span className="message-label">{isUser ? 'Tú' : 'Asistente'}</span>

        {/* Bubble */}
        <div className={`message-bubble ${isUser ? 'user-bubble' : 'bot-bubble'}`}>
          {text}

          {/* Source page tags */}
          {sources && sources.length > 0 && (
            <div className="sources">
              <div className="sources-header">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                <span>Páginas fuente</span>
              </div>
              <div className="source-tags">
                {sources.map((page) => (
                  <span key={page} className="source-tag">
                    Pág. {page}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="avatar user-avatar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </div>
      )}
    </div>
  )
}

export default ChatMessage
