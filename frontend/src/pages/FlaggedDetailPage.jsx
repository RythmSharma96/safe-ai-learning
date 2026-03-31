import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from '../components/Layout'
import FlagBadge from '../components/FlagBadge'
import { getFlaggedConversation } from '../api'

export default function FlaggedDetailPage() {
  const { id } = useParams()
  const [conversation, setConversation] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getFlaggedConversation(id)
      .then((res) => setConversation(res.data))
      .catch((err) => console.error('Failed to load conversation', err))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto p-6 text-gray-400">Loading...</div>
      </Layout>
    )
  }

  if (!conversation) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto p-6 text-gray-400">Conversation not found.</div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto p-6">
        <Link to="/flagged" className="text-sm text-blue-600 hover:underline mb-4 inline-block">
          &larr; Back to flagged list
        </Link>

        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
          <h1 className="text-xl font-bold text-gray-800">
            {conversation.title || 'Untitled Conversation'}
          </h1>
          <div className="text-sm text-gray-500 mt-1">
            Learner: {conversation.learner_email} &middot;{' '}
            {new Date(conversation.created_at).toLocaleString()}
          </div>
        </div>

        <div className="space-y-4">
          {conversation.messages?.map((msg) => {
            const isFlagged = msg.moderation?.is_flagged
            return (
              <div
                key={msg.id}
                className={`bg-white rounded-lg border p-4 ${
                  isFlagged ? 'border-red-300 bg-red-50' : 'border-gray-200'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded ${
                      msg.role === 'user'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-green-100 text-green-700'
                    }`}
                  >
                    {msg.role === 'user' ? 'Learner' : 'Assistant'}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(msg.created_at).toLocaleTimeString()}
                  </span>
                  {isFlagged && (
                    <span className="text-xs font-medium text-red-600">FLAGGED</span>
                  )}
                </div>

                <p className="text-sm text-gray-800 whitespace-pre-wrap mb-2">{msg.content}</p>

                {isFlagged && msg.moderation && (
                  <div className="mt-3 p-3 bg-white rounded border border-red-200">
                    <div className="text-xs font-medium text-gray-500 mb-2">
                      Moderation Details
                    </div>
                    <div className="flex flex-wrap gap-1 mb-2">
                      {msg.moderation.flag_categories?.map((cat) => (
                        <FlagBadge key={cat} category={cat} />
                      ))}
                    </div>
                    {msg.moderation.flag_reasons?.map((reason, i) => (
                      <div key={i} className="text-xs text-gray-600 mb-1">
                        &bull; {reason}
                      </div>
                    ))}
                    {msg.moderation.checker_results && (
                      <details className="mt-2">
                        <summary className="text-xs text-gray-400 cursor-pointer">
                          Raw checker output
                        </summary>
                        <pre className="text-xs text-gray-500 mt-1 overflow-x-auto">
                          {JSON.stringify(msg.moderation.checker_results, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </Layout>
  )
}
