import { useEffect } from 'react'

/**
 * ChunksPanel.jsx — Slide-out drawer / modal showing the top 5 retrieved
 * document chunks for the current question.
 *
 * Props:
 *   - isOpen:   boolean controlling visibility
 *   - onClose:  function to close the panel
 *   - chunks:   array of { page: number, content: string }
 *   - question: current question string
 */

function cleanChunkText(text) {
  if (!text) return ''
  // Replace single newlines within paragraphs with spaces, preserving real paragraph breaks
  return text.replace(/(?<!\n)\n(?!\n)/g, ' ')
}

function ChunksPanel({ isOpen, onClose, chunks = [], question = '' }) {
  // Close on Escape key press
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div className="chunks-backdrop" onClick={onClose} aria-modal="true" role="dialog">
      <div className="chunks-drawer" onClick={(e) => e.stopPropagation()}>
        {/* Mobile handle indicator */}
        <div className="drawer-handle-bar">
          <div className="drawer-handle"></div>
        </div>

        {/* Drawer Header */}
        <div className="chunks-header">
          <div className="chunks-title-group">
            <div className="chunks-badge-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
              </svg>
            </div>
            <div>
              <h3>Fragmentos Recuperados</h3>
              <p className="chunks-subtitle">Top 5 chunks utilizados por el sistema RAG</p>
            </div>
          </div>
          <button
            type="button"
            className="chunks-close-btn"
            onClick={onClose}
            aria-label="Cerrar panel de fragmentos"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Question context bar */}
        {question && (
          <div className="chunks-question-bar">
            <span className="question-tag">Pregunta:</span>
            <span className="question-text">"{question}"</span>
          </div>
        )}

        {/* Body with Chunks */}
        <div className="chunks-body">
          {chunks.length === 0 ? (
            <div className="chunks-empty">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <p>No hay fragmentos disponibles para esta consulta aún.</p>
            </div>
          ) : (
            chunks.map((chunk, index) => (
              <div key={index} className="chunk-card">
                <div className="chunk-card-header">
                  <span className="chunk-rank">#{index + 1}</span>
                  <span className="chunk-page-tag">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                    </svg>
                    Página {chunk.page}
                  </span>
                </div>
                <div className="chunk-content">
                  {cleanChunkText(chunk.content)}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Drawer footer */}
        <div className="chunks-footer">
          <p>
            Recuperado mediante búsqueda híbrida (60% Semántica MMR + 40% Léxica BM25)
          </p>
        </div>
      </div>
    </div>
  )
}

export default ChunksPanel
