import { prisma } from '../../utils/prisma'
import type { CartItemEntity, PaymentMethodType } from '../domain/entities'

export class PrismaProductRepository {
  async findByBarcode(barcode: string) {
    return prisma.product.findUnique({
      where: { barcode: barcode.trim(), isActive: true },
    })
  }

  async search(query: string) {
    const term = query.trim()
    return prisma.product.findMany({
      where: {
        isActive: true,
        OR: [
          { name: { contains: term } },
          { barcode: { contains: term } },
          { category: { contains: term } },
        ],
      },
      take: 25,
      orderBy: { name: 'asc' },
    })
  }

  async listAll() {
    return prisma.product.findMany({
      where: { isActive: true },
      orderBy: { name: 'asc' },
    })
  }

  async create(data: {
    barcode: string
    name: string
    category?: string
    salePrice: number
    costPrice?: number
    stock: number
    minStock?: number
    unit?: string
    metadata?: Record<string, unknown>
  }) {
    return prisma.product.create({
      data: {
        barcode: data.barcode.trim(),
        name: data.name.trim(),
        category: data.category?.trim() || null,
        salePrice: data.salePrice,
        costPrice: data.costPrice ?? 0,
        stock: data.stock,
        minStock: data.minStock ?? 5,
        unit: data.unit ?? 'unit',
        metadata: data.metadata ?? undefined,
      },
    })
  }

  async updateStock(productId: string, quantityDelta: number) {
    return prisma.product.update({
      where: { id: productId },
      data: {
        stock: { increment: quantityDelta },
      },
    })
  }
}

export class PrismaCustomerRepository {
  async findById(id: string) {
    return prisma.customer.findUnique({
      where: { id },
    })
  }

  async listAll() {
    return prisma.customer.findMany({
      where: { isActive: true },
      orderBy: { name: 'asc' },
    })
  }

  async listWithDebt() {
    return prisma.customer.findMany({
      where: { isActive: true, currentDebt: { gt: 0 } },
      orderBy: { currentDebt: 'desc' },
    })
  }

  async create(data: {
    name: string
    phone?: string
    email?: string
    address?: string
    creditLimit?: number
  }) {
    return prisma.customer.create({
      data: {
        name: data.name.trim(),
        phone: data.phone?.trim() || null,
        email: data.email?.trim() || null,
        address: data.address?.trim() || null,
        creditLimit: data.creditLimit ?? 0,
        currentDebt: 0,
      },
    })
  }

  async recordPayment(customerId: string, userId: string, amount: number, notes?: string) {
    return prisma.$transaction(async (tx) => {
      const customer = await tx.customer.findUnique({ where: { id: customerId } })
      if (!customer) throw new Error('Cliente no encontrado.')

      const newDebt = Math.max(0, customer.currentDebt - amount)

      await tx.customer.update({
        where: { id: customerId },
        data: { currentDebt: newDebt },
      })

      const payment = await tx.debtPayment.create({
        data: {
          customerId,
          userId,
          amount,
          notes: notes || null,
        },
      })

      return { payment, newDebt }
    })
  }
}

export class PrismaSaleRepository {
  async executeAtomicSale(input: {
    userId: string
    customerId?: string | null
    items: CartItemEntity[]
    total: number
    receivedAmount?: number
    changeAmount?: number
    paymentMethod: PaymentMethodType
    shouldIncreaseCustomerDebt: boolean
    debtAmountToAdd?: number
  }) {
    return prisma.$transaction(async (tx) => {
      // 1. Verificar stock disponible para cada producto
      for (const item of input.items) {
        const prod = await tx.product.findUnique({ where: { id: item.productId } })
        if (!prod) throw new Error(`Producto ${item.name} no encontrado.`)
        if (prod.stock < item.quantity) {
          throw new Error(`Stock insuficiente para "${prod.name}". Disponible: ${prod.stock}, Solicitado: ${item.quantity}.`)
        }
      }

      // 2. Crear cabecera de la venta
      const sale = await tx.sale.create({
        data: {
          userId: input.userId,
          customerId: input.customerId || null,
          total: input.total,
          receivedAmount: input.receivedAmount ?? null,
          changeAmount: input.changeAmount ?? null,
          paymentMethod: input.paymentMethod,
          isVoided: false,
          items: {
            create: input.items.map((i) => ({
              productId: i.productId,
              productName: i.name,
              quantity: i.quantity,
              unitPrice: i.unitPrice,
              subtotal: i.subtotal,
            })),
          },
        },
        include: {
          items: true,
          customer: true,
          user: {
            select: { id: true, fullName: true, username: true },
          },
        },
      })

      // 3. Descontar stock
      for (const item of input.items) {
        await tx.product.update({
          where: { id: item.productId },
          data: { stock: { decrement: item.quantity } },
        })
      }

      // 4. Si fue a fiado/crédito, sumar a la cuenta corriente del cliente
      if (input.shouldIncreaseCustomerDebt && input.customerId && input.debtAmountToAdd) {
        await tx.customer.update({
          where: { id: input.customerId },
          data: { currentDebt: { increment: input.debtAmountToAdd } },
        })
      }

      return sale
    })
  }

  async getSalesByDate(date: Date = new Date()) {
    const startOfDay = new Date(date)
    startOfDay.setHours(0, 0, 0, 0)
    const endOfDay = new Date(date)
    endOfDay.setHours(23, 59, 59, 999)

    return prisma.sale.findMany({
      where: {
        createdAt: { gte: startOfDay, lte: endOfDay },
        isVoided: false,
      },
      include: {
        user: { select: { fullName: true, username: true } },
        customer: { select: { name: true } },
        items: true,
      },
      orderBy: { createdAt: 'desc' },
    })
  }

  async getDailySummary(date: Date = new Date()) {
    const startOfDay = new Date(date)
    startOfDay.setHours(0, 0, 0, 0)
    const endOfDay = new Date(date)
    endOfDay.setHours(23, 59, 59, 999)

    const sales = await prisma.sale.findMany({
      where: {
        createdAt: { gte: startOfDay, lte: endOfDay },
        isVoided: false,
      },
    })

    const summary = {
      cash: 0,
      card: 0,
      credit: 0,
      grandTotal: 0,
      salesCount: sales.length,
    }

    for (const s of sales) {
      if (s.paymentMethod === 'CASH') summary.cash += s.total
      else if (s.paymentMethod === 'CARD') summary.card += s.total
      else if (s.paymentMethod === 'CREDIT_DEBT') summary.credit += s.total
      summary.grandTotal += s.total
    }

    return summary
  }

  async getTopProducts(limit: number = 5, date: Date = new Date()) {
    const startOfDay = new Date(date)
    startOfDay.setHours(0, 0, 0, 0)
    const endOfDay = new Date(date)
    endOfDay.setHours(23, 59, 59, 999)

    const items = await prisma.saleItem.groupBy({
      by: ['productName'],
      where: {
        sale: {
          createdAt: { gte: startOfDay, lte: endOfDay },
          isVoided: false,
        },
      },
      _sum: {
        quantity: true,
        subtotal: true,
      },
      orderBy: {
        _sum: {
          quantity: 'desc',
        },
      },
      take: limit,
    })

    return items.map((i) => ({
      productName: i.productName,
      units: i._sum.quantity ?? 0,
      revenue: i._sum.subtotal ?? 0,
    }))
  }
}

export class PrismaCashRegisterRepository {
  async saveClose(data: {
    userId: string
    cashTotal: number
    cardTotal: number
    creditTotal: number
    grandTotal: number
    salesCount: number
    notes?: string
  }) {
    return prisma.cashRegisterClose.create({
      data: {
        userId: data.userId,
        cashTotal: data.cashTotal,
        cardTotal: data.cardTotal,
        creditTotal: data.creditTotal,
        grandTotal: data.grandTotal,
        salesCount: data.salesCount,
        notes: data.notes || null,
      },
      include: {
        user: { select: { fullName: true, username: true } },
      },
    })
  }

  async listCloses(limit: number = 20) {
    return prisma.cashRegisterClose.findMany({
      take: limit,
      orderBy: { createdAt: 'desc' },
      include: {
        user: { select: { fullName: true, username: true } },
      },
    })
  }
}
