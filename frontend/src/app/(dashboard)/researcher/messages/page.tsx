"use client"

import { useEffect, useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { 
  getMessagingRequests, 
  getChatMessages, 
  sendChatMessage, 
  acceptRentalOffer,
  deleteMessagingRequest 
} from "@/services/messaging.service"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  MapPin, 
  Package, 
  Calendar, 
  MessageSquare, 
  Send, 
  RefreshCcw,
  CheckCircle2,
  TrendingUp,
  History,
  Store,
  User,
  Trash2
} from "lucide-react"
import { toast } from "sonner"
import { useAuth } from "@/providers/auth-provider"
import { cn } from "@/lib/utils"

export default function ResearcherMessagesPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [requests, setRequests] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("all")
  
  // Chat state
  const [selectedReqId, setSelectedReqId] = useState<string | null>(null)
  const [chatMessages, setChatMessages] = useState<any[]>([])
  const [newMessage, setNewMessage] = useState("")
  const [sending, setSending] = useState(false)
  const [accepting, setAccepting] = useState(false)
  
  const scrollRef = useRef<HTMLDivElement>(null)

  const loadRequests = async () => {
    try {
      const data = await getMessagingRequests()
      setRequests(data || [])
    } catch (error) {
      toast.error("Erreur chargement messages")
    } finally {
      setLoading(false)
    }
  }

  const loadChat = async (reqId: string) => {
    try {
      const data = await getChatMessages(reqId)
      setChatMessages(data || [])
    } catch (error) {
      toast.error("Erreur chargement chat")
    }
  }

  useEffect(() => {
    loadRequests()
  }, [])

  useEffect(() => {
    if (selectedReqId) {
      loadChat(selectedReqId)
      const interval = setInterval(() => loadChat(selectedReqId), 5000)
      return () => clearInterval(interval)
    }
  }, [selectedReqId])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [chatMessages])

  const handleSendMessage = async () => {
    if (!selectedReqId || !newMessage.trim()) return
    setSending(true)
    try {
      await sendChatMessage(selectedReqId, newMessage)
      setNewMessage("")
      loadChat(selectedReqId)
    } catch (error) {
      toast.error("Erreur envoi message")
    } finally {
      setSending(false)
    }
  }

  const handleAcceptOffer = async (warehouseId: string) => {
    setAccepting(true)
    try {
      const res = await acceptRentalOffer(warehouseId)
      toast.success(res.message || "Offre acceptée ! Redirection vers le dashboard IoT...")
      
      // Petit délai pour laisser l'utilisateur lire le message de succès
      setTimeout(() => {
        router.push(`/iot/${warehouseId}`)
      }, 1500)
      
      loadRequests()
      if (selectedReqId) loadChat(selectedReqId)
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || "Erreur lors de l'acceptation"
      toast.error(errorMsg)
    } finally {
      setAccepting(false)
    }
  }

  const handleDeleteRequest = async (reqId: string) => {
    if (!confirm("Voulez-vous vraiment supprimer cet historique ? Cette action est irréversible.")) return
    try {
      await deleteMessagingRequest(reqId)
      toast.success("Historique supprimé")
      setSelectedReqId(null)
      loadRequests()
    } catch (error) {
      toast.error("Erreur lors de la suppression")
    }
  }

  const pending = requests.filter(r => r.status === "pending")
  const active = requests.filter(r => r.status === "accepted")
  const history = requests.filter(r => r.status !== "pending" && r.status !== "accepted")

  const selectedRequest = requests.find(r => r.request_id === selectedReqId)

  const getFilteredRequests = () => {
    if (activeTab === "all") return requests
    if (activeTab === "accepted") return active
    if (activeTab === "pending") return pending
    if (activeTab === "history") return history
    return requests
  }

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <RefreshCcw className="h-8 w-8 animate-spin text-primary/30" />
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-10">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Réponses des Propriétaires</h1>
        <p className="text-muted-foreground mt-1">
          Suivez vos demandes et discutez des conditions de location.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[700px]">
        {/* Sidebar Liste */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-muted/50">
              <TabsTrigger value="all" className="text-xs">Toutes</TabsTrigger>
              <TabsTrigger value="accepted" className="text-xs">Chats</TabsTrigger>
              <TabsTrigger value="pending" className="text-xs">Attente</TabsTrigger>
            </TabsList>
          </Tabs>

          <Card className="flex-1 overflow-hidden border-muted/60 shadow-sm flex flex-col">
            <CardHeader className="py-4 px-4 bg-muted/20 border-b">
              <CardTitle className="text-sm font-bold flex items-center gap-2">
                <Store className="h-4 w-4 text-primary" /> Vos Demandes
              </CardTitle>
            </CardHeader>
            <ScrollArea className="flex-1">
              <div className="p-2 space-y-1">
                {getFilteredRequests().length === 0 ? (
                  <p className="p-8 text-center text-xs text-muted-foreground italic">Aucune demande trouvée</p>
                ) : (
                  getFilteredRequests().map(req => (
                    <button
                      key={req.request_id}
                      onClick={() => setSelectedReqId(req.request_id)}
                      className={cn(
                        "w-full text-left p-4 rounded-xl transition-all border border-transparent",
                        selectedReqId === req.request_id 
                          ? "bg-primary/5 border-primary/20 ring-1 ring-primary/20 shadow-sm" 
                          : "hover:bg-muted/50",
                        "cursor-pointer"
                      )}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <p className={cn("font-bold text-sm truncate flex-1 mr-2", selectedReqId === req.request_id ? "text-primary" : "")}>
                          {req.warehouse_name}
                        </p>
                        <div className="flex items-center gap-2">
                          <Badge 
                            variant="outline" 
                            className={cn(
                              "text-[10px] px-1.5 py-0",
                              req.status === "accepted" ? "bg-green-50 text-green-600 border-green-200" :
                              req.status === "pending" ? "bg-yellow-50 text-yellow-600 border-yellow-200" :
                              "bg-red-50 text-red-600 border-red-200"
                            )}
                          >
                            {req.status === "accepted" ? "ACTIF" : req.status === "pending" ? "ATTENTE" : "REFUSÉ"}
                          </Badge>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 text-muted-foreground hover:text-red-500 p-0"
                            onClick={(e) => { e.stopPropagation(); handleDeleteRequest(req.request_id); }}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <User className="h-3 w-3" />
                        <span>Propriétaire : {req.owner_first_name}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                        <Package className="h-3 w-3" />
                        <span>Produit : {req.product_name}</span>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </ScrollArea>
          </Card>
        </div>

        {/* Chat Window */}
        <div className="lg:col-span-8 flex flex-col h-full border rounded-2xl overflow-hidden bg-background shadow-lg">
          {selectedReqId ? (
            <>
              <div className="p-4 border-b flex justify-between items-center bg-muted/10">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold">
                    {selectedRequest?.owner_first_name?.charAt(0) || "P"}
                  </div>
                  <div>
                    <h4 className="font-bold text-sm">{selectedRequest?.owner_first_name}</h4>
                    <p className="text-[10px] text-muted-foreground">Propriétaire de {selectedRequest?.warehouse_name}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                   <Badge variant="outline" className="text-[10px] text-green-600 border-green-200">
                     Canal de discussion sécurisé
                   </Badge>
                   <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-8 w-8 text-muted-foreground hover:text-red-500 hover:bg-red-50"
                    onClick={() => handleDeleteRequest(selectedReqId)}
                   >
                     <Trash2 className="h-4 w-4" />
                   </Button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-muted/5 scroll-smooth" ref={scrollRef}>
                {chatMessages.map((m, idx) => {
                  const isMe = m.sender_role === "researcher"
                  const isOffer = m.message.includes("**OFFRE DE LOCATION**")
                  
                  return (
                    <div key={m.message_id || idx} className={cn("flex w-full", isMe ? "justify-end" : "justify-start")}>
                      <div className={cn(
                        "max-w-[80%] rounded-2xl p-4 shadow-sm text-sm relative transition-all",
                        isMe 
                          ? "bg-primary text-primary-foreground rounded-br-none" 
                          : isOffer 
                            ? "bg-gradient-to-br from-green-500 to-green-600 text-white border-none rounded-bl-none shadow-green-200"
                            : "bg-background border border-border/50 rounded-bl-none"
                      )}>
                        {isOffer ? (
                          <div className="space-y-3">
                            <div className="flex items-center gap-2 border-b border-white/20 pb-2 mb-2">
                              <TrendingUp className="h-5 w-5" />
                              <span className="font-bold text-base">NOUVELLE OFFRE</span>
                            </div>
                            <p className="whitespace-pre-line leading-relaxed text-sm italic">{m.message}</p>
                            <Button 
                              onClick={() => handleAcceptOffer(selectedRequest?.warehouse_id)}
                              disabled={accepting}
                              className="w-full bg-white text-green-600 hover:bg-green-50 font-bold mt-2"
                            >
                              {accepting ? <RefreshCcw className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4 mr-2" />}
                              ACCEPTER & DÉBLOQUER IOT
                            </Button>
                          </div>
                        ) : (
                          <p className="whitespace-pre-line leading-relaxed">{m.message}</p>
                        )}
                        <span className={cn("block text-[9px] mt-2 opacity-50 text-right", isMe ? "" : "text-muted-foreground")}>
                          {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>

              <div className="p-4 border-t bg-background">
                <div className="flex gap-2">
                  <Input 
                    placeholder={selectedRequest?.status === "pending" ? "En attente d'acceptation du propriétaire..." : "Posez vos questions au propriétaire..."} 
                    className="rounded-full px-4 border-muted-foreground/20 focus-visible:ring-primary"
                    value={newMessage}
                    onChange={e => setNewMessage(e.target.value)}
                    onKeyDown={e => e.key === "Enter" && handleSendMessage()}
                    disabled={selectedRequest?.status === "pending"}
                  />
                  <Button 
                    onClick={handleSendMessage} 
                    disabled={sending || !newMessage.trim() || selectedRequest?.status === "pending"} 
                    className="rounded-full h-10 w-10 p-0 shrink-0 shadow-md"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground bg-muted/5">
              <div className="h-24 w-24 rounded-full bg-muted flex items-center justify-center mb-6">
                <MessageSquare className="h-12 w-12 text-muted-foreground/20" />
              </div>
              <h3 className="text-xl font-bold text-foreground/80">Votre Messagerie</h3>
              <p className="text-sm max-w-sm text-center mt-3 px-6 leading-relaxed">
                {active.length > 0 
                  ? "Sélectionnez une discussion acceptée dans la liste de gauche pour échanger avec le propriétaire."
                  : "Dès qu'un propriétaire accepte votre demande, vous pourrez discuter ici et recevoir des offres de location."}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
