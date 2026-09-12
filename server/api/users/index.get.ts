import { prisma } from '../../utils/prisma'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { requireAdmin } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  try {
    requireAdmin(event)
    const users = await prisma.user.findMany({
      select: {
        id: true,
        fullName: true,
        username: true,
        role: true,
        isActive: true,
        createdAt: true,
      },
      orderBy: { fullName: 'asc' },
    })
    return sendSafeSuccess(users)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al listar usuarios.'
    return sendSafeError(msg, 403)
  }
})
