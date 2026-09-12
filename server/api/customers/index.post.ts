import { z } from 'zod'
import { posFacade } from '../../core/facade/PosFacade'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { getCurrentUser } from '../../utils/auth'

const CreateCustomerSchema = z.object({
  name: z.string().min(2, 'El nombre debe tener al menos 2 caracteres'),
  phone: z.string().optional(),
  email: z.string().email('Email inválido').optional().or(z.literal('')),
  address: z.string().optional(),
  creditLimit: z.number().min(0, 'El límite no puede ser negativo').default(0),
})

export default defineEventHandler(async (event) => {
  try {
    getCurrentUser(event)
    const body = await readBody(event)
    const parsed = CreateCustomerSchema.safeParse(body)

    if (!parsed.success) {
      return sendSafeError(parsed.error.errors[0]?.message || 'Datos de cliente inválidos', 400)
    }

    const customer = await posFacade.createCustomer(parsed.data)
    return sendSafeSuccess(customer)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al registrar cliente.'
    return sendSafeError(msg, 500)
  }
})
