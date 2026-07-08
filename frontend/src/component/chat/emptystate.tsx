'use client'

interface EmptyStateProps {
  onSuggest: (question: string) => void
}

const suggestions = [
  'Summarize the latest policies',
  'What are the key takeaways from this document?',
  'Show me the most relevant citations',
]

export default function EmptyState({ onSuggest }: EmptyStateProps) {
  return (
    <div className="flex h-full items-center justify-center px-6 py-10">
      <div className="w-full max-w-2xl rounded-2xl border border-border bg-white p-8 shadow-sm">
        <div className="space-y-3">
          <p className="text-sm font-semibold text-ink">Start a new conversation</p>
          <p className="text-sm text-muted">
            Ask anything about your documents and I’ll help you find the answer.
          </p>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => onSuggest(suggestion)}
              className="rounded-xl border border-border bg-surface px-3 py-3 text-left text-sm text-ink transition hover:border-teal hover:bg-teal/10"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
