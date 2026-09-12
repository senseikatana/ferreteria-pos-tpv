import { z } from 'zod'
import { posFacade } from '../../core/facade/PosFacade'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { getCurrentUser } from '../../utils/auth'

const CloseRegisterSchema = z.object({
  notes: z.string().optional(),
})

export default defineEventHandler(async (event) => {
  try {
    const user = getCurrentUser(event)
    const body = await readBody(event).catch(() => ({}))
    const parsed = CloseRegisterSchema.safeParse(body)

    const result = await posFacade.performCashRegisterClose(
      user.userId,
      parsed.success ? parsed.data.notes : undefined
    )

    return sendSafeSuccess(result)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al cerrar caja.'
    return sendSafeError(msg, 500)
  }
})
