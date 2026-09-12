import {
  PrismaProductRepository,
  PrismaCustomerRepository,
  PrismaSaleRepository,
  PrismaCashRegisterRepository,
} from '../adapters/PrismaRepositories'
import { PaymentStrategyFactory } from '../factories/PaymentStrategyFactory'
import { eventBus } from '../observers/DomainEventBus'
import { withAudit } from '../decorators/AuditDecorator'
import type { CartItemEntity, PaymentMethodType } from '../domain/entities'

/**
 * Facade Pattern: Punto de entrada unificado y desacoplado para todas
 * las operaciones del Punto de Venta. Oculta la complejidad interna
 * de repositorios, fábricas de estrategias, auditorías y eventos.
 */
export class PosFacade {
  private productRepo = new PrismaProductRepository()
  private customerRepo = new PrismaCustomerRepository()
  private saleRepo = new PrismaSaleRepository()
  private cashRepo = new PrismaCashRegisterRepository()

  // ---------------------------------------------------------------------------
  // Inventario / Productos
  // ---------------------------------------------------------------------------

  public async lookupProductByBarcode(barcode: string) {
    return this.productRepo.findByBarcode(barcode)
  }

  public async searchProducts(query: string) {
    return this.productRepo.search(query)
  }

  public async listProducts() {
    return this.productRepo.listAll()
  }

  public async createProduct(data: Parameters<PrismaProductRepository['create']>[0]) {
    return this.productRepo.create(data)
  }

  // ---------------------------------------------------------------------------
  // Clientes y Cuentas por Cobrar
  // ---------------------------------------------------------------------------

  public async listCustomers() {
    return this.customerRepo.listAll()
  }

  public async listCustomersWithDebt() {
    return this.customerRepo.listWithDebt()
  }

  public async createCustomer(data: Parameters<PrismaCustomerRepository['create']>[0]) {
    return this.customerRepo.create(data)
  }

  public async registerCustomerPayment(customerId: string, userId: string, amount: number, notes?: string) {
    return this.customerRepo.recordPayment(customerId, userId, amount, notes)
  }

  // ---------------------------------------------------------------------------
  // Ventas Transaccionales (Strategy + Factory + Observer + Decorator)
  // ---------------------------------------------------------------------------

  public processSale = withAudit(
    'PosFacade.processSale',
    async (input: {
      userId: string
      customerId?: string | null
      items: CartItemEntity[]
      paymentMethod: PaymentMethodType
      receivedAmount?: number
    }) => {
      if (!input.items || input.items.length === 0) {
        throw new Error('El carrito no puede estar vacío.')
      }

      // 1. Calcular total
      const total = input.items.reduce((acc, item) => acc + item.subtotal, 0)

      // 2. Obtener cliente si aplica
      let customer = null
      if (input.customerId) {
        customer = await this.customerRepo.findById(input.customerId)
      }

      // 3. Obtener estrategia de pago mediante Factory
      const paymentStrategy = PaymentStrategyFactory.getStrategy(input.paymentMethod)
      const validation = paymentStrategy.validateAndProcess({
        total,
        receivedAmount: input.receivedAmount,
        customer,
      })

      if (!validation.isValid) {
        throw new Error(validation.errorMessage || 'Error en la validación del pago.')
      }

      // 4. Ejecución atómica en base de datos
      const sale = await this.saleRepo.executeAtomicSale({
        userId: input.userId,
        customerId: input.customerId,
        items: input.items,
        total,
        receivedAmount: validation.receivedAmount,
        changeAmount: validation.changeAmount,
        paymentMethod: input.paymentMethod,
        shouldIncreaseCustomerDebt: validation.shouldIncreaseCustomerDebt,
        debtAmountToAdd: validation.debtAmountToAdd,
      })

      // 5. Notificar a observadores desacoplados
      await eventBus.publish({
        name: 'SaleCompleted',
        occurredOn: new Date(),
        payload: {
          saleId: sale.id,
          total: sale.total,
          userId: sale.userId,
          customerId: sale.customerId,
          items: input.items.map((i) => ({
            productId: i.productId,
            productName: i.name,
            quantity: i.quantity,
          })),
        },
      })

      return sale
    }
  )

  // ---------------------------------------------------------------------------
  // Caja y Reportes
  // ---------------------------------------------------------------------------

  public async getTodaySales() {
    return this.saleRepo.getSalesByDate(new Date())
  }

  public async getTodaySummary() {
    return this.saleRepo.getDailySummary(new Date())
  }

  public async performCashRegisterClose(userId: string, notes?: string) {
    const summary = await this.saleRepo.getDailySummary(new Date())
    return this.cashRepo.saveClose({
      userId,
      cashTotal: summary.cash,
      cardTotal: summary.card,
      creditTotal: summary.credit,
      grandTotal: summary.grandTotal,
      salesCount: summary.salesCount,
      notes,
    })
  }

  public async getReports(limit: number = 5) {
    const [summary, topProducts, customersWithDebt] = await Promise.all([
      this.saleRepo.getDailySummary(new Date()),
      this.saleRepo.getTopProducts(limit, new Date()),
      this.customerRepo.listWithDebt(),
    ])

    return {
      summary,
      topProducts,
      customersWithDebt,
    }
  }
}

// Instancia única (Singleton) de la Fachada
export const posFacade = new PosFacade()
