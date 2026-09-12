import { z } from 'zod'
import bcrypt from 'bcrypt'
import { prisma } from '../../utils/prisma'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { requireAdmin } from '../../utils/auth'

const ResetPasswordSchema = z.object({
  userId: z.string().min(1),
  newPassword: z.string().min(6, 'La nueva contraseña debe tener al menos 6 caracteres'),
})

export default defineEventHandler(async (event) => {
  try {
    requireAdmin(event)
    const body = await readBody(event)
    const parsed = ResetPasswordSchema.safeParse(body)

    if (!parsed.success) {
      return sendSafeError(parsed.error.errors[0]?.message || 'Datos inválidos', 400)
    }

    const passwordHash = await bcrypt.hash(parsed.data.newPassword, 10)

    await prisma.user.update({
      where: { id: parsed.data.userId },
      data: { passwordHash },
    })

    return sendSafeSuccess({ message: 'Contraseña actualizada correctamente.' })
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al cambiar contraseña.'
    return sendSafeError(msg, 500)
  }
})
