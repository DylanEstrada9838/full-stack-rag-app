import { useState, useRef, useEffect } from 'react'
import Header from './components/Header'
import ChatMessage from './components/ChatMessage'
import ChatInput from './components/ChatInput'
import ThinkingIndicator from './components/ThinkingIndicator'
import WelcomeCard from './components/WelcomeCard'
import './App.css'

/**
 * App.jsx — Root component that orchestrates the chat experience.
 *
 * - Manages the message list and input state.
 * - Delegates rendering to Header, WelcomeCard, ChatMessage, ChatInput, ThinkingIndicator.
 * - Sends questions to the FastAPI backend (POST /ask).
 */

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  // Auto-scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Send a question to the API
  const askQuestion = async (question) => {
    if (!question.trim() || isLoading) return

    setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: 'user', text: question }])
    setInput('')
    setIsLoading(true)

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })

      if (!res.ok) throw new Error('Server error')
      const data = await res.json()

      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: 'bot', text: data.answer, sources: data.sources },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'bot',
          text: 'Lo siento, hubo un error al procesar tu pregunta. Verifica que el servidor backend esté corriendo.',
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

  return (
    <div className="app">
      <Header />

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
          />
        ))}

        {/* Thinking animation */}
        {isLoading && <ThinkingIndicator />}

        <div ref={messagesEndRef} />
      </main>

      <ChatInput
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onSubmit={handleSubmit}
        isLoading={isLoading}
      />
    </div>
  )
}

export default App
