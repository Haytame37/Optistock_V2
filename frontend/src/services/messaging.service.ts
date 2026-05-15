import api from "./api"

export async function getMessagingRequests() {
  const { data } = await api.get("/messaging/requests")
  return data
}

export async function contactOwner(warehouseId: string, ownerId: number, productName: string, message: string) {
  const { data } = await api.post(`/messaging/contact?warehouse_id=${warehouseId}&owner_id=${ownerId}&product_name=${productName}&message=${encodeURIComponent(message)}`)
  return data
}

export async function respondToRequest(requestId: string, action: "accepted" | "rejected") {
  const { data } = await api.post(`/messaging/respond/${requestId}?action=${action}`)
  return data
}

export async function getChatMessages(requestId: string) {
  const { data } = await api.get(`/messaging/chat/${requestId}`)
  return data
}

export async function sendChatMessage(requestId: string, message: string) {
  const { data } = await api.post(`/messaging/chat/${requestId}?msg=${encodeURIComponent(message)}`)
  return data
}

export async function sendRentalOffer(requestId: string, price: number, startDate: string) {
  const { data } = await api.post(`/messaging/offer/${requestId}?price=${price}&start_date=${startDate}`)
  return data
}

export async function acceptRentalOffer(requestIdOrWarehouseId: string) {
  const { data } = await api.post(`/messaging/reservation/${requestIdOrWarehouseId}/accept`)
  return data
}

export async function deleteMessagingRequest(requestId: string) {
  const { data } = await api.delete(`/messaging/request/${requestId}`)
  return data
}
