import { posFacade } from '../../core/facade/PosFacade'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { getCurrentUser } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  try {
    getCurrentUser(event)
    const query = getQuery(event)
    const withDebt = query.withDebt === 'true'

    const customers = withDebt
      ? await posFacade.listCustomersWithDebt()
      : await posFacade.listCustomers()

    return sendSafeSuccess(customers)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al consultar clientes.'
    return sendSafeError(msg, 500)
  }
})
