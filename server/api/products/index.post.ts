import { z } from 'zod'
import { posFacade } from '../../core/facade/PosFacade'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { getCurrentUser } from '../../utils/auth'

const CreateProductSchema = z.object({
  barcode: z.string().min(1, 'El código de barras es requerido'),
  name: z.string().min(1, 'El nombre del producto es requerido'),
  category: z.string().optional(),
  salePrice: z.number().positive('El precio de venta debe ser mayor a 0'),
  costPrice: z.number().min(0).optional(),
  stock: z.number().int().min(0, 'El stock no puede ser negativo'),
  minStock: z.number().int().min(0).optional(),
  unit: z.string().default('unit'),
  metadata: z.record(z.unknown()).optional(),
})

export default defineEventHandler(async (event) => {
  try {
    getCurrentUser(event)
    const body = await readBody(event)
    const parsed = CreateProductSchema.safeParse(body)

    if (!parsed.success) {
      return sendSafeError(parsed.error.errors[0]?.message || 'Datos de producto inválidos', 400)
    }

    const existing = await posFacade.lookupProductByBarcode(parsed.data.barcode)
    if (existing) {
      return sendSafeError(`Ya existe un producto registrado con el código «${parsed.data.barcode}».`, 409)
    }

    const created = await posFacade.createProduct(parsed.data)
    return sendSafeSuccess(created)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al crear producto.'
    return sendSafeError(msg, 500)
  }
})
