import { useState } from 'react'
import { chatWithAgent } from '../services/api'
import './Chat.css'

function Chat() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m your AI Sales Assistant. I can help you with orders, revenue, refunds, warranties, and more. How can I assist you today?' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const quickActions = [
    { label: '📊 Today\'s Orders', query: 'How many orders today?' },
    { label: '💰 Daily Revenue', query: 'What is today\'s revenue?' },
    { label: '🏆 Top Products', query: 'What are the top selling products?' },
    { label: '📈 Sales Report', query: 'Show me the sales report' },
    { label: '🔄 Refund Status', query: 'I want a refund for order 1' },
    { label: '🚚 Delivery Status', query: 'Track my delivery for order 1' },
  ]

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
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role} ${msg.isError ? 'error' : ''}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <div className="message-header">
                <span className="message-role">{msg.role === 'user' ? 'You' : 'AI Assistant'}</span>
                {msg.agent && <span className="message-agent">{msg.agent} agent</span>}
              </div>
              <div className="message-text">{msg.content}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
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
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
          disabled={loading}
          className="chat-input"
        />
        <button
          onClick={() => sendMessage()}
          disabled={loading || !input.trim()}
          className="send-btn"
        >
          ➤
        </button>
      </div>
    </div>
  )
}

export default Chat
