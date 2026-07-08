'use client'

import React, { createContext, useContext, useMemo, useState } from 'react'
import type { Conversation, Message } from '@/types'

interface ConversationsContextValue {
  conversations: Conversation[]
  activeId: string | null
  active: Conversation | null
  createConversation: () => string
  addMessage: (conversationId: string, message: Omit<Message, 'id' | 'timestamp'>) => Message
  updateMessage: (conversationId: string, messageId: string, updates: Partial<Message>) => void
  selectConversation: (conversationId: string) => void
  deleteConversation: (conversationId: string) => void
  renameConversation: (conversationId: string, title: string) => void
  loadHistoryIntoConversation: (conversationId: string, history: Message[]) => void
}

const ConversationsContext = createContext<ConversationsContextValue | undefined>(undefined)

function buildConversation(id: string): Conversation {
  const now = new Date().toISOString()
  return {
    id,
    title: 'New chat',
    messages: [],
    createdAt: now,
    updatedAt: now,
  }
}

export function ConversationsProvider({ children }: { children: React.ReactNode }) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)

  const active = useMemo(() => {
    if (!activeId) return null
    return conversations.find((conversation) => conversation.id === activeId) ?? null
  }, [activeId, conversations])

  const createConversation = () => {
    const id = crypto.randomUUID()
    const conversation = buildConversation(id)
    setConversations((current) => [conversation, ...current])
    setActiveId(id)
    return id
  }

  const addMessage = (conversationId: string, message: Omit<Message, 'id' | 'timestamp'>) => {
    const now = new Date().toISOString()
    const newMessage: Message = {
      id: crypto.randomUUID(),
      timestamp: now,
      ...message,
    }

    setConversations((current) =>
      current.map((conversation) => {
        if (conversation.id !== conversationId) return conversation

        const nextMessages = [...conversation.messages, newMessage]
        const title = conversation.title === 'New chat' && newMessage.role === 'user'
          ? newMessage.content.slice(0, 40) || 'New chat'
          : conversation.title

        return {
          ...conversation,
          title,
          messages: nextMessages,
          updatedAt: now,
        }
      })
    )

    return newMessage
  }

  const updateMessage = (conversationId: string, messageId: string, updates: Partial<Message>) => {
    setConversations((current) =>
      current.map((conversation) => {
        if (conversation.id !== conversationId) return conversation

        return {
          ...conversation,
          messages: conversation.messages.map((message) =>
            message.id === messageId ? { ...message, ...updates } : message
          ),
          updatedAt: new Date().toISOString(),
        }
      })
    )
  }

  const selectConversation = (conversationId: string) => {
    setActiveId(conversationId)
  }

  const deleteConversation = (conversationId: string) => {
    setConversations((current) => current.filter((conversation) => conversation.id !== conversationId))
    setActiveId((current) => (current === conversationId ? null : current))
  }

  const renameConversation = (conversationId: string, title: string) => {
    setConversations((current) =>
      current.map((conversation) =>
        conversation.id === conversationId ? { ...conversation, title, updatedAt: new Date().toISOString() } : conversation
      )
    )
  }

  const loadHistoryIntoConversation = (conversationId: string, history: Message[]) => {
    setConversations((current) =>
      current.map((conversation) => {
        if (conversation.id !== conversationId) return conversation

        return {
          ...conversation,
          messages: history,
          updatedAt: new Date().toISOString(),
        }
      })
    )
  }

  const value = useMemo<ConversationsContextValue>(
    () => ({
      conversations,
      activeId,
      active,
      createConversation,
      addMessage,
      updateMessage,
      selectConversation,
      deleteConversation,
      renameConversation,
      loadHistoryIntoConversation,
    }),
    [active, activeId, conversations]
  )

  return <ConversationsContext.Provider value={value}>{children}</ConversationsContext.Provider>
}

export function useConversations() {
  const context = useContext(ConversationsContext)
  if (!context) {
    throw new Error('useConversations must be used within a ConversationsProvider')
  }
  return context
}
