'use client'
import { useState, useRef, useEffect } from 'react'
import { Send, Square } from 'lucide-react'
import { clsx } from 'clsx'

interface ChatInputProps {
    onSend: (message: string) => void
    disabled?: boolean
    isLoading?: boolean
    onStop?: () => void
}

export default function ChatInput({ onSend, disabled, isLoading, onStop }: ChatInputProps) {
    const [value, setValue] = useState('')
    const textareaRef = useRef<HTMLTextAreaElement>(null)

    // Auto-resize textarea
    useEffect(() => {
        const ta = textareaRef.current
        if (!ta) return
        ta.style.height = 'auto'
        ta.style.height = Math.min(ta.scrollHeight, 200) + 'px'
    }, [value])

    const handleSend = () => {
        const trimmed = value.trim()
        if (!trimmed || disabled || isLoading) return
        onSend(trimmed)
        setValue('')
        if (textareaRef.current) textareaRef.current.style.height = 'auto'
    }

    const handleKey = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <div className="px-4 pb-4 pt-2">
            <div className={clsx(
                'flex items-end gap-3 bg-card border rounded-2xl px-4 py-3',
                'transition-colors duration-150',
                disabled ? 'border-border opacity-60' : 'border-border hover:border-muted/50 focus-within:border-teal focus-within:shadow-[0_0_0_3px_rgba(14,165,160,0.1)]'
            )}>
                <textarea
                    ref={textareaRef}
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    onKeyDown={handleKey}
                    disabled={disabled}
                    placeholder="Ask a medical question… (Shift+Enter for new line)"
                    rows={1}
                    className={clsx(
                        'flex-1 resize-none bg-transparent text-sm text-ink placeholder-muted',
                        'outline-none leading-relaxed min-h-[24px] max-h-[200px]',
                        'scrollbar-thin'
                    )}
                />

                {isLoading ? (
                    <button
                        onClick={onStop}
                        className="flex-shrink-0 w-8 h-8 rounded-lg bg-red-500/20 hover:bg-red-500/30
                       text-red-400 flex items-center justify-center transition-colors"
                        title="Stop generating"
                    >
                        <Square size={14} fill="currentColor" />
                    </button>
                ) : (
                    <button
                        onClick={handleSend}
                        disabled={!value.trim() || disabled}
                        className={clsx(
                            'flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center transition-all',
                            value.trim() && !disabled
                                ? 'bg-teal hover:bg-teal-hover text-white shadow-sm'
                                : 'bg-border text-muted cursor-not-allowed'
                        )}
                        title="Send message (Enter)"
                    >
                        <Send size={14} />
                    </button>
                )}
            </div>
            <p className="text-[10px] text-muted/50 text-center mt-2">
                MediQuery AI may produce errors. Always verify with a qualified healthcare professional.
            </p>
        </div>
    )
}