'use client'
import { useState } from 'react'
import { ChevronDown, ChevronUp, BookOpen, Stethoscope, User } from 'lucide-react'
import { clsx } from 'clsx'
import type { Message } from '@/types'

export default function MessageBubble({ message }: { message: Message }) {
    const [showSources, setShowSources] = useState(false)
    const isUser = message.role === 'user'

    return (
        <div className={clsx('flex gap-3 animate-fade-in', isUser && 'flex-row-reverse')}>
            {/* Avatar */}
            <div className={clsx(
                'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5',
                isUser ? 'bg-teal/20' : 'bg-card border border-border'
            )}>
                {isUser
                    ? <User size={16} className="text-teal" />
                    : <Stethoscope size={16} className="text-teal" />
                }
            </div>

            {/* Bubble */}
            <div className={clsx('max-w-[80%] space-y-1', isUser && 'items-end flex flex-col')}>
                <div className={clsx(
                    'rounded-2xl px-4 py-3 text-sm leading-relaxed',
                    isUser
                        ? 'bg-teal text-white rounded-tr-sm'
                        : 'bg-card border border-border text-ink rounded-tl-sm',
                    message.isStreaming && 'typing-cursor'
                )}>
                    {isUser ? (
                        <p className="whitespace-pre-wrap">{message.content}</p>
                    ) : (
                        <div
                            className="prose-medical"
                            dangerouslySetInnerHTML={{ __html: formatResponse(message.content) }}
                        />
                    )}
                </div>

                {/* Sources */}
                {!isUser && message.sources && message.sources.length > 0 && !message.isStreaming && (
                    <div className="w-full">
                        <button
                            onClick={() => setShowSources(!showSources)}
                            className="flex items-center gap-1.5 text-xs text-muted hover:text-teal transition-colors py-1"
                        >
                            <BookOpen size={12} />
                            {message.sources.length} source{message.sources.length > 1 ? 's' : ''}
                            {showSources ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                        </button>
                        {showSources && (
                            <div className="mt-1 space-y-1 animate-fade-in">
                                {message.sources.map((src, i) => (
                                    <div key={i} className="flex items-start gap-2 text-xs bg-card border border-border rounded-lg px-3 py-2">
                                        <BookOpen size={11} className="text-teal flex-shrink-0 mt-0.5" />
                                        <span className="text-muted">{src}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Timestamp */}
                <p className="text-[10px] text-muted/60 px-1">
                    {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
            </div>
        </div>
    )
}

function formatResponse(text: string): string {
    // Minimal markdown → HTML for AI responses
    return text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/^### (.+)$/gm, '<h3 class="text-sm font-semibold mt-3 mb-1">$1</h3>')
        .replace(/^## (.+)$/gm, '<h2 class="text-base font-semibold mt-3 mb-1">$1</h2>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/^(?!<)(.+)$/gm, (m) => m.trim() ? m : '')
        .replace(/\n/g, '<br/>')
}