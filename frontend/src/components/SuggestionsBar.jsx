/**
 * SuggestionsBar.jsx — Horizontal scrollable bar with prompt suggestion pills.
 *
 * Placed immediately above the ChatInput to keep suggested questions
 * persistently accessible after the first question has been asked.
 *
 * Props:
 *   - suggestions: Array of question strings
 *   - onSelect:    Callback invoked when a suggestion pill is clicked
 *   - disabled:    Whether interactions should be prevented (e.g. while loading)
 */

function SuggestionsBar({ suggestions, onSelect, disabled }) {
  if (!suggestions || suggestions.length === 0) return null

  return (
    <div className="suggestions-bar">
      <div className="suggestions-bar-header">
        <svg
          width="13"
          height="13"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        <span>Preguntas sugeridas</span>
      </div>

      <div className="suggestions-bar-track">
        {suggestions.map((text, idx) => (
          <button
            key={idx}
            type="button"
            className="suggestion-pill"
            disabled={disabled}
            onClick={() => onSelect(text)}
            title={text}
          >
            <svg
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="9 18 15 12 9 6" />
            </svg>
            <span>{text}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

export default SuggestionsBar
