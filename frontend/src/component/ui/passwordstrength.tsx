'use client'
import { checkPasswordStrength } from '@/lib/password'
import { CheckCircle2, XCircle } from 'lucide-react'

export default function PasswordStrengthMeter({ password }: { password: string }) {
    if (!password) return null
    const { score, label, color, checks } = checkPasswordStrength(password)

    return (
        <div className="mt-2 space-y-2 animate-fade-in">
            {/* Bar */}
            <div className="flex items-center gap-2">
                <div className="flex-1 h-1.5 rounded-full bg-border overflow-hidden">
                    <div
                        className="strength-bar h-full rounded-full"
                        style={{ width: `${(score / 5) * 100}%`, background: color }}
                    />
                </div>
                {label && (
                    <span className="text-xs font-medium min-w-[72px] text-right" style={{ color }}>
                        {label}
                    </span>
                )}
            </div>

            {/* Checklist */}
            <div className="grid grid-cols-1 gap-0.5">
                {checks.map((c) => (
                    <div key={c.label} className="flex items-center gap-1.5">
                        {c.passed ? (
                            <CheckCircle2 size={12} className="text-teal flex-shrink-0" />
                        ) : (
                            <XCircle size={12} className="text-muted flex-shrink-0" />
                        )}
                        <span
                            className={`text-xs ${c.passed ? 'text-teal' : 'text-muted'}`}
                        >
                            {c.label}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    )
}