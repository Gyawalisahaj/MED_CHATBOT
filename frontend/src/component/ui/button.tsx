import React from 'react'
import { clsx } from 'clsx'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'ghost' | 'danger' | 'outline'
    size?: 'sm' | 'md' | 'lg'
    loading?: boolean
    fullWidth?: boolean
}

export default function Button({
    children,
    variant = 'primary',
    size = 'md',
    loading = false,
    fullWidth = false,
    disabled,
    className,
    ...props
}: ButtonProps) {
    return (
        <button
            disabled={disabled || loading}
            className={clsx(
                'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-150',
                'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-surface',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                size === 'sm' && 'px-3 py-1.5 text-xs',
                size === 'md' && 'px-4 py-2.5 text-sm',
                size === 'lg' && 'px-6 py-3 text-base',
                variant === 'primary' && 'bg-teal text-white hover:bg-teal-hover focus:ring-teal',
                variant === 'ghost' && 'text-ink/70 hover:text-ink hover:bg-card focus:ring-border',
                variant === 'danger' && 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
                variant === 'outline' && 'border border-border text-ink/80 hover:bg-card hover:text-ink focus:ring-teal',
                fullWidth && 'w-full',
                className
            )}
            {...props}
        >
            {loading ? (
                <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            ) : null}
            {children}
        </button>
    )
}