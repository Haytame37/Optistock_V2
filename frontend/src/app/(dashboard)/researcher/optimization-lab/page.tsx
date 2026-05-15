"use client"

import { useEffect, useState, useRef } from "react"
import { GlassCard } from "@/components/shared/glass-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { toast } from "sonner"
import { 
  Zap, 
  MapPin, 
  Building2, 
  Package, 
  Plus, 
  Trash2, 
  Loader2, 
  ChevronRight,
  Upload
} from "lucide-react"
import dynamic from "next/dynamic"
import api from "@/services/api"

// Dynamic import for Map to avoid SSR issues
const LogisticMap = dynamic(() => import("@/components/map/logistic-map").then(m => m.LogisticMap), { 
  ssr: false,
  loading: () => <div className="h-[400px] w-full bg-slate-100 animate-pulse rounded-xl flex items-center justify-center">Chargement de la carte...</div>
})

const DEFAULT_EXISTING = [
  { name: "Entrepôt Casablanca", lat: 33.5731, lon: -7.5898, capacity: 500 },
  { name: "Entrepôt Marrakech", lat: 31.6295, lon: -7.9811, capacity: 400 },
]

const DEFAULT_CANDIDATES = [
  { name: "Site Candidat Beni Mellal", lat: 32.3373, lon: -6.3498, capacity: 300 },
  { name: "Site Candidat Khouribga", lat: 32.8810, lon: -6.9063, capacity: 300 },
  { name: "Site Candidat Fquih Ben Salah", lat: 32.5028, lon: -6.6911, capacity: 300 },
]

const DEFAULT_CLIENTS = [
  { name: "Client Azilal", lat: 31.9667, lon: -6.5667, demand: 80 },
  { name: "Client Demnate", lat: 31.7333, lon: -7.0333, demand: 60 },
  { name: "Client Kasba Tadla", lat: 32.5972, lon: -6.2694, demand: 120 },
]

type Site = { name: string; lat: number; lon: number; capacity: number }
type Client = { name: string; lat: number; lon: number; demand: number }

function SiteRow({ site, onRemove }: { site: Site; onRemove: () => void }) {
  return (
    <div className="flex items-center gap-2 p-2 rounded-lg border text-sm">
      <Building2 className="h-4 w-4 text-muted-foreground shrink-0" />
      <span className="flex-1 font-medium truncate">{site.name}</span>
      <span className="text-xs text-muted-foreground">{site.lat.toFixed(3)}, {site.lon.toFixed(3)}</span>
      <Button variant="ghost" size="icon" className="h-6 w-6" onClick={onRemove}><Trash2 className="h-3 w-3" /></Button>
    </div>
  )
}

function ClientRow({ client, onRemove }: { client: Client; onRemove: () => void }) {
  return (
    <div className="flex items-center gap-2 p-2 rounded-lg border text-sm">
      <MapPin className="h-4 w-4 text-muted-foreground shrink-0" />
      <span className="flex-1 font-medium truncate">{client.name}</span>
      <Badge variant="outline" className="text-xs shrink-0">Dem: {client.demand}</Badge>
      <Button variant="ghost" size="icon" className="h-6 w-6" onClick={onRemove}><Trash2 className="h-3 w-3" /></Button>
    </div>
  )
}

export default function OptimizationLabPage() {
  const [existing, setExisting] = useState<Site[]>(DEFAULT_EXISTING)
  const [candidates, setCandidates] = useState<Site[]>(DEFAULT_CANDIDATES)
  const [clients, setClients] = useState<Client[]>(DEFAULT_CLIENTS)
  const [nToAdd, setNToAdd] = useState(1)
  const [running, setRunning] = useState(false)
  const [results, setResults] = useState<any>(null)

  // New item forms
  const [newEx, setNewEx] = useState({ name: "", lat: 32.5, lon: -6.5, capacity: 300 })
  const [newCa, setNewCa] = useState({ name: "", lat: 32.5, lon: -6.5, capacity: 300 })
  const [newCl, setNewCl] = useState({ name: "", lat: 32.5, lon: -6.5, demand: 80 })

  const clientCsvRef = useRef<HTMLInputElement>(null)

  const handleClientCsv = (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const lines = (e.target?.result as string).trim().split("\n")
      const headers = lines[0].split(",").map(h => h.trim().toLowerCase())
      const nameIdx = headers.findIndex(h => ["nom","name","client"].includes(h))
      const latIdx  = headers.findIndex(h => h.includes("lat"))
      const lonIdx  = headers.findIndex(h => h.includes("lon"))
      const demIdx  = headers.findIndex(h => ["demande","demand","volume","qty","quantite"].includes(h))
      
      if (nameIdx < 0 || latIdx < 0 || lonIdx < 0) { 
        toast.error("CSV invalide. Colonnes requises : nom, latitude, longitude")
        return 
      }
      
      const imported: Client[] = lines.slice(1).map(l => {
        const c = l.split(",").map(v => v.trim())
        return { 
          name: c[nameIdx], 
          lat: parseFloat(c[latIdx]), 
          lon: parseFloat(c[lonIdx]), 
          demand: demIdx >= 0 ? (parseInt(c[demIdx]) || 10) : 10 
        }
      }).filter(c => c.name && !isNaN(c.lat))
      
      setClients(prev => [...prev, ...imported])
      toast.success(`${imported.length} clients importés avec succès`)
    }
    reader.readAsText(file)
  }

  const run = async () => {
    if (candidates.length === 0 || clients.length === 0) {
      toast.error("Ajoutez au moins 1 candidat et 1 client")
      return
    }
    setRunning(true)
    setResults(null)
    try {
      const { data } = await api.post("/researcher/optimization-lab", {
        existing: existing.map(s => ({ name: s.name, lat: s.lat, lon: s.lon, capacity: s.capacity })),
        candidates: candidates.map(s => ({ name: s.name, lat: s.lat, lon: s.lon, capacity: s.capacity })),
        clients: clients.map(c => ({ name: c.name, lat: c.lat, lon: c.lon, demand: c.demand })),
        n_to_add: nToAdd,
      })
      setResults(data)
      toast.success("Analyse terminée !")
    } catch {
      toast.error("Erreur lors de l'analyse")
    } finally {
      setRunning(false)
    }
  }

  // Build map points from results
  const mapResults = results
    ? candidates
        .filter((_: Site, i: number) => results.site_result?.selected_candidate_indices?.includes(i))
        .map((s: Site) => ({ name: s.name, lat: s.lat, lng: s.lon, type: "result" as const }))
    : []
  const mapWarehouses = existing.map(s => ({ name: s.name, lat: s.lat, lng: s.lon, type: "warehouse" as const }))
  const mapClients = clients.map(c => ({ name: c.name, lat: c.lat, lng: c.lon, type: "client" as const }))

  const selectedNames: string[] = results?.site_result?.selected_candidate_names ?? []
  const vrpOrder: number[] = results?.vrp_result?.delivery_order ?? []
  const vrpLabels: string[] = results?.vrp_result?.route_labels ?? []

  return (
    <div className="space-y-8 p-6">
      {/* Header */}
      <div className="space-y-1">
        <div className="flex items-center gap-2 text-xs font-bold text-primary uppercase tracking-widest">
          <Zap className="h-4 w-4" /> Optimization Lab
        </div>
        <h1 className="text-3xl font-black tracking-tight">Planification de Réseau & Économies de Transport</h1>
        <p className="text-muted-foreground max-w-2xl">
          Simulez l'implantation de vos futurs entrepôts et optimisez vos trajets de livraison. Cet outil utilise des algorithmes de pointe pour identifier les sites les plus rentables et organiser vos tournées, vous permettant de réduire drastiquement vos coûts de carburant et vos temps de trajet.
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* ── Configuration Panel ── */}
        <div className="xl:col-span-1 space-y-4">

          {/* Existing Warehouses */}
          <GlassCard className="p-5 space-y-3">
            <h3 className="font-bold flex items-center gap-2 text-sm uppercase tracking-wider">
              <Building2 className="h-4 w-4 text-blue-500" /> Entrepôts Existants
            </h3>
            <div className="space-y-1 max-h-40 overflow-y-auto">
              {existing.map((s, i) => <SiteRow key={i} site={s} onRemove={() => setExisting(existing.filter((_, j) => j !== i))} />)}
            </div>
            <div className="grid grid-cols-4 gap-1">
              <Input placeholder="Nom" className="col-span-2 h-8 text-xs" value={newEx.name} onChange={e => setNewEx({...newEx, name: e.target.value})} />
              <Input type="number" placeholder="Lat" className="h-8 text-xs" value={newEx.lat} onChange={e => setNewEx({...newEx, lat: +e.target.value})} />
              <Input type="number" placeholder="Lon" className="h-8 text-xs" value={newEx.lon} onChange={e => setNewEx({...newEx, lon: +e.target.value})} />
            </div>
            <Button size="sm" variant="outline" className="w-full gap-1 h-8" onClick={() => { if (newEx.name) { setExisting([...existing, newEx]); setNewEx({name:"",lat:32.5,lon:-6.5,capacity:300}) } }}>
              <Plus className="h-3 w-3" /> Ajouter
            </Button>
          </GlassCard>

          {/* Candidates */}
          <GlassCard className="p-5 space-y-3">
            <h3 className="font-bold flex items-center gap-2 text-sm uppercase tracking-wider">
              <MapPin className="h-4 w-4 text-orange-500" /> Sites Candidats
            </h3>
            <div className="space-y-1 max-h-40 overflow-y-auto">
              {candidates.map((s, i) => <SiteRow key={i} site={s} onRemove={() => setCandidates(candidates.filter((_, j) => j !== i))} />)}
            </div>
            <div className="grid grid-cols-4 gap-1">
              <Input placeholder="Nom" className="col-span-2 h-8 text-xs" value={newCa.name} onChange={e => setNewCa({...newCa, name: e.target.value})} />
              <Input type="number" placeholder="Lat" className="h-8 text-xs" value={newCa.lat} onChange={e => setNewCa({...newCa, lat: +e.target.value})} />
              <Input type="number" placeholder="Lon" className="h-8 text-xs" value={newCa.lon} onChange={e => setNewCa({...newCa, lon: +e.target.value})} />
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" className="flex-1 gap-1 h-8" onClick={() => { if (newCa.name) { setCandidates([...candidates, newCa]); setNewCa({name:"",lat:32.5,lon:-6.5,capacity:300}) } }}>
                <Plus className="h-3 w-3" /> Ajouter
              </Button>
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs font-medium">Entrepôts à ouvrir :</span>
              <Input type="number" min={1} max={candidates.length} value={nToAdd} onChange={e => setNToAdd(+e.target.value)} className="h-7 w-16 text-xs" />
            </div>
          </GlassCard>

          {/* Clients */}
          <GlassCard className="p-5 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold flex items-center gap-2 text-sm uppercase tracking-wider">
                <Package className="h-4 w-4 text-red-500" /> Clients à Livrer
              </h3>
              <div>
                <input ref={clientCsvRef} type="file" accept=".csv" className="hidden" onChange={e => { if (e.target.files?.[0]) handleClientCsv(e.target.files[0]); e.target.value="" }} />
                <Button size="sm" variant="ghost" className="h-7 gap-1 text-xs" onClick={() => clientCsvRef.current?.click()}>
                  <Upload className="h-3 w-3" /> CSV
                </Button>
              </div>
            </div>
            <div className="space-y-1 max-h-44 overflow-y-auto">
              {clients.map((c, i) => <ClientRow key={i} client={c} onRemove={() => setClients(clients.filter((_, j) => j !== i))} />)}
            </div>
            <div className="grid grid-cols-5 gap-1">
              <Input placeholder="Nom" className="col-span-2 h-8 text-xs" value={newCl.name} onChange={e => setNewCl({...newCl, name: e.target.value})} />
              <Input type="number" placeholder="Lat" className="h-8 text-xs" value={newCl.lat} onChange={e => setNewCl({...newCl, lat: +e.target.value})} />
              <Input type="number" placeholder="Lon" className="h-8 text-xs" value={newCl.lon} onChange={e => setNewCl({...newCl, lon: +e.target.value})} />
              <Input type="number" placeholder="Demande" title="Volume de demande" className="h-8 text-xs" value={newCl.demand} onChange={e => setNewCl({...newCl, demand: +e.target.value})} />
            </div>
            <Button size="sm" variant="outline" className="w-full gap-1 h-8" onClick={() => { if (newCl.name) { setClients([...clients, newCl]); setNewCl({name:"",lat:32.5,lon:-6.5,demand:80}) } }}>
              <Plus className="h-3 w-3" /> Ajouter
            </Button>
          </GlassCard>

          {/* Run Button */}
          <Button className="w-full h-14 text-lg font-black gap-3 shadow-xl" onClick={run} disabled={running}>
            {running ? <Loader2 className="h-6 w-6 animate-spin" /> : <Zap className="h-6 w-6" />}
            {running ? "Analyse en cours…" : "LANCER L'ANALYSE MIP + VRP"}
          </Button>
        </div>

        {/* ── Results Panel ── */}
        <div className="xl:col-span-2 space-y-6">
          {/* Map Preview (always visible) */}
          <GlassCard className="p-4">
            <h3 className="font-bold mb-3 text-sm uppercase tracking-wider flex items-center gap-2">
              <MapPin className="h-4 w-4 text-primary" /> Carte du Scénario
            </h3>
            <LogisticMap
              results={mapResults}
              warehouses={mapWarehouses}
              clients={mapClients}
            />
          </GlassCard>

          {/* Results */}
          {results && (
            <>
              {/* KPIs */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <GlassCard className="p-4 text-center">
                  <p className="text-[10px] font-bold uppercase text-muted-foreground mb-1">Site Sélectionné</p>
                  <p className="font-black text-primary text-sm truncate">{selectedNames.join(", ") || "—"}</p>
                </GlassCard>
                <GlassCard className="p-4 text-center">
                  <p className="text-[10px] font-bold uppercase text-muted-foreground mb-1">Coût Total</p>
                  <p className="font-black text-lg">{results.site_result?.objective_value?.toFixed(0) ?? "—"} <span className="text-xs font-normal">min</span></p>
                </GlassCard>
                <GlassCard className="p-4 text-center">
                  <p className="text-[10px] font-bold uppercase text-muted-foreground mb-1">Économie</p>
                  <p className="font-black text-green-500 text-lg">{results.site_result?.savings_vs_random?.toFixed(1) ?? "0"}%</p>
                </GlassCard>
                <GlassCard className="p-4 text-center">
                  <p className="text-[10px] font-bold uppercase text-muted-foreground mb-1">Distance VRP</p>
                  <p className="font-black text-lg">{results.vrp_result?.total_distance?.toFixed(1) ?? "—"} <span className="text-xs font-normal">km</span></p>
                </GlassCard>
              </div>

              {/* Solver badges */}
              <div className="flex gap-2 flex-wrap">
                <Badge className="bg-blue-500/10 text-blue-700 dark:text-blue-300 border border-blue-500/20 font-bold">
                  🧮 MIP: {results.site_result?.solver ?? "—"}
                </Badge>
                <Badge className="bg-purple-500/10 text-purple-700 dark:text-purple-300 border border-purple-500/20 font-bold">
                  🚚 VRP: {results.vrp_result?.solver ?? "—"}
                </Badge>
                <Badge className="bg-slate-500/10 text-muted-foreground border font-bold">
                  📍 Distances: Haversine (×1.3)
                </Badge>
              </div>

              {/* VRP Route */}
              <GlassCard className="p-5">
                <h4 className="font-bold mb-4 flex items-center gap-2">
                  <Package className="h-4 w-4 text-primary" /> Ordre Optimal de Livraison
                </h4>
                <div className="space-y-2">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                    <div className="h-7 w-7 rounded-full bg-green-500 text-white flex items-center justify-center text-xs font-black">🏭</div>
                    <div>
                      <p className="font-bold text-sm">{results.depot?.name}</p>
                      <p className="text-[10px] text-muted-foreground">Dépôt de départ</p>
                    </div>
                  </div>
                  {vrpOrder.map((clientIdx, step) => (
                    <div key={step} className="flex items-center gap-3 p-3 rounded-lg border">
                      <div className="h-7 w-7 rounded-full bg-primary text-white flex items-center justify-center text-xs font-black shrink-0">{step + 1}</div>
                      <div className="flex-1">
                        <p className="font-bold text-sm">{vrpLabels[step] ?? `Client ${clientIdx + 1}`}</p>
                        <p className="text-[10px] text-muted-foreground">
                          Demande: {clients[clientIdx]?.demand ?? "—"} unités
                        </p>
                      </div>
                      {step < vrpOrder.length - 1 && <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0" />}
                    </div>
                  ))}
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                    <div className="h-7 w-7 rounded-full bg-green-500 text-white flex items-center justify-center text-xs font-black">🏭</div>
                    <div>
                      <p className="font-bold text-sm">{results.depot?.name}</p>
                      <p className="text-[10px] text-muted-foreground">Retour au dépôt</p>
                    </div>
                  </div>
                </div>
              </GlassCard>
            </>
          )}

          {!results && !running && (
            <GlassCard className="p-10 flex flex-col items-center text-center gap-4 text-muted-foreground">
              <Zap className="h-12 w-12 opacity-20" />
              <div>
                <p className="font-bold text-lg">Prêt à analyser</p>
                <p className="text-sm">Configurez votre scénario et lancez l'analyse.</p>
              </div>
            </GlassCard>
          )}
        </div>
      </div>
    </div>
  )
}
