import { z } from 'zod'
import { posFacade } from '../../core/facade/PosFacade'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { getCurrentUser } from '../../utils/auth'

const SaleItemSchema = z.object({
  productId: z.string().min(1),
  name: z.string().min(1),
  quantity: z.number().int().positive(),
  unitPrice: z.number().positive(),
  subtotal: z.number().positive(),
})

const CreateSaleSchema = z.object({
  items: z.array(SaleItemSchema).min(1, 'El carrito debe tener al menos un producto'),
  paymentMethod: z.enum(['CASH', 'CARD', 'CREDIT_DEBT']),
  customerId: z.string().optional().nullable(),
  receivedAmount: z.number().positive().optional(),
})

export default defineEventHandler(async (event) => {
  try {
    const user = getCurrentUser(event)
    const body = await readBody(event)
    const parsed = CreateSaleSchema.safeParse(body)

    if (!parsed.success) {
      return sendSafeError(parsed.error.errors[0]?.message || 'Datos de venta inválidos', 400)
    }

    const sale = await posFacade.processSale({
      userId: user.userId,
      customerId: parsed.data.customerId,
      items: parsed.data.items,
      paymentMethod: parsed.data.paymentMethod,
      receivedAmount: parsed.data.receivedAmount,
    })

    return sendSafeSuccess(sale)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al procesar la venta.'
    return sendSafeError(msg, 400)
  }
})
