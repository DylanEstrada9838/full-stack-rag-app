import { SUGGESTED_QUESTIONS } from '../constants/suggestions'

/**
 * WelcomeCard.jsx — Shown at the top of the chat with helpful suggestions.
 *
 * Props:
 *   - onSuggestionClick: handler called with the suggestion text when clicked
 */
function WelcomeCard({ onSuggestionClick }) {
  return (
    <div className="welcome-card">
      <div className="welcome-icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      </div>
      <h2>¿En qué puedo ayudarte?</h2>
      <p>
        Soy un asistente especializado en el Reglamento General de Estudiantes
        del Tecnológico de Monterrey. Puedes preguntarme sobre cualquier artículo,
        procedimiento o normativa.
      </p>

      {/* Azure Container Apps Cold Start Latency Notice */}
      <div className="latency-notice">
        <div className="latency-notice-header">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
          </svg>
          <span>Velocidad de respuesta</span>
        </div>
        <p className="latency-notice-text">
          El <strong>primer mensaje</strong> puede tardar de <strong>5 a 9s</strong> por reactivación del servidor (Azure Container Apps). Luego las respuestas son inmediatas.
        </p>
      </div>
      <div className="suggestions">
        {SUGGESTED_QUESTIONS.map((text, i) => (
          <button
            key={i}
            className="suggestion-chip"
            onClick={() => onSuggestionClick(text)}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6" />
            </svg>
            {text}
          </button>
        ))}
      </div>
    </div>
  )
}

export default WelcomeCard
