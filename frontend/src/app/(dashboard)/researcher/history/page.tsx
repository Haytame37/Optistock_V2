"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getSearchHistory } from "@/services/researcher.service"
import { GlassCard } from "@/components/shared/glass-card"
import { GradientHero } from "@/components/shared/gradient-hero"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { ClipboardList, Calendar, Package, ArrowRight, TrendingUp, History } from "lucide-react"
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
        <Skeleton className="h-48 w-full rounded-3xl" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-40 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-10">
      <GradientHero
        title="Historique des Simulations"
        subtitle="Analysez vos décisions passées et relancez vos scénarios de recherche en un instant."
      />

      {history.length === 0 ? (
        <GlassCard className="p-16 text-center border-dashed border-2">
          <div className="flex flex-col items-center gap-6">
            <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center">
               <History className="h-10 w-10 text-muted-foreground/30" />
            </div>
            <div className="space-y-2">
               <h3 className="text-2xl font-bold">Aucune trace de recherche</h3>
               <p className="text-muted-foreground max-w-sm">Vous n'avez pas encore effectué d'analyse logistique sur la plateforme.</p>
            </div>
            <Button size="lg" className="rounded-full px-8 shadow-lg shadow-primary/20" onClick={() => router.push("/researcher/search")}>
               Démarrer ma première simulation
            </Button>
          </div>
        </GlassCard>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {history.map((item, index) => {
            const resultsCount = JSON.parse(item.results_json || "[]").length
            
            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <GlassCard className="group p-6 hover:border-primary/40 transition-all duration-300 h-full flex flex-col bg-background/50 relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-3">
                     <Badge variant="outline" className="bg-primary/5 text-primary border-primary/10 font-bold text-[10px]">
                        ID: #{item.id.toString().slice(-4)}
                     </Badge>
                  </div>
                  
                  <div className="flex items-center gap-4 mb-6">
                    <div className="h-14 w-14 rounded-2xl bg-primary/10 text-primary flex items-center justify-center group-hover:scale-110 transition-transform shadow-inner">
                      <Package className="h-7 w-7" />
                    </div>
                    <div>
                      <h4 className="font-bold text-xl group-hover:text-primary transition-colors">{item.product_name}</h4>
                      <p className="text-xs text-muted-foreground flex items-center gap-1.5 mt-0.5 font-medium">
                        <Calendar className="h-3 w-3" />
                        Effectuée le {format(new Date(item.created_at), "d MMMM yyyy", { locale: fr })}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-8">
                     <div className="p-3 rounded-xl bg-muted/30 border border-muted-foreground/5">
                        <span className="text-[10px] uppercase font-bold text-muted-foreground/60 block mb-1">Volume requis</span>
                        <span className="font-bold text-foreground/80">{item.volume} m³</span>
                     </div>
                     <div className="p-3 rounded-xl bg-muted/30 border border-muted-foreground/5">
                        <span className="text-[10px] uppercase font-bold text-muted-foreground/60 block mb-1">Durée prévue</span>
                        <span className="font-bold text-foreground/80">{item.duration_days} jours</span>
                     </div>
                  </div>

                  <div className="mt-auto pt-6 border-t border-muted-foreground/10 flex items-center justify-between">
                    <div className="flex flex-col">
                       <span className="text-[10px] uppercase font-bold text-muted-foreground/60 tracking-wider">Résultats trouvés</span>
                       <div className="flex items-center gap-1.5 mt-0.5 text-primary font-bold">
                          <TrendingUp className="h-4 w-4" />
                          {resultsCount} entrepôts
                       </div>
                    </div>
                    <Button 
                      variant="default" 
                      size="sm"
                      className="rounded-full shadow-lg shadow-primary/10 group/btn px-6"
                      onClick={() => {
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
                      Relancer
                      <ArrowRight className="h-4 w-4 ml-2 group-hover/btn:translate-x-1 transition-transform" />
                    </Button>
                  </div>
                </GlassCard>
              </motion.div>
            )
          })}
        </div>
      )}
    </div>
  )
}
