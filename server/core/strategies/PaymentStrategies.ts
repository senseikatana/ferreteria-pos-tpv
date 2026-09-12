import type { IPaymentStrategy, PaymentExecutionInput, PaymentExecutionResult } from '../ports/services/IPaymentStrategy'

/**
 * Strategy Pattern: Estrategia de pago en Efectivo.
 * Calcula el cambio / vuelto y asegura que el monto recibido sea suficiente.
 */
export class CashPaymentStrategy implements IPaymentStrategy {
  public readonly code = 'CASH'

  public validateAndProcess(input: PaymentExecutionInput): PaymentExecutionResult {
    const received = input.receivedAmount ?? input.total

    if (received < input.total) {
      return {
        isValid: false,
        errorMessage: `El monto recibido (${received.toFixed(2)}) es menor al total de la venta (${input.total.toFixed(2)}).`,
        shouldIncreaseCustomerDebt: false,
      }
    }

    const change = Math.max(0, received - input.total)

    return {
      isValid: true,
      receivedAmount: received,
      changeAmount: change,
      shouldIncreaseCustomerDebt: false,
    }
  }
}

/**
 * Strategy Pattern: Estrategia de pago con Tarjeta / PosNet.
 */
export class CardPaymentStrategy implements IPaymentStrategy {
  public readonly code = 'CARD'

  public validateAndProcess(input: PaymentExecutionInput): PaymentExecutionResult {
    return {
      isValid: true,
      receivedAmount: input.total,
      changeAmount: 0,
      shouldIncreaseCustomerDebt: false,
    }
  }
}

/**
 * Strategy Pattern: Estrategia de pago a Crédito / Fiado.
 * Valida la existencia del cliente y el límite de crédito disponible.
 */
export class CreditDebtPaymentStrategy implements IPaymentStrategy {
  public readonly code = 'CREDIT_DEBT'

  public validateAndProcess(input: PaymentExecutionInput): PaymentExecutionResult {
    if (!input.customer) {
      return {
        isValid: false,
        errorMessage: 'Para compras a crédito/fiado es obligatorio seleccionar un cliente registrado.',
        shouldIncreaseCustomerDebt: false,
      }
    }

    const proposedDebt = input.customer.currentDebt + input.total

    // Verificación estricta de cupo si el límite es mayor a 0
    if (input.customer.creditLimit > 0 && proposedDebt > input.customer.creditLimit) {
      return {
        isValid: false,
        errorMessage: `El cliente supera su límite de crédito autorizado (${input.customer.creditLimit.toFixed(2)}). Deuda resultante: ${proposedDebt.toFixed(2)}.`,
        shouldIncreaseCustomerDebt: false,
      }
    }

    return {
      isValid: true,
      receivedAmount: 0,
      changeAmount: 0,
      shouldIncreaseCustomerDebt: true,
      debtAmountToAdd: input.total,
    }
  }
}
