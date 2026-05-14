"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { useAuth } from "@/providers/auth-provider"
import {
  Search,
  ClipboardList,
  MessageSquare,
  Warehouse,
  BarChart3,
  Home,
  LogOut,
  Activity,
} from "lucide-react"
import { Button } from "@/components/ui/button"

const researcherLinks = [
  { href: "/researcher", label: "Accueil", icon: Home },
  { href: "/researcher/search", label: "Recherche", icon: Search },
  { href: "/researcher/results", label: "Résultats", icon: ClipboardList },
  { href: "/researcher/messages", label: "Messagerie", icon: MessageSquare },
  { href: "/researcher/my-warehouses", label: "Mes Entrepôts", icon: Warehouse },
]

const ownerLinks = [
  { href: "/owner", label: "Accueil", icon: Home },
  { href: "/owner/warehouses", label: "Entrepôts", icon: Warehouse },
]

export function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()

  const links = user?.role === "researcher" ? researcherLinks : user?.role === "owner" ? ownerLinks : []

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r bg-card/95 backdrop-blur-xl">
      <div className="flex h-16 items-center gap-2 border-b px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
          OS
        </div>
        <span className="font-display text-lg font-bold">OptiStock</span>
      </div>

      <nav className="flex flex-col gap-1 p-4">
        {links.map((link) => {
          const Icon = link.icon
          const isActive = pathname === link.href
          return (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {link.label}
            </Link>
          )
        })}
      </nav>

      <div className="absolute bottom-4 left-4 right-4">
        <div className="mb-2 rounded-xl bg-muted/50 p-3">
          <p className="text-xs font-medium text-muted-foreground">{user?.first_name} {user?.last_name}</p>
          <p className="text-xs capitalize text-muted-foreground/60">{user?.role}</p>
        </div>
        <Button variant="ghost" className="w-full justify-start gap-3 text-muted-foreground" onClick={logout}>
          <LogOut className="h-4 w-4" />
          Déconnexion
        </Button>
      </div>
    </aside>
  )
}
