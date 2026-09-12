import type { IPaymentStrategy } from '../ports/services/IPaymentStrategy'
import type { PaymentMethodType } from '../domain/entities'
import {
  CashPaymentStrategy,
  CardPaymentStrategy,
  CreditDebtPaymentStrategy,
} from '../strategies/PaymentStrategies'

/**
 * Factory Pattern: Fabrica la estrategia de pago correcta según el método seleccionado.
 */
export class PaymentStrategyFactory {
  private static strategies: Map<PaymentMethodType, IPaymentStrategy> = new Map([
    ['CASH', new CashPaymentStrategy()],
    ['CARD', new CardPaymentStrategy()],
    ['CREDIT_DEBT', new CreditDebtPaymentStrategy()],
  ])

  public static getStrategy(method: PaymentMethodType): IPaymentStrategy {
    const strategy = this.strategies.get(method)
    if (!strategy) {
      throw new Error(`Método de pago no soportado: ${method}`)
    }
    return strategy
  }
}
