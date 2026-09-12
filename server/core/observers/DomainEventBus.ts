import type { DomainEvent } from '../domain/events/DomainEvent'

export type DomainEventListener<T = unknown> = (event: DomainEvent<T>) => Promise<void> | void

/**
 * Observer Pattern & Singleton Pattern:
 * Bus centralizado para suscripción y publicación desacoplada de eventos de dominio.
 */
export class DomainEventBus {
  private static instance: DomainEventBus | null = null
  private listeners: Map<string, Set<DomainEventListener>> = new Map()

  private constructor() {}

  public static getInstance(): DomainEventBus {
    if (!DomainEventBus.instance) {
      DomainEventBus.instance = new DomainEventBus()
    }
    return DomainEventBus.instance
  }

  public subscribe<T = unknown>(eventName: string, listener: DomainEventListener<T>): () => void {
    if (!this.listeners.has(eventName)) {
      this.listeners.set(eventName, new Set())
    }
    const eventListeners = this.listeners.get(eventName)!
    eventListeners.add(listener as DomainEventListener)

    // Devuelve funcion de desuscripcion (limpieza limpia)
    return () => {
      eventListeners.delete(listener as DomainEventListener)
    }
  }

  public async publish<T = unknown>(event: DomainEvent<T>): Promise<void> {
    const eventListeners = this.listeners.get(event.name)
    if (!eventListeners || eventListeners.size === 0) return

    const executions = Array.from(eventListeners).map((listener) => {
      try {
        return Promise.resolve(listener(event))
      } catch (err) {
        console.error(`[EventBus] Error executing subscriber for ${event.name}:`, err)
        return Promise.resolve()
      }
    })

    await Promise.all(executions)
  }
}

export const eventBus = DomainEventBus.getInstance()
