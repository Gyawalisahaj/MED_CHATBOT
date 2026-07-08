import type { Metadata } from 'next'
import './globals.css'
import { AuthProvider } from '@/context/authcontext'
import { ConversationsProvider } from '@/context/conversationcontext'

export const metadata: Metadata = {
  title: 'MedChat',
  description: 'AI-powered medical chat assistant',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        <AuthProvider>
          <ConversationsProvider>{children}</ConversationsProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
