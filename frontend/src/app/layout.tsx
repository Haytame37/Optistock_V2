import type { Metadata } from "next"
import { Providers } from "@/providers/providers"
import "./globals.css"

export const metadata: Metadata = {
  title: "OptiStock Solutions",
  description: "Système d'Aide à la Décision Logistique",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className="min-h-screen">
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
