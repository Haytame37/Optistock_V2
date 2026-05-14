import type { Metadata } from "next"
import { Providers } from "@/providers/providers"
import "./globals.css"
import "leaflet/dist/leaflet.css"

export const metadata: Metadata = {
  title: "OptiStock Solutions",
  description: "Système d'Aide à la Décision Logistique",
}

import { ChatbotWidget } from "@/components/ui/chatbot"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className="min-h-screen">
        <Providers>
          {children}
          <ChatbotWidget />
        </Providers>
      </body>
    </html>
  )
}
