export type UserRole = 'ADMIN' | 'CASHIER'
export type PaymentMethodType = 'CASH' | 'CARD' | 'CREDIT_DEBT'

export interface UserEntity {
  id: string
  fullName: string
  username: string
  role: UserRole
  isActive: boolean
  createdAt: Date
}

export interface ProductEntity {
  id: string
  barcode: string
  sku?: string | null
  name: string
  category?: string | null
  salePrice: number
  costPrice: number
  stock: number
  minStock: number
  unit: string
  isActive: boolean
  metadata?: Record<string, unknown> | null
  createdAt: Date
}

export interface CustomerEntity {
  id: string
  name: string
  taxId?: string | null
  phone?: string | null
  email?: string | null
  address?: string | null
  creditLimit: number
  currentDebt: number
  isActive: boolean
  notes?: string | null
  createdAt: Date
}

export interface CartItemEntity {
  productId: string
  name: string
  quantity: number
  unitPrice: number
  subtotal: number
}

export interface SaleEntity {
  id: string
  userId: string
  customerId?: string | null
  total: number
  receivedAmount?: number | null
  changeAmount?: number | null
  paymentMethod: PaymentMethodType
  isVoided: boolean
  notes?: string | null
  createdAt: Date
  items: CartItemEntity[]
}

export interface CashRegisterSummary {
  cashTotal: number
  cardTotal: number
  creditTotal: number
  grandTotal: number
  salesCount: number
}
