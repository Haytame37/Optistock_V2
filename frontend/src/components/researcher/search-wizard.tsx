"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { GlassCard } from "@/components/shared/glass-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { LogisticMap } from "@/components/map/logistic-map"
import { searchWarehouses, calculateWeber } from "@/services/researcher.service"
import { toast } from "sonner"
import type { ProductListItem, SearchResultItem, MyWarehouse as WH, ClientPoint, WeberResponse } from "@/types/researcher"
import api from "@/services/api"
import { Loader2, Plus, Trash2, Search, TrendingUp, RefreshCcw, MapPin, MessageSquare, Thermometer, Upload, Star, Store } from "lucide-react"
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
  const router = useRouter()
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
  const [weberResult, setWeberResult] = useState<WeberResponse | null>(null)
  const [calculatingWeber, setCalculatingWeber] = useState(false)

  const whCsvRef = useRef<HTMLInputElement>(null)
  const clientCsvRef = useRef<HTMLInputElement>(null)

  const [whForm, setWhForm] = useState({ nom: "", adresse: "", latitude: 33.57, longitude: -7.59, volume_m3: 5000 })
  const [clientForm, setClientForm] = useState({ name: "", latitude: 33.5731, longitude: -7.5898, demand: 10 })

  // Contact state
  const [contactingWh, setContactingWh] = useState<SearchResultItem | null>(null)
  const [contactMessage, setContactMessage] = useState("")
  const [sendingContact, setSendingContact] = useState(false)

  // CSV parsers
  const handleWarehouseCsv = (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      const lines = text.trim().split("\n")
      const headers = lines[0].split(",").map(h => h.trim().toLowerCase())
      const nomIdx = headers.findIndex(h => ["nom", "name", "entrepot"].includes(h))
      const adrIdx = headers.findIndex(h => ["adresse", "address"].includes(h))
      const latIdx = headers.findIndex(h => h.includes("lat"))
      const lonIdx = headers.findIndex(h => h.includes("lon"))
      if (nomIdx < 0 || latIdx < 0 || lonIdx < 0) {
        toast.error("CSV invalide. Colonnes requises : nom, latitude, longitude")
        return
      }
      const imported: WH[] = []
      lines.slice(1).forEach(line => {
        const cols = line.split(",").map(c => c.trim())
        if (!cols[nomIdx]) return
        imported.push({
          id_entrepot: Math.random().toString(36).slice(2, 8).toUpperCase(),
          nom: cols[nomIdx],
          adresse: adrIdx >= 0 ? cols[adrIdx] : "",
          latitude: parseFloat(cols[latIdx]),
          longitude: parseFloat(cols[lonIdx]),
          volume_m3: 5000,
        })
      })
      setWarehouses(prev => [...prev, ...imported])
      toast.success(`${imported.length} entrepôt(s) importé(s) depuis CSV`)
    }
    reader.readAsText(file)
  }

  const handleClientCsv = (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      const lines = text.trim().split("\n")
      const headers = lines[0].split(",").map(h => h.trim().toLowerCase())
      const nameIdx = headers.findIndex(h => ["nom", "name", "client", "point"].includes(h))
      const latIdx = headers.findIndex(h => h.includes("lat"))
      const lonIdx = headers.findIndex(h => h.includes("lon"))
      const demandIdx = headers.findIndex(h => ["demande", "demand", "volume", "qty", "quantite"].includes(h))
      if (nameIdx < 0 || latIdx < 0 || lonIdx < 0) {
        toast.error("CSV invalide. Colonnes requises : nom/name, latitude, longitude")
        return
      }
      const imported: ClientPoint[] = []
      lines.slice(1).forEach(line => {
        const cols = line.split(",").map(c => c.trim())
        if (!cols[nameIdx]) return
        imported.push({
          name: cols[nameIdx],
          latitude: parseFloat(cols[latIdx]),
          longitude: parseFloat(cols[lonIdx]),
          demand: demandIdx >= 0 ? (parseFloat(cols[demandIdx]) || 10) : 10,
        })
      })
      setClients(prev => [...prev, ...imported])
      toast.success(`${imported.length} client(s) importé(s) depuis CSV`)
    }
    reader.readAsText(file)
  }

  const handleCalculateWeber = async () => {
    if (clients.length < 2) {
      toast.warning("Ajoutez au moins 2 clients pour calculer le Centre de Gravité")
      return
    }
    setCalculatingWeber(true)
    try {
      const result = await calculateWeber(clients)
      setWeberResult(result)
      toast.success("Centre de Gravité calculé avec succès !")
    } catch {
      toast.error("Erreur lors du calcul Weber")
    } finally {
      setCalculatingWeber(false)
    }
  }

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
      } catch (e) { }
    }
  }, [])

  const handleSearch = async () => {
    setSearching(true)
    setWeberResult(null)
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
      // Auto-calculate Weber if clients provided
      if (!quickMode && clients.length >= 2) {
        try {
          const w = await calculateWeber(clients)
          setWeberResult(w)
        } catch { }
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
      toast.success("Demande envoyée au propriétaire ! Redirection vers vos messages...")
      setContactingWh(null)
      setContactMessage("")
      setTimeout(() => {
        router.push("/researcher/messages")
      }, 1500)
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
            <div className="flex items-end">
              <Button
                variant="secondary"
                onClick={() => { setQuickMode(true); handleSearch() }}
                disabled={searching}
                className="w-full h-10 gap-2 border-dashed border-2 hover:border-primary transition-all"
              >
                {searching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                Recherche Rapide (Sans import)
              </Button>
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <Button onClick={() => setStep(2)} className="flex-1 h-12 text-lg font-bold">
              Suivant : Ajouter mes données →
            </Button>
          </div>
        </GlassCard>
      )}

      {/* Step 2: Warehouses */}
      {step === 2 && (
        <GlassCard className="p-6 space-y-6">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <h3 className="font-bold text-xl flex items-center gap-2">
                <Plus className="h-5 w-5 text-primary" /> Vos propres entrepôts
              </h3>
              <p className="text-sm text-muted-foreground">Ajoutez manuellement ou importez un CSV (colonnes : nom, adresse, latitude, longitude).</p>
            </div>
            <div>
              <input ref={whCsvRef} type="file" accept=".csv" className="hidden" onChange={e => { if (e.target.files?.[0]) handleWarehouseCsv(e.target.files[0]); e.target.value = "" }} />
              <Button variant="outline" size="sm" className="gap-2" onClick={() => whCsvRef.current?.click()}>
                <Upload className="h-4 w-4" /> Importer CSV
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-semibold ml-1">Nom de l'entrepôt</label>
              <Input placeholder="Ex: Entrepôt Casablanca Port" value={whForm.nom} onChange={(e) => setWhForm({ ...whForm, nom: e.target.value })} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold ml-1">Adresse complète</label>
              <Input placeholder="Ex: 12 Rue de l'Océan, Casablanca" value={whForm.adresse} onChange={(e) => setWhForm({ ...whForm, adresse: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-semibold ml-1">Latitude</label>
                <Input type="number" placeholder="Ex: 33.573" value={whForm.latitude} onChange={(e) => setWhForm({ ...whForm, latitude: Number(e.target.value) })} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-semibold ml-1">Longitude</label>
                <Input type="number" placeholder="Ex: -7.589" value={whForm.longitude} onChange={(e) => setWhForm({ ...whForm, longitude: Number(e.target.value) })} />
              </div>
            </div>
          </div>

          <Button
            className="w-full md:w-auto px-8"
            onClick={() => {
              if (whForm.nom && whForm.adresse) {
                setWarehouses([...warehouses, { id_entrepot: Math.random().toString(36).slice(2, 8).toUpperCase(), ...whForm }])
                setWhForm({ nom: "", adresse: "", latitude: 33.57, longitude: -7.59, volume_m3: 5000 })
                toast.success("Entrepôt ajouté à la liste d'analyse")
              } else {
                toast.error("Veuillez remplir au moins le nom et l'adresse")
              }
            }}
          >
            <Plus className="h-4 w-4 mr-2" /> Ajouter à ma sélection
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
        <GlassCard className="p-6 space-y-6">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <h3 className="font-bold text-xl flex items-center gap-2">
                <MapPin className="h-5 w-5 text-primary" /> Points de livraison (Clients)
              </h3>
              <p className="text-sm text-muted-foreground">Ajoutez manuellement ou importez un CSV (colonnes : nom/name, latitude, longitude,Demande).</p>
            </div>
            <div>
              <input ref={clientCsvRef} type="file" accept=".csv" className="hidden" onChange={e => { if (e.target.files?.[0]) handleClientCsv(e.target.files[0]); e.target.value = "" }} />
              <Button variant="outline" size="sm" className="gap-2" onClick={() => clientCsvRef.current?.click()}>
                <Upload className="h-4 w-4" /> Importer CSV
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold ml-1">Nom du point</label>
              <Input placeholder="Ex: Client Tanger" value={clientForm.name} onChange={(e) => setClientForm({ ...clientForm, name: e.target.value })} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold ml-1">Latitude</label>
              <Input type="number" placeholder="Ex: 35.759" value={clientForm.latitude} onChange={(e) => setClientForm({ ...clientForm, latitude: Number(e.target.value) })} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold ml-1">Longitude</label>
              <Input type="number" placeholder="Ex: -5.833" value={clientForm.longitude} onChange={(e) => setClientForm({ ...clientForm, longitude: Number(e.target.value) })} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold ml-1">Demande (Unités)</label>
              <Input type="number" placeholder="Ex: 50" value={clientForm.demand} onChange={(e) => setClientForm({ ...clientForm, demand: Number(e.target.value) })} />
            </div>
          </div>

          <Button
            className="w-full md:w-auto px-8"
            onClick={() => {
              if (clientForm.name && clientForm.demand > 0) {
                setClients([...clients, { ...clientForm }])
                setClientForm({ name: "", latitude: 33.5731, longitude: -7.5898, demand: 10 })
                toast.success("Point de livraison ajouté")
              } else {
                toast.error("Veuillez remplir le nom et une demande > 0")
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
                    <p className="text-xs text-muted-foreground">{c.latitude}°N, {c.longitude}°E | Demande: <span className="font-bold text-primary">{c.demand}</span></p>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => setClients(clients.filter((_, j) => j !== i))}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-3">
            <Button variant="outline" onClick={() => setStep(2)} className="h-12 flex-1">← Entrepôts</Button>
            <Button
              onClick={() => { setQuickMode(false); handleSearch() }}
              className="flex-[2] h-12 text-lg font-bold shadow-lg shadow-primary/20"
              disabled={searching}
            >
              {searching ? <Loader2 className="h-5 w-5 animate-spin mr-2" /> : <TrendingUp className="h-5 w-5 mr-2" />}
              Lancer l'Analyse Logistique →
            </Button>
          </div>
        </GlassCard>
      )}

      {/* Step 4: Results */}
      {step === 4 && (
        <div className="space-y-4">
          {results.length > 0 ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {results.map((r, i) => (
                  <GlassCard key={i} className="group p-6 hover:border-primary/50 transition-all flex flex-col relative overflow-hidden bg-background/40">
                    {/* Ranking Badge */}
                    <div className={cn(
                      "absolute top-0 left-0 px-4 py-1.5 text-[10px] font-black uppercase tracking-widest rounded-br-2xl shadow-sm z-10",
                      i === 0 ? "bg-yellow-500 text-white" : "bg-primary/20 text-primary"
                    )}>
                      {i === 0 ? "🥇 Recommandation n°1" : `${i + 1}ème choix`}
                    </div>

                    <div className="mt-4 flex justify-between items-start mb-6">
                      <div className="h-12 w-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Store className="h-6 w-6" />
                      </div>
                    </div>

                    <h4 className="font-bold text-xl mb-1 group-hover:text-primary transition-colors line-clamp-1">{r.nom}</h4>
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-6">
                      <MapPin className="h-3.5 w-3.5 text-primary/60" />
                      <span className="line-clamp-1">{r.adresse}</span>
                    </div>

                    <div className="grid grid-cols-3 gap-3 mb-8">
                      <div className="p-2.5 rounded-xl bg-muted/30 border border-muted-foreground/5 text-center">
                        <span className="text-[9px] uppercase font-bold text-muted-foreground/60 block mb-1">Distance</span>
                        <span className="text-sm font-bold">{r.distance_km?.toFixed(1) ?? "—"} km</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-muted/30 border border-muted-foreground/5 text-center">
                        <span className="text-[9px] uppercase font-bold text-muted-foreground/60 block mb-1">Temp.</span>
                        <span className="text-sm font-bold">{r.avg_temp}°C</span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-muted/30 border border-muted-foreground/5 text-center">
                        <span className="text-[9px] uppercase font-bold text-muted-foreground/60 block mb-1">Hum.</span>
                        <span className="text-sm font-bold">{r.avg_hum}%</span>
                      </div>
                    </div>

                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button
                          className="w-full mt-auto rounded-full gap-2 shadow-lg shadow-primary/10 group/btn"
                          onClick={() => {
                            setContactingWh(r)
                            setContactMessage(`Bonjour, je suis intéressé par votre entrepôt "${r.nom}" pour stocker mon produit "${product}".`)
                          }}
                        >
                          <MessageSquare className="h-4 w-4" />
                          Contacter le propriétaire
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent className="bg-background/95 backdrop-blur-2xl border-primary/20 z-[100]">
                        <AlertDialogHeader>
                          <AlertDialogTitle className="flex items-center gap-2">
                            <MessageSquare className="h-5 w-5 text-primary" /> Contacter le propriétaire
                          </AlertDialogTitle>
                          <AlertDialogDescription>
                            Envoyez un premier message pour entamer la discussion sur la location de l'entrepôt <strong>{r.nom}</strong>.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <div className="py-4 space-y-4">
                          <div className="space-y-2">
                            <label className="text-sm font-semibold ml-1">Votre message</label>
                            <Textarea
                              rows={4}
                              className="rounded-2xl"
                              value={contactMessage}
                              onChange={e => setContactMessage(e.target.value)}
                              placeholder="Ex: Bonjour, j'aimerais en savoir plus sur les tarifs..."
                            />
                          </div>
                        </div>
                        <AlertDialogFooter className="gap-2">
                          <AlertDialogCancel className="rounded-full" onClick={() => setContactingWh(null)}>Annuler</AlertDialogCancel>
                          <AlertDialogAction
                            className="rounded-full px-8"
                            onClick={handleContact}
                            disabled={sendingContact || !contactMessage.trim()}
                          >
                            {sendingContact ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                            Envoyer la demande
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </GlassCard>
                ))}
              </div>

              <LogisticMap
                results={results.map((r) => ({ name: r.nom, lat: r.latitude, lng: r.longitude, type: "result" as const }))}
                warehouses={warehouses.map((w) => ({ name: w.nom, lat: w.latitude, lng: w.longitude, type: "warehouse" as const }))}
                clients={clients.map((c) => ({ name: c.name, lat: c.latitude, lng: c.longitude, type: "client" as const }))}
                weberPoint={weberResult ? { lat: weberResult.lat_opt, lng: weberResult.lon_opt } : undefined}
              />

              <div className="pt-6 flex justify-center">
                <Button
                  variant="outline"
                  size="lg"
                  onClick={() => setStep(1)}
                  className="gap-2 border-primary/20 hover:bg-primary/5"
                >
                  <RefreshCcw className="h-4 w-4" /> Relancer une nouvelle recherche
                </Button>
              </div>
            </>
          ) : (
            <GlassCard className="p-8 text-center text-muted-foreground flex flex-col items-center gap-4">
              <p>Aucun résultat. Essayez d'ajuster vos critères ou de changer de produit.</p>
              <Button onClick={() => setStep(1)} variant="default">Modifier les paramètres</Button>
            </GlassCard>
          )}
        </div>
      )}
    </div>
  )
}
