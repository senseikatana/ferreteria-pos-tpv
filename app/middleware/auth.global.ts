export default defineNuxtRouteMiddleware(async (to) => {
  const { user, isChecked, checkAuth } = useAuth()

  // En el cliente, si no se verificó la sesión, la comprobamos
  if (import.meta.client && !isChecked.value) {
    await checkAuth()
  }

  const isPublicRoute = to.path === '/login'

  // Si no está autenticado y no es ruta pública, redirigir al login
  if (!user.value && !isPublicRoute) {
    return navigateTo('/login')
  }

  // Si ya está autenticado e intenta ir a login, redirigir a ventas
  if (user.value && isPublicRoute) {
    return navigateTo('/ventas')
  }

  // Rutas exclusivas de Administrador
  const adminRoutes = ['/reportes', '/usuarios']
  if (adminRoutes.some((route) => to.path.startsWith(route))) {
    if (user.value?.role !== 'ADMIN') {
      return navigateTo('/ventas')
    }
  }
})
