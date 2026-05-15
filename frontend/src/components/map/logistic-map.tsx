"use client"

import { useEffect, useMemo } from "react"
import dynamic from "next/dynamic"
import { Skeleton } from "@/components/ui/skeleton"

// Dynamically import react-leaflet to avoid SSR issues
const MapContainer = dynamic(() => import("react-leaflet").then((m) => m.MapContainer), { ssr: false, loading: () => <Skeleton className="h-[400px] w-full rounded-2xl" /> })
const TileLayer = dynamic(() => import("react-leaflet").then((m) => m.TileLayer), { ssr: false })
const LayersControl = dynamic(() => import("react-leaflet").then((m) => m.LayersControl), { ssr: false })
const BaseLayer = dynamic(() => import("react-leaflet").then((m) => m.LayersControl).then(l => l.BaseLayer), { ssr: false })
const Marker = dynamic(() => import("react-leaflet").then((m) => m.Marker), { ssr: false })
const Popup = dynamic(() => import("react-leaflet").then((m) => m.Popup), { ssr: false })
const Polyline = dynamic(() => import("react-leaflet").then((m) => m.Polyline), { ssr: false })

// This internal component will fix the map layout
const MapFixer = () => {
  const { useMap } = require("react-leaflet")
  const map = useMap()
  useEffect(() => {
    setTimeout(() => {
      map.invalidateSize()
    }, 200)
  }, [map])
  return null
}

interface MapPoint {
  name: string
  lat: number
  lng: number
  type: "result" | "warehouse" | "client"
}

interface MapLine {
  from: { lat: number; lng: number }
  to: { lat: number; lng: number }
}

interface LogisticMapProps {
  results: MapPoint[]
  warehouses: MapPoint[]
  clients: MapPoint[]
  lines?: MapLine[]
  weberPoint?: { lat: number; lng: number }
}

const iconColors = {
  result: { color: "#22c55e", icon: "check" },
  warehouse: { color: "#ef4444", icon: "building" },
  client: { color: "#3b82f6", icon: "user" },
}

function createIcon(color: string) {
  if (typeof window === "undefined") return null
  const L = require("leaflet")
  return new L.DivIcon({
    className: "custom-marker",
    html: `<div style="width:24px;height:24px;border-radius:50%;background:${color};border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3);"></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12],
  })
}

export function LogisticMap({ results, warehouses, clients, lines, weberPoint }: LogisticMapProps) {
  const allPoints = useMemo(() => [
    ...results, ...warehouses, ...clients,
    ...(weberPoint ? [{ name: "Weber", lat: weberPoint.lat, lng: weberPoint.lng, type: "result" as const }] : [])
  ], [results, warehouses, clients, weberPoint])
  const center = useMemo(() => {
    if (allPoints.length === 0) return { lat: 31.7917, lng: -7.0926 }
    const lat = allPoints.reduce((s, p) => s + p.lat, 0) / allPoints.length
    const lng = allPoints.reduce((s, p) => s + p.lng, 0) / allPoints.length
    return { lat, lng }
  }, [allPoints])

  const resultIcon = useMemo(() => {
    if (typeof window === "undefined") return null
    const L = require("leaflet")
    return L.divIcon({
      className: "",
      html: `<div style="width:28px;height:28px;border-radius:50%;background:#22c55e;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div>`,
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    })
  }, [])

  const warehouseIcon = useMemo(() => {
    if (typeof window === "undefined") return null
    const L = require("leaflet")
    return L.divIcon({
      className: "",
      html: `<div style="width:24px;height:24px;border-radius:50%;background:#ef4444;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3);"></div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    })
  }, [])

  const clientIcon = useMemo(() => {
    if (typeof window === "undefined") return null
    const L = require("leaflet")
    return L.divIcon({
      className: "",
      html: `<div style="width:20px;height:20px;border-radius:50%;background:#3b82f6;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3);"></div>`,
      iconSize: [20, 20],
      iconAnchor: [10, 10],
    })
  }, [])

  const weberIcon = useMemo(() => {
    if (typeof window === "undefined") return null
    const L = require("leaflet")
    return L.divIcon({
      className: "",
      html: `<div style="width:38px;height:38px;border-radius:50%;background:#f59e0b;border:4px solid white;box-shadow:0 4px 16px rgba(245,158,11,0.6);display:flex;align-items:center;justify-content:center;font-size:18px;">⭐</div>`,
      iconSize: [38, 38],
      iconAnchor: [19, 19],
      popupAnchor: [0, -19],
    })
  }, [])

  return (
    <div className="space-y-2">
      <div className="flex gap-4 text-xs flex-wrap">
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-green-500" /> Résultats</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-red-500" /> Mes Entrepôts</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-blue-500" /> Clients</div>
        {weberPoint && <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-amber-400" /> Centre de Gravité (Weber)</div>}
      </div>
      <div className="h-[400px] w-full rounded-2xl overflow-hidden border relative z-0">
        <MapContainer center={[center.lat, center.lng]} zoom={6} className="h-full w-full" scrollWheelZoom={true} style={{ zIndex: 0 }}>
          <MapFixer />
          <LayersControl position="topright">
            <BaseLayer checked name="Plan (Clair)">
              <TileLayer
                attribution='&copy; <a href="https://carto.com/">CARTO</a>'
                url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
              />
            </BaseLayer>
            <BaseLayer name="Vue Satellite">
              <TileLayer
                attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EBP, and the GIS User Community'
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              />
            </BaseLayer>
          </LayersControl>
          {clients.map((p, i) => p.lat && p.lng && clientIcon && (
            <Marker key={`c-${i}`} position={[p.lat, p.lng]} icon={clientIcon}>
              <Popup><b>{p.name}</b><br />Client</Popup>
            </Marker>
          ))}
          {warehouses.map((p, i) => p.lat && p.lng && warehouseIcon && (
            <Marker key={`w-${i}`} position={[p.lat, p.lng]} icon={warehouseIcon}>
              <Popup><b>{p.name}</b><br />Entrepôt</Popup>
            </Marker>
          ))}
          {results.map((p, i) => p.lat && p.lng && resultIcon && (
            <Marker key={`r-${i}`} position={[p.lat, p.lng]} icon={resultIcon}>
              <Popup><b>{p.name}</b><br />Résultat</Popup>
            </Marker>
          ))}
          {lines?.map((line, i) => (
            <Polyline key={i} positions={[[line.from.lat, line.from.lng], [line.to.lat, line.to.lng]]} color="gray" weight={1.5} opacity={0.6} dashArray="5" />
          ))}
          {weberPoint && weberIcon && (
            <Marker position={[weberPoint.lat, weberPoint.lng]} icon={weberIcon}>
              <Popup>
                <b>⭐ Centre de Gravité (Weber)</b><br />
                Lat: {weberPoint.lat.toFixed(4)}° / Lon: {weberPoint.lng.toFixed(4)}°<br />
                <span style={{color:"#f59e0b",fontWeight:"bold"}}>Point d'implantation optimal</span>
              </Popup>
            </Marker>
          )}
        </MapContainer>
      </div>
    </div>
  )
}
