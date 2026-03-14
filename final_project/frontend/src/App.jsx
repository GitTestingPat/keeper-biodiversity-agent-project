// frontend/src/App.jsx
import { useState } from 'react'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage = input.trim()
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          session_id: 'default'
        })
      })

      const data = await response.json()
      
      if (data.success) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.response 
        }])
      } else {
        setMessages(prev => [...prev, { 
          role: 'system', 
          content: `Error: ${data.error}` 
        }])
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: `Error de conexión: ${error.message}` 
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex flex-col">
      {/* Header */}
      <header className="p-6 text-center">
        <h1 className="text-4xl font-bold text-emerald-400 mb-2">
          🌿 Biodiversity Sentinel
        </h1>
        <p className="text-gray-300">
          Monitoreo en tiempo real con IA para conservación
        </p>
      </header>

      {/* Chat Container */}
      <div className="flex-1 max-w-4xl mx-auto w-full px-4 pb-4">
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl border border-slate-700 h-[600px] overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-400 mt-32">
              <p className="text-xl mb-2">👋 ¡Bienvenido!</p>
              <p>Pregúntame sobre:</p>
              <ul className="mt-4 space-y-2 text-sm">
                <li>🛰️ Análisis de deforestación</li>
                <li>🌊 Detección de pesca ilegal</li>
                <li>🦁 Monitoreo de vida silvestre</li>
                <li>📊 Reportes de conservación</li>
              </ul>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                  msg.role === 'user'
                    ? 'bg-emerald-600 text-white'
                    : msg.role === 'system'
                    ? 'bg-red-600/20 border border-red-500 text-red-200'
                    : 'bg-slate-700 text-gray-100'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-700 rounded-2xl px-4 py-2">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={sendMessage} className="mt-4 flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe tu consulta sobre biodiversidad..."
            className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-xl font-semibold transition-colors"
          >
            {loading ? '⏳' : 'Enviar'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default App