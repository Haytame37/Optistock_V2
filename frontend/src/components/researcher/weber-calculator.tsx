"use client"

import { useState } from "react"
import { GlassCard } from "@/components/shared/glass-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { KpiCard } from "@/components/shared/kpi-card"
import { LogisticMap } from "@/components/map/logistic-map"
import { calculateWeber } from "@/services/researcher.service"
import { toast } from "sonner"
import { Plus, Trash2, Loader2 } from "lucide-react"
import type { ClientPoint, WeberResponse } from "@/types/researcher"

export function WeberCalculator() {
  const [clients, setClients] = useState<ClientPoint[]>([])
  const [form, setForm] = useState({ name: "", latitude: 33.5731, longitude: -7.5898 })
  const [result, setResult] = useState<WeberResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const handleCalculate = async () => {
    if (clients.length < 2) {
      toast.warning("Ajoutez au moins 2 clients")
      return
    }
    setLoading(true)
    try {
      const res = await calculateWeber(clients)
      setResult(res)
      toast.success("Point optimal calculé")
    } catch {
      toast.error("Erreur de calcul")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <GlassCard className="p-6 space-y-4">
        <h3 className="font-semibold text-lg">Points de livraison (Clients)</h3>
        <div className="grid grid-cols-3 gap-3">
          <Input placeholder="Nom" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <Input type="number" placeholder="Latitude" value={form.latitude} onChange={(e) => setForm({ ...form, latitude: Number(e.target.value) })} />
          <Input type="number" placeholder="Longitude" value={form.longitude} onChange={(e) => setForm({ ...form, longitude: Number(e.target.value) })} />
        </div>
        <Button onClick={() => { if (form.name) { setClients([...clients, { ...form, demand: 1 }]); setForm({ name: "", latitude: 33.5731, longitude: -7.5898 }) } }}>
          <Plus className="h-4 w-4 mr-2" /> Ajouter
        </Button>

        {clients.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium">Clients ({clients.length})</p>
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

        {clients.length >= 2 && (
          <Button onClick={handleCalculate} disabled={loading} className="w-full" size="lg">
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
            Calculer le point optimal d'implantation
          </Button>
        )}
      </GlassCard>

      {result && (
        <>
          <div className="grid grid-cols-3 gap-4">
            <KpiCard label="Latitude optimale" value={result.lat_opt.toFixed(4)} />
            <KpiCard label="Longitude optimale" value={result.lon_opt.toFixed(4)} />
            <KpiCard label="Distance moyenne" value={`${result.avg_distance_km.toFixed(2)} km`} />
          </div>

          <LogisticMap
            results={[{ name: "Point optimal", lat: result.lat_opt, lng: result.lon_opt, type: "result" as const }]}
            warehouses={[]}
            clients={clients.map((c) => ({ name: c.name, lat: c.latitude, lng: c.longitude, type: "client" as const }))}
            lines={clients.map((c) => ({
              from: { lat: c.latitude, lng: c.longitude },
              to: { lat: result.lat_opt, lng: result.lon_opt },
            }))}
          />
        </>
      )}
    </div>
  )
}
