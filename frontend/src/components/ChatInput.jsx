/**
 * ChatInput.jsx — The input bar at the bottom of the chat.
 *
 * Props:
 *   - value:      current input string
 *   - onChange:    handler for input changes
 *   - onSubmit:   handler for form submission
 *   - isLoading:  whether a request is in progress
 */

function ChatInput({ value, onChange, onSubmit, isLoading }) {
  return (
    <form className="input-bar" onSubmit={onSubmit}>
      <div className="input-wrapper">
        <input
          type="text"
          value={value}
          onChange={onChange}
          placeholder="Escribe tu pregunta sobre el reglamento..."
          disabled={isLoading}
          autoFocus
        />
        <button type="submit" disabled={isLoading || !value.trim()} aria-label="Enviar">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
      <p className="input-hint">
        Presiona Enter para enviar · Basado en el Reglamento General de Estudiantes 2025
      </p>
    </form>
  )
}

export default ChatInput
