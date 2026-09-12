export interface CurrentUser {
  userId: string
  username: string
  fullName: string
  role: 'ADMIN' | 'CASHIER'
}

export function useAuth() {
  const user = useState<CurrentUser | null>('auth_user', () => null)
  const isChecked = useState<boolean>('auth_checked', () => false)
  const router = useRouter()
  const { post, get } = useKatanaApi()

  const checkAuth = async () => {
    try {
      const res = await get<CurrentUser>('auth/me')
      if (res.ok && res.data) {
        user.value = res.data
      } else {
        user.value = null
      }
    } catch {
      user.value = null
    } finally {
      isChecked.value = true
    }
  }

  const login = async (username: string, password: string) => {
    const res = await post<any>('auth/login', { username, password })
    if (res.ok && res.data) {
      user.value = {
        userId: res.data.id,
        username: res.data.username,
        fullName: res.data.fullName,
        role: res.data.role,
      }
      return { success: true }
    }
    return { success: false, error: res.error?.message || 'Error al iniciar sesión' }
  }

  const logout = async () => {
    await post('auth/logout')
    user.value = null
    router.push('/login')
  }

  const isAdmin = computed(() => user.value?.role === 'ADMIN')

  return {
    user,
    isChecked,
    isAdmin,
    checkAuth,
    login,
    logout,
  }
}
