export default function ChatMessage({ message }) {
  const isUser = message.role === 'user'
  const isFlagged = message.moderation?.is_flagged

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-white border border-gray-200 text-gray-800'
        } ${isFlagged ? 'ring-2 ring-yellow-400' : ''}`}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        <div className="flex items-center gap-2 mt-1">
          <span className={`text-xs ${isUser ? 'text-blue-200' : 'text-gray-400'}`}>
            {new Date(message.created_at).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
          {isFlagged && (
            <span className="text-xs bg-yellow-100 text-yellow-800 px-1.5 py-0.5 rounded">
              flagged
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
