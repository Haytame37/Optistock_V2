"use client"

import { useEffect, useState } from "react"
import { GlassCard } from "@/components/shared/glass-card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { 
  Users, 
  Warehouse, 
  Calendar, 
  ShieldAlert, 
  Search, 
  RefreshCcw, 
  Trash2, 
  Eye, 
  UserPlus,
  ArrowUpRight,
  TrendingUp,
  Settings,
  AlertCircle
} from "lucide-react"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from "recharts"
import { 
  getAdminStats, 
  getUsers, 
  toggleUserStatus, 
  deleteUser, 
  runCleanup, 
  purgeLocks,
  getUserProfile,
  updateWarehouseToken
} from "@/services/admin.service"
import { toast } from "sonner"
import { cn } from "@/lib/utils"

const COLORS = ["#005da7", "#2563eb", "#16a34a", "#dc2626", "#eab308"]

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>(null)
  const [users, setUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [roleFilter, setRoleFilter] = useState("all")
  
  const [selectedUser, setSelectedUser] = useState<any>(null)
  const [inspecting, setInspecting] = useState(false)

  const loadData = async () => {
    setLoading(true)
    try {
      const [s, u] = await Promise.all([getAdminStats(), getUsers()])
      setStats(s)
      setUsers(u)
    } catch {
      toast.error("Erreur chargement des données admin")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData() }, [])

  const handleToggleStatus = async (userId: number) => {
    try {
      await toggleUserStatus(userId)
      toast.success("Statut utilisateur mis à jour")
      loadData()
    } catch {
      toast.error("Erreur lors de la modification")
    }
  }

  const handleDeleteUser = async (userId: number) => {
    if (!confirm("Supprimer définitivement cet utilisateur ?")) return
    try {
      await deleteUser(userId)
      toast.success("Utilisateur supprimé")
      loadData()
    } catch {
      toast.error("Erreur lors de la suppression")
    }
  }

  const handleMaintenance = async (type: "cleanup" | "purge") => {
    try {
      if (type === "cleanup") await runCleanup()
      else await purgeLocks()
      toast.success("Maintenance effectuée")
      loadData()
    } catch {
      toast.error("Erreur maintenance")
    }
  }

  const handleInspect = async (userId: number) => {
    try {
      const profile = await getUserProfile(userId)
      setSelectedUser(profile)
      setInspecting(true)
    } catch {
      toast.error("Erreur chargement profil")
    }
  }

  const handleUpdateToken = async (warehouseId: string, token: string) => {
    try {
      await updateWarehouseToken(warehouseId, token);
      toast.success("Dashboard IoT activé pour cet entrepôt");
      loadData();
    } catch {
      toast.error("Erreur lors de l'activation IoT");
    }
  }

  if (loading && !stats) return <div className="p-12 text-center">Chargement du panel admin...</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Shield Admin Panel</h1>
          <p className="text-muted-foreground mt-1">Contrôle centralisé de la plateforme OptiStock.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={loadData}>
            <RefreshCcw className="h-4 w-4 mr-2" /> Actualiser
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="bg-muted/50 p-1">
          <TabsTrigger value="overview">📈 Vue d'ensemble</TabsTrigger>
          <TabsTrigger value="users">👥 Utilisateurs</TabsTrigger>
          <TabsTrigger value="warehouses">🏢 Entrepôts</TabsTrigger>
          <TabsTrigger value="maintenance">⚙️ Maintenance</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <GlassCard className="p-5 border-l-4 border-l-blue-600">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Utilisateurs</p>
                  <p className="text-3xl font-extrabold mt-1">{stats?.total_users ?? 0}</p>
                </div>
                <Users className="h-8 w-8 text-blue-600/20" />
              </div>
              <div className="flex items-center mt-4 text-xs text-green-600 font-medium">
                <TrendingUp className="h-3 w-3 mr-1" /> +100% actifs
              </div>
            </GlassCard>

            <GlassCard className="p-5 border-l-4 border-l-emerald-600">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Entrepôts</p>
                  <p className="text-3xl font-extrabold mt-1">{stats?.total_warehouses ?? 0}</p>
                </div>
                <Warehouse className="h-8 w-8 text-emerald-600/20" />
              </div>
              <div className="flex items-center mt-4 text-xs text-blue-600 font-medium">
                <ArrowUpRight className="h-3 w-3 mr-1" /> Gestion multi-sites
              </div>
            </GlassCard>

            <GlassCard className="p-5 border-l-4 border-l-amber-600">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Réservations</p>
                  <p className="text-3xl font-extrabold mt-1">{stats?.total_reservations ?? 0}</p>
                </div>
                <Calendar className="h-8 w-8 text-amber-600/20" />
              </div>
              <div className="flex items-center mt-4 text-xs text-amber-600 font-medium">
                <RefreshCcw className="h-3 w-3 mr-1" /> Flux dynamique
              </div>
            </GlassCard>

          </div>


          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <GlassCard className="lg:col-span-2 p-6">
              <h3 className="font-bold mb-6">📉 Analyse de l'Activité (Réservations)</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={stats?.activity_history?.reverse() ?? []}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="date" fontSize={12} stroke="#64748b" />
                  <YAxis fontSize={12} stroke="#64748b" />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#005da7" strokeWidth={3} dot={{ r: 4, fill: "#005da7" }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </GlassCard>

            <GlassCard className="p-6">
              <h3 className="font-bold mb-6">👥 Profils</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={Object.entries(stats?.user_distribution ?? {}).map(([name, value]) => ({ name, value }))}
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {Object.entries(stats?.user_distribution ?? {}).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2 mt-4">
                {Object.entries(stats?.user_distribution ?? {}).map(([role, count], i) => (
                  <div key={role} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                      <span className="capitalize">{role}</span>
                    </div>
                    <span className="font-bold">{count as any}</span>
                  </div>
                ))}
              </div>
            </GlassCard>
          </div>
        </TabsContent>

        <TabsContent value="users" className="space-y-6">
          <GlassCard className="p-6">
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input 
                  placeholder="Rechercher par email ou nom..." 
                  className="pl-9"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
              </div>
              <div className="flex gap-2">
                {["all", "admin", "owner", "researcher"].map(role => (
                  <Button 
                    key={role}
                    variant={roleFilter === role ? "default" : "outline"}
                    size="sm"
                    className="capitalize"
                    onClick={() => setRoleFilter(role)}
                  >
                    {role}
                  </Button>
                ))}
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground font-medium">
                    <th className="pb-3 pl-2">Utilisateur</th>
                    <th className="pb-3">Rôle</th>
                    <th className="pb-3">Statut</th>
                    <th className="pb-3">Créé le</th>
                    <th className="pb-3 text-right pr-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.filter(u => {
                    const matchesSearch = u.email.toLowerCase().includes(search.toLowerCase()) || 
                                          u.first_name.toLowerCase().includes(search.toLowerCase())
                    const matchesRole = roleFilter === "all" || u.role === roleFilter
                    return matchesSearch && matchesRole
                  }).map(u => (
                    <tr key={u.user_id} className="border-b last:border-0 hover:bg-muted/50 transition-colors group">
                      <td className="py-4 pl-2">
                        <div>
                          <p className="font-bold">{u.first_name} {u.last_name}</p>
                          <p className="text-xs text-muted-foreground">{u.email}</p>
                        </div>
                      </td>
                      <td className="py-4">
                        <Badge variant="outline" className={cn(
                          "capitalize",
                          u.role === 'admin' ? "border-red-200 text-red-700 bg-red-50" :
                          u.role === 'owner' ? "border-blue-200 text-blue-700 bg-blue-50" :
                          "border-green-200 text-green-700 bg-green-50"
                        )}>
                          {u.role}
                        </Badge>
                      </td>
                      <td className="py-4">
                        <span className={cn(
                          "flex items-center gap-1.5 text-xs font-medium",
                          u.is_active ? "text-green-600" : "text-red-500"
                        )}>
                          <div className={cn("w-2 h-2 rounded-full", u.is_active ? "bg-green-600" : "bg-red-500")} />
                          {u.is_active ? "Actif" : "Suspendu"}
                        </span>
                      </td>
                      <td className="py-4 text-muted-foreground text-xs">
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-4 text-right pr-2">
                        <div className="flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button variant="ghost" size="icon" onClick={() => handleInspect(u.user_id)}>
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" onClick={() => handleToggleStatus(u.user_id)}>
                            <ShieldAlert className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" className="text-red-500" onClick={() => handleDeleteUser(u.user_id)}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCard>
        </TabsContent>

        <TabsContent value="warehouses" className="space-y-6">
          <GlassCard className="p-6">
            <h3 className="font-bold mb-6 flex items-center gap-2">
              <Warehouse className="h-5 w-5 text-primary" />
              Gestion des Activations IoT
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground font-medium">
                    <th className="pb-3 pl-2">Entrepôt</th>
                    <th className="pb-3">Propriétaire</th>
                    <th className="pb-3">Token IoT (ThingsBoard)</th>
                    <th className="pb-3">Statut</th>
                    <th className="pb-3 text-right pr-2">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {stats?.all_warehouses?.map((w: any) => (
                    <tr key={w.id} className="border-b last:border-0 hover:bg-muted/50 transition-colors group">
                      <td className="py-4 pl-2">
                        <p className="font-bold">{w.name}</p>
                        <p className="text-xs text-muted-foreground">{w.id}</p>
                      </td>
                      <td className="py-4 text-xs font-medium">
                        {w.owner_name}
                      </td>
                      <td className="py-4 font-mono text-[10px]">
                        {w.iot_token ? (
                          <span className="text-green-600 font-bold">{w.iot_token}</span>
                        ) : (
                          <span className="text-muted-foreground italic">Non activé</span>
                        )}
                      </td>
                      <td className="py-4">
                        <Badge variant={w.iot_token ? "default" : "outline"} className={cn(w.iot_token && "bg-green-500 hover:bg-green-600")}>
                          {w.iot_token ? "Connecté" : "En attente"}
                        </Badge>
                      </td>
                      <td className="py-4 text-right pr-2">
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="gap-2"
                          onClick={() => {
                            const token = prompt(`Saisir le Token ThingsBoard pour [${w.name}]`, w.iot_token || "");
                            if (token !== null) handleUpdateToken(w.id, token);
                          }}
                        >
                          <Settings className="h-3 w-3" />
                          {w.iot_token ? "Modifier" : "Activer"}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCard>
        </TabsContent>

        <TabsContent value="maintenance" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <GlassCard className="p-6 space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-blue-100 text-blue-700">
                  <Users className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-bold text-lg">Nettoyage des Comptes</h3>
                  <p className="text-sm text-muted-foreground">Suspendre automatiquement les utilisateurs inactifs.</p>
                </div>
              </div>
              <p className="text-sm border rounded-lg p-4 bg-muted/30">
                Cette opération analyse les dernières connexions et suspend les comptes n'ayant pas eu d'activité depuis plus de 30 jours.
              </p>
              <Button className="w-full" onClick={() => handleMaintenance("cleanup")}>
                <RefreshCcw className="h-4 w-4 mr-2" /> Lancer le nettoyage
              </Button>
            </GlassCard>

            <GlassCard className="p-6 space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-amber-100 text-amber-700">
                  <ShieldAlert className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-bold text-lg">Purge des Verrous</h3>
                  <p className="text-sm text-muted-foreground">Libérer tous les entrepôts bloqués.</p>
                </div>
              </div>
              <p className="text-sm border rounded-lg p-4 bg-muted/30">
                En cas de bug ou de crash, certains entrepôts peuvent rester bloqués en statut 'locked'. Cette action réinitialise tout le parc.
              </p>
              <Button variant="secondary" className="w-full" onClick={() => handleMaintenance("purge")}>
                <Trash2 className="h-4 w-4 mr-2" /> Forcer la libération totale
              </Button>
            </GlassCard>
          </div>


        </TabsContent>
      </Tabs>

      {/* User Inspector Modal/Slide-over */}
      {inspecting && selectedUser && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex justify-end">
          <div className="w-full max-w-2xl bg-background shadow-2xl p-8 overflow-y-auto animate-in slide-in-from-right duration-300">
            <div className="flex justify-between items-start mb-8">
              <div>
                <Badge className="mb-2 uppercase">{selectedUser.role}</Badge>
                <h2 className="text-3xl font-bold">{selectedUser.first_name} {selectedUser.last_name}</h2>
                <p className="text-muted-foreground">{selectedUser.email}</p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setInspecting(false)}>
                <Trash2 className="h-6 w-6 rotate-45" />
              </Button>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-8 text-center">
              <div className="p-4 rounded-xl border bg-muted/20">
                <p className="text-xs font-bold uppercase text-muted-foreground">Entrepôts</p>
                <p className="text-2xl font-bold">{selectedUser.warehouses.length}</p>
              </div>
              <div className="p-4 rounded-xl border bg-muted/20">
                <p className="text-xs font-bold uppercase text-muted-foreground">Réservations</p>
                <p className="text-2xl font-bold">{selectedUser.reservations.length}</p>
              </div>
              <div className="p-4 rounded-xl border bg-muted/20">
                <p className="text-xs font-bold uppercase text-muted-foreground">Messages</p>
                <p className="text-2xl font-bold">{selectedUser.recent_messages.length}</p>
              </div>
            </div>

            <Tabs defaultValue="wh" className="w-full">
              <TabsList className="w-full">
                <TabsTrigger value="wh" className="flex-1">Entrepôts</TabsTrigger>
                <TabsTrigger value="res" className="flex-1">Réservations</TabsTrigger>
                <TabsTrigger value="msg" className="flex-1">Messages</TabsTrigger>
              </TabsList>

              <TabsContent value="wh" className="py-4 space-y-4">
                {selectedUser.warehouses.map((w: any) => (
                  <div key={w.warehouse_id} className="p-4 rounded-xl border flex justify-between items-center">
                    <div>
                      <p className="font-bold">{w.name}</p>
                      <p className="text-xs text-muted-foreground">{w.address}</p>
                    </div>
                    <Badge variant="outline">{w.status}</Badge>
                  </div>
                ))}
                {selectedUser.warehouses.length === 0 && <p className="text-center py-8 text-muted-foreground italic">Aucun entrepôt.</p>}
              </TabsContent>

              <TabsContent value="res" className="py-4 space-y-4">
                {selectedUser.reservations.map((r: any) => (
                  <div key={r.reservation_id} className="p-4 rounded-xl border flex justify-between items-center">
                    <div>
                      <p className="font-bold">{r.warehouse_name}</p>
                      <p className="text-xs text-muted-foreground">ID: {r.reservation_id}</p>
                    </div>
                    <Badge>{r.status}</Badge>
                  </div>
                ))}
                {selectedUser.reservations.length === 0 && <p className="text-center py-8 text-muted-foreground italic">Aucune réservation.</p>}
              </TabsContent>

              <TabsContent value="msg" className="py-4 space-y-3">
                {selectedUser.recent_messages.map((m: any, i: number) => (
                  <div key={i} className="p-3 rounded-lg bg-muted/30 text-sm">
                    <p className="text-xs text-muted-foreground mb-1">{new Date(m.created_at).toLocaleString()}</p>
                    <p>{m.message}</p>
                  </div>
                ))}
                {selectedUser.recent_messages.length === 0 && <p className="text-center py-8 text-muted-foreground italic">Aucun message.</p>}
              </TabsContent>
            </Tabs>

            <div className="mt-12 flex gap-3 pt-6 border-t">
              <Button 
                variant="outline" 
                className="flex-1"
                onClick={() => handleToggleStatus(selectedUser.user_id)}
              >
                {selectedUser.is_active ? "Suspendre le compte" : "Activer le compte"}
              </Button>
              <Button 
                variant="destructive" 
                className="flex-1"
                onClick={() => handleDeleteUser(selectedUser.user_id)}
              >
                Supprimer Définitivement
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
