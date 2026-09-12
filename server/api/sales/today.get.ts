import { posFacade } from '../../core/facade/PosFacade'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { getCurrentUser } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  try {
    getCurrentUser(event)
    const sales = await posFacade.getTodaySales()
    return sendSafeSuccess(sales)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al obtener ventas del día.'
    return sendSafeError(msg, 500)
  }
})
