"use client"

import { useEffect, useState, useRef } from "react"
import { useParams } from "next/navigation"
import { GlassCard } from "@/components/shared/glass-card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { getLiveTelemetry } from "@/services/thingsboard.service"
import { getWarehouse } from "@/services/warehouse.service"
import api from "@/services/api"
import { Activity, Radio, Thermometer, Droplets } from "lucide-react"
import { cn } from "@/lib/utils"
import { useAuth } from "@/providers/auth-provider"
import { Badge } from "@/components/ui/badge"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"

// Composant de Jauge Circulaire
const CircularGauge = ({ value, min, max, label, unit, color, icon: Icon }: any) => {
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const progress = Math.min(Math.max((value - min) / (max - min), 0), 1);
  const strokeDashoffset = circumference - progress * circumference;

  return (
    <GlassCard className="p-6 flex flex-col items-center justify-center relative overflow-hidden group border-primary/10">
      <div className="relative h-40 w-40">
        {/* Cercle de fond */}
        <svg className="h-full w-full transform -rotate-90">
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke="currentColor"
            strokeWidth="10"
            fill="transparent"
            className="text-slate-100 dark:text-slate-800"
          />
          {/* Cercle de progression */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke={color}
            strokeWidth="10"
            strokeDasharray={circumference}
            style={{ strokeDashoffset, transition: 'stroke-dashoffset 0.8s ease-in-out' }}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>
        {/* Texte au centre */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <Icon className={cn("h-6 w-6 mb-1 opacity-50", `text-[${color}]`)} style={{ color }} />
          <span className="text-3xl font-black">{value.toFixed(1)}<small className="text-sm font-bold opacity-70">{unit}</small></span>
          <span className="text-[10px] font-bold uppercase tracking-tighter opacity-50">{label}</span>
        </div>
      </div>
      <div className="mt-4 flex items-center gap-2 px-3 py-1 bg-primary/5 rounded-full border border-primary/10">
        <div className="h-1.5 w-1.5 rounded-full animate-pulse" style={{ backgroundColor: color }} />
        <span className="text-[9px] font-bold uppercase tracking-widest opacity-70">Flux Direct</span>
      </div>
    </GlassCard>
  );
};

export default function IotDashboardPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const [products, setProducts] = useState<string[]>([])
  const [product, setProduct] = useState("")
  const [loading, setLoading] = useState(true)
  
  const [currentData, setCurrentData] = useState<{ temp: number, hum: number }>({ temp: 0, hum: 0 })
  const [history, setHistory] = useState<any[]>([])
  const [iotToken, setIotToken] = useState<string | null>(null)
  const [countdown, setCountdown] = useState<number | null>(null)
  
  const liveIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const violationCounterRef = useRef<number>(0)
  const alertSentRef = useRef<boolean>(false)

  useEffect(() => {
    // 1. Charger les produits
    api.get("/products").then(({ data: prods }) => {
      setProducts(prods.map((p: any) => p.name))
    }).catch(() => {})

    // 2. Charger le Token IoT et le Produit associé
    if (id) {
      getWarehouse(id).then((wh) => {
        if (wh.iot_token) {
          setIotToken(wh.iot_token)
          // Si l'entrepôt a un produit spécifique (cas du chercheur)
          if (wh.product_name) {
            setProduct(wh.product_name)
          }
          setLoading(false)
        } else {
          toast.warning("Dashboard en attente d'activation par l'Admin")
          setLoading(false)
        }
      }).catch(() => setLoading(false))
    }
  }, [id])

  const THRESHOLDS: any = {
    "Tomates": { temp: { min: 7, max: 10 }, hum: { min: 90, max: 95 } },
    "Produits Laitiers": { temp: { min: 2, max: 6 }, hum: { min: 65, max: 80 } },
    "Produits Pharmaceutiques": { temp: { min: 15, max: 25 }, hum: { min: 35, max: 50 } },
    "Materiaux de Construction": { temp: { min: -100, max: 200 }, hum: { min: 0, max: 100 } }
  }


  useEffect(() => {
    if (!iotToken) return;

    const fetchLive = async () => {
      try {
        const tele = await getLiveTelemetry(id);
        if (tele && tele.temperature && tele.humidity) {
          const newTemp = tele.temperature[0]?.value;
          const newHum = tele.humidity[0]?.value;
          
          const newPoint = {
            time: new Date().toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
            temperature: newTemp,
            humidity: newHum,
          };

          setCurrentData({ temp: newTemp, hum: newHum });
          setHistory(prev => {
            const updated = [...prev, newPoint];
            return updated.slice(-20); 
          });

          // VERIFICATION DES SEUILS ET ALERTE
          if (product && THRESHOLDS[product]) {
            const limits = THRESHOLDS[product];
            const isTempCritical = newTemp < limits.temp.min || newTemp > limits.temp.max;
            const isHumCritical = newHum < limits.hum.min || newHum > limits.hum.max;

            if (isTempCritical || isHumCritical) {
              // INCRÉMENTER LE COMPTEUR DE VIOLATION
              violationCounterRef.current += 1;
              const count = violationCounterRef.current;
              console.log(`[ALERTE] Lecture hors-norme détectée #${count} / 4`);

              // MISE À JOUR DU COMPTE À REBOURS VISUEL (Approximate)
              const remaining = Math.max(0, 4 - count) * 3;
              setCountdown(count < 4 && !alertSentRef.current ? remaining : null);

              if (count % 2 === 0) {
                toast.error(`ALERTE CRITIQUE : Seuil dépassé (${count}/4)`, {
                  description: `Temp: ${newTemp}°C | Hum: ${newHum}%`,
                  duration: 1500,
                });
              }

              // DÉCLENCHEMENT SI 4 LECTURES CONSÉCUTIVES (Environ 12s)
              if (count >= 4 && !alertSentRef.current) {
                alertSentRef.current = true;
                setCountdown(null);
                console.log("🚨 DÉCLENCHEMENT AUTOMATIQUE DE L'ALERTE EMAIL");
                
                api.post("/warehouses/alert", {
                  email: user?.email || "najat.pfa@gmail.com",
                  warehouse_name: `Entrepôt ${id}`,
                  product_name: product,
                  temp: newTemp,
                  hum: newHum
                }).then(() => {
                  toast.success("🚨 ALERTE EMAIL ENVOYÉE !", {
                    description: `Conditions hors-normes persistantes. Email envoyé à ${user?.email || "najat.pfa@gmail.com"}`,
                  });
                }).catch(err => {
                  console.error("Erreur API Alerte Auto:", err);
                });
              }
            } else {
              // RÉINITIALISER SI RETOUR À LA NORMALE
              if (violationCounterRef.current > 0) {
                console.log("[IOT] Retour aux conditions normales.");
              }
              violationCounterRef.current = 0;
              alertSentRef.current = false;
              setCountdown(null);
            }
          }
        }
      } catch (e) {
        console.error("ThingsBoard Error", e);
      }
    };

    fetchLive();
    liveIntervalRef.current = setInterval(fetchLive, 3000);
    return () => { if (liveIntervalRef.current) clearInterval(liveIntervalRef.current) }
  }, [iotToken, product])

  if (loading) return <div className="p-8 space-y-4"><Skeleton className="h-48 w-full" /><Skeleton className="h-64 w-full" /></div>
  
  if (!iotToken) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
        <div className="h-24 w-24 rounded-full bg-amber-500/10 flex items-center justify-center border-2 border-dashed border-amber-500 animate-pulse">
          <Radio className="h-10 w-10 text-amber-600" />
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-bold">Dashboard en attente d'activation</h2>
          <p className="text-muted-foreground max-w-md">
            L'administrateur système doit configurer le Token ThingsBoard pour cet entrepôt avant que les données temps réel ne soient disponibles.
          </p>
        </div>
        <div className="p-4 bg-muted/50 rounded-xl border border-border text-xs font-mono">
          Warehouse ID: {id} | Statut: <span className="text-amber-600 font-bold">DÉCONNECTÉ</span>
        </div>
      </div>
    )
  }

  // Vérifier si le produit est verrouillé (cas chercheur)
  const isResearcher = user?.role === "researcher"

  // Calcul des états critiques pour l'affichage visuel
  const limits = product ? THRESHOLDS[product] : null;
  const isTempCritical = limits && (currentData.temp < limits.temp.min || currentData.temp > limits.temp.max);
  const isHumCritical = limits && (currentData.hum < limits.hum.min || currentData.hum > limits.hum.max);
  const isAnyCritical = isTempCritical || isHumCritical;

  return (
    <div className="space-y-6">
      {/* BANNIÈRE D'ALERTE CRITIQUE */}
      {isAnyCritical && (
        <div className="bg-red-600 text-white p-4 rounded-xl flex items-center justify-between animate-pulse border-2 border-red-700 shadow-[0_0_25px_rgba(220,38,38,0.6)]">
          <div className="flex items-center gap-3">
            <Activity className="h-6 w-6 animate-bounce" />
            <div>
              <p className="font-black text-lg uppercase tracking-wider">Alerte : Conditions Hors Normes !</p>
              <p className="text-sm opacity-90 font-medium">Les paramètres de stockage ne respectent plus les contraintes pour : {product}</p>
              {countdown !== null && (
                <p className="text-xs font-bold mt-1 bg-white/20 inline-block px-2 py-0.5 rounded border border-white/30">
                  📧 Envoi d'un e-mail d'alerte dans {countdown}s...
                </p>
              )}
            </div>
          </div>
          <Badge variant="outline" className="bg-white text-red-600 font-bold border-none px-4 py-1">CRITIQUE</Badge>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-3">
            <Activity className="h-6 w-6 text-primary" />
            Monitoring Industriel Live
            <span className={cn(
              "flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border animate-pulse",
              isAnyCritical ? "bg-red-600 text-white border-red-700" : "bg-red-500/10 text-red-500 border-red-500/20"
            )}>
              <div className={cn("h-2 w-2 rounded-full", isAnyCritical ? "bg-white" : "bg-red-500")} />
              {isAnyCritical ? "DANGER" : "LIVE"}
            </span>
          </h2>
          <div className="flex items-center gap-2 mt-1">
            <p className="text-sm text-muted-foreground uppercase font-medium">Entrepôt ID: {id}</p>
            {isResearcher && product && (
              <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20 animate-in fade-in zoom-in duration-500">
                Produit : {product}
              </Badge>
            )}
          </div>
        </div>
        
        {!isResearcher ? (
          <Select value={product} onValueChange={setProduct}>
            <SelectTrigger className="w-56 bg-background/50 backdrop-blur-xl border-primary/20">
              <SelectValue placeholder="Seuils par produit" />
            </SelectTrigger>
            <SelectContent>
              {products.map((p) => <SelectItem key={p} value={p}>{p}</SelectItem>)}
            </SelectContent>
          </Select>
        ) : (
          <div className="px-4 py-2 bg-muted/50 rounded-lg border border-border flex items-center gap-2 text-sm font-bold text-muted-foreground">
             Seuils verrouillés ({product})
          </div>
        )}
      </div>

      {/* KPIs CERCLES */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <CircularGauge 
          value={currentData.temp} 
          min={0} 
          max={50} 
          label="Température" 
          unit="°C" 
          color={isTempCritical ? "#ef4444" : "#f43f5e"}
          icon={Thermometer}
        />
        
        <CircularGauge 
          value={currentData.hum} 
          min={0} 
          max={100} 
          label="Humidité" 
          unit="%" 
          color={isHumCritical ? "#ef4444" : "#3b82f6"}
          icon={Droplets}
        />

        <GlassCard className="p-6 border-primary/20 flex flex-col justify-center items-center text-center bg-primary/5">
          <Radio className="h-10 w-10 text-primary mb-3 animate-ping" />
          <p className="text-sm font-bold text-primary uppercase tracking-tighter">Status Réseau</p>
          <div className="mt-4 px-6 py-2 bg-green-500 text-white text-[10px] font-black rounded-full uppercase shadow-lg shadow-green-500/20">
            ThingsBoard OK
          </div>
          <p className="text-[9px] text-muted-foreground mt-4 italic">Réception continue via Proteus Gateway</p>
        </GlassCard>
      </div>

      {/* CHART */}
      <GlassCard className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="font-bold text-lg">Analyse Graphique Temps Réel</h3>
          <div className="flex items-center gap-4 text-[10px] font-bold">
            <div className="flex items-center gap-1.5"><div className="h-2 w-2 bg-red-500 rounded-full" /> TEMP (°C)</div>
            <div className="flex items-center gap-1.5"><div className="h-2 w-2 bg-blue-500 rounded-full" /> HUM (%)</div>
          </div>
        </div>
        
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--muted-foreground)/0.1)" />
              <XAxis dataKey="time" fontSize={10} stroke="hsl(var(--muted-foreground))" />
              <YAxis fontSize={10} stroke="hsl(var(--muted-foreground))" />
              <Tooltip contentStyle={{ borderRadius: '12px', border: 'none' }} />
              <Line type="monotone" dataKey="temperature" stroke="#ef4444" strokeWidth={3} dot={false} animationDuration={300} />
              <Line type="monotone" dataKey="humidity" stroke="#3b82f6" strokeWidth={3} dot={false} animationDuration={300} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </GlassCard>
    </div>
  )
}
