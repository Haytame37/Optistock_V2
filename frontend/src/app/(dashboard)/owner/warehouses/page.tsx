"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getOwnerWarehouses, deleteWarehouse } from "@/services/warehouse.service"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { MapPin, Search, Edit2, Trash2, Activity } from "lucide-react"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { toast } from "sonner"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

export default function WarehousesList() {
  const router = useRouter()
  const [warehouses, setWarehouses] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [filter, setFilter] = useState("Tous")

  const loadData = async () => {
    setLoading(true)
    try {
      const data = await getOwnerWarehouses()
      setWarehouses(data || [])
    } catch (error) {
      toast.error("Erreur lors du chargement des entrepôts")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleDelete = async (id: string, name: string) => {
    try {
      await deleteWarehouse(id)
      toast.success(`${name} a été supprimé avec succès.`)
      loadData()
    } catch (error) {
      toast.error("Erreur lors de la suppression")
    }
  }

  const filteredWarehouses = warehouses.filter((wh) => {
    const matchesSearch = wh.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          wh.address.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filter === "Tous" || wh.status === filter
    return matchesSearch && matchesFilter
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Liste des Entrepôts</h1>
          <p className="text-muted-foreground mt-1">
            Gérez vos unités de stockage et surveillez leur état.
          </p>
        </div>
        <Button onClick={() => router.push("/owner/warehouses/add")} className="bg-primary hover:bg-primary/90">
          ➕ Ajouter un entrepôt
        </Button>
      </div>

      <div className="flex flex-col md:flex-row gap-6 items-center bg-card p-4 rounded-xl border shadow-sm">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Rechercher un entrepôt ou une ville..." 
            className="pl-9 w-full"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        
        <div className="w-full md:w-auto">
          <RadioGroup defaultValue="Tous" onValueChange={setFilter} className="flex gap-4 overflow-x-auto pb-2 md:pb-0">
            <div className="flex items-center space-x-2 whitespace-nowrap">
              <RadioGroupItem value="Tous" id="r1" />
              <Label htmlFor="r1">Tous</Label>
            </div>
            <div className="flex items-center space-x-2 whitespace-nowrap">
              <RadioGroupItem value="Disponible" id="r2" />
              <Label htmlFor="r2">Disponible</Label>
            </div>
            <div className="flex items-center space-x-2 whitespace-nowrap">
              <RadioGroupItem value="Actif" id="r3" />
              <Label htmlFor="r3">Actif</Label>
            </div>
            <div className="flex items-center space-x-2 whitespace-nowrap">
              <RadioGroupItem value="Non disponible" id="r4" />
              <Label htmlFor="r4">Indisponible</Label>
            </div>
          </RadioGroup>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-muted-foreground">Chargement...</div>
      ) : filteredWarehouses.length === 0 ? (
        <Card className="border-dashed border-2 bg-transparent shadow-none">
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground mb-4">Aucun entrepôt trouvé avec ces critères.</p>
            {warehouses.length === 0 && (
              <Button onClick={() => router.push("/owner/warehouses/add")}>Créer votre premier entrepôt</Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredWarehouses.map((wh) => (
            <Card key={wh.id} className="hover:shadow-md transition-shadow group flex flex-col">
              <CardHeader className="pb-3 flex-none">
                <div className="flex justify-between items-start mb-2">
                  <span className={`text-xs font-bold px-2 py-1 rounded-md ${
                    wh.status === 'Disponible' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
                    wh.status === 'Non disponible' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400' :
                    wh.status === 'Actif' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' :
                    'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300'
                  }`}>
                    {wh.status?.toUpperCase() || 'INCONNU'}
                  </span>
                </div>
                <CardTitle className="text-lg line-clamp-1" title={wh.name}>{wh.name}</CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-start gap-2 text-sm text-muted-foreground mb-1">
                    <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span className="line-clamp-2" title={wh.address}>{wh.address}</span>
                  </div>
                  <div className="text-xs text-muted-foreground ml-6 mb-4">
                    GPS: {wh.gps}
                  </div>
                </div>
                
                <div className="flex gap-2 mt-auto pt-4 border-t">
                  <Button variant="outline" size="sm" className="flex-1" onClick={() => router.push(`/owner/warehouses/${wh.id}/edit`)}>
                    <Edit2 className="h-3 w-3 mr-1" /> Modif
                  </Button>
                  
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="outline" size="sm" className="flex-1 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/30">
                        <Trash2 className="h-3 w-3 mr-1" /> Suppr
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Êtes-vous sûr ?</AlertDialogTitle>
                        <AlertDialogDescription>
                          Cette action supprimera définitivement l'entrepôt "{wh.name}" et toutes ses données IoT associées.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Annuler</AlertDialogCancel>
                        <AlertDialogAction onClick={() => handleDelete(wh.id, wh.name)} className="bg-red-600 hover:bg-red-700">
                          Supprimer
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                  
                  <Button variant="default" size="sm" className="flex-1" onClick={() => router.push(`/iot/${wh.id}`)}>
                    <Activity className="h-3 w-3 mr-1" /> IoT
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
