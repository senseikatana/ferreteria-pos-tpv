/**
 * Helper compatible con el patrón Safe Result de KatanaKit para Nuxt/Nitro.
 * Garantiza respuestas estructuradas y tipadas { ok, data, error }.
 */
export function sendSafeSuccess<T>(data: T) {
  return {
    ok: true,
    data,
    error: null,
  }
}

export function sendSafeError(message: string, status: number = 400) {
  return {
    ok: false,
    data: null,
    error: {
      message,
      status,
    },
  }
}
