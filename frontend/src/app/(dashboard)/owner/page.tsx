"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/providers/auth-provider"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { PlusCircle, Package, MessageSquare, MapPin } from "lucide-react"
import { getOwnerWarehouses, getRecentOwnerWarehouses } from "@/services/warehouse.service"
import { getMessagingRequests } from "@/services/messaging.service"

export default function OwnerDashboard() {
  const { user } = useAuth()
  const router = useRouter()
  
  const [stats, setStats] = useState({ totalWarehouses: 0, pendingMessages: 0 })
  const [recentWarehouses, setRecentWarehouses] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getOwnerWarehouses().then((d: any[]) => setStats(s => ({ ...s, totalWarehouses: d?.length || 0 }))).catch(() => {}),
      getMessagingRequests().then((d: any[]) => {
        const pendingCount = d?.filter((m: any) => m.status === 'pending').length || 0
        setStats(s => ({ ...s, pendingMessages: pendingCount }))
      }).catch(() => {}),
      getRecentOwnerWarehouses().then((d: any[]) => setRecentWarehouses(d || [])).catch(() => {})
    ]).finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Tableau de bord Propriétaire</h1>
          <p className="text-muted-foreground mt-1">
            👋 Bonjour, {user?.first_name || "Propriétaire"} ! Voici un aperçu de vos entrepôts.
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-primary">Gérer les entrepôts</CardTitle>
            <Package className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{loading ? "..." : stats.totalWarehouses}</div>
            <p className="text-xs text-muted-foreground mb-4">Visualisez et surveillez vos unités.</p>
            <Button variant="outline" className="w-full" onClick={() => router.push("/owner/warehouses")}>
              Accéder à la liste ➜
            </Button>
          </CardContent>
        </Card>
        
        <Card className="hover:shadow-md transition-shadow border-orange-200 dark:border-orange-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-600 dark:text-orange-400">Ajouter un entrepôt</CardTitle>
            <PlusCircle className="h-4 w-4 text-orange-600 dark:text-orange-400" />
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground mb-6 mt-2">Enregistrez une nouvelle unité et configurez ses capteurs IoT.</p>
            <Button variant="default" className="w-full bg-orange-600 hover:bg-orange-700" onClick={() => router.push("/owner/warehouses/add")}>
              Démarrer la configuration ➜
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow border-blue-200 dark:border-blue-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-600 dark:text-blue-400">Messagerie</CardTitle>
            <MessageSquare className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <div className="text-2xl font-bold">{loading ? "..." : stats.pendingMessages}</div>
              {stats.pendingMessages > 0 && (
                <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                  Nouveau
                </span>
              )}
            </div>
            <p className="text-xs text-muted-foreground mb-4">Gérez les demandes de location.</p>
            <Button variant="default" className="w-full bg-blue-600 hover:bg-blue-700" onClick={() => router.push("/owner/messages")}>
              Ouvrir la messagerie ➜
            </Button>
          </CardContent>
        </Card>
      </div>
      
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Unités récentes</h2>
        {loading ? (
          <p className="text-sm text-muted-foreground">Chargement...</p>
        ) : recentWarehouses.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center">
              <p className="text-muted-foreground">Aucun entrepôt enregistré pour le moment.</p>
              <Button variant="outline" className="mt-4" onClick={() => router.push("/owner/warehouses/add")}>
                Ajouter un premier entrepôt
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {recentWarehouses.map((wh) => (
              <Card key={wh.id} className="hover:border-primary/50 transition-colors">
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start">
                    <span className={`text-[10px] font-bold px-2 py-1 rounded-md ${
                      wh.status === 'Disponible' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
                      wh.status === 'Non disponible' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400' :
                      'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300'
                    }`}>
                      {wh.status}
                    </span>
                  </div>
                  <CardTitle className="text-lg mt-2">{wh.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-start gap-2 text-sm text-muted-foreground mt-2">
                    <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>{wh.address}</span>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1" onClick={() => router.push(`/owner/warehouses/${wh.id}/edit`)}>
                      Modifier
                    </Button>
                    <Button variant="default" size="sm" className="flex-1" onClick={() => router.push(`/iot/${wh.id}`)}>
                      IoT
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
