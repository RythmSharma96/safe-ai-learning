import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import FlagBadge from '../components/FlagBadge'
import { listFlaggedConversations } from '../api'

export default function FlaggedListPage() {
  const [conversations, setConversations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listFlaggedConversations()
      .then((res) => setConversations(res.data.results || []))
      .catch((err) => console.error('Failed to load flagged conversations', err))
      .finally(() => setLoading(false))
  }, [])

  return (
    <Layout>
      <div className="max-w-5xl mx-auto p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-1">Flagged Conversations</h1>
        <p className="text-sm text-gray-500 mb-6">
          Review conversations that were flagged by the safety system.
        </p>

        {loading ? (
          <div className="text-gray-400">Loading...</div>
        ) : conversations.length === 0 ? (
          <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-400">
            No flagged conversations yet.
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">
                    Learner
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">
                    Title
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">
                    Flags
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">
                    Date
                  </th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {conversations.map((conv) => (
                  <tr key={conv.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-800">{conv.learner_email}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{conv.title || 'Untitled'}</td>
                    <td className="px-4 py-3">
                      <span className="text-sm font-medium text-red-600">{conv.flag_count}</span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-400">
                      {new Date(conv.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        to={`/flagged/${conv.id}`}
                        className="text-sm text-blue-600 hover:underline"
                      >
                        Review
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  )
}
