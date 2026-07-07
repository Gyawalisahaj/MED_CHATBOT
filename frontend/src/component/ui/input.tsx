import React, { forwardRef } from 'react'
import { clsx } from 'clsx'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string
    error?: string
    hint?: string
    leftIcon?: React.ReactNode
    rightIcon?: React.ReactNode
}

const Input = forwardRef<HTMLInputElement, InputProps>(
    ({ label, error, hint, leftIcon, rightIcon, className, ...props }, ref) => {
        return (
            <div className="flex flex-col gap-1">
                {label && (
                    <label className="text-sm font-medium text-ink/80">{label}</label>
                )}
                <div className="relative">
                    {leftIcon && (
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted">
                            {leftIcon}
                        </span>
                    )}
                    <input
                        ref={ref}
                        className={clsx(
                            'w-full rounded-lg border bg-card px-3 py-2.5 text-sm text-ink placeholder-muted',
                            'focus:outline-none focus:ring-2 focus:ring-teal focus:border-teal',
                            'transition-colors duration-150',
                            error ? 'border-red-500 focus:ring-red-500' : 'border-border hover:border-muted/50',
                            leftIcon && 'pl-10',
                            rightIcon && 'pr-10',
                            className
                        )}
                        {...props}
                    />
                    {rightIcon && (
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted">
                            {rightIcon}
                        </span>
                    )}
                </div>
                {error && <p className="text-xs text-red-400">{error}</p>}
                {hint && !error && <p className="text-xs text-muted">{hint}</p>}
            </div>
        )
    }
)
Input.displayName = 'Input'
export default Input