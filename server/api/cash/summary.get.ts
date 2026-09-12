import { posFacade } from '../../core/facade/PosFacade'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { getCurrentUser } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  try {
    getCurrentUser(event)
    const summary = await posFacade.getTodaySummary()
    return sendSafeSuccess(summary)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al obtener resumen de caja.'
    return sendSafeError(msg, 500)
  }
})
