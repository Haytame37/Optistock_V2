"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"
import { getWarehouse, updateWarehouse } from "@/services/warehouse.service"
import { Save, X, Settings2 } from "lucide-react"
import { cn } from "@/lib/utils"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export default function EditWarehousePage() {
  const router = useRouter()
  const params = useParams()
  const id = params.id as string

  const [loading, setLoading] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)
  const [formData, setFormData] = useState({
    name: "",
    address: "",
    latitude: "",
    longitude: "",
    volume_m3: "",
    status: "available",
  })

  useEffect(() => {
    const loadWarehouse = async () => {
      try {
        const data = await getWarehouse(id)
        setFormData({
          name: data.name,
          address: data.address,
          latitude: data.latitude.toString(),
          longitude: data.longitude.toString(),
          volume_m3: data.volume_m3.toString(),
          status: data.status || "available",
        })
      } catch (error) {
        toast.error("Impossible de charger les données de l'entrepôt")
        router.push("/owner/warehouses")
      } finally {
        setInitialLoading(false)
      }
    }
    
    if (id) {
      loadWarehouse()
    }
  }, [id, router])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name || !formData.latitude || !formData.longitude) {
      toast.error("Le nom et les coordonnées GPS sont obligatoires")
      return
    }

    setLoading(true)
    try {
      const payload = {
        name: formData.name,
        address: formData.address,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        volume_m3: formData.volume_m3 ? parseFloat(formData.volume_m3) : 0,
        status: formData.status,
      }

      await updateWarehouse(id, payload)
      toast.success("Entrepôt mis à jour avec succès")
      router.push("/owner/warehouses")
    } catch (error) {
      toast.error("Erreur lors de la mise à jour de l'entrepôt")
    } finally {
      setLoading(false)
    }
  }

  if (initialLoading) {
    return <div className="text-center py-12 text-muted-foreground">Chargement des données...</div>
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Modifier un Entrepôt</h1>
          <p className="text-muted-foreground mt-1">
            Mettez à jour les informations de votre unité de stockage.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="grid gap-6 md:grid-cols-3">
          <div className="md:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">ℹ️ Informations Générales</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nom de l'entrepôt *</Label>
                  <Input id="name" name="name" placeholder="Ex : Hub Logistique Nord-Est" value={formData.name} onChange={handleChange} required />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="address">Adresse complète</Label>
                  <Textarea id="address" name="address" placeholder="Numéro, rue, ville" value={formData.address} onChange={handleChange} className="resize-none" rows={3} />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="latitude">Latitude *</Label>
                    <Input id="latitude" name="latitude" type="number" step="any" placeholder="48.8566" value={formData.latitude} onChange={handleChange} required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="longitude">Longitude *</Label>
                    <Input id="longitude" name="longitude" type="number" step="any" placeholder="2.3522" value={formData.longitude} onChange={handleChange} required />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">⚙️ Statut Opérationnel</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Label>État de disponibilité</Label>
                  <Select 
                    value={formData.status} 
                    onValueChange={(val) => setFormData(prev => ({ ...prev, status: val }))}
                  >
                    <SelectTrigger className={cn(
                      "w-full font-bold",
                      formData.status === 'available' ? 'text-green-600' :
                      formData.status === 'rented' ? 'text-blue-600' :
                      'text-amber-600'
                    )}>
                      <SelectValue placeholder="Choisir un statut" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="available">Disponible</SelectItem>
                      <SelectItem value="rented">Occupé / Actif</SelectItem>
                      <SelectItem value="maintenance">En Maintenance</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-[10px] text-muted-foreground mt-2 italic">
                    Note: Un entrepôt en maintenance n'est pas visible par les chercheurs.
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">📦 Capacité & Volume</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Label htmlFor="volume_m3">Volume total (m³)</Label>
                  <Input id="volume_m3" name="volume_m3" type="number" min="0" step="100" placeholder="50000" value={formData.volume_m3} onChange={handleChange} />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4 flex flex-col gap-3">
                <Button type="submit" className="w-full bg-primary hover:bg-primary/90" disabled={loading}>
                  <Save className="w-4 h-4 mr-2" />
                  {loading ? "Mise à jour..." : "Mettre à jour"}
                </Button>
                <Button type="button" variant="outline" className="w-full" onClick={() => router.push("/owner/warehouses")} disabled={loading}>
                  <X className="w-4 h-4 mr-2" />
                  Annuler
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </form>
    </div>
  )
}
