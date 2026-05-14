"use client"

import { useState, useEffect } from "react"
import { GlassCard } from "@/components/shared/glass-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { LogisticMap } from "@/components/map/logistic-map"
import { searchWarehouses } from "@/services/researcher.service"
import { toast } from "sonner"
import type { ProductListItem, SearchResultItem, MyWarehouse as WH, ClientPoint } from "@/types/researcher"
import api from "@/services/api"
import { Loader2, Plus, Trash2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { contactOwner } from "@/services/messaging.service"
import { 
  AlertDialog, 
  AlertDialogAction, 
  AlertDialogCancel, 
  AlertDialogContent, 
  AlertDialogDescription, 
  AlertDialogFooter, 
  AlertDialogHeader, 
  AlertDialogTitle, 
  AlertDialogTrigger 
} from "@/components/ui/alert-dialog"
import { Textarea } from "@/components/ui/textarea"

const steps = ["Produit", "Entrepôts", "Clients", "Résultats"]

export function SearchWizard() {
  const [step, setStep] = useState(1)
  const [products, setProducts] = useState<ProductListItem[]>([])
  const [product, setProduct] = useState("")
  const [volume, setVolume] = useState(0)
  const [duration, setDuration] = useState(7)
  const [warehouses, setWarehouses] = useState<WH[]>([])
  const [clients, setClients] = useState<ClientPoint[]>([])
  const [results, setResults] = useState<SearchResultItem[]>([])
  const [loading, setLoading] = useState(false)
  const [searching, setSearching] = useState(false)
  const [quickMode, setQuickMode] = useState(false)
  const [costWeight, setCostWeight] = useState(0.5)
  const [distWeight, setDistWeight] = useState(0.5)

  const [whForm, setWhForm] = useState({ nom: "", adresse: "", latitude: 33.57, longitude: -7.59, volume_m3: 5000 })
  const [clientForm, setClientForm] = useState({ name: "", latitude: 33.5731, longitude: -7.5898 })
  
  // Contact state
  const [contactingWh, setContactingWh] = useState<SearchResultItem | null>(null)
  const [contactMessage, setContactMessage] = useState("")
  const [sendingContact, setSendingContact] = useState(false)

  useEffect(() => {
    // Load products
    api.get("/products").then(({ data }) => {
      setProducts(data)
      // Only set default if not loading from history
      const saved = localStorage.getItem("last_search")
      if (!saved && data.length > 0) setProduct(data[0].name)
    }).catch(() => toast.error("Erreur chargement produits"))

    // Check for history reload
    const saved = localStorage.getItem("last_search")
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        setProduct(parsed.product)
        setVolume(parsed.volume)
        setDuration(parsed.duration_days)
        if (parsed.cost_weight !== undefined) setCostWeight(parsed.cost_weight)
        if (parsed.dist_weight !== undefined) setDistWeight(parsed.dist_weight)
        localStorage.removeItem("last_search")
        toast.info("Recherche chargée depuis l'historique")
      } catch (e) {}
    }
  }, [])

  const handleSearch = async () => {
    setSearching(true)
    try {
      const res = await searchWarehouses({
        product,
        volume,
        duration_days: duration,
        cost_weight: costWeight,
        dist_weight: distWeight,
        warehouses: quickMode ? [] : warehouses,
        clients: quickMode ? [] : clients,
        quick_search: quickMode,
      })
      setResults(res.results)
      setStep(4)
      if (res.results.length > 0) {
        toast.success(`${res.results.length} entrepôt(s) trouvé(s)`)
      } else {
        toast.warning("Aucun entrepôt conforme trouvé")
      }
    } catch {
      toast.error("Erreur lors de l'analyse")
    } finally {
      setSearching(false)
    }
  }

  const handleContact = async () => {
    if (!contactingWh || !contactMessage.trim()) return
    setSendingContact(true)
    try {
      await contactOwner(
        contactingWh.id,
        contactingWh.owner_id || 0,
        product,
        contactMessage
      )
      toast.success("Demande envoyée au propriétaire !")
      setContactingWh(null)
      setContactMessage("")
    } catch (error) {
      toast.error("Erreur lors de l'envoi du message")
    } finally {
      setSendingContact(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Step indicator */}
      <div className="flex gap-2">
        {steps.map((label, i) => (
          <Button
            key={i}
            variant={step === i + 1 ? "default" : "outline"}
            size="sm"
            className="flex-1"
            onClick={() => setStep(i + 1)}
          >
            {String(i + 1).padStart(2, "0")} {label}
          </Button>
        ))}
      </div>

      {/* Step 1: Product */}
      {step === 1 && (
        <GlassCard className="p-6 space-y-4">
          <h3 className="font-semibold text-lg">Paramètres produit</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Produit</label>
              <Select value={product} onValueChange={setProduct}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {products.map((p) => (
                    <SelectItem key={p.name} value={p.name}>{p.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Volume total (m³)</label>
              <Input type="number" min={0} step={0.1} value={volume} onChange={(e) => setVolume(Number(e.target.value))} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Durée de stockage (jours)</label>
              <Input type="number" min={1} max={365} value={duration} onChange={(e) => setDuration(Number(e.target.value))} />
            </div>
            <div className="space-y-2">
               <label className="text-sm font-medium">Priorité : Coût vs Proximité</label>
               <div className="flex items-center gap-2 mt-2">
                  <span className="text-xs text-muted-foreground">Économie</span>
                  <Input 
                    type="range" 
                    min="0" max="1" step="0.1" 
                    value={costWeight} 
                    onChange={(e) => {
                      const val = Number(e.target.value);
                      setCostWeight(val);
                      setDistWeight(Number((1 - val).toFixed(1)));
                    }} 
                    className="h-4 accent-primary"
                  />
                  <span className="text-xs text-muted-foreground">Rapidité</span>
               </div>
               <p className="text-[10px] text-center text-muted-foreground italic">
                 {costWeight * 100}% Coût | {distWeight * 100}% Distance
               </p>
            </div>
          </div>
          <div className="flex gap-3">
            <Button onClick={() => setStep(2)} className="flex-1">Suivant — Entrepôts</Button>
            <Button variant="secondary" onClick={() => { setQuickMode(true); handleSearch() }} disabled={searching}>
              {searching ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              Recherche rapide
            </Button>
          </div>
        </GlassCard>
      )}

      {/* Step 2: Warehouses */}
      {step === 2 && (
        <GlassCard className="p-6 space-y-4">
          <h3 className="font-semibold text-lg">Ajouter un entrepôt</h3>
          <div className="grid grid-cols-2 gap-3">
            <Input placeholder="Nom" value={whForm.nom} onChange={(e) => setWhForm({ ...whForm, nom: e.target.value })} />
            <Input placeholder="Adresse" value={whForm.adresse} onChange={(e) => setWhForm({ ...whForm, adresse: e.target.value })} />
            <Input type="number" placeholder="Latitude" value={whForm.latitude} onChange={(e) => setWhForm({ ...whForm, latitude: Number(e.target.value) })} />
            <Input type="number" placeholder="Longitude" value={whForm.longitude} onChange={(e) => setWhForm({ ...whForm, longitude: Number(e.target.value) })} />
            <Input type="number" placeholder="Volume m³" value={whForm.volume_m3} onChange={(e) => setWhForm({ ...whForm, volume_m3: Number(e.target.value) })} />
          </div>
          <Button
            onClick={() => {
              if (whForm.nom && whForm.adresse) {
                setWarehouses([...warehouses, { id_entrepot: Math.random().toString(36).slice(2, 8).toUpperCase(), ...whForm }])
                setWhForm({ nom: "", adresse: "", latitude: 33.57, longitude: -7.59, volume_m3: 5000 })
              }
            }}
          >
            <Plus className="h-4 w-4 mr-2" /> Ajouter
          </Button>

          {warehouses.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium">Mes entrepôts ({warehouses.length})</p>
              {warehouses.map((wh, i) => (
                <div key={i} className="flex items-center justify-between rounded-xl border p-3">
                  <div>
                    <p className="font-medium">{wh.nom}</p>
                    <p className="text-xs text-muted-foreground">{wh.adresse} · {wh.volume_m3} m³</p>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => setWarehouses(warehouses.filter((_, j) => j !== i))}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-3">
            <Button variant="outline" onClick={() => setStep(1)} className="flex-1">← Produit</Button>
            <Button onClick={() => setStep(3)} className="flex-1">Clients →</Button>
            <Button variant="ghost" onClick={() => { setQuickMode(false); handleSearch() }}>Passer aux résultats</Button>
          </div>
        </GlassCard>
      )}

      {/* Step 3: Clients */}
      {step === 3 && (
        <GlassCard className="p-6 space-y-4">
          <h3 className="font-semibold text-lg">Ajouter un client / point de livraison</h3>
          <div className="grid grid-cols-3 gap-3">
            <Input placeholder="Nom" value={clientForm.name} onChange={(e) => setClientForm({ ...clientForm, name: e.target.value })} />
            <Input type="number" placeholder="Latitude" value={clientForm.latitude} onChange={(e) => setClientForm({ ...clientForm, latitude: Number(e.target.value) })} />
            <Input type="number" placeholder="Longitude" value={clientForm.longitude} onChange={(e) => setClientForm({ ...clientForm, longitude: Number(e.target.value) })} />
          </div>
          <Button
            onClick={() => {
              if (clientForm.name) {
                setClients([...clients, { ...clientForm }])
                setClientForm({ name: "", latitude: 33.5731, longitude: -7.5898 })
              }
            }}
          >
            <Plus className="h-4 w-4 mr-2" /> Ajouter client
          </Button>

          {clients.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium">Mes clients ({clients.length})</p>
              {clients.map((c, i) => (
                <div key={i} className="flex items-center justify-between rounded-xl border p-3">
                  <div>
                    <p className="font-medium">{c.name}</p>
                    <p className="text-xs text-muted-foreground">{c.latitude}°N, {c.longitude}°E</p>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => setClients(clients.filter((_, j) => j !== i))}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-3">
            <Button variant="outline" onClick={() => setStep(2)} className="flex-1">← Entrepôts</Button>
            <Button onClick={() => { setQuickMode(false); handleSearch() }} className="flex-1" disabled={searching}>
              {searching ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Analyser →
            </Button>
          </div>
        </GlassCard>
      )}

      {/* Step 4: Results */}
      {step === 4 && (
        <div className="space-y-4">
          {results.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-muted-foreground">
                      <th className="pb-3 font-medium">Nom</th>
                      <th className="pb-3 font-medium">Score</th>
                      <th className="pb-3 font-medium">Distance</th>
                      <th className="pb-3 font-medium">Température</th>
                      <th className="pb-3 font-medium">Humidité</th>
                      <th className="pb-3 font-medium text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((r, i) => (
                      <tr key={i} className="border-b last:border-0 hover:bg-muted/50 transition-colors">
                        <td className="py-3 font-medium">{r.nom}</td>
                        <td className="py-3">
                          <Badge className={cn(
                            "font-bold",
                            r.score_logistique >= 70 ? "bg-green-100 text-green-700 hover:bg-green-100" : 
                            r.score_logistique >= 40 ? "bg-yellow-100 text-yellow-700 hover:bg-yellow-100" : 
                            "bg-red-100 text-red-700 hover:bg-red-100"
                          )}>
                            {r.score_logistique.toFixed(1)}%
                          </Badge>
                        </td>
                        <td className="py-3">{r.distance_km?.toFixed(1) ?? "—"} km</td>
                        <td className="py-3">{r.avg_temp}°C</td>
                        <td className="py-3">{r.avg_hum}%</td>
                        <td className="py-3 text-right">
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button variant="outline" size="sm" onClick={() => {
                                setContactingWh(r)
                                setContactMessage(`Bonjour, je suis intéressé par votre entrepôt "${r.nom}" pour stocker mon produit "${product}".`)
                              }}>
                                Contacter
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Contacter le propriétaire</AlertDialogTitle>
                                <AlertDialogDescription>
                                  Envoyez un premier message pour entamer la discussion sur la location de l'entrepôt <strong>{r.nom}</strong>.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <div className="py-4 space-y-4">
                                <div className="space-y-2">
                                  <label className="text-sm font-medium">Votre message</label>
                                  <Textarea 
                                    rows={4} 
                                    value={contactMessage} 
                                    onChange={e => setContactMessage(e.target.value)}
                                    placeholder="Ex: Bonjour, j'aimerais en savoir plus sur les tarifs..."
                                  />
                                </div>
                              </div>
                              <AlertDialogFooter>
                                <AlertDialogCancel onClick={() => setContactingWh(null)}>Annuler</AlertDialogCancel>
                                <AlertDialogAction 
                                  onClick={handleContact}
                                  disabled={sendingContact || !contactMessage.trim()}
                                >
                                  {sendingContact ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                                  Envoyer la demande
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <LogisticMap
                results={results.map((r) => ({ name: r.nom, lat: r.latitude, lng: r.longitude, type: "result" as const }))}
                warehouses={warehouses.map((w) => ({ name: w.nom, lat: w.latitude, lng: w.longitude, type: "warehouse" as const }))}
                clients={clients.map((c) => ({ name: c.name, lat: c.latitude, lng: c.longitude, type: "client" as const }))}
              />
            </>
          ) : (
            <GlassCard className="p-8 text-center text-muted-foreground">
              Aucun résultat. Lancez une nouvelle recherche.
            </GlassCard>
          )}
        </div>
      )}
    </div>
  )
}
