import { getCurrentUser } from '../../utils/auth'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'

export default defineEventHandler((event) => {
  try {
    const user = getCurrentUser(event)
    return sendSafeSuccess(user)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'No autenticado'
    return sendSafeError(msg, 401)
  }
})
