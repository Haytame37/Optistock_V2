"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"
import { createWarehouse } from "@/services/warehouse.service"
import { importIoTData } from "@/services/iot.service"
import { Save, X, UploadCloud, FileText } from "lucide-react"

export default function AddWarehousePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    address: "",
    latitude: "",
    longitude: "",
    volume_m3: "",
  })
  const [file, setFile] = useState<File | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0]
      if (selectedFile.name.endsWith('.csv')) {
        setFile(selectedFile)
      } else {
        toast.error("Veuillez sélectionner un fichier CSV")
        e.target.value = ''
      }
    }
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
      }

      // 1. Create warehouse
      const res = await createWarehouse(payload)
      const warehouseId = res.warehouse_id

      // 2. Upload CSV if exists
      if (file && warehouseId) {
        try {
          await importIoTData(warehouseId, file)
          toast.success("Entrepôt créé et données IoT importées avec succès")
        } catch (iotErr) {
          toast.warning("Entrepôt créé, mais l'importation IoT a échoué")
        }
      } else {
        toast.success("Entrepôt créé avec succès")
      }

      router.push("/owner/warehouses")
    } catch (error) {
      toast.error("Erreur lors de la création de l'entrepôt")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Configurer un Entrepôt</h1>
          <p className="text-muted-foreground mt-1">
            Définissez les paramètres structurels et environnementaux pour activer le monitoring IoT.
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

            <Card className="border-orange-200 dark:border-orange-900 bg-orange-50/30 dark:bg-orange-950/10">
              <CardHeader>
                <CardTitle className="text-lg">🌡️ Historique environnemental</CardTitle>
                <CardDescription>Fichier CSV des capteurs IoT (température & humidité)</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center w-full">
                  <label htmlFor="dropzone-file" className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer bg-white dark:bg-slate-900 border-orange-300 dark:border-orange-700 hover:bg-orange-50 dark:hover:bg-orange-900/20">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      {file ? (
                        <>
                          <FileText className="w-8 h-8 mb-2 text-orange-500" />
                          <p className="mb-2 text-sm font-semibold text-orange-600">{file.name}</p>
                          <p className="text-xs text-muted-foreground">Fichier sélectionné. Sera importé après l'enregistrement.</p>
                        </>
                      ) : (
                        <>
                          <UploadCloud className="w-8 h-8 mb-2 text-muted-foreground" />
                          <p className="mb-2 text-sm text-muted-foreground"><span className="font-semibold">Cliquez pour téléverser</span> ou glissez-déposez</p>
                          <p className="text-xs text-muted-foreground">CSV uniquement</p>
                        </>
                      )}
                    </div>
                    <input id="dropzone-file" type="file" accept=".csv" className="hidden" onChange={handleFileChange} />
                  </label>
                </div>
                
                <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg text-sm">
                  <h4 className="font-semibold text-yellow-800 dark:text-yellow-500 mb-2">📋 Colonnes du fichier CSV attendues :</h4>
                  <ul className="list-disc pl-5 text-yellow-700 dark:text-yellow-600 space-y-1 text-xs">
                    <li><code className="bg-yellow-100 dark:bg-yellow-900 px-1 rounded">date</code> : Obligatoire (ex: datetime, timestamp)</li>
                    <li><code className="bg-yellow-100 dark:bg-yellow-900 px-1 rounded">temp_1</code> : Obligatoire (température capteur 1)</li>
                    <li><code className="bg-yellow-100 dark:bg-yellow-900 px-1 rounded">hum_1</code> : Obligatoire (humidité capteur 1)</li>
                    <li><code className="bg-yellow-100 dark:bg-yellow-900 px-1 rounded">temp_2</code>, <code className="bg-yellow-100 dark:bg-yellow-900 px-1 rounded">hum_2</code> : Optionnels</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">📦 Capacité & Volume</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Label htmlFor="volume_m3">Volume total (m³)</Label>
                  <Input id="volume_m3" name="volume_m3" type="number" min="0" step="100" placeholder="50000" value={formData.volume_m3} onChange={handleChange} />
                  <p className="text-xs text-muted-foreground mt-1">Calculé sur la base de la zone de stockage utile.</p>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4 flex flex-col gap-3">
                <Button type="submit" className="w-full bg-primary hover:bg-primary/90" disabled={loading}>
                  <Save className="w-4 h-4 mr-2" />
                  {loading ? "Enregistrement..." : "Enregistrer & Activer"}
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
