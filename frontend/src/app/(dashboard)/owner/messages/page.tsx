"use client"

import { useEffect, useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { 
  getMessagingRequests, 
  respondToRequest, 
  getChatMessages, 
  sendChatMessage, 
  sendRentalOffer,
  deleteMessagingRequest 
} from "@/services/messaging.service"
import { Card, CardContent, CardHeader, CardTitle, CardFooter, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { 
  User, 
  MapPin, 
  Package, 
  Calendar, 
  Clock, 
  Check, 
  X, 
  MessageSquare, 
  Send, 
  RefreshCcw,
  PlusCircle,
  TrendingUp,
  History,
  Trash2,
  ArrowLeft
} from "lucide-react"
import { toast } from "sonner"
import { useAuth } from "@/providers/auth-provider"
import { cn } from "@/lib/utils"

export default function OwnerMessagesPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [requests, setRequests] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("pending")
  
  // Chat state
  const [selectedReqId, setSelectedReqId] = useState<string | null>(null)
  const [chatMessages, setChatMessages] = useState<any[]>([])
  const [newMessage, setNewMessage] = useState("")
  const [sending, setSending] = useState(false)
  
  // Offer form
  const [showOfferForm, setShowOfferForm] = useState(false)
  const [offerPrice, setOfferPrice] = useState("")
  const [offerDate, setOfferDate] = useState("")
  
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

  const handleStatusUpdate = async (reqId: string, action: "accepted" | "rejected") => {
    try {
      await respondToRequest(reqId, action)
      toast.success(`Demande ${action === "accepted" ? "acceptée" : "refusée"}`)
      loadRequests()
      if (action === "accepted") setActiveTab("chat")
    } catch (error) {
      toast.error("Erreur mise à jour statut")
    }
  }

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

  const handleSendOffer = async () => {
    if (!selectedReqId || !offerPrice || !offerDate) {
      toast.error("Veuillez remplir tous les champs de l'offre")
      return
    }
    try {
      const res = await sendRentalOffer(selectedReqId, parseFloat(offerPrice), offerDate)
      if (res.ok) {
        toast.success("Offre envoyée !")
        setShowOfferForm(false)
        setOfferPrice("")
        setOfferDate("")
        loadChat(selectedReqId)
      } else {
        toast.error(res.feedback)
      }
    } catch (error) {
      toast.error("Erreur envoi offre")
    }
  }

  const handleDeleteRequest = async (reqId: string) => {
    if (!confirm("Voulez-vous vraiment supprimer cet historique ?")) return
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
  const history = requests.filter(r => r.status !== "pending")

  const selectedRequest = requests.find(r => r.request_id === selectedReqId)

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <RefreshCcw className="h-8 w-8 animate-spin text-primary/30" />
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="mb-2">
        <Button 
          variant="ghost" 
          size="sm" 
          className="gap-2 text-muted-foreground hover:text-foreground pl-0" 
          onClick={() => router.push("/owner")}
        >
          <ArrowLeft className="h-4 w-4" /> Retour au tableau de bord
        </Button>
      </div>
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
            Messagerie Professionnelle
          </h1>
          <p className="text-muted-foreground mt-1">
            Gérez vos négociations et proposez des offres de location.
          </p>
        </div>
        <div className="flex gap-2">
          <Badge variant="outline" className="h-fit py-1 px-3">
            <TrendingUp className="h-3 w-3 mr-2 text-green-500" />
            {active.length} Discussions actives
          </Badge>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3 h-12 bg-muted/50 p-1 rounded-xl">
          <TabsTrigger value="pending" className="rounded-lg data-[state=active]:bg-background data-[state=active]:shadow-sm transition-all">
            Nouvelles demandes {pending.length > 0 && <Badge className="ml-2 bg-red-500">{pending.length}</Badge>}
          </TabsTrigger>
          <TabsTrigger value="chat" className="rounded-lg data-[state=active]:bg-background data-[state=active]:shadow-sm transition-all">
            Chat actif
          </TabsTrigger>
          <TabsTrigger value="history" className="rounded-lg data-[state=active]:bg-background data-[state=active]:shadow-sm transition-all">
            Historique complet
          </TabsTrigger>
        </TabsList>

        <TabsContent value="pending" className="mt-6">
          {pending.length === 0 ? (
            <Card className="border-dashed flex flex-col items-center py-16 text-center">
              <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
                <Clock className="h-6 w-6 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-medium">Aucune nouvelle demande</h3>
              <p className="text-muted-foreground max-w-xs mx-auto mt-2 text-sm">
                Les demandes des clients logistiques apparaîtront ici dès qu'ils vous contacteront.
              </p>
            </Card>
          ) : (
            <div className="grid gap-4">
              {pending.map((req) => (
                <Card key={req.request_id} className="overflow-hidden border-blue-100 dark:border-blue-900/50 hover:border-blue-300 transition-all shadow-sm">
                  <div className="flex flex-col md:flex-row">
                    <div className="p-6 flex-1">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <CardTitle className="text-xl mb-1">{req.warehouse_name || "Entrepôt sans nom"}</CardTitle>
                          <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <MapPin className="h-3.5 w-3.5" /> {req.warehouse_address}
                          </p>
                        </div>
                        <Badge variant="secondary" className="bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                          Reçu le {new Date(req.created_at).toLocaleDateString()}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 bg-muted/30 p-4 rounded-xl text-sm mb-4 border border-border/50">
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4 text-primary" />
                          <div>
                            <p className="text-[10px] uppercase font-bold text-muted-foreground/50">Client Logistique</p>
                            <p className="font-semibold">{req.researcher_first_name}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Package className="h-4 w-4 text-primary" />
                          <div>
                            <p className="text-[10px] uppercase font-bold text-muted-foreground/50">Produit</p>
                            <p className="font-semibold">{req.product_name || "Non spécifié"}</p>
                          </div>
                        </div>
                      </div>

                      <div className="relative p-4 bg-blue-50/50 dark:bg-blue-900/10 rounded-xl border border-blue-100 dark:border-blue-800/30 italic text-sm text-blue-900 dark:text-blue-200">
                        <span className="absolute -top-3 left-4 bg-background px-2 text-[10px] font-bold text-blue-500 uppercase">Message</span>
                        "{req.message}"
                      </div>
                    </div>
                    <div className="bg-muted/30 p-4 flex md:flex-col justify-center gap-2 border-l border-border/50">
                      <Button 
                        onClick={() => handleStatusUpdate(req.request_id, "accepted")} 
                        className="bg-green-600 hover:bg-green-700 w-full"
                      >
                        <Check className="mr-2 h-4 w-4" /> Accepter
                      </Button>
                      <Button 
                        onClick={() => handleStatusUpdate(req.request_id, "rejected")} 
                        variant="outline" 
                        className="text-red-500 hover:text-red-600 border-red-200 w-full"
                      >
                        <X className="mr-2 h-4 w-4" /> Refuser
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="chat" className="mt-6 border rounded-2xl overflow-hidden bg-background h-[600px] flex shadow-lg">
          {/* Liste conversations */}
          <div className="w-80 border-r bg-muted/20 flex flex-col">
            <div className="p-4 border-b bg-muted/40">
              <h3 className="font-semibold flex items-center gap-2">
                <MessageSquare className="h-4 w-4" /> Conversations
              </h3>
            </div>
            <ScrollArea className="flex-1">
              {active.length === 0 ? (
                <p className="p-8 text-center text-xs text-muted-foreground italic">Aucune conversation active</p>
              ) : (
                <div className="p-2 space-y-1">
                  {active.map(req => (
                    <button
                      key={req.request_id}
                      onClick={() => setSelectedReqId(req.request_id)}
                      className={cn(
                        "w-full text-left p-3 rounded-xl transition-all flex items-center gap-3 group",
                        selectedReqId === req.request_id 
                          ? "bg-primary text-primary-foreground shadow-md" 
                          : "hover:bg-muted/50"
                      )}
                    >
                      <div className={cn(
                        "h-10 w-10 rounded-full flex items-center justify-center font-bold text-sm",
                        selectedReqId === req.request_id ? "bg-white/20" : "bg-primary/10 text-primary"
                      )}>
                        {req.researcher_first_name?.charAt(0) || "C"}
                      </div>
                      <div className="flex-1 overflow-hidden">
                        <p className="font-semibold text-sm truncate">{req.warehouse_name}</p>
                        <p className={cn("text-xs truncate opacity-70", selectedReqId === req.request_id ? "" : "text-muted-foreground")}>
                          {req.researcher_first_name}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className={cn(
                          "h-7 w-7 p-0 opacity-0 group-hover:opacity-100 transition-opacity",
                          selectedReqId === req.request_id ? "text-white hover:text-red-200" : "text-muted-foreground hover:text-red-500"
                        )}
                        onClick={(e) => { e.stopPropagation(); handleDeleteRequest(req.request_id); }}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </button>
                  ))}
                </div>
              )}
            </ScrollArea>
          </div>

          {/* Chat Window */}
          <div className="flex-1 flex flex-col bg-background">
            {selectedReqId ? (
              <>
                <div className="p-4 border-b flex justify-between items-center bg-muted/10">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold">
                      {selectedRequest?.researcher_first_name?.charAt(0) || "C"}
                    </div>
                    <div>
                      <h4 className="font-bold text-sm">{selectedRequest?.researcher_first_name}</h4>
                      <p className="text-[10px] text-muted-foreground">Entrepôt : {selectedRequest?.warehouse_name}</p>
                    </div>
                  </div>
                  <div className="flex gap-2 items-center">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="rounded-full gap-2 border-primary/20 text-primary hover:bg-primary/5"
                      onClick={() => setShowOfferForm(!showOfferForm)}
                    >
                      <TrendingUp className="h-4 w-4" /> 
                      {showOfferForm ? "Annuler l'offre" : "Proposer offre"}
                    </Button>
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

                {showOfferForm && (
                  <div className="p-4 bg-primary/5 border-b animate-in slide-in-from-top duration-300">
                    <h5 className="text-xs font-bold uppercase text-primary mb-3">Nouvelle offre de location</h5>
                    <div className="grid grid-cols-2 gap-3 mb-3">
                      <div>
                        <label className="text-[10px] font-bold text-muted-foreground mb-1 block">PRIX PROPOSÉ (DH)</label>
                        <Input 
                          type="number" 
                          placeholder="Ex: 5000" 
                          value={offerPrice}
                          onChange={e => setOfferPrice(e.target.value)}
                          className="h-9"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] font-bold text-muted-foreground mb-1 block">DATE DE DÉBUT</label>
                        <Input 
                          type="date" 
                          value={offerDate}
                          onChange={e => setOfferDate(e.target.value)}
                          className="h-9"
                        />
                      </div>
                    </div>
                    <Button className="w-full h-9 gap-2" onClick={handleSendOffer}>
                      <Send className="h-3.5 w-3.5" /> Envoyer l'offre formelle
                    </Button>
                  </div>
                )}

                <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/5 scroll-smooth" ref={scrollRef}>
                  {chatMessages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-muted-foreground/40 italic text-sm">
                      <MessageSquare className="h-8 w-8 mb-2" />
                      Pas encore de messages. Dites bonjour !
                    </div>
                  ) : (
                    chatMessages.map((m, idx) => {
                      const isMe = m.sender_role === "owner"
                      return (
                        <div key={m.message_id || idx} className={cn("flex w-full", isMe ? "justify-end" : "justify-start")}>
                          <div className={cn(
                            "max-w-[75%] rounded-2xl p-3 shadow-sm text-sm relative transition-all",
                            isMe 
                              ? "bg-primary text-primary-foreground rounded-br-none" 
                              : "bg-background border border-border/50 rounded-bl-none"
                          )}>
                            {/* Détection d'offre (Simple check sur le texte car c'est injecté par le backend) */}
                            {m.message.includes("**OFFRE DE LOCATION**") ? (
                              <div className="space-y-2">
                                <div className="flex items-center gap-2 border-b border-white/20 pb-2 mb-2">
                                  <TrendingUp className="h-4 w-4" />
                                  <span className="font-bold">OFFRE DE LOCATION</span>
                                </div>
                                <p className="whitespace-pre-line leading-relaxed">{m.message}</p>
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
                    })
                  )}
                </div>

                <div className="p-4 border-t bg-background">
                  <div className="flex gap-2">
                    <Input 
                      placeholder="Écrivez votre message..." 
                      className="rounded-full px-4 border-muted-foreground/20 focus-visible:ring-primary"
                      value={newMessage}
                      onChange={e => setNewMessage(e.target.value)}
                      onKeyDown={e => e.key === "Enter" && handleSendMessage()}
                    />
                    <Button 
                      onClick={handleSendMessage} 
                      disabled={sending || !newMessage.trim()} 
                      className="rounded-full h-10 w-10 p-0 shrink-0 shadow-md"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground bg-muted/5">
                <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center mb-4">
                  <MessageSquare className="h-10 w-10 text-muted-foreground/30" />
                </div>
                <h3 className="text-lg font-semibold text-foreground/70">Sélectionnez une discussion</h3>
                <p className="text-sm max-w-xs text-center mt-2">
                  Choisissez un client logistique dans la liste de gauche pour négocier les conditions de location.
                </p>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="history" className="mt-6">
          <Card className="rounded-2xl border shadow-sm">
            <CardHeader className="border-b bg-muted/20">
              <div className="flex items-center gap-2">
                <History className="h-5 w-5 text-primary" />
                <CardTitle>Historique des interactions</CardTitle>
              </div>
              <CardDescription>Liste de toutes les demandes traitées et en cours.</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-muted/50 text-muted-foreground font-medium text-left">
                      <th className="p-4">Entrepôt</th>
                      <th className="p-4">Client Logistique</th>
                      <th className="p-4">Produit</th>
                      <th className="p-4">Statut</th>
                      <th className="p-4">Date</th>
                      <th className="p-4 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {history.map(req => (
                      <tr key={req.request_id} className="hover:bg-muted/30 transition-colors">
                        <td className="p-4 font-medium">{req.warehouse_name}</td>
                        <td className="p-4">{req.researcher_first_name}</td>
                        <td className="p-4">{req.product_name || "—"}</td>
                        <td className="p-4">
                          <Badge variant={req.status === "accepted" ? "outline" : "secondary"} className={cn(
                            req.status === "accepted" ? "text-green-500 border-green-200" : 
                            req.status === "rejected" ? "text-red-400 border-red-100" : ""
                          )}>
                            {req.status === "accepted" ? "Chat Actif" : req.status === "rejected" ? "Refusé" : req.status}
                          </Badge>
                        </td>
                        <td className="p-4 text-muted-foreground">{new Date(req.created_at).toLocaleDateString()}</td>
                        <td className="p-4 text-center">
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="h-8 w-8 text-muted-foreground hover:text-red-500"
                            onClick={() => handleDeleteRequest(req.request_id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                    {history.length === 0 && (
                      <tr>
                        <td colSpan={6} className="p-8 text-center text-muted-foreground italic">Aucun historique disponible</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
