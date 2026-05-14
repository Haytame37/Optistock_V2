"use client"

import { ThemeToggle } from "./theme-toggle"
import { useAuth } from "@/providers/auth-provider"
import { Button } from "@/components/ui/button"
import { LogOut } from "lucide-react"

export function Header() {
  const { user, logout } = useAuth()

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-end gap-4 border-b bg-background/95 backdrop-blur-xl px-6">
      <ThemeToggle />
      <span className="text-sm text-muted-foreground">
        {user?.first_name} {user?.last_name}
      </span>
      <Button variant="ghost" size="icon" onClick={logout} className="rounded-full">
        <LogOut className="h-4 w-4" />
      </Button>
    </header>
  )
}
