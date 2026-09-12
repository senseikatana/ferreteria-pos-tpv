import bcrypt from 'bcrypt'
import { z } from 'zod'
import { prisma } from '../../utils/prisma'
import { signToken } from '../../utils/auth'
import { sendSafeSuccess, sendSafeError } from '../../utils/response'
import { setCookie } from 'h3'

const LoginSchema = z.object({
  username: z.string().min(1, 'El nombre de usuario es requerido'),
  password: z.string().min(1, 'La contraseña es requerida'),
})

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const parsed = LoginSchema.safeParse(body)

    if (!parsed.success) {
      return sendSafeError(parsed.error.errors[0]?.message || 'Datos inválidos', 400)
    }

    const { username, password } = parsed.data
    const user = await prisma.user.findUnique({
      where: { username: username.trim() },
    })

    if (!user) {
      return sendSafeError('Usuario o contraseña incorrectos.', 401)
    }

    if (!user.isActive) {
      return sendSafeError('El usuario se encuentra desactivado. Contacte al administrador.', 403)
    }

    const isValidPassword = await bcrypt.compare(password, user.passwordHash)
    if (!isValidPassword) {
      return sendSafeError('Usuario o contraseña incorrectos.', 401)
    }

    const token = signToken({
      userId: user.id,
      username: user.username,
      fullName: user.fullName,
      role: user.role,
    })

    // Cookie segura httpOnly
    setCookie(event, 'auth_token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
      maxAge: 60 * 60 * 12, // 12 horas
    })

    return sendSafeSuccess({
      id: user.id,
      username: user.username,
      fullName: user.fullName,
      role: user.role,
      token,
    })
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error interno al autenticar.'
    return sendSafeError(msg, 500)
  }
})
