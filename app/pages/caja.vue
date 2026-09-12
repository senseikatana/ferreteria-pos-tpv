<script setup lang="ts">
import { ref, onMounted } from 'vue'

const summary = ref({
  cash: 0,
  card: 0,
  credit: 0,
  grandTotal: 0,
  salesCount: 0,
})

const todaySales = ref<any[]>([])
const loading = ref(false)
const isClosing = ref(false)
const closeNotes = ref('')
const feedback = ref<{ message: string; type: 'success' | 'error' } | null>(null)
const showCloseModal = ref(false)

const { get, post } = useKatanaApi()

const loadData = async () => {
  loading.value = true
  try {
    const [sumRes, salesRes] = await Promise.all([
      get<any>('cash/summary'),
      get<any[]>('sales/today'),
    ])

    if (sumRes.ok && sumRes.data) summary.value = sumRes.data
    if (salesRes.ok && salesRes.data) todaySales.value = salesRes.data
  } catch (err: any) {
    feedback.value = { message: err.message, type: 'error' }
  } finally {
    loading.value = false
  }
}

const handleCloseRegister = async () => {
  isClosing.value = true
  try {
    const res = await post('cash/close', { notes: closeNotes.value })
    if (res.ok) {
      feedback.value = { message: 'Cierre de caja registrado exitosamente.', type: 'success' }
      showCloseModal.value = false
      closeNotes.value = ''
      await loadData()
    } else {
      feedback.value = { message: res.error?.message || 'Error al cerrar caja', type: 'error' }
    }
  } catch (err: any) {
    feedback.value = { message: err.message, type: 'error' }
  } finally {
    isClosing.value = false
  }
}

const formatTime = (isoString: string) => {
  const d = new Date(isoString)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="flex-1 flex flex-col p-6 overflow-hidden max-w-7xl mx-auto w-full">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-white tracking-tight flex items-center">
          <span class="mr-2">🧾</span> Cierre y Arqueo de Caja
        </h2>
        <p class="text-xs text-slate-400">Resumen de operaciones y conciliación del turno diario</p>
      </div>

      <div class="flex items-center space-x-3">
        <button
          @click="loadData"
          class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition-colors"
        >
          🔄 Actualizar
        </button>
        <button
          @click="showCloseModal = true"
          class="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-purple-600/20"
        >
          🔒 Guardar Cierre de Caja
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

    <!-- 4 Summary Metric Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="p-5 bg-slate-900 border border-emerald-500/30 rounded-2xl shadow-xl">
        <div class="flex justify-between items-start">
          <div>
            <div class="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Efectivo</div>
            <div class="text-2xl font-black text-white font-mono mt-1">${{ summary.cash.toFixed(2) }}</div>
          </div>
          <span class="text-2xl">💵</span>
        </div>
      </div>

      <div class="p-5 bg-slate-900 border border-sky-500/30 rounded-2xl shadow-xl">
        <div class="flex justify-between items-start">
          <div>
            <div class="text-xs font-semibold text-sky-400 uppercase tracking-wider">Tarjeta / PosNet</div>
            <div class="text-2xl font-black text-white font-mono mt-1">${{ summary.card.toFixed(2) }}</div>
          </div>
          <span class="text-2xl">💳</span>
        </div>
      </div>

      <div class="p-5 bg-slate-900 border border-amber-500/30 rounded-2xl shadow-xl">
        <div class="flex justify-between items-start">
          <div>
            <div class="text-xs font-semibold text-amber-400 uppercase tracking-wider">Fiado / Crédito</div>
            <div class="text-2xl font-black text-white font-mono mt-1">${{ summary.credit.toFixed(2) }}</div>
          </div>
          <span class="text-2xl">📝</span>
        </div>
      </div>

      <div class="p-5 bg-gradient-to-br from-indigo-950 to-slate-900 border border-indigo-500/40 rounded-2xl shadow-xl">
        <div class="flex justify-between items-start">
          <div>
            <div class="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Total General</div>
            <div class="text-2xl font-black text-white font-mono mt-1">${{ summary.grandTotal.toFixed(2) }}</div>
            <div class="text-[11px] text-slate-400 mt-1">{{ summary.salesCount }} tickets emitidos hoy</div>
          </div>
          <span class="text-2xl">⚡</span>
        </div>
      </div>
    </div>

    <!-- Today Sales Table -->
    <div class="flex-1 flex flex-col bg-slate-900 border border-slate-800 rounded-2xl p-5 overflow-hidden shadow-xl">
      <h3 class="text-sm font-semibold uppercase tracking-wider text-slate-300 mb-3">Ventas Registradas en la Jornada</h3>

      <div class="flex-1 overflow-y-auto border border-slate-800/80 rounded-xl bg-slate-950/60">
        <table class="w-full text-left text-sm">
          <thead class="sticky top-0 bg-slate-800/90 backdrop-blur text-xs uppercase text-slate-400 border-b border-slate-800">
            <tr>
              <th class="py-3 px-4 font-semibold">Hora</th>
              <th class="py-3 px-4 font-semibold">Cajero</th>
              <th class="py-3 px-4 font-semibold">Cliente</th>
              <th class="py-3 px-4 font-semibold">Método</th>
              <th class="py-3 px-4 font-semibold text-right">Total</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            <tr v-if="todaySales.length === 0">
              <td colspan="5" class="py-16 text-center text-slate-400 text-sm">
                No hay ventas registradas en la fecha actual.
              </td>
            </tr>
            <tr
              v-for="sale in todaySales"
              :key="sale.id"
              class="hover:bg-slate-800/30 transition-colors"
            >
              <td class="py-3 px-4 font-mono text-xs text-slate-300">
                {{ formatTime(sale.createdAt) }}
              </td>
              <td class="py-3 px-4 text-slate-200">
                {{ sale.user?.fullName || sale.user?.username }}
              </td>
              <td class="py-3 px-4 text-slate-300">
                {{ sale.customer?.name || 'Cliente Ocasional' }}
              </td>
              <td class="py-3 px-4">
                <span
                  :class="{
                    'text-emerald-400 bg-emerald-500/10 border-emerald-500/20': sale.paymentMethod === 'CASH',
                    'text-sky-400 bg-sky-500/10 border-sky-500/20': sale.paymentMethod === 'CARD',
                    'text-amber-400 bg-amber-500/10 border-amber-500/20': sale.paymentMethod === 'CREDIT_DEBT',
                  }"
                  class="text-[11px] font-bold uppercase px-2 py-0.5 rounded-full border"
                >
                  {{ sale.paymentMethod }}
                </span>
              </td>
              <td class="py-3 px-4 text-right font-mono font-bold text-white">
                ${{ sale.total.toFixed(2) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal: Cerrar Caja -->
    <div
      v-if="showCloseModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4"
    >
      <div class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
        <h3 class="text-lg font-bold text-white">Confirmar Cierre de Caja</h3>
        <p class="text-xs text-slate-400">
          Se guardará una instantánea con el arqueo actual de ${{ summary.grandTotal.toFixed(2) }} ({{ summary.salesCount }} ventas).
        </p>

        <div>
          <label class="block text-xs text-slate-300 mb-1">Notas u Observaciones</label>
          <textarea
            v-model="closeNotes"
            rows="3"
            placeholder="Ej. Cierre de turno tarde sin novedades en el conteo físico de billetes."
            class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-xs outline-none focus:border-purple-500"
          />
        </div>

        <div class="flex space-x-3 pt-3">
          <button
            type="button"
            @click="showCloseModal = false"
            class="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold"
          >
            Cancelar
          </button>
          <button
            type="button"
            @click="handleCloseRegister"
            :disabled="isClosing"
            class="flex-1 py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold disabled:opacity-50"
          >
            <span v-if="isClosing">Guardando...</span>
            <span v-else>Confirmar Cierre</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
