"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getSearchHistory } from "@/services/researcher.service"
import { GlassCard } from "@/components/shared/glass-card"
import { GradientHero } from "@/components/shared/gradient-hero"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { ClipboardList, Calendar, Package, ArrowRight, Trash2 } from "lucide-react"
import { format } from "date-fns"
import { fr } from "date-fns/locale"
import { motion } from "framer-motion"

export default function SearchHistoryPage() {
  const router = useRouter()
  const [history, setHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getSearchHistory()
      .then(setHistory)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-32 w-full" />
        <div className="grid grid-cols-1 gap-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <GradientHero
        title="Historique des recherches"
        subtitle="Retrouvez vos analyses passées et relancez-les en un clic."
      />

      {history.length === 0 ? (
        <GlassCard className="p-12 text-center">
          <div className="flex flex-col items-center gap-4">
            <ClipboardList className="h-12 w-12 text-muted-foreground" />
            <h3 className="text-xl font-semibold">Aucun historique</h3>
            <p className="text-muted-foreground">Vous n'avez pas encore effectué de recherche d'entrepôt.</p>
            <Button onClick={() => router.push("/researcher/search")}>Lancer ma première recherche</Button>
          </div>
        </GlassCard>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {history.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <GlassCard className="p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 hover:border-primary/50 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                    <Package className="h-6 w-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-lg">{item.product_name}</h4>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground mt-1">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {format(new Date(item.created_at), "PPP", { locale: fr })}
                      </span>
                      <span className="flex items-center gap-1">
                        <Package className="h-3 w-3" />
                        {item.volume} m³ • {item.duration_days} jours
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 w-full md:w-auto">
                  <div className="text-right hidden md:block mr-4">
                    <p className="text-xs text-muted-foreground uppercase font-bold tracking-wider">Résultats</p>
                    <p className="text-lg font-semibold text-primary">
                      {JSON.parse(item.results_json || "[]").length} entrepôts
                    </p>
                  </div>
                  <Button 
                    variant="outline" 
                    className="flex-1 md:flex-none gap-2"
                    onClick={() => {
                        // Store the search in local storage to reload it in the search page
                        localStorage.setItem("last_search", JSON.stringify({
                            product: item.product_name,
                            volume: item.volume,
                            duration_days: item.duration_days,
                            cost_weight: item.cost_weight,
                            dist_weight: item.dist_weight
                        }));
                        router.push("/researcher/search");
                    }}
                  >
                    Relancer <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
