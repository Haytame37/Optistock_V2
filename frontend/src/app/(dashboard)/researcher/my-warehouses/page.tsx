"use client"

import { useEffect, useState } from "react"
import { GlassCard } from "@/components/shared/glass-card"
import { getMyWarehouses } from "@/services/warehouse.service"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { Store, MapPin, Activity, Calendar, ArrowRight } from "lucide-react"
import { Badge } from "@/components/ui/badge"

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

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => <Skeleton key={i} className="h-48 rounded-2xl" />)}
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight text-foreground/90">Mes Entrepôts Actifs</h2>
        <p className="text-muted-foreground italic text-sm">
          Gérez vos locations et surveillez les conditions environnementales en temps réel.
        </p>
      </div>

      {warehouses.length === 0 ? (
        <GlassCard className="p-12 text-center flex flex-col items-center justify-center border-dashed border-2 border-muted-foreground/20">
          <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center mb-4">
             <Store className="h-10 w-10 text-muted-foreground/30" />
          </div>
          <h3 className="text-xl font-bold">Aucun entrepôt loué</h3>
          <p className="text-muted-foreground max-w-xs mx-auto mt-2 text-sm leading-relaxed">
            Dès que vous aurez accepté une offre de location, vos entrepôts apparaîtront ici.
          </p>
          <Button onClick={() => router.push("/researcher/search")} variant="outline" className="mt-6">
             Lancer une recherche
          </Button>
        </GlassCard>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {warehouses.map((wh: any, i: number) => (
            <GlassCard key={i} className="group hover:border-primary/40 transition-all duration-300 overflow-hidden flex flex-col bg-background/50">
              <div className="h-1.5 bg-primary/20 w-full group-hover:bg-primary transition-colors" />
              <div className="p-6 flex-1 flex flex-col">
                <div className="flex justify-between items-start mb-4">
                  <div className="h-12 w-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Store className="h-6 w-6" />
                  </div>
                  <Badge variant="secondary" className="bg-green-50 text-green-600 border-green-100 uppercase text-[10px] font-bold">
                    Actif
                  </Badge>
                </div>

                <h3 className="font-bold text-lg mb-1 group-hover:text-primary transition-colors line-clamp-1">
                  {wh.nom || wh.name}
                </h3>
                
                <div className="flex items-start gap-2 text-sm text-muted-foreground mt-2">
                  <MapPin className="h-4 w-4 shrink-0 mt-0.5 text-primary/60" />
                  <span className="line-clamp-2 leading-relaxed">{wh.adresse || wh.address}</span>
                </div>

                <div className="mt-auto pt-6 flex items-center justify-between">
                   <div className="flex flex-col">
                      <span className="text-[10px] uppercase font-bold text-muted-foreground/60 tracking-wider">État IOT</span>
                      <div className="flex items-center gap-1.5 mt-0.5 text-green-600 font-bold text-xs uppercase tracking-tight">
                         <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                         Connecté
                      </div>
                   </div>
                   <Button
                    variant="default"
                    size="sm"
                    className="rounded-full shadow-lg shadow-primary/10 group/btn"
                    onClick={() => router.push(`/iot/${wh.warehouse_id || wh.id_entrepot}`)}
                  >
                    Dashboard 
                    <ArrowRight className="h-3 w-3 ml-2 group-hover/btn:translate-x-1 transition-transform" />
                  </Button>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  )
}
