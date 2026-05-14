"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"
import { useAuth } from "@/providers/auth-provider"
import {
  Search,
  ClipboardList,
  MessageSquare,
  Warehouse,
  Home,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Sun,
  Moon,
  ExternalLink,
  RefreshCcw,
  Zap,
} from "lucide-react"
import { Button } from "@/components/ui/button"

const researcherLinks = [
  { href: "/researcher", label: "Accueil", icon: Home, exact: true },
  { href: "/researcher/search", label: "Recherche", icon: Search },
  { href: "/researcher/results", label: "Résultats", icon: ClipboardList },
  { href: "/researcher/messages", label: "Messagerie", icon: MessageSquare },
  { href: "/researcher/my-warehouses", label: "Mes Entrepôts", icon: Warehouse },
  { href: "/researcher/optimization-lab", label: "Optimization Lab", icon: Zap },
]

const ownerLinks = [
  { href: "/owner", label: "Accueil", icon: Home },
  { href: "/owner/warehouses", label: "Entrepôts", icon: Warehouse },
  { href: "/owner/messages", label: "Messagerie", icon: MessageSquare },
]

const adminLinks = [
  { href: "/admin", label: "Dashboard", icon: Home },
  { href: "/admin", label: "Utilisateurs", icon: Search },
  { href: "/admin", label: "Maintenance", icon: RefreshCcw },
]

export function Sidebar({ 
  collapsed, 
  setCollapsed 
}: { 
  collapsed: boolean, 
  setCollapsed: (v: boolean) => void 
}) {
  const pathname = usePathname()
  const { user, logout } = useAuth()
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Avoid hydration mismatch
  useEffect(() => setMounted(true), [])

  const links = 
    user?.role === "researcher" ? researcherLinks : 
    user?.role === "owner" ? ownerLinks : 
    user?.role === "admin" ? adminLinks : []

  if (!mounted) return null

  return (
    <aside 
      className={cn(
        "fixed left-0 top-0 z-40 h-screen border-r bg-card/95 backdrop-blur-xl transition-all duration-300 ease-in-out",
        collapsed ? "w-20" : "w-64"
      )}
    >
      <div className="flex h-16 items-center justify-between border-b px-4">
        <Link href="/" className={cn("flex items-center gap-2 overflow-hidden transition-all", collapsed ? "w-0 opacity-0" : "w-auto opacity-100")}>
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
            OS
          </div>
          <span className="font-display text-lg font-bold truncate">OptiStock</span>
        </Link>
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={() => setCollapsed(!collapsed)}
          className="h-8 w-8 rounded-full hover:bg-primary/10 hover:text-primary"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      <nav className="flex flex-col gap-1 p-3">
        {links.map((link) => {
          const Icon = link.icon
          const isActive = link.exact ? pathname === link.href : pathname.startsWith(link.href)
          return (
            <Link
              key={link.href}
              href={link.href}
              title={collapsed ? link.label : ""}
              className={cn(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all group",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <Icon className={cn("h-4 w-4 shrink-0 transition-transform", !isActive && "group-hover:scale-110")} />
              <span className={cn("transition-all duration-300", collapsed ? "w-0 opacity-0 hidden" : "w-auto opacity-100 block")}>
                {link.label}
              </span>
            </Link>
          )
        })}
      </nav>

      <div className="absolute bottom-4 left-3 right-3 flex flex-col gap-2">
        {/* Link to Landing Page */}
        <Link 
          href="/" 
          title={collapsed ? "Page d'accueil" : ""}
          className={cn(
            "flex items-center gap-3 rounded-xl px-3 py-2 text-xs font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-all",
            collapsed ? "justify-center" : ""
          )}
        >
          <ExternalLink className="h-4 w-4 shrink-0" />
          <span className={cn(collapsed ? "hidden" : "block")}>Site Public</span>
        </Link>

        {/* Theme Toggle */}
        <Button
          variant="ghost"
          size="sm"
          className={cn("w-full justify-start gap-3 text-muted-foreground", collapsed ? "px-0 justify-center" : "px-3")}
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          title={collapsed ? "Changer de thème" : ""}
        >
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          <span className={cn(collapsed ? "hidden" : "block")}>
            {theme === "dark" ? "Mode Clair" : "Mode Sombre"}
          </span>
        </Button>

        <div className={cn("mb-2 rounded-xl bg-muted/50 p-3 transition-all", collapsed ? "hidden" : "block")}>
          <p className="text-[10px] font-bold uppercase text-muted-foreground/40 mb-1">Session</p>
          <p className="text-xs font-semibold truncate text-primary">{user?.first_name} {user?.last_name}</p>
          <p className="text-[10px] capitalize text-muted-foreground/60">{user?.role}</p>
        </div>

        <Button 
          variant="ghost" 
          size="sm" 
          className={cn("w-full justify-start gap-3 text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30", collapsed ? "px-0 justify-center" : "px-3")} 
          onClick={logout}
          title={collapsed ? "Déconnexion" : ""}
        >
          <LogOut className="h-4 w-4" />
          <span className={cn(collapsed ? "hidden" : "block")}>Déconnexion</span>
        </Button>
      </div>
    </aside>
  )
}
