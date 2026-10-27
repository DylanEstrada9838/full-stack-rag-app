import { useState, useRef, useEffect } from 'react'
import Header from './components/Header'
import ChatMessage from './components/ChatMessage'
import ChatInput from './components/ChatInput'
import ThinkingIndicator from './components/ThinkingIndicator'
import WelcomeCard from './components/WelcomeCard'
import ChunksPanel from './components/ChunksPanel'
import SuggestionsBar from './components/SuggestionsBar'
import { SUGGESTED_QUESTIONS } from './constants/suggestions'
import './App.css'

/**
 * App.jsx — Root component that orchestrates the chat experience.
 *
 * - Manages the message list, input state, and active chunks inspection panel.
 * - Measures and displays latency for each message in seconds (2 decimals).
 * - Delegates rendering to Header, WelcomeCard, ChatMessage, ChatInput, ThinkingIndicator, ChunksPanel.
 * - Sends questions to the FastAPI backend (POST /ask).
 */

const RAW_API_URL = import.meta.env.VITE_API_URL || import.meta.env.API_URL || 'http://localhost:8000'
const API_URL = RAW_API_URL.replace(/\/+$/, '')

const MAX_CHARS = 500
const MIN_CHARS = 3

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentChunks, setCurrentChunks] = useState([])
  const [currentQuestion, setCurrentQuestion] = useState('')
  const [isChunksOpen, setIsChunksOpen] = useState(false)
  const messagesEndRef = useRef(null)

  // Auto-scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Send a question to the API
  const askQuestion = async (question) => {
    const trimmed = question.trim()
    if (!trimmed || trimmed.length < MIN_CHARS || trimmed.length > MAX_CHARS || isLoading) {
      return
    }

    setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'user', text: trimmed }])
    setInput('')
    setIsLoading(true)
    setCurrentQuestion(trimmed)

    const startTime = performance.now()

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: trimmed }),
      })

      if (!res.ok) throw new Error('Server error')
      const data = await res.json()

      const clientLatencySec = ((performance.now() - startTime) / 1000).toFixed(2)
      const resolvedLatency = data.latency != null ? Number(data.latency).toFixed(2) : clientLatencySec
      const chunks = data.chunks || []

      // Update current question chunks
      setCurrentChunks(chunks)

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'bot',
          text: data.answer,
          sources: data.sources,
          latency: resolvedLatency,
          chunks: chunks,
        },
      ])
    } catch {
      const clientLatencySec = ((performance.now() - startTime) / 1000).toFixed(2)
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'bot',
          text: 'Lo siento, hubo un error al procesar tu pregunta. Verifica que el servidor backend esté corriendo.',
          latency: clientLatencySec,
          chunks: [],
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    askQuestion(input)
  }

  const handleSuggestion = (text) => {
    askQuestion(text)
  }

  const handleOpenChunks = (chunks) => {
    if (chunks && chunks.length > 0) {
      setCurrentChunks(chunks)
    }
    setIsChunksOpen(true)
  }

  return (
    <div className="app">
      <Header
        onToggleChunks={() => setIsChunksOpen((prev) => !prev)}
        hasChunks={currentChunks.length > 0}
      />

      <main className="messages">
        {/* Welcome card shown when no messages yet */}
        {messages.length === 0 && !isLoading && (
          <WelcomeCard onSuggestionClick={handleSuggestion} />
        )}

        {/* Message list */}
        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            role={msg.role}
            text={msg.text}
            sources={msg.sources}
            latency={msg.latency}
            chunks={msg.chunks}
            onOpenChunks={handleOpenChunks}
          />
        ))}

        {/* Thinking animation */}
        {isLoading && <ThinkingIndicator isFirstMessage={messages.length <= 1} />}

        <div ref={messagesEndRef} />
      </main>

      {/* Persistent horizontal suggestions bar when conversation is active */}
      {messages.length > 0 && (
        <SuggestionsBar
          suggestions={SUGGESTED_QUESTIONS}
          onSelect={handleSuggestion}
          disabled={isLoading}
        />
      )}

      <ChatInput
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onSubmit={handleSubmit}
        isLoading={isLoading}
        maxChars={MAX_CHARS}
        minChars={MIN_CHARS}
      />

      {/* Slide-out / Bottom-sheet Chunks Inspection Panel */}
      <ChunksPanel
        isOpen={isChunksOpen}
        onClose={() => setIsChunksOpen(false)}
        chunks={currentChunks}
        question={currentQuestion}
      />
    </div>
  )
}

export default App
