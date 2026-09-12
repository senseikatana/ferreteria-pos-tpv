import { z } from 'zod'
import { prisma } from '../../utils/prisma'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { requireAdmin } from '../../utils/auth'

const ToggleUserSchema = z.object({
  userId: z.string().min(1),
  isActive: z.boolean(),
})

export default defineEventHandler(async (event) => {
  try {
    const admin = requireAdmin(event)
    const body = await readBody(event)
    const parsed = ToggleUserSchema.safeParse(body)

    if (!parsed.success) {
      return sendSafeError(parsed.error.errors[0]?.message || 'Datos inválidos', 400)
    }

    if (parsed.data.userId === admin.userId) {
      return sendSafeError('No puedes desactivar tu propio usuario administrador.', 400)
    }

    const updated = await prisma.user.update({
      where: { id: parsed.data.userId },
      data: { isActive: parsed.data.isActive },
      select: { id: true, username: true, isActive: true },
    })

    return sendSafeSuccess(updated)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al cambiar estado de usuario.'
    return sendSafeError(msg, 500)
  }
})
