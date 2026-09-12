import { z } from 'zod'
import { posFacade } from '../../core/facade/PosFacade'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { getCurrentUser } from '../../utils/auth'

const PaymentSchema = z.object({
  customerId: z.string().min(1, 'ID de cliente requerido'),
  amount: z.number().positive('El monto a abonar debe ser mayor a 0'),
  notes: z.string().optional(),
})

export default defineEventHandler(async (event) => {
  try {
    const user = getCurrentUser(event)
    const body = await readBody(event)
    const parsed = PaymentSchema.safeParse(body)

    if (!parsed.success) {
      return sendSafeError(parsed.error.errors[0]?.message || 'Datos de abono inválidos', 400)
    }

    const result = await posFacade.registerCustomerPayment(
      parsed.data.customerId,
      user.userId,
      parsed.data.amount,
      parsed.data.notes
    )

    return sendSafeSuccess(result)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al registrar abono.'
    return sendSafeError(msg, 400)
  }
})
