'use client'

import { useCallback, useEffect, useRef } from 'react'
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
  const abortRef = useRef(false)
  const isGenerating = active?.messages.some((message) => message.isStreaming) ?? false

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.replace('/login')
  }, [isAuthenticated, isLoading, router])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [active?.messages.length, isGenerating])

  useEffect(() => {
    if (!activeId) return
    const conversation = conversations.find((item) => item.id === activeId)
    if (!conversation || conversation.messages.length > 0) return

    chatApi.history(activeId)
      .then(({ data }) => {
        if (data.length > 0) {
          const historyMessages: Message[] = data.flatMap((item) => [
            {
              id: `user-${item.id}`,
              role: 'user' as const,
              content: item.message,
              timestamp: item.timestamp,
            },
            {
              id: `assistant-${item.id}`,
              role: 'assistant' as const,
              content: item.response,
              sources: item.sources,
              timestamp: item.timestamp,
            },
          ])

          loadHistoryIntoConversation(activeId, historyMessages)
        }
      })
      .catch(() => undefined)
  }, [activeId, conversations, loadHistoryIntoConversation])

  const handleNewChat = useCallback(() => {
    createConversation()
  }, [createConversation])

  const handleSend = useCallback(async (text: string) => {
    let conversationId = activeId

    if (!conversationId) {
      conversationId = createConversation()
    }

    addMessage(conversationId, { role: 'user', content: text })

    const placeholder: Omit<Message, 'id' | 'timestamp'> = {
      role: 'assistant',
      content: '',
      isStreaming: true,
    }
    const assistantMessage = addMessage(conversationId, placeholder)

    abortRef.current = false

    try {
      const { data } = await chatApi.send(text, conversationId)

      if (abortRef.current) return

      let displayed = ''
      const words = data.answer.split(' ')
      for (let index = 0; index < words.length; index += 1) {
        if (abortRef.current) break
        displayed += (index > 0 ? ' ' : '') + words[index]
        updateMessage(conversationId, assistantMessage.id, {
          content: displayed,
          isStreaming: index < words.length - 1,
          sources: index === words.length - 1 ? data.sources : undefined,
        })
        await new Promise((resolve) => setTimeout(resolve, 18))
      }

      updateMessage(conversationId, assistantMessage.id, {
        content: data.answer,
        sources: data.sources,
        isStreaming: false,
      })
    } catch (error) {
      updateMessage(conversationId, assistantMessage.id, {
        content: `⚠️ ${getErrorMessage(error)}`,
        isStreaming: false,
        sources: [],
      })
    }
  }, [activeId, addMessage, createConversation, updateMessage])

  const handleStop = () => {
    abortRef.current = true
  }

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
      <Sidebar onNewChat={handleNewChat} />

      <div className="flex flex-col flex-1 min-w-0">
        <div className="flex items-center justify-between px-6 py-3 border-b border-border flex-shrink-0">
          <div>
            <h1 className="text-sm font-semibold text-ink">
              {active?.title || 'MediQuery AI'}
            </h1>
            {active && (
              <p className="text-xs text-muted">
                {active.messages.filter((message) => message.role === 'user').length} question
                {active.messages.filter((message) => message.role === 'user').length !== 1 ? 's' : ''}
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

        <div className="flex-1 overflow-y-auto">
          {(!active || active.messages.length === 0) ? (
            <EmptyState onSuggest={handleSuggest} />
          ) : (
            <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
              {active.messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

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
