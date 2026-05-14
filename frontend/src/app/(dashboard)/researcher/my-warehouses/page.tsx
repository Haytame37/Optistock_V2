"use client"

import { useEffect, useState } from "react"
import { GlassCard } from "@/components/shared/glass-card"
import { getMyWarehouses } from "@/services/warehouse.service"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useRouter } from "next/navigation"
import { toast } from "sonner"

export default function MyWarehousesPage() {
  const [warehouses, setWarehouses] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    getMyWarehouses()
      .then(setWarehouses)
      .catch(() => toast.error("Erreur chargement"))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="space-y-4">{[1, 2].map((i) => <Skeleton key={i} className="h-24" />)}</div>

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Mes entrepôts loués</h2>
      {warehouses.length === 0 ? (
        <GlassCard className="p-8 text-center text-muted-foreground">
          Aucun entrepôt importé ou loué pour le moment
        </GlassCard>
      ) : (
        <div className="grid gap-4">
          {warehouses.map((wh: any, i: number) => (
            <GlassCard key={i} className="p-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-lg">{wh.nom || wh.name}</h3>
                  <p className="text-sm text-muted-foreground">{wh.adresse || wh.address}</p>
                  {wh.latitude && wh.longitude && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {wh.latitude}°N, {wh.longitude}°E
                    </p>
                  )}
                </div>
                <Button
                  variant="default"
                  size="sm"
                  onClick={() => router.push(`/iot/${wh.warehouse_id || wh.id_entrepot}`)}
                >
                  Dashboard IoT
                </Button>
              </div>
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  )
}
