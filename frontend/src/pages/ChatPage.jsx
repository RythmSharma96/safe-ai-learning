import { useState, useEffect, useRef } from 'react'
import Layout from '../components/Layout'
import ConversationSidebar from '../components/ConversationSidebar'
import ChatMessage from '../components/ChatMessage'
import ChatInput from '../components/ChatInput'
import {
  listConversations,
  createConversation,
  getConversation,
  sendMessage,
} from '../api'

export default function ChatPage() {
  const [conversations, setConversations] = useState([])
  const [activeConvId, setActiveConvId] = useState(null)
  const [messages, setMessages] = useState([])
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef(null)

  // Load conversations list
  useEffect(() => {
    loadConversations()
  }, [])

  // Load messages when active conversation changes
  useEffect(() => {
    if (activeConvId) loadMessages(activeConvId)
  }, [activeConvId])

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadConversations = async () => {
    try {
      const res = await listConversations()
      setConversations(res.data.results || [])
    } catch (err) {
      console.error('Failed to load conversations', err)
    }
  }

  const loadMessages = async (convId) => {
    try {
      const res = await getConversation(convId)
      setMessages(res.data.messages || [])
    } catch (err) {
      console.error('Failed to load messages', err)
    }
  }

  const handleCreateConversation = async () => {
    try {
      const res = await createConversation({ title: '' })
      await loadConversations()
      setActiveConvId(res.data.id)
    } catch (err) {
      console.error('Failed to create conversation', err)
    }
  }

  const handleSendMessage = async (content) => {
    if (!activeConvId) return
    setSending(true)

    // Show user message immediately
    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
      moderation: null,
    }
    setMessages((prev) => [...prev, tempUserMsg])

    try {
      const res = await sendMessage(activeConvId, content)
      // Replace temp message with real one + add assistant response
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== tempUserMsg.id),
        res.data.user_message,
        res.data.assistant_message,
      ])
      loadConversations()
    } catch (err) {
      console.error('Failed to send message', err)
      // Remove temp message on error
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMsg.id))
    } finally {
      setSending(false)
    }
  }

  return (
    <Layout>
      <div className="flex" style={{ height: 'calc(100vh - 57px)' }}>
        <ConversationSidebar
          conversations={conversations}
          activeId={activeConvId}
          onSelect={setActiveConvId}
          onCreate={handleCreateConversation}
        />
        <div className="flex-1 flex flex-col">
          {activeConvId ? (
            <>
              <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
                {messages.length === 0 && (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    <div className="text-center">
                      <p className="text-lg mb-2">Hi there! I'm Jurneego</p>
                      <p className="text-sm">Ask me anything you'd like to learn about!</p>
                    </div>
                  </div>
                )}
                {messages.map((msg) => (
                  <ChatMessage key={msg.id} message={msg} />
                ))}
                <div ref={messagesEndRef} />
              </div>
              <ChatInput onSend={handleSendMessage} disabled={sending} />
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              <div className="text-center">
                <p className="text-lg mb-2">Welcome to Jurneego!</p>
                <p className="text-sm">Select a conversation or create a new one to start learning.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
