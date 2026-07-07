'use client'
import { useState } from 'react'
import { Plus, MessageSquare, Trash2, Pencil, Stethoscope, LogOut, ChevronLeft, ChevronRight, Check, X } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { useConversations } from '@/context/ConversationContext'
import { chatApi } from '@/lib/api'
import { clsx } from 'clsx'

export default function Sidebar({ onNewChat }: { onNewChat: () => void }) {
    const { user, logout } = useAuth()
    const { conversations, activeId, selectConversation, deleteConversation, renameConversation } = useConversations()
    const [collapsed, setCollapsed] = useState(false)
    const [renamingId, setRenamingId] = useState<string | null>(null)
    const [renameVal, setRenameVal] = useState('')

    const startRename = (id: string, currentTitle: string) => {
        setRenamingId(id)
        setRenameVal(currentTitle)
    }
    const commitRename = () => {
        if (renamingId && renameVal.trim()) renameConversation(renamingId, renameVal.trim())
        setRenamingId(null)
    }

    const handleDelete = async (e: React.MouseEvent, id: string) => {
        e.stopPropagation()
        await chatApi.clearHistory(id).catch(() => { })
        deleteConversation(id)
    }

    // Group conversations by date
    const today = new Date().toDateString()
    const yesterday = new Date(Date.now() - 86400000).toDateString()
    const groups: { label: string; items: typeof conversations }[] = []
    const todayItems = conversations.filter((c) => new Date(c.updatedAt).toDateString() === today)
    const yesterdayItems = conversations.filter((c) => new Date(c.updatedAt).toDateString() === yesterday)
    const olderItems = conversations.filter(
        (c) => new Date(c.updatedAt).toDateString() !== today && new Date(c.updatedAt).toDateString() !== yesterday
    )
    if (todayItems.length) groups.push({ label: 'Today', items: todayItems })
    if (yesterdayItems.length) groups.push({ label: 'Yesterday', items: yesterdayItems })
    if (olderItems.length) groups.push({ label: 'Older', items: olderItems })

    return (
        <div className={clsx(
            'flex flex-col h-full bg-sidebar border-r border-sidebar-border sidebar-transition flex-shrink-0',
            collapsed ? 'w-14' : 'w-64'
        )}>
            {/* Header */}
            <div className="flex items-center gap-2 p-3 border-b border-sidebar-border">
                {!collapsed && (
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                        <div className="w-7 h-7 rounded-lg bg-teal/20 flex items-center justify-center flex-shrink-0">
                            <Stethoscope size={15} className="text-teal" />
                        </div>
                        <span className="text-sm font-semibold text-ink truncate">MediQuery AI</span>
                    </div>
                )}
                <button
                    onClick={() => setCollapsed(!collapsed)}
                    className="p-1.5 rounded-lg hover:bg-sidebar-hover text-muted hover:text-ink transition-colors ml-auto"
                    title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                >
                    {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
                </button>
            </div>

            {/* New Chat */}
            <div className="p-2">
                <button
                    onClick={onNewChat}
                    className={clsx(
                        'flex items-center gap-2 rounded-lg px-3 py-2 w-full text-sm font-medium',
                        'bg-teal/15 hover:bg-teal/25 text-teal transition-colors duration-150',
                        collapsed && 'justify-center px-0'
                    )}
                    title="New chat"
                >
                    <Plus size={16} />
                    {!collapsed && 'New chat'}
                </button>
            </div>

            {/* Conversation list */}
            <div className="flex-1 overflow-y-auto py-1 px-2 space-y-4">
                {conversations.length === 0 && !collapsed && (
                    <p className="text-xs text-muted text-center pt-8 px-4 leading-relaxed">
                        Ask your first medical question to start a conversation.
                    </p>
                )}
                {groups.map((group) => (
                    <div key={group.label}>
                        {!collapsed && (
                            <p className="text-[10px] font-semibold text-muted uppercase tracking-widest px-2 mb-1">
                                {group.label}
                            </p>
                        )}
                        {group.items.map((conv) => (
                            <div
                                key={conv.id}
                                onClick={() => selectConversation(conv.id)}
                                className={clsx(
                                    'group flex items-center gap-2 rounded-lg px-2 py-2 cursor-pointer mb-0.5',
                                    'transition-colors duration-100',
                                    activeId === conv.id
                                        ? 'bg-sidebar-hover text-ink'
                                        : 'text-muted hover:bg-sidebar-hover/60 hover:text-ink',
                                    collapsed && 'justify-center'
                                )}
                            >
                                <MessageSquare size={15} className="flex-shrink-0" />
                                {!collapsed && (
                                    <>
                                        {renamingId === conv.id ? (
                                            <input
                                                className="flex-1 bg-transparent text-xs text-ink outline-none border-b border-teal"
                                                value={renameVal}
                                                autoFocus
                                                onChange={(e) => setRenameVal(e.target.value)}
                                                onKeyDown={(e) => { if (e.key === 'Enter') commitRename(); if (e.key === 'Escape') setRenamingId(null) }}
                                                onClick={(e) => e.stopPropagation()}
                                            />
                                        ) : (
                                            <span className="flex-1 text-xs truncate">{conv.title}</span>
                                        )}

                                        <div className="flex-shrink-0 flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                                            {renamingId === conv.id ? (
                                                <>
                                                    <button onClick={(e) => { e.stopPropagation(); commitRename() }} className="p-1 hover:text-teal"><Check size={12} /></button>
                                                    <button onClick={(e) => { e.stopPropagation(); setRenamingId(null) }} className="p-1 hover:text-red-400"><X size={12} /></button>
                                                </>
                                            ) : (
                                                <>
                                                    <button onClick={(e) => { e.stopPropagation(); startRename(conv.id, conv.title) }} className="p-1 hover:text-teal"><Pencil size={12} /></button>
                                                    <button onClick={(e) => handleDelete(e, conv.id)} className="p-1 hover:text-red-400"><Trash2 size={12} /></button>
                                                </>
                                            )}
                                        </div>
                                    </>
                                )}
                            </div>
                        ))}
                    </div>
                ))}
            </div>

            {/* User footer */}
            <div className="border-t border-sidebar-border p-2">
                <div className={clsx(
                    'flex items-center gap-2 rounded-lg px-2 py-2',
                    collapsed && 'justify-center'
                )}>
                    {user?.picture ? (
                        <img src={user.picture} alt="" className="w-7 h-7 rounded-full flex-shrink-0" />
                    ) : (
                        <div className="w-7 h-7 rounded-full bg-teal/20 flex items-center justify-center flex-shrink-0">
                            <span className="text-xs font-semibold text-teal">
                                {(user?.full_name || user?.username || '?')[0].toUpperCase()}
                            </span>
                        </div>
                    )}
                    {!collapsed && (
                        <>
                            <div className="flex-1 min-w-0">
                                <p className="text-xs font-medium text-ink truncate">{user?.full_name || user?.username}</p>
                                <p className="text-[10px] text-muted truncate">{user?.email}</p>
                            </div>
                            <button
                                onClick={logout}
                                className="p-1.5 rounded hover:bg-sidebar-hover text-muted hover:text-red-400 transition-colors"
                                title="Sign out"
                            >
                                <LogOut size={14} />
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}