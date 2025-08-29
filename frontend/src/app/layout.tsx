import './globals.css'
import { Providers } from './providers'

export const metadata = {
  title: 'YYC³ EasyVizAI',
  description: 'AI-powered visualization and chat application',
  keywords: ['AI', 'chat', 'visualization', 'machine learning'],
  authors: [{ name: 'YY-Nexus' }],
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        <Providers>
          <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
            {children}
          </div>
        </Providers>
      </body>
    </html>
  )
}