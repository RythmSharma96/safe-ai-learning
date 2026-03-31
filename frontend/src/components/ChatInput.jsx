import { useState } from 'react'

export default function ChatInput({ onSend, disabled }) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!message.trim() || disabled) return
    onSend(message.trim())
    setMessage('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-4 bg-white border-t border-gray-200">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your question..."
        disabled={disabled}
        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
      />
      <button
        type="submit"
        disabled={disabled || !message.trim()}
        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {disabled ? 'Thinking...' : 'Send'}
      </button>
    </form>
  )
}
