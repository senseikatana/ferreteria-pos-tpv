import type { CustomerEntity } from '../../domain/entities'

export interface PaymentExecutionInput {
  total: number
  receivedAmount?: number
  customer?: CustomerEntity | null
}

export interface PaymentExecutionResult {
  isValid: boolean
  errorMessage?: string
  receivedAmount?: number
  changeAmount?: number
  shouldIncreaseCustomerDebt: boolean
  debtAmountToAdd?: number
}

export interface IPaymentStrategy {
  readonly code: string
  validateAndProcess(input: PaymentExecutionInput): PaymentExecutionResult
}
