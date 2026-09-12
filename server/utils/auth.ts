import jwt from 'jsonwebtoken'
import type { H3Event } from 'h3'
import { getCookie, getHeader, createError } from 'h3'
import type { UserRole } from '../core/domain/entities'

const JWT_SECRET = process.env.JWT_SECRET || 'pos-universal-secret-key-change-in-prod-2026'

export interface TokenPayload {
  userId: string
  username: string
  fullName: string
  role: UserRole
}

export function signToken(payload: TokenPayload): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: '12h' })
}

export function verifyToken(token: string): TokenPayload | null {
  try {
    return jwt.verify(token, JWT_SECRET) as TokenPayload
  } catch {
    return null
  }
}

export function getCurrentUser(event: H3Event): TokenPayload {
  const cookieToken = getCookie(event, 'auth_token')
  const authHeader = getHeader(event, 'authorization')
  const bearerToken = authHeader?.startsWith('Bearer ') ? authHeader.substring(7) : null

  const token = cookieToken || bearerToken

  if (!token) {
    throw createError({
      statusCode: 401,
      statusMessage: 'No autenticado. Por favor inicie sesión.',
    })
  }

  const user = verifyToken(token)
  if (!user) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Sesión inválida o expirada.',
    })
  }

  return user
}

export function requireAdmin(event: H3Event): TokenPayload {
  const user = getCurrentUser(event)
  if (user.role !== 'ADMIN') {
    throw createError({
      statusCode: 403,
      statusMessage: 'Acceso denegado: se requieren permisos de Administrador.',
    })
  }
  return user
}
