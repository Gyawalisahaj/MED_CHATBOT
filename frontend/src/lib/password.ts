import type { PasswordStrength } from '@/types'

export function checkPasswordStrength(password: string): PasswordStrength {
    const checks = [
        { label: 'At least 8 characters', passed: password.length >= 8 },
        { label: 'One uppercase letter (A–Z)', passed: /[A-Z]/.test(password) },
        { label: 'One lowercase letter (a–z)', passed: /[a-z]/.test(password) },
        { label: 'One digit (0–9)', passed: /\d/.test(password) },
        { label: 'One special character (!@#$%^&*…)', passed: /[!@#$%^&*()\-_=+\[\]{}|;:',.<>?/`~"\\]/.test(password) },
    ]

    const score = checks.filter((c) => c.passed).length

    const labels = ['', 'Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong']
    const colors = [
        '',
        '#EF4444', // red
        '#F97316', // orange
        '#EAB308', // yellow
        '#22C55E', // green
        '#0EA5A0', // teal
    ]

    return { score, label: labels[score], color: colors[score], checks }
}