/**
 * ChatInput.jsx — The input bar at the bottom of the chat.
 *
 * Props:
 *   - value:      current input string
 *   - onChange:   handler for input changes
 *   - onSubmit:   handler for form submission
 *   - isLoading:  whether a request is in progress
 *   - maxChars:   maximum allowed characters (default 500)
 *   - minChars:   minimum characters required (default 3)
 */

function ChatInput({ value, onChange, onSubmit, isLoading, maxChars = 500, minChars = 3 }) {
  const trimmed = value.trim()
  const charCount = value.length
  const isOverLimit = charCount > maxChars
  const isNearLimit = charCount >= maxChars * 0.8 && !isOverLimit
  const isValid = trimmed.length >= minChars && !isOverLimit

  return (
    <form className="input-bar" onSubmit={onSubmit}>
      {isOverLimit && (
        <div className="input-error-msg">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          La pregunta supera el límite de {maxChars} caracteres ({charCount}/{maxChars}).
        </div>
      )}

      <div className={`input-wrapper ${isOverLimit ? 'input-wrapper-error' : ''}`}>
        <input
          type="text"
          value={value}
          onChange={onChange}
          placeholder="Escribe tu pregunta sobre el reglamento..."
          disabled={isLoading}
          maxLength={maxChars + 50}
          autoFocus
        />
        <button
          type="submit"
          disabled={isLoading || !isValid}
          aria-label="Enviar"
          title={!isValid && trimmed.length > 0 ? (isOverLimit ? 'Pregunta demasiado larga' : 'Mínimo 3 caracteres') : 'Enviar pregunta'}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>

      <div className="input-meta">
        <span className="input-hint">
          Presiona Enter para enviar · Reglamento 2025
        </span>
        {charCount > 0 && (
          <span
            className={`char-counter ${
              isOverLimit ? 'char-counter-error' : isNearLimit ? 'char-counter-warning' : ''
            }`}
          >
            {charCount}/{maxChars}
          </span>
        )}
      </div>

      <div className="app-credit">
        Creado por <span className="credit-author">Dylan Estrada</span>
      </div>
    </form>
  )
}

export default ChatInput
