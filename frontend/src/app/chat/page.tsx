'use client'
import { useEffect, useRef, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/authcontext'
import { useConversations } from '@/context/conversationcontext'
import { chatApi, getErrorMessage } from '@/lib/api'
import Sidebar from '@/component/chat/sidebar'
import MessageBubble from '@/component/chat/messagebubble'
import ChatInput from '@/component/chat/chatinput'
import EmptyState from '@/component/chat/emptystate'
import type { Message } from '@/types'

export default function ChatPage() {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const {
    conversations,
    active,
    activeId,
    createConversation,
    addMessage,
    updateMessage,
    loadHistoryIntoConversation,
  } = useConversations()

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<boolean>(false)
  const isGenerating = active?.messages.some((m) => m.isStreaming) ?? false

  // ── Auth guard ────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace('/login')
  }, [isAuthenticated, isLoading, router])

  // ── Scroll to bottom on new messages ─────────────────────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [active?.messages.length, isGenerating])

  // ── Load chat history when switching conversations ────────────────────────
  useEffect(() => {
    if (!activeId) return
    const conv = conversations.find((c) => c.id === activeId)
    if (!conv || conv.messages.length > 0) return   // already loaded or new

    chatApi.history(activeId)
      .then(({ data }) => {
        if (data.length > 0) loadHistoryIntoConversation(activeId, data)
      })
      .catch(() => { })
  }, [activeId])  // eslint-disable-line react-hooks/exhaustive-deps

  // ── New conversation ───────────────────────────────────────────────────────
  const handleNewChat = useCallback(() => {
    createConversation()
  }, [createConversation])

  // ── Send message ──────────────────────────────────────────────────────────
  const handleSend = useCallback(async (text: string) => {
    let convId = activeId

    // Create a new conversation if none is active
    if (!convId) {
      convId = createConversation()
    }

    // Add user message immediately
    addMessage(convId, { role: 'user', content: text })

    // Add a streaming placeholder for the assistant
    const placeholder: Omit<Message, 'id' | 'timestamp'> = {
      role: 'assistant',
      content: '',
      isStreaming: true,
    }
    const assistantMsg = addMessage(convId, placeholder)

    abortRef.current = false

    try {
      const { data } = await chatApi.send(text, convId)

      if (abortRef.current) return

      // Simulate streaming by typing the response character by character
      let displayed = ''
      const words = data.answer.split(' ')
      for (let i = 0; i < words.length; i++) {
        if (abortRef.current) break
        displayed += (i > 0 ? ' ' : '') + words[i]
        updateMessage(convId, assistantMsg.id, {
          content: displayed,
          isStreaming: i < words.length - 1,
          sources: i === words.length - 1 ? data.sources : undefined,
        })
        // Small delay between words for streaming effect
        await new Promise((r) => setTimeout(r, 18))
      }

      // Final update — streaming done
      updateMessage(convId, assistantMsg.id, {
        content: data.answer,
        sources: data.sources,
        isStreaming: false,
      })
    } catch (err) {
      updateMessage(convId, assistantMsg.id, {
        content: `⚠️ ${getErrorMessage(err)}`,
        isStreaming: false,
        sources: [],
      })
    }
  }, [activeId, createConversation, addMessage, updateMessage])

  const handleStop = () => { abortRef.current = true }

  const handleSuggest = (question: string) => handleSend(question)

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center bg-surface">
        <div className="w-8 h-8 border-2 border-teal border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="flex h-full bg-surface overflow-hidden">
      {/* Sidebar */}
      <Sidebar onNewChat={handleNewChat} />

      {/* Main area */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Top bar */}
        <div className="flex items-center justify-between px-6 py-3 border-b border-border flex-shrink-0">
          <div>
            <h1 className="text-sm font-semibold text-ink">
              {active?.title || 'MediQuery AI'}
            </h1>
            {active && (
              <p className="text-xs text-muted">
                {active.messages.filter((m) => m.role === 'user').length} question
                {active.messages.filter((m) => m.role === 'user').length !== 1 ? 's' : ''}
              </p>
            )}
          </div>
          {isGenerating && (
            <div className="flex items-center gap-2 text-xs text-teal animate-pulse">
              <div className="w-1.5 h-1.5 rounded-full bg-teal animate-bounce" />
              <div className="w-1.5 h-1.5 rounded-full bg-teal animate-bounce [animation-delay:0.15s]" />
              <div className="w-1.5 h-1.5 rounded-full bg-teal animate-bounce [animation-delay:0.3s]" />
              <span>Generating…</span>
            </div>
          )}
        </div>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto">
          {(!active || active.messages.length === 0) ? (
            <EmptyState onSuggest={handleSuggest} />
          ) : (
            <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
              {active.messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="flex-shrink-0 max-w-3xl mx-auto w-full">
          <ChatInput
            onSend={handleSend}
            onStop={handleStop}
            isLoading={isGenerating}
            disabled={false}
          />
        </div>
      </div>
    </div>
  )
}