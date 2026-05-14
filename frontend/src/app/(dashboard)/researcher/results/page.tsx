"use client"

import { useEffect, useState } from "react"
import { GlassCard } from "@/components/shared/glass-card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { getSearchHistory, getHistoryDetail } from "@/services/researcher.service"
import type { SearchHistoryItem, SearchResponse, SearchResultItem } from "@/types/researcher"
import { LogisticMap } from "@/components/map/logistic-map"
import { toast } from "sonner"
import { formatDate } from "@/lib/utils"

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
    return <div className="space-y-4">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-20 w-full" />)}</div>
  }

  return (
    <div className="space-y-6">
      <GlassCard className="p-6">
        <h2 className="text-xl font-bold mb-4">Historique des recherches</h2>
        {history.length === 0 ? (
          <p className="text-muted-foreground">Aucune recherche enregistrée</p>
        ) : (
          <div className="space-y-2">
            {history.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between rounded-xl border p-4 cursor-pointer hover:bg-accent transition-colors"
                onClick={() => loadDetail(item.id)}
              >
                <div>
                  <p className="font-medium">{item.product_name}</p>
                  <p className="text-sm text-muted-foreground">
                    {item.volume} m³ · {item.duration_days} jours · {formatDate(item.created_at)}
                  </p>
                </div>
                <Button variant="ghost" size="sm">Voir</Button>
              </div>
            ))}
          </div>
        )}
      </GlassCard>

      {selected && (
        <div className="space-y-4">
          <GlassCard className="p-6">
            <h2 className="text-lg font-bold mb-4">Détails: {selected.product}</h2>
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="rounded-xl bg-muted p-4 text-center">
                <p className="text-xs text-muted-foreground">Produit</p>
                <p className="text-lg font-bold">{selected.product}</p>
              </div>
              <div className="rounded-xl bg-muted p-4 text-center">
                <p className="text-xs text-muted-foreground">Volume</p>
                <p className="text-lg font-bold">{selected.volume} m³</p>
              </div>
              <div className="rounded-xl bg-muted p-4 text-center">
                <p className="text-xs text-muted-foreground">Durée</p>
                <p className="text-lg font-bold">{selected.duration_days} jours</p>
              </div>
              <div className="rounded-xl bg-muted p-4 text-center">
                <p className="text-xs text-muted-foreground">Résultats</p>
                <p className="text-lg font-bold">{selected.results.length}</p>
              </div>
            </div>
            {selected.results.length > 0 && (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left text-muted-foreground">
                        <th className="pb-2 font-medium">Nom</th>
                        <th className="pb-2 font-medium">Score</th>
                        <th className="pb-2 font-medium">Distance</th>
                        <th className="pb-2 font-medium">Temp.</th>
                        <th className="pb-2 font-medium">Hum.</th>
                        <th className="pb-2 font-medium">Statut</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selected.results.map((r, i) => (
                        <tr key={i} className="border-b last:border-0">
                          <td className="py-3 font-medium">{r.nom}</td>
                          <td className="py-3">{r.score_logistique.toFixed(2)}</td>
                          <td className="py-3">{r.distance_km?.toFixed(2) ?? "—"} km</td>
                          <td className="py-3">{r.avg_temp}°C</td>
                          <td className="py-3">{r.avg_hum}%</td>
                          <td className="py-3">{r.status}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="mt-6">
                  <LogisticMap
                    results={selected.results.map((r) => ({ name: r.nom, lat: r.latitude, lng: r.longitude, type: "result" as const }))}
                    warehouses={[]}
                    clients={[]}
                  />
                </div>
              </>
            )}
          </GlassCard>
        </div>
      )}
    </div>
  )
}
