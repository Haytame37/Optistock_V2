"use client"

import { useEffect, useState, useRef, useCallback } from "react"
import { useParams } from "next/navigation"
import { GlassCard } from "@/components/shared/glass-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { getIoTReadings } from "@/services/iot.service"
import api from "@/services/api"
import type { IoTReadingResponse, IoTReading } from "@/types/iot"
import { toast } from "sonner"
import { Play, Pause, SkipForward, AlertTriangle } from "lucide-react"

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts"

export default function IotDashboardPage() {
  const { id } = useParams<{ id: string }>()
  const [data, setData] = useState<IoTReadingResponse | null>(null)
  const [products, setProducts] = useState<string[]>([])
  const [product, setProduct] = useState("")
  const [index, setIndex] = useState(0)
  const [running, setRunning] = useState(false)
  const [loading, setLoading] = useState(true)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    api.get("/products").then(({ data: prods }) => {
      const names = prods.map((p: any) => p.name)
      setProducts(names)
    }).catch(() => {})
  }, [])

  const loadData = useCallback(async (idx?: number) => {
    if (!id) return
    try {
      const res = await getIoTReadings(id, product || undefined, idx ?? index)
      setData(res)
      if (idx === undefined) setIndex(res.index)
      else setIndex(idx)
    } catch {
      toast.error("Erreur chargement données IoT")
    } finally {
      setLoading(false)
    }
  }, [id, product, index])

  useEffect(() => { loadData(0) }, [id, product])

  useEffect(() => {
    if (running) {
      intervalRef.current = setInterval(() => {
        setIndex((prev) => {
          const next = prev + 1
          if (data && next >= data.total) {
            setRunning(false)
            return prev
          }
          loadData(next)
          return next
        })
      }, 2000)
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current) }
  }, [running, data?.total])

  const chartData = data?.readings.map((r, i) => ({
    time: new Date(r.recorded_at).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" }),
    temperature: i <= index ? (r.temp_sensor_1 ?? 0) : null,
    humidity: i <= index ? (r.hum_sensor_1 ?? 0) : null,
  })).filter((_, i) => i <= index) || []

  if (loading) return <div className="space-y-4"><Skeleton className="h-48 w-full" /><Skeleton className="h-64 w-full" /></div>

  const kpi = data?.kpi
  const isAlert = kpi?.temp_status !== "Optimal" || kpi?.hum_status !== "Optimal"

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Dashboard IoT</h2>
          <p className="text-sm text-muted-foreground">Entrepôt: {id}</p>
        </div>
        <Select value={product} onValueChange={setProduct}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Produit (optionnel)" />
          </SelectTrigger>
          <SelectContent>
            {products.map((p) => <SelectItem key={p} value={p}>{p}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      {isAlert && (
        <div className="flex items-center gap-3 rounded-2xl border border-red-200 bg-red-50 dark:bg-red-950 dark:border-red-800 p-4 text-red-800 dark:text-red-200">
          <AlertTriangle className="h-5 w-5" />
          <p className="text-sm font-medium">
            {kpi?.temp_status !== "Optimal" && `Température: ${kpi?.temp_status}`}
            {kpi?.hum_status !== "Optimal" && (kpi?.temp_status !== "Optimal" ? " · " : "") + `Humidité: ${kpi?.hum_status}`}
          </p>
        </div>
      )}

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4">
        <GlassCard className="p-4" style={kpi ? { borderLeftColor: kpi.temp_color, borderLeftWidth: 4 } : {}}>
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Température</p>
          <p className="text-2xl font-bold">{kpi?.current_temp ?? "—"}°C</p>
          <p className="text-xs" style={{ color: kpi?.temp_color }}>{kpi?.temp_status}</p>
        </GlassCard>
        <GlassCard className="p-4" style={kpi ? { borderLeftColor: kpi.hum_color, borderLeftWidth: 4 } : {}}>
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Humidité</p>
          <p className="text-2xl font-bold">{kpi?.current_hum ?? "—"}%</p>
          <p className="text-xs" style={{ color: kpi?.hum_color }}>{kpi?.hum_status}</p>
        </GlassCard>
        <GlassCard className="p-4">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Moy. Température</p>
          <p className="text-2xl font-bold">{kpi?.avg_temp ?? "—"}°C</p>
        </GlassCard>
        <GlassCard className="p-4">
          <p className="text-xs text-muted-foreground uppercase tracking-wider">Stabilité</p>
          <p className="text-2xl font-bold">{kpi?.stability_score ?? "—"}/100</p>
        </GlassCard>
      </div>

      {/* Time controls */}
      <GlassCard className="p-4">
        <div className="flex items-center gap-4">
          <Button variant={running ? "secondary" : "default"} onClick={() => setRunning(!running)}>
            {running ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
            {running ? "Pause" : "Lecture"}
          </Button>
          <Button variant="outline" onClick={() => setIndex((prev) => { const next = Math.min(prev + 1, (data?.total || 1) - 1); loadData(next); return next })}>
            <SkipForward className="h-4 w-4 mr-2" /> +1
          </Button>
          <div className="flex-1">
            <Input
              type="range"
              min={0}
              max={(data?.total || 1) - 1}
              value={index}
              onChange={(e) => { const v = Number(e.target.value); setIndex(v); loadData(v) }}
              className="w-full"
            />
          </div>
          <span className="text-xs text-muted-foreground">{index + 1}/{data?.total}</span>
        </div>
      </GlassCard>

      {/* Chart */}
      <GlassCard className="p-4">
        <p className="text-sm font-medium mb-4">
          {product ? `Conditions optimales pour ${product}` : "Évolution des capteurs"}
        </p>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={12} />
            <YAxis yAxisId="temp" stroke="hsl(var(--muted-foreground))" fontSize={12} />
            <YAxis yAxisId="hum" orientation="right" stroke="hsl(var(--muted-foreground))" fontSize={12} />
            <Tooltip />
            <Line yAxisId="temp" type="monotone" dataKey="temperature" stroke="#ef4444" strokeWidth={2} dot={false} name="Température °C" />
            <Line yAxisId="hum" type="monotone" dataKey="humidity" stroke="#3b82f6" strokeWidth={2} dot={false} strokeDasharray="5 5" name="Humidité %" />
          </LineChart>
        </ResponsiveContainer>
      </GlassCard>
    </div>
  )
}
