"use client"

import { useEffect, useState } from "react"
import { GlassCard } from "@/components/shared/glass-card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { getSearchHistory, getHistoryDetail } from "@/services/researcher.service"
import type { SearchHistoryItem, SearchResponse, SearchResultItem } from "@/types/researcher"
import { LogisticMap } from "@/components/map/logistic-map"
import { toast } from "sonner"
import { formatDate, cn } from "@/lib/utils"
import { 
  Package, 
  Calendar, 
  Database, 
  ChevronRight, 
  History, 
  TrendingUp, 
  MapPin, 
  Thermometer, 
  Droplets,
  Store,
  Info
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { motion, AnimatePresence } from "framer-motion"

export default function ResultsPage() {
  const [history, setHistory] = useState<SearchHistoryItem[]>([])
  const [selected, setSelected] = useState<SearchResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getSearchHistory()
      .then(setHistory)
      .catch(() => toast.error("Erreur chargement historique"))
      .finally(() => setLoading(false))
  }, [])

  const loadDetail = async (id: number) => {
    try {
      const detail = await getHistoryDetail(id)
      setSelected(detail)
    } catch {
      toast.error("Erreur chargement détail")
    }
  }

  if (loading) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto">
        <Skeleton className="h-40 w-full rounded-3xl" />
        <div className="grid grid-cols-1 gap-4">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-20 w-full rounded-2xl" />)}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-10">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight text-foreground/90 flex items-center gap-3">
          <History className="h-8 w-8 text-primary" /> Historique des simulations
        </h2>
        <p className="text-muted-foreground italic text-sm">
          Consultez les détails de vos analyses logistiques passées et visualisez-les sur la carte.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: History List */}
        <div className="lg:col-span-1 space-y-4">
          <GlassCard className="p-6 border-primary/10">
            <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground/60 mb-4">Recherches récentes</h3>
            {history.length === 0 ? (
              <div className="py-10 text-center space-y-3">
                 <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mx-auto opacity-40">
                    <History className="h-6 w-6" />
                 </div>
                 <p className="text-sm text-muted-foreground">Aucune recherche enregistrée</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
                {history.map((item) => (
                  <div
                    key={item.id}
                    className={`group flex items-center justify-between rounded-2xl border p-4 cursor-pointer transition-all duration-300 ${
                      selected && selected.id === item.id 
                      ? "bg-primary/10 border-primary shadow-md shadow-primary/5 translate-x-1" 
                      : "bg-background/40 hover:bg-background/80 hover:border-primary/40"
                    }`}
                    onClick={() => loadDetail(item.id)}
                  >
                    <div className="flex items-center gap-3">
                       <div className={`h-10 w-10 rounded-xl flex items-center justify-center transition-colors ${
                          selected && selected.id === item.id ? "bg-primary text-white" : "bg-primary/10 text-primary"
                       }`}>
                          <Package className="h-5 w-5" />
                       </div>
                       <div>
                         <p className="font-bold text-sm line-clamp-1">{item.product_name}</p>
                         <p className="text-[10px] text-muted-foreground uppercase font-semibold">
                            {formatDate(item.created_at)}
                         </p>
                       </div>
                    </div>
                    <ChevronRight className={`h-4 w-4 text-muted-foreground group-hover:text-primary transition-transform ${
                       selected && selected.id === item.id ? "translate-x-1 text-primary" : ""
                    }`} />
                  </div>
                ))}
              </div>
            )}
          </GlassCard>
        </div>

        {/* Right Column: Details */}
        <div className="lg:col-span-2">
          <AnimatePresence mode="wait">
            {selected ? (
              <motion.div
                key={selected.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <GlassCard className="p-8 border-primary/20 overflow-hidden relative">
                  <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
                    Détails: <span className="text-primary">{selected.product}</span>
                  </h3>

                  {/* KPIs */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <div className="rounded-2xl bg-primary/5 border border-primary/10 p-4 flex flex-col items-center text-center">
                      <Package className="h-5 w-5 text-primary mb-2" />
                      <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-tight">Produit</p>
                      <p className="text-sm font-bold line-clamp-1">{selected.product}</p>
                    </div>
                    <div className="rounded-2xl bg-blue-500/5 border border-blue-500/10 p-4 flex flex-col items-center text-center">
                      <Database className="h-5 w-5 text-blue-500 mb-2" />
                      <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-tight">Volume</p>
                      <p className="text-sm font-bold">{selected.volume} m³</p>
                    </div>
                    <div className="rounded-2xl bg-orange-500/5 border border-orange-500/10 p-4 flex flex-col items-center text-center">
                      <Calendar className="h-5 w-5 text-orange-500 mb-2" />
                      <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-tight">Durée</p>
                      <p className="text-sm font-bold">{selected.duration_days} jours</p>
                    </div>
                    <div className="rounded-2xl bg-green-500/5 border border-green-500/10 p-4 flex flex-col items-center text-center">
                      <TrendingUp className="h-5 w-5 text-green-500 mb-2" />
                      <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-tight">Résultats</p>
                      <p className="text-sm font-bold">{selected.results.length} entrepôts</p>
                    </div>
                  </div>

                  {/* Results Grid */}
                  <div className="space-y-4 mb-8">
                    <h4 className="text-sm font-bold uppercase tracking-widest text-muted-foreground/60">Entrepôts trouvés</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {selected.results.map((r, i) => (
                        <div key={i} className="group p-4 rounded-2xl border border-muted-foreground/10 bg-background/40 hover:border-primary/40 transition-all flex flex-col">
                           <div className="flex justify-between items-start mb-3">
                              <div className="h-10 w-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                                 <Store className="h-5 w-5" />
                              </div>
                           </div>
                           <h5 className="font-bold text-sm group-hover:text-primary transition-colors mb-1">{r.nom}</h5>
                           <div className="flex items-center gap-1 text-[10px] text-muted-foreground mb-4">
                              <MapPin className="h-3 w-3" /> {r.adresse}
                           </div>
                           <div className="grid grid-cols-3 gap-2 mt-auto">
                              <div className="p-1.5 rounded-lg bg-muted/30 text-center">
                                <span className="text-[8px] uppercase font-bold text-muted-foreground/60 block">Dist.</span>
                                <span className="text-[10px] font-bold">{r.distance_km?.toFixed(1) ?? "—"}km</span>
                              </div>
                              <div className="p-1.5 rounded-lg bg-muted/30 text-center">
                                <span className="text-[8px] uppercase font-bold text-muted-foreground/60 block">Temp.</span>
                                <span className="text-[10px] font-bold">{r.avg_temp}°C</span>
                              </div>
                              <div className="p-1.5 rounded-lg bg-muted/30 text-center">
                                <span className="text-[8px] uppercase font-bold text-muted-foreground/60 block">Hum.</span>
                                <span className="text-[10px] font-bold">{r.avg_hum}%</span>
                              </div>
                           </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Map */}
                  <div className="space-y-4">
                    <h4 className="text-sm font-bold uppercase tracking-widest text-muted-foreground/60 flex items-center gap-2">
                       <MapPin className="h-4 w-4 text-primary" /> Visualisation géographique
                    </h4>
                    <div className="rounded-3xl overflow-hidden border border-primary/20 shadow-xl shadow-primary/5">
                      <LogisticMap
                        results={selected.results.map((r) => ({ name: r.nom, lat: r.latitude, lng: r.longitude, type: "result" as const }))}
                        warehouses={[]}
                        clients={[]}
                      />
                    </div>
                  </div>
                </GlassCard>
              </motion.div>
            ) : (
              <GlassCard className="h-full flex flex-col items-center justify-center p-20 text-center border-dashed border-2">
                 <div className="h-24 w-24 rounded-full bg-muted flex items-center justify-center mb-6 opacity-30">
                    <Info className="h-12 w-12" />
                 </div>
                 <h3 className="text-2xl font-bold mb-2">Sélectionnez une recherche</h3>
                 <p className="text-muted-foreground max-w-sm">
                   Cliquez sur une simulation dans la liste de gauche pour afficher son analyse logistique détaillée et sa position sur la carte.
                 </p>
              </GlassCard>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
