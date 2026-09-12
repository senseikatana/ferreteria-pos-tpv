import { ref } from 'vue'

export interface KatanaResponse<T> {
  ok: boolean
  data: T | null
  error: { message: string; status: number } | null
}

let katanaInitialized = false
let katanaModule: any = null

/**
 * KatanaKit CDN Integration Composable.
 * Carga e inicializa la librería del usuario desde el CDN (esm.sh) en el cliente,
 * proveyendo acceso al adaptador y a las utilidades de fetching de KatanaKit.
 */
export function useKatanaApi() {
  const isLoaded = ref(katanaInitialized)

  const initKatanaFromCdn = async () => {
    if (katanaInitialized || !import.meta.client) return

    try {
      // Importación dinámica desde el CDN especificado
      katanaModule = await import(/* @vite-ignore */ 'https://esm.sh/katanakit-js@2.14.1')

      if (katanaModule?.useInitApis) {
        katanaModule.useInitApis({
          pos: {
            baseUri: '/api',
            endpoints: {
              login: '/auth/login',
              me: '/auth/me',
              logout: '/auth/logout',
              products: '/products',
              sales: '/sales',
              todaySales: '/sales/today',
              customers: '/customers',
              customerPayment: '/customers/payment',
              cashSummary: '/cash/summary',
              cashClose: '/cash/close',
              reports: '/reports',
              users: '/users',
              toggleUser: '/users/toggle',
              userPassword: '/users/password',
            },
          },
        })
        katanaInitialized = true
        isLoaded.value = true
        console.log('[KatanaKit CDN] Inicializado correctamente desde CDN v2.14.1')
      }
    } catch (err) {
      console.warn('[KatanaKit CDN] CDN offline o no disponible; usando fallback nativo:', err)
    }
  }

  // Wrapper agnóstico para llamadas GET
  const get = async <T>(endpoint: string, options?: { query?: Record<string, string> }): Promise<KatanaResponse<T>> => {
    if (import.meta.client && !katanaInitialized) {
      await initKatanaFromCdn()
    }

    if (katanaModule?.useGetApi) {
      try {
        const result = await katanaModule.useGetApi('pos', endpoint, { query: options?.query })
        return result
      } catch (err) {
        console.warn(`[KatanaKit] Falló useGetApi para ${endpoint}, recurriendo a fetch nativo:`, err)
      }
    }

    // Fallback nativo
    let url = `/api/${endpoint}`
    if (options?.query) {
      const q = new URLSearchParams(options.query).toString()
      url += `?${q}`
    }

    try {
      const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
      })
      const json = await res.json()
      return json
    } catch (e: any) {
      return {
        ok: false,
        data: null,
        error: { message: e.message || 'Error de red', status: 500 },
      }
    }
  }

  // Wrapper agnóstico para llamadas POST
  const post = async <T>(endpoint: string, body?: unknown): Promise<KatanaResponse<T>> => {
    if (import.meta.client && !katanaInitialized) {
      await initKatanaFromCdn()
    }

    if (katanaModule?.usePost) {
      try {
        const result = await katanaModule.usePost('pos', endpoint, body)
        return result
      } catch (err) {
        console.warn(`[KatanaKit] Falló usePost para ${endpoint}, recurriendo a fetch nativo:`, err)
      }
    }

    // Fallback nativo
    try {
      const res = await fetch(`/api/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : undefined,
      })
      const json = await res.json()
      return json
    } catch (e: any) {
      return {
        ok: false,
        data: null,
        error: { message: e.message || 'Error de red', status: 500 },
      }
    }
  }

  return {
    isLoaded,
    initKatanaFromCdn,
    get,
    post,
  }
}
