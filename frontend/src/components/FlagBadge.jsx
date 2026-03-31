const CATEGORY_COLORS = {
  self_harm: 'bg-red-100 text-red-800',
  sexual_content: 'bg-red-100 text-red-800',
  pii_request: 'bg-orange-100 text-orange-800',
  manipulation: 'bg-purple-100 text-purple-800',
  harm_content: 'bg-red-100 text-red-800',
  moderation_unavailable: 'bg-gray-100 text-gray-800',
}

const CATEGORY_LABELS = {
  self_harm: 'Self-harm',
  sexual_content: 'Sexual Content',
  pii_request: 'PII Request',
  manipulation: 'Manipulation',
  harm_content: 'Harmful Content',
  moderation_unavailable: 'Review Needed',
}

export default function FlagBadge({ category }) {
  const color = CATEGORY_COLORS[category] || 'bg-gray-100 text-gray-800'
  const label = CATEGORY_LABELS[category] || category

  return (
    <span className={`inline-block text-xs px-2 py-0.5 rounded ${color}`}>
      {label}
    </span>
  )
}
