"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { GradientHero } from "@/components/shared/gradient-hero"
import { KpiCard } from "@/components/shared/kpi-card"
import { GlassCard } from "@/components/shared/glass-card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/providers/auth-provider"
import { getMyWarehouses } from "@/services/warehouse.service"
import { getSearchHistory } from "@/services/researcher.service"
import { getMessagingRequests } from "@/services/messaging.service"
import { motion } from "framer-motion"
import { Search, Warehouse, MessageSquare, ClipboardList } from "lucide-react"

export default function ResearcherPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [stats, setStats] = useState({ warehouses: 0, responses: 0, historyCount: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getMyWarehouses().then((d: any[]) => setStats((s) => ({ ...s, warehouses: d?.length || 0 }))).catch(() => {}),
      getMessagingRequests().then((d: any[]) => setStats((s) => ({ ...s, responses: d?.length || 0 }))).catch(() => {}),
      getSearchHistory().then((d: any[]) => setStats((s) => ({ ...s, historyCount: d?.length || 0 }))).catch(() => {}),
    ]).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-24" />)}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <GradientHero
        title={`Bonjour ${user?.first_name || "Chercheur"}`}
        subtitle="Cette interface vous permet de lancer une recherche d'entrepôt, consulter les résultats de vos analyses et suivre les retours des propriétaires."
      />

      <div className="grid grid-cols-3 gap-4">
        <KpiCard label="Entrepôts importés" value={stats.warehouses} icon="🏭" />
        <KpiCard label="Points de livraison" value="-" icon="📍" />
        <KpiCard label="Historique recherches" value={stats.historyCount} icon="📊" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <GlassCard className="p-6 cursor-pointer h-full flex flex-col" onClick={() => router.push("/researcher/search")}>
            <Search className="h-8 w-8 text-primary mb-3" />
            <h3 className="font-semibold mb-1 text-lg text-primary">Recherche d'entrepôt</h3>
            <p className="text-sm text-muted-foreground flex-grow">Lancer une analyse logistique complète et trouver l'unité idéale.</p>
            <Button className="mt-4 w-full" variant="default" onClick={(e) => { e.stopPropagation(); router.push("/researcher/search"); }}>
              Ouvrir la recherche
            </Button>
          </GlassCard>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <GlassCard className="p-6 cursor-pointer h-full flex flex-col" onClick={() => router.push("/researcher/history")}>
            <ClipboardList className="h-8 w-8 text-amber-500 mb-3" />
            <h3 className="font-semibold mb-1 text-lg text-amber-600">Historique</h3>
            <p className="text-sm text-muted-foreground flex-grow">Consulter vos recherches passées, les critères utilisés et les résultats obtenus.</p>
            <Button className="mt-4 w-full" variant="outline" onClick={(e) => { e.stopPropagation(); router.push("/researcher/history"); }}>
              Voir l'historique
            </Button>
          </GlassCard>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <GlassCard className="p-6 cursor-pointer h-full flex flex-col" onClick={() => router.push("/researcher/my-warehouses")}>
            <Warehouse className="h-8 w-8 text-green-500 mb-3" />
            <h3 className="font-semibold mb-1 text-lg text-green-600">Mes entrepôts</h3>
            <p className="text-sm text-muted-foreground flex-grow">Consulter la liste de vos entrepôts loués et leur état IoT.</p>
            <Button className="mt-4 w-full" variant="outline" onClick={(e) => { e.stopPropagation(); router.push("/researcher/my-warehouses"); }}>
              Voir mes entrepôts
            </Button>
          </GlassCard>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <GlassCard className="p-6 cursor-pointer h-full flex flex-col" onClick={() => router.push("/researcher/messages")}>
            <MessageSquare className="h-8 w-8 text-blue-500 mb-3" />
            <h3 className="font-semibold mb-1 text-lg text-blue-600">Réponses propriétaires</h3>
            <p className="text-sm text-muted-foreground flex-grow">Suivre les statuts de vos demandes de réservation.</p>
            <Button className="mt-4 w-full" variant="outline" onClick={(e) => { e.stopPropagation(); router.push("/researcher/messages"); }}>
              Voir les réponses
            </Button>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  )
}
