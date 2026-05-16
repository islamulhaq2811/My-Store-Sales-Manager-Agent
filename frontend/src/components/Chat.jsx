import { useState, useRef, useEffect } from 'react'
import { chatWithAgent } from '../services/api'
import './Chat.css'

const quickActions = [
  { label: "Today's Orders", query: 'How many orders today?', icon: 'O' },
  { label: 'Daily Revenue', query: 'What is today\'s revenue?', icon: '$' },
  { label: 'Top Products', query: 'What are the top selling products?', icon: 'T' },
  { label: 'Sales Report', query: 'Show me the sales report', icon: 'R' },
  { label: 'Refund Status', query: 'I want a refund for order 1', icon: 'F' },
  { label: 'Delivery Status', query: 'Track my delivery for order 1', icon: 'D' },
]

function Chat() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hey there! I'm your AI Sales Assistant. I can help you with orders, revenue, refunds, warranties, and more. How can I assist you today?" }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const sendMessage = async (query) => {
    const message = query || input
    if (!message.trim()) return

    setMessages(prev => [...prev, { role: 'user', content: message }])
    setInput('')
    setLoading(true)

    try {
      const res = await chatWithAgent(message)
      const data = res.data
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        agent: data.agent,
        timestamp: data.timestamp
      }])
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        isError: true
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-header-left">
          <div className="chat-avatar">AI</div>
          <div>
            <h3>AI Assistant</h3>
            <span className="chat-status">Online</span>
          </div>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role} ${msg.isError ? 'error' : ''}`}>
            <div className={`message-avatar ${msg.role}`}>
              {msg.role === 'user' ? (
                <span className="user-avatar-text">You</span>
              ) : (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2a4 4 0 014 4v2a4 4 0 01-8 0V6a4 4 0 014-4z" />
                  <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                </svg>
              )}
            </div>
            <div className="message-content">
            <div className="message-header">
                <span className="message-role">{msg.role === 'user' ? 'You' : 'AI Assistant'}</span>
                {msg.agent && <span className="message-agent">{msg.agent}</span>}
              </div>
              <div className="message-text">{msg.content}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-avatar assistant">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a4 4 0 014 4v2a4 4 0 01-8 0V6a4 4 0 014-4z" />
                <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
              </svg>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="quick-actions">
        {quickActions.map((action, idx) => (
          <button
            key={idx}
            className="quick-action-btn"
            onClick={() => sendMessage(action.query)}
            disabled={loading}
          >
            {action.label}
          </button>
        ))}
      </div>

      <div className="chat-input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
          disabled={loading}
          className="chat-input"
        />
        <button
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
          className="send-btn"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
    </div>
  )
}

export default Chat
