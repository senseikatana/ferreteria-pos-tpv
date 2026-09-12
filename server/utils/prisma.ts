import { PrismaClient } from '@prisma/client'
import path from 'node:path'

/**
 * Singleton Pattern: asegura una única instancia de PrismaClient
 * en el ciclo de vida del servidor Nitro/Node.js para evitar fugas de conexiones.
 */
class DatabaseClient {
  private static instance: PrismaClient | null = null

  private constructor() {}

  public static getInstance(): PrismaClient {
    if (!DatabaseClient.instance) {
      if (!process.env.DATABASE_URL) {
        const defaultDbPath = path.resolve(process.cwd(), 'prisma/dev.db')
        process.env.DATABASE_URL = `file:${defaultDbPath}`
      }

      DatabaseClient.instance = new PrismaClient({
        datasources: {
          db: {
            url: process.env.DATABASE_URL,
          },
        },
        log: process.env.NODE_ENV === 'development' ? ['warn', 'error'] : ['error'],
      })
    }
    return DatabaseClient.instance
  }
}

export const prisma = DatabaseClient.getInstance()
export default prisma
