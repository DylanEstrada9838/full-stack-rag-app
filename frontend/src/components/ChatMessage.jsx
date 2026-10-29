import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

/**
 * ChatMessage.jsx — A single message bubble (user or bot).
 *
 * Props:
 *   - role:    'user' | 'bot'
 *   - text:    The message content string
 *   - sources: (optional) Array of page numbers retrieved
 */

function ChatMessage({
  role,
  text,
  sources,
  latency,
  chunks,
  retrievalSec,
  llmSec,
  retrievalMs,
  llmMs,
  inputTokens,
  outputTokens,
  totalCost,
  model,
  onOpenChunks,
}) {
  const isUser = role === 'user'

  const formattedRetrievalSec =
    retrievalSec != null
      ? Number(retrievalSec).toFixed(2)
      : retrievalMs != null
      ? (Number(retrievalMs) / 1000).toFixed(2)
      : null

  const formattedLlmSec =
    llmSec != null
      ? Number(llmSec).toFixed(2)
      : llmMs != null
      ? (Number(llmMs) / 1000).toFixed(2)
      : null

  const hasDetails =
    !isUser &&
    (model ||
      inputTokens != null ||
      outputTokens != null ||
      totalCost != null)

  const hasTelemetry =
    !isUser &&
    (formattedRetrievalSec != null ||
      formattedLlmSec != null ||
      hasDetails ||
      latency != null ||
      (chunks && chunks.length > 0))

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
          {isUser ? (
            <div className="user-message-text">{text}</div>
          ) : (
            <div className="markdown-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
            </div>
          )}


          {/* Bot telemetry footer: 2 Latencies directly visible, details on hover, and Chunks */}
          {hasTelemetry && (
            <div className="message-telemetry-container">
              <div className="message-telemetry-grid">
                {formattedRetrievalSec != null && (
                  <div className="telemetry-pill latency-retrieval" title="Latencia de recuperación en base vectorial + BM25">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                    </svg>
                    <span>Recuperación: {formattedRetrievalSec}s</span>
                  </div>
                )}

                {formattedLlmSec != null && (
                  <div className="telemetry-pill latency-model" title="Latencia de generación del modelo OpenAI">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10" />
                      <polyline points="12 6 12 12 16 14" />
                    </svg>
                    <span>Modelo: {formattedLlmSec}s</span>
                  </div>
                )}

                {hasDetails && (
                  <div className="telemetry-info-wrapper">
                    <button
                      type="button"
                      className="telemetry-info-trigger"
                      aria-label="Más información sobre modelo, tokens y costo"
                    >
                      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="12" y1="16" x2="12" y2="12" />
                        <line x1="12" y1="8" x2="12.01" y2="8" />
                      </svg>
                      <span>+ Info</span>
                    </button>

                    <div className="telemetry-popover" role="tooltip">
                      <div className="telemetry-popover-header">Detalles de la respuesta</div>
                      <div className="telemetry-popover-list">
                        {model && (
                          <div className="telemetry-popover-item">
                            <span className="popover-label">Modelo:</span>
                            <span className="popover-value popover-model-badge">{model}</span>
                          </div>
                        )}
                        {inputTokens != null && (
                          <div className="telemetry-popover-item">
                            <span className="popover-label">Tokens entrada:</span>
                            <span className="popover-value">{inputTokens} tok</span>
                          </div>
                        )}
                        {outputTokens != null && (
                          <div className="telemetry-popover-item">
                            <span className="popover-label">Tokens salida:</span>
                            <span className="popover-value">{outputTokens} tok</span>
                          </div>
                        )}
                        {inputTokens != null && outputTokens != null && (
                          <div className="telemetry-popover-item">
                            <span className="popover-label">Total tokens:</span>
                            <span className="popover-value">{inputTokens + outputTokens} tok</span>
                          </div>
                        )}
                        {totalCost != null && (
                          <div className="telemetry-popover-item popover-cost-item">
                            <span className="popover-label">Costo estimado:</span>
                            <span className="popover-value popover-cost-value">
                              ${Number(totalCost).toFixed(5)}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {chunks && chunks.length > 0 && (
                  <button
                    type="button"
                    className="open-chunks-btn"
                    onClick={() => onOpenChunks(chunks)}
                    title="Ver los fragmentos recuperados para esta respuesta"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                    </svg>
                    <span>Ver 5 Chunks</span>
                  </button>
                )}
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
