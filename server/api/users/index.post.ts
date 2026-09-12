import { z } from 'zod'
import bcrypt from 'bcrypt'
import { prisma } from '../../utils/prisma'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { requireAdmin } from '../../utils/auth'

const CreateUserSchema = z.object({
  fullName: z.string().min(2, 'El nombre debe tener al menos 2 caracteres'),
  username: z.string().min(3, 'El usuario debe tener al menos 3 caracteres'),
  password: z.string().min(6, 'La contraseña debe tener al menos 6 caracteres'),
  role: z.enum(['ADMIN', 'CASHIER']).default('CASHIER'),
})

export default defineEventHandler(async (event) => {
  try {
    requireAdmin(event)
    const body = await readBody(event)
    const parsed = CreateUserSchema.safeParse(body)

    if (!parsed.success) {
      return sendSafeError(parsed.error.errors[0]?.message || 'Datos de usuario inválidos', 400)
    }

    const existing = await prisma.user.findUnique({
      where: { username: parsed.data.username.trim() },
    })

    if (existing) {
      return sendSafeError(`El nombre de usuario «${parsed.data.username}» ya está en uso.`, 409)
    }

    const passwordHash = await bcrypt.hash(parsed.data.password, 10)

    const user = await prisma.user.create({
      data: {
        fullName: parsed.data.fullName.trim(),
        username: parsed.data.username.trim(),
        passwordHash,
        role: parsed.data.role,
        isActive: true,
      },
      select: {
        id: true,
        fullName: true,
        username: true,
        role: true,
        isActive: true,
        createdAt: true,
      },
    })

    return sendSafeSuccess(user)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al crear usuario.'
    return sendSafeError(msg, 500)
  }
})
