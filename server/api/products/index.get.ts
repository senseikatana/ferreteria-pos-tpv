import { posFacade } from '../../core/facade/PosFacade'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { getCurrentUser } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  try {
    getCurrentUser(event) // Requiere autenticación
    const query = getQuery(event)

    const barcode = query.barcode as string | undefined
    const searchTerm = (query.query || query.q) as string | undefined

    if (barcode) {
      const product = await posFacade.lookupProductByBarcode(barcode)
      if (!product) {
        return sendSafeError(`Producto no encontrado con el código «${barcode}».`, 404)
      }
      return sendSafeSuccess(product)
    }

    if (searchTerm) {
      const results = await posFacade.searchProducts(searchTerm)
      return sendSafeSuccess(results)
    }

    const allProducts = await posFacade.listProducts()
    return sendSafeSuccess(allProducts)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al consultar productos.'
    return sendSafeError(msg, 500)
  }
})
