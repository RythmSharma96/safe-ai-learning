export default function ConversationSidebar({
  conversations,
  activeId,
  onSelect,
  onCreate,
}) {
  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-full">
      <div className="p-3">
        <button
          onClick={onCreate}
          className="w-full px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
        >
          + New Conversation
        </button>
      </div>
      <div className="flex-1 overflow-y-auto">
        {conversations.map((conv) => (
          <button
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            className={`w-full text-left px-4 py-3 border-b border-gray-100 hover:bg-gray-50 ${
              activeId === conv.id ? 'bg-blue-50 border-l-2 border-l-blue-600' : ''
            }`}
          >
            <div className="text-sm font-medium text-gray-800 truncate">
              {conv.title || 'Untitled'}
            </div>
            <div className="text-xs text-gray-400 mt-0.5">
              {conv.message_count} messages
              {conv.is_flagged && (
                <span className="ml-1 text-yellow-600">&#9888;</span>
              )}
            </div>
          </button>
        ))}
        {conversations.length === 0 && (
          <div className="p-4 text-sm text-gray-400 text-center">
            No conversations yet
          </div>
        )}
      </div>
    </div>
  )
}
