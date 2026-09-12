export interface DomainEvent<T = unknown> {
  name: string
  occurredOn: Date
  payload: T
}

export interface SaleCompletedPayload {
  saleId: string
  total: number
  userId: string
  customerId?: string | null
  items: { productId: string; productName: string; quantity: number }[]
}

export interface LowStockPayload {
  productId: string
  productName: string
  remainingStock: number
  minStock: number
}
