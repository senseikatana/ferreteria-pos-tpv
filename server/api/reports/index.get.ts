import { posFacade } from '../../core/facade/PosFacade'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { requireAdmin } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  try {
    requireAdmin(event) // Solo ADMIN
    const reports = await posFacade.getReports(5)
    return sendSafeSuccess(reports)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al obtener reportes.'
    return sendSafeError(msg, 403)
  }
})
