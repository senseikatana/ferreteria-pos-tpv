import { deleteCookie } from 'h3'
import { sendSafeSuccess } from '../../utils/response'

export default defineEventHandler((event) => {
  deleteCookie(event, 'auth_token', {
    path: '/',
  })
  return sendSafeSuccess({ message: 'Sesión cerrada exitosamente.' })
})
