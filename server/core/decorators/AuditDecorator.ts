/**
 * Decorator Pattern: Envoltorio transparente para auditoría,
 * medición de latencia y control de errores en servicios de dominio.
 */
export function withAudit<TArgs extends unknown[], TReturn>(
  operationName: string,
  fn: (...args: TArgs) => Promise<TReturn>
): (...args: TArgs) => Promise<TReturn> {
  return async (...args: TArgs): Promise<TReturn> => {
    const start = performance.now()
    try {
      const result = await fn(...args)
      const duration = (performance.now() - start).toFixed(2)
      if (process.env.NODE_ENV !== 'production') {
        console.log(`[Audit] ${operationName} completed successfully in ${duration}ms`)
      }
      return result
    } catch (error) {
      const duration = (performance.now() - start).toFixed(2)
      console.error(`[Audit Error] ${operationName} failed after ${duration}ms:`, error)
      throw error
    }
  }
}
