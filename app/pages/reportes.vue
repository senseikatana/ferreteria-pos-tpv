<script setup lang="ts">
import { ref, onMounted } from 'vue'

const reports = ref<any>(null)
const loading = ref(false)
const feedback = ref<string | null>(null)

const { get } = useKatanaApi()

const loadReports = async () => {
  loading.value = true
  try {
    const res = await get<any>('reports')
    if (res.ok && res.data) {
      reports.value = res.data
    } else {
      feedback.value = res.error?.message || 'Error al cargar reportes'
    }
  } catch (err: any) {
    feedback.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadReports()
})
</script>

<template>
  <div class="flex-1 flex flex-col p-6 overflow-hidden max-w-7xl mx-auto w-full">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-white tracking-tight flex items-center">
          <span class="mr-2">📊</span> Reportes y Métricas (Solo Administrador)
        </h2>
        <p class="text-xs text-slate-400">Rendimiento comercial del día, productos líderes y cuentas pendientes</p>
      </div>

      <button
        @click="loadReports"
        class="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition-colors flex items-center space-x-2"
      >
        <span>🔄</span>
        <span>Refrescar</span>
      </button>
    </div>

    <!-- Error Alert -->
    <div
      v-if="feedback"
      class="mb-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs"
    >
      {{ feedback }}
    </div>

    <div v-if="reports" class="flex-1 flex flex-col space-y-6 overflow-hidden">
      <!-- 2 Hero Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 shrink-0">
        <!-- Top 1 Product -->
        <div class="p-6 bg-gradient-to-br from-amber-500/10 via-slate-900 to-slate-900 border border-amber-500/30 rounded-2xl shadow-xl">
          <div class="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-amber-400 mb-2">
            <span>⭐</span>
            <span>Producto Más Vendido Hoy</span>
          </div>
          <div v-if="reports.topProducts && reports.topProducts.length > 0">
            <h3 class="text-xl font-black text-white">{{ reports.topProducts[0].productName }}</h3>
            <p class="text-sm text-slate-400 mt-1">
              <strong class="text-amber-400 font-mono">{{ reports.topProducts[0].units }}</strong> unidades vendidas (${{ reports.topProducts[0].revenue.toFixed(2) }} acumulado)
            </p>
          </div>
          <div v-else class="text-slate-400 text-sm py-2">
            Sin ventas registradas en la jornada.
          </div>
        </div>

        <!-- Total Revenue -->
        <div class="p-6 bg-gradient-to-br from-emerald-500/10 via-slate-900 to-slate-900 border border-emerald-500/30 rounded-2xl shadow-xl">
          <div class="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-emerald-400 mb-2">
            <span>💰</span>
            <span>Ventas Totales Hoy</span>
          </div>
          <div class="text-3xl font-black text-white font-mono">
            ${{ reports.summary?.grandTotal?.toFixed(2) }}
          </div>
          <p class="text-xs text-slate-400 mt-1">
            {{ reports.summary?.salesCount }} transacciones en total
          </p>
        </div>
      </div>

      <!-- Tables Grid: Top 5 & Debtors -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 overflow-hidden">
        <!-- Top 5 Products Table -->
        <div class="flex flex-col bg-slate-900 border border-slate-800 rounded-2xl p-5 overflow-hidden shadow-xl">
          <h3 class="text-sm font-semibold uppercase tracking-wider text-slate-300 mb-3 flex items-center">
            <span class="mr-2">🏆</span> Top 5 Productos del Día
          </h3>
          <div class="flex-1 overflow-y-auto border border-slate-800/80 rounded-xl bg-slate-950/60">
            <table class="w-full text-left text-sm">
              <thead class="sticky top-0 bg-slate-800/90 text-xs uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th class="py-2.5 px-3">#</th>
                  <th class="py-2.5 px-3">Producto</th>
                  <th class="py-2.5 px-3 text-center">Unidades</th>
                  <th class="py-2.5 px-3 text-right">Recaudado</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-800/60">
                <tr v-if="!reports.topProducts || reports.topProducts.length === 0">
                  <td colspan="4" class="py-8 text-center text-slate-400 text-xs">Sin actividad hoy</td>
                </tr>
                <tr v-for="(p, index) in reports.topProducts" :key="p.productName" class="hover:bg-slate-800/30">
                  <td class="py-2.5 px-3 font-mono text-xs text-slate-400">{{ index + 1 }}</td>
                  <td class="py-2.5 px-3 font-medium text-slate-200 text-xs">{{ p.productName }}</td>
                  <td class="py-2.5 px-3 text-center font-mono font-bold text-sky-400 text-xs">{{ p.units }}</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-emerald-400 text-xs">${{ p.revenue.toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Debtors Table -->
        <div class="flex flex-col bg-slate-900 border border-slate-800 rounded-2xl p-5 overflow-hidden shadow-xl">
          <h3 class="text-sm font-semibold uppercase tracking-wider text-slate-300 mb-3 flex items-center">
            <span class="mr-2">⚠️</span> Clientes con Saldo Deudor Pendiente
          </h3>
          <div class="flex-1 overflow-y-auto border border-slate-800/80 rounded-xl bg-slate-950/60">
            <table class="w-full text-left text-sm">
              <thead class="sticky top-0 bg-slate-800/90 text-xs uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th class="py-2.5 px-3">Cliente</th>
                  <th class="py-2.5 px-3">Teléfono</th>
                  <th class="py-2.5 px-3 text-right">Deuda Pendiente</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-800/60">
                <tr v-if="!reports.customersWithDebt || reports.customersWithDebt.length === 0">
                  <td colspan="3" class="py-8 text-center text-emerald-400 text-xs">¡Excelente! No hay clientes con deuda pendiente.</td>
                </tr>
                <tr v-for="c in reports.customersWithDebt" :key="c.id" class="hover:bg-slate-800/30">
                  <td class="py-2.5 px-3 font-medium text-slate-200 text-xs">{{ c.name }}</td>
                  <td class="py-2.5 px-3 text-xs font-mono text-slate-400">{{ c.phone || '-' }}</td>
                  <td class="py-2.5 px-3 text-right font-mono font-bold text-amber-400 text-xs">${{ c.currentDebt.toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
