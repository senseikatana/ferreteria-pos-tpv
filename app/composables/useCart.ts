export interface CartItem {
  productId: string
  barcode: string
  name: string
  unitPrice: number
  quantity: number
  subtotal: number
}

export interface Product {
  id: string
  barcode: string
  name: string
  category?: string | null
  salePrice: number
  costPrice: number
  stock: number
  minStock: number
  unit: string
  isActive: boolean
}

/**
 * Composable que gestiona el carrito del POS.
 * Usa `useState` de Nuxt para que el estado persista
 * entre navegaciones de página (no se borra al cambiar de sección).
 */
export function useCart() {
  const items = useState<CartItem[]>('pos_cart', () => [])

  const total = computed(() =>
    items.value.reduce((acc, item) => acc + item.subtotal, 0)
  )

  const totalUnits = computed(() =>
    items.value.reduce((acc, item) => acc + item.quantity, 0)
  )

  const itemCount = computed(() => items.value.length)

  /**
   * Agrega un producto al carrito o incrementa cantidad si ya existe.
   * Retorna { ok, message } para feedback visual.
   */
  const addItem = (prod: Product): { ok: boolean; message?: string } => {
    if (prod.stock <= 0) {
      return { ok: false, message: `«${prod.name}» sin stock disponible.` }
    }

    const existing = items.value.find((i) => i.productId === prod.id)

    if (existing) {
      if (existing.quantity + 1 > prod.stock) {
        return {
          ok: false,
          message: `Stock máximo alcanzado para «${prod.name}» (${prod.stock} un.).`,
        }
      }
      existing.quantity++
      existing.subtotal = existing.quantity * existing.unitPrice
    } else {
      items.value.push({
        productId: prod.id,
        barcode: prod.barcode,
        name: prod.name,
        unitPrice: prod.salePrice,
        quantity: 1,
        subtotal: prod.salePrice,
      })
    }

    return { ok: true, message: `«${prod.name}» agregado al carrito.` }
  }

  const updateQuantity = (index: number, delta: number) => {
    const item = items.value[index]
    if (!item) return

    const nextQty = item.quantity + delta
    if (nextQty <= 0) {
      items.value.splice(index, 1)
    } else {
      item.quantity = nextQty
      item.subtotal = item.quantity * item.unitPrice
    }
  }

  const removeItem = (index: number) => {
    items.value.splice(index, 1)
  }

  const clearCart = () => {
    items.value = []
  }

  return {
    items,
    total,
    totalUnits,
    itemCount,
    addItem,
    updateQuantity,
    removeItem,
    clearCart,
  }
}
