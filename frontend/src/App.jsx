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

  // Pre-warm backend on page load to eliminate/reduce cold start latency
  useEffect(() => {
    fetch(`${API_URL}/health`).catch(() => {
      // Ignore network errors on silent pre-warm
    })
  }, [])

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
    const botMsgId = crypto.randomUUID()
    let botMsgCreated = false

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: trimmed, stream: true }),
      })

      if (!res.ok) throw new Error('Server error')

      const contentType = res.headers.get('content-type') || ''
      if (contentType.includes('text/event-stream')) {
        let accumulatedText = ''
        let firstTokenTime = null
        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() // keep uncompleted tail

          for (const line of lines) {
            const trimmedLine = line.trim()
            if (!trimmedLine || !trimmedLine.startsWith('data:')) continue
            const jsonStr = trimmedLine.slice(5).trim()
            if (!jsonStr) continue

            try {
              const payload = JSON.parse(jsonStr)

              if (payload.type === 'retrieval') {
                const chunks = payload.chunks || []
                setCurrentChunks(chunks)
                setIsLoading(false)
                botMsgCreated = true
                setMessages((prev) => [
                  ...prev,
                  {
                    id: botMsgId,
                    role: 'bot',
                    text: '',
                    chunks: chunks,
                    sources: payload.sources || [],
                    retrievalSec: payload.retrieval_sec != null ? Number(payload.retrieval_sec).toFixed(2) : null,
                    isStreaming: true,
                  },
                ])
              } else if (payload.type === 'delta') {
                if (firstTokenTime === null && payload.delta) {
                  firstTokenTime = performance.now()
                }
                accumulatedText += payload.delta
                if (!botMsgCreated) {
                  botMsgCreated = true
                  setIsLoading(false)
                  setMessages((prev) => [
                    ...prev,
                    {
                      id: botMsgId,
                      role: 'bot',
                      text: accumulatedText,
                      chunks: [],
                      isStreaming: true,
                    },
                  ])
                } else {
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === botMsgId ? { ...msg, text: accumulatedText } : msg
                    )
                  )
                }
              } else if (payload.type === 'done') {
                const clientLatencySec = ((performance.now() - startTime) / 1000).toFixed(2)
                const clientTtftSec = firstTokenTime ? ((firstTokenTime - startTime) / 1000).toFixed(2) : null
                const resolvedTtft = payload.ttft_sec != null ? Number(payload.ttft_sec).toFixed(2) : clientTtftSec

                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === botMsgId
                      ? {
                          ...msg,
                          text: payload.answer || accumulatedText,
                          latency: clientLatencySec,
                          retrievalSec: payload.retrieval_sec != null ? Number(payload.retrieval_sec).toFixed(2) : msg.retrievalSec,
                          llmSec: payload.llm_sec != null ? Number(payload.llm_sec).toFixed(2) : null,
                          ttftSec: resolvedTtft,
                          inputTokens: payload.input_tokens,
                          outputTokens: payload.output_tokens,
                          totalCost: payload.total_cost,
                          model: payload.model,
                          isStreaming: false,
                        }
                      : msg
                  )
                )
              } else if (payload.type === 'error') {
                throw new Error(payload.error || 'Streaming error')
              }
            } catch (err) {
              if (err.message && err.message.includes('Streaming error')) {
                throw err
              }
              console.error('Error parsing SSE line:', err)
            }
          }
        }
      } else {
        const data = await res.json()
        const clientLatencySec = ((performance.now() - startTime) / 1000).toFixed(2)
        const resolvedLatency = data.latency != null ? Number(data.latency).toFixed(2) : clientLatencySec
        const chunks = data.chunks || []

        setCurrentChunks(chunks)
        setMessages((prev) => [
          ...prev,
          {
            id: botMsgId,
            role: 'bot',
            text: data.answer,
            sources: data.sources,
            latency: resolvedLatency,
            chunks: chunks,
            retrievalSec: data.retrieval_sec != null ? Number(data.retrieval_sec).toFixed(2) : (data.retrieval_ms != null ? (data.retrieval_ms / 1000).toFixed(2) : null),
            llmSec: data.llm_sec != null ? Number(data.llm_sec).toFixed(2) : (data.llm_ms != null ? (data.llm_ms / 1000).toFixed(2) : null),
            inputTokens: data.input_tokens,
            outputTokens: data.output_tokens,
            totalCost: data.total_cost,
            model: data.model,
            isStreaming: false,
          },
        ])
      }
    } catch {
      const clientLatencySec = ((performance.now() - startTime) / 1000).toFixed(2)
      setMessages((prev) => {
        const exists = prev.find((m) => m.id === botMsgId)
        if (exists) {
          return prev.map((m) =>
            m.id === botMsgId
              ? {
                  ...m,
                  text: m.text ? `${m.text}\n\n*(Error al completar la respuesta)*` : 'Lo siento, hubo un error al procesar tu pregunta. Verifica que el servidor backend esté corriendo.',
                  isStreaming: false,
                }
              : m
          )
        }
        return [
          ...prev,
          {
            id: botMsgId,
            role: 'bot',
            text: 'Lo siento, hubo un error al procesar tu pregunta. Verifica que el servidor backend esté corriendo.',
            latency: clientLatencySec,
            chunks: [],
            isStreaming: false,
          },
        ]
      })
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
            retrievalSec={msg.retrievalSec}
            llmSec={msg.llmSec}
            inputTokens={msg.inputTokens}
            outputTokens={msg.outputTokens}
            totalCost={msg.totalCost}
            model={msg.model}
            isStreaming={msg.isStreaming}
            ttftSec={msg.ttftSec}
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
