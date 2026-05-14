"use client"

import { useEffect, useState } from "react"
import { GlassCard } from "@/components/shared/glass-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { KpiCard } from "@/components/shared/kpi-card"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { getMessages, getChat, sendChat } from "@/services/researcher.service"
import { toast } from "sonner"
import { formatDate } from "@/lib/utils"

interface Message {
  request_id: string
  warehouse_name?: string
  warehouse_address?: string
  owner_first_name?: string
  product_name?: string
  message?: string
  status: string
  created_at?: string
  updated_at?: string
}

interface ChatMsg {
  message_id: string
  sender_id: number
  sender_role: string
  message: string
  created_at?: string
}

export default function MessagesPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedRequest, setSelectedRequest] = useState<string | null>(null)
  const [chatMessages, setChatMessages] = useState<ChatMsg[]>([])
  const [newMessage, setNewMessage] = useState("")
  const [sending, setSending] = useState(false)
  const [userId, setUserId] = useState<number>(0)

  useEffect(() => {
    const userStr = localStorage.getItem("user")
    if (userStr) {
      try { setUserId(JSON.parse(userStr).user_id) } catch {}
    }
    loadMessages()
  }, [])

  const loadMessages = async () => {
    try {
      const data = await getMessages()
      setMessages(data || [])
    } catch {
      toast.error("Erreur chargement messages")
    } finally {
      setLoading(false)
    }
  }

  const loadChat = async (requestId: string) => {
    setSelectedRequest(requestId)
    try {
      const data = await getChat(requestId)
      setChatMessages(data || [])
    } catch {
      setChatMessages([])
    }
  }

  const handleSend = async () => {
    if (!selectedRequest || !newMessage.trim()) return
    setSending(true)
    try {
      await sendChat(selectedRequest, newMessage.trim())
      setNewMessage("")
      loadChat(selectedRequest)
    } catch {
      toast.error("Erreur envoi message")
    } finally {
      setSending(false)
    }
  }

  const statusCount = (status: string) => messages.filter((m) => m.status === status).length

  if (loading) return <div className="space-y-4">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-20" />)}</div>

  const tabs = [
    { value: "all", label: `Toutes (${messages.length})` },
    { value: "accepted", label: `Chat (${statusCount("accepted")})` },
    { value: "pending", label: `En attente (${statusCount("pending")})` },
    { value: "rejected", label: `Refusées (${statusCount("rejected")})` },
  ]

  const filterByStatus = (status: string) => status === "all" ? messages : messages.filter((m) => m.status === status)

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        <KpiCard label="En attente" value={statusCount("pending")} color="#f59e0b" />
        <KpiCard label="Acceptées" value={statusCount("accepted")} color="#22c55e" />
        <KpiCard label="Refusées" value={statusCount("rejected")} color="#ef4444" />
      </div>

      <Tabs defaultValue="all">
        <TabsList>
          {tabs.map((t) => <TabsTrigger key={t.value} value={t.value}>{t.label}</TabsTrigger>)}
        </TabsList>
        {tabs.map((tab) => (
          <TabsContent key={tab.value} value={tab.value} className="space-y-3">
            {filterByStatus(tab.value).length === 0 ? (
              <GlassCard className="p-8 text-center text-muted-foreground">
                Aucune demande dans cette catégorie
              </GlassCard>
            ) : (
              filterByStatus(tab.value).map((msg) => (
                <GlassCard
                  key={msg.request_id}
                  className={`p-4 cursor-pointer transition-all hover:shadow-md ${
                    selectedRequest === msg.request_id ? "ring-2 ring-primary" : ""
                  }`}
                  onClick={() => msg.status === "accepted" && loadChat(msg.request_id)}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-semibold">{msg.warehouse_name || "Entrepôt"}</p>
                      <p className="text-xs text-muted-foreground">{msg.warehouse_address}</p>
                    </div>
                    <Badge variant={msg.status === "accepted" ? "success" : msg.status === "pending" ? "warning" : "danger"}>
                      {msg.status === "accepted" ? "Acceptée" : msg.status === "pending" ? "En attente" : "Refusée"}
                    </Badge>
                  </div>
                  <p className="mt-2 text-sm">
                    {msg.owner_first_name} · {msg.product_name} · {formatDate(msg.created_at || "")}
                  </p>
                  {tab.value === "accepted" && selectedRequest === msg.request_id && (
                    <div className="mt-4 border-t pt-4">
                      <div className="max-h-64 overflow-y-auto space-y-2 mb-3">
                        {chatMessages.map((cm, i) => (
                          <div key={i} className={`flex ${cm.sender_id === userId ? "justify-end" : "justify-start"}`}>
                            <div className={`max-w-[70%] rounded-2xl px-4 py-2 text-sm ${
                              cm.sender_id === userId
                                ? "bg-primary text-primary-foreground rounded-br-sm"
                                : "bg-muted rounded-bl-sm"
                            }`}>
                              <p>{cm.message}</p>
                              <p className="text-[10px] opacity-60 mt-1">{cm.created_at ? formatDate(cm.created_at) : ""}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="flex gap-2">
                        <Input
                          placeholder="Écrire un message..."
                          value={newMessage}
                          onChange={(e) => setNewMessage(e.target.value)}
                          onKeyDown={(e) => e.key === "Enter" && handleSend()}
                        />
                        <Button onClick={handleSend} disabled={sending}>Envoyer</Button>
                      </div>
                    </div>
                  )}
                </GlassCard>
              ))
            )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}
