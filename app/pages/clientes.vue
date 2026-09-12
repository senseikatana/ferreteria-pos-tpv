<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Customer {
  id: string
  name: string
  phone?: string | null
  email?: string | null
  address?: string | null
  creditLimit: number
  currentDebt: number
}

const customers = ref<Customer[]>([])
const loading = ref(false)
const filterWithDebtOnly = ref(false)

// Modales
const showNewCustomerModal = ref(false)
const showPaymentModal = ref(false)
const selectedCustomer = ref<Customer | null>(null)

// Formularios
const newCustomerForm = ref({
  name: '',
  phone: '',
  email: '',
  address: '',
  creditLimit: 0,
})

const paymentForm = ref({
  amount: 0,
  notes: '',
})

const feedback = ref<{ message: string; type: 'success' | 'error' } | null>(null)

const { get, post } = useKatanaApi()

const loadCustomers = async () => {
  loading.value = true
  try {
    const res = await get<Customer[]>('customers', {
      query: { withDebt: filterWithDebtOnly.value ? 'true' : 'false' },
    })
    if (res.ok && res.data) {
      customers.value = res.data
    }
  } catch (err: any) {
    feedback.value = { message: err.message, type: 'error' }
  } finally {
    loading.value = false
  }
}

const handleCreateCustomer = async () => {
  if (!newCustomerForm.value.name.trim()) return

  try {
    const res = await post<Customer>('customers', newCustomerForm.value)
    if (res.ok) {
      feedback.value = { message: 'Cliente registrado correctamente.', type: 'success' }
      showNewCustomerModal.value = false
      newCustomerForm.value = { name: '', phone: '', email: '', address: '', creditLimit: 0 }
      await loadCustomers()
    } else {
      feedback.value = { message: res.error?.message || 'Error al guardar cliente', type: 'error' }
    }
  } catch (err: any) {
    feedback.value = { message: err.message, type: 'error' }
  }
}

const openPaymentModal = (customer: Customer) => {
  selectedCustomer.value = customer
  paymentForm.value = { amount: customer.currentDebt, notes: '' }
  showPaymentModal.value = true
}

const handleRecordPayment = async () => {
  if (!selectedCustomer.value || paymentForm.value.amount <= 0) return

  try {
    const res = await post('customers/payment', {
      customerId: selectedCustomer.value.id,
      amount: paymentForm.value.amount,
      notes: paymentForm.value.notes,
    })

    if (res.ok) {
      feedback.value = { message: 'Abono registrado correctamente.', type: 'success' }
      showPaymentModal.value = false
      await loadCustomers()
    } else {
      feedback.value = { message: res.error?.message || 'Error al registrar abono', type: 'error' }
    }
  } catch (err: any) {
    feedback.value = { message: err.message, type: 'error' }
  }
}

onMounted(() => {
  loadCustomers()
})
</script>

<template>
  <div class="flex-1 flex flex-col p-6 overflow-hidden max-w-7xl mx-auto w-full">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-white tracking-tight flex items-center">
          <span class="mr-2">👥</span> Clientes y Cuentas por Cobrar (Fiado)
        </h2>
        <p class="text-xs text-slate-400">Gestión de créditos, deudas y registro de abonos</p>
      </div>

      <div class="flex items-center space-x-3">
        <label class="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer">
          <input
            type="checkbox"
            v-model="filterWithDebtOnly"
            @change="loadCustomers"
            class="rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-0"
          />
          <span>Solo con deuda</span>
        </label>

        <button
          @click="showNewCustomerModal = true"
          class="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-sky-600/20"
        >
          + Nuevo Cliente
        </button>
      </div>
    </div>

    <!-- Feedback Message -->
    <div
      v-if="feedback"
      :class="feedback.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-rose-500/10 border-rose-500/30 text-rose-300'"
      class="mb-4 p-3 border rounded-xl text-xs flex items-center justify-between"
    >
      <span>{{ feedback.message }}</span>
      <button @click="feedback = null" class="opacity-70 hover:opacity-100">✕</button>
    </div>

    <!-- Table Container -->
    <div class="flex-1 overflow-y-auto bg-slate-900 border border-slate-800 rounded-2xl shadow-xl">
      <table class="w-full text-left text-sm">
        <thead class="sticky top-0 bg-slate-800/90 backdrop-blur text-xs uppercase text-slate-400 border-b border-slate-800">
          <tr>
            <th class="py-3.5 px-4 font-semibold">Cliente</th>
            <th class="py-3.5 px-4 font-semibold">Teléfono</th>
            <th class="py-3.5 px-4 font-semibold text-right">Límite Crédito</th>
            <th class="py-3.5 px-4 font-semibold text-right">Saldo Deuda</th>
            <th class="py-3.5 px-4 font-semibold text-center">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/60">
          <tr v-if="customers.length === 0">
            <td colspan="5" class="py-16 text-center text-slate-400 text-sm">
              No se encontraron clientes registrados.
            </td>
          </tr>
          <tr
            v-for="customer in customers"
            :key="customer.id"
            class="hover:bg-slate-800/30 transition-colors"
          >
            <td class="py-3.5 px-4">
              <div class="font-semibold text-slate-200">{{ customer.name }}</div>
              <div class="text-xs text-slate-400">{{ customer.address || 'Sin dirección' }}</div>
            </td>
            <td class="py-3.5 px-4 text-xs font-mono text-slate-300">
              {{ customer.phone || '-' }}
            </td>
            <td class="py-3.5 px-4 text-right font-mono text-xs text-slate-300">
              ${{ customer.creditLimit.toFixed(2) }}
            </td>
            <td class="py-3.5 px-4 text-right font-mono font-bold">
              <span :class="customer.currentDebt > 0 ? 'text-amber-400' : 'text-slate-400'">
                ${{ customer.currentDebt.toFixed(2) }}
              </span>
            </td>
            <td class="py-3.5 px-4 text-center">
              <button
                v-if="customer.currentDebt > 0"
                @click="openPaymentModal(customer)"
                class="px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 rounded-lg text-xs font-semibold transition-colors"
              >
                Abonar
              </button>
              <span v-else class="text-xs text-slate-400">Al día</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal: Nuevo Cliente -->
    <div
      v-if="showNewCustomerModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4"
    >
      <div class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
        <h3 class="text-lg font-bold text-white">Registrar Nuevo Cliente</h3>
        <form @submit.prevent="handleCreateCustomer" class="space-y-3">
          <div>
            <label class="block text-xs text-slate-300 mb-1">Nombre Completo *</label>
            <input
              v-model="newCustomerForm.name"
              type="text"
              required
              class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-sky-500"
            />
          </div>
          <div>
            <label class="block text-xs text-slate-300 mb-1">Teléfono</label>
            <input
              v-model="newCustomerForm.phone"
              type="text"
              class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-sky-500"
            />
          </div>
          <div>
            <label class="block text-xs text-slate-300 mb-1">Dirección</label>
            <input
              v-model="newCustomerForm.address"
              type="text"
              class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-sky-500"
            />
          </div>
          <div>
            <label class="block text-xs text-slate-300 mb-1">Límite de Crédito ($)</label>
            <input
              v-model.number="newCustomerForm.creditLimit"
              type="number"
              step="0.01"
              min="0"
              class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-sky-500"
            />
          </div>

          <div class="flex space-x-3 pt-3">
            <button
              type="button"
              @click="showNewCustomerModal = false"
              class="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold"
            >
              Cancelar
            </button>
            <button
              type="submit"
              class="flex-1 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold"
            >
              Guardar
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal: Registrar Abono -->
    <div
      v-if="showPaymentModal && selectedCustomer"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4"
    >
      <div class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
        <h3 class="text-lg font-bold text-white">Registrar Abono</h3>
        <p class="text-xs text-slate-400">
          Cliente: <strong class="text-slate-200">{{ selectedCustomer.name }}</strong> (Deuda actual: ${{ selectedCustomer.currentDebt.toFixed(2) }})
        </p>

        <form @submit.prevent="handleRecordPayment" class="space-y-3">
          <div>
            <label class="block text-xs text-slate-300 mb-1">Monto a Abonar ($)</label>
            <input
              v-model.number="paymentForm.amount"
              type="number"
              step="0.01"
              :max="selectedCustomer.currentDebt"
              required
              class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-emerald-500 font-mono font-bold"
            />
          </div>
          <div>
            <label class="block text-xs text-slate-300 mb-1">Notas / Referencia</label>
            <input
              v-model="paymentForm.notes"
              type="text"
              placeholder="Ej. Pago en efectivo comprobante #102"
              class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-emerald-500"
            />
          </div>

          <div class="flex space-x-3 pt-3">
            <button
              type="button"
              @click="showPaymentModal = false"
              class="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold"
            >
              Cancelar
            </button>
            <button
              type="submit"
              class="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold"
            >
              Confirmar Abono
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
