<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import type { Product } from '~/composables/useCart'

interface Customer {
  id: string
  name: string
  creditLimit: number
  currentDebt: number
}

const barcodeInput = ref('')
const barcodeInputRef = ref<HTMLInputElement | null>(null)
const paymentMethod = ref<'CASH' | 'CARD' | 'CREDIT_DEBT'>('CASH')
const receivedAmount = ref<number | null>(null)
const selectedCustomerId = ref<string>('')
const customers = ref<Customer[]>([])
const feedbackMessage = ref('')
const feedbackType = ref<'error' | 'success' | 'warning'>('error')
const isProcessing = ref(false)
const lastSale = ref<any>(null)
const showSuccessModal = ref(false)

// Search Modal
const showSearchModal = ref(false)
const searchQuery = ref('')
const searchResults = ref<Product[]>([])
const searchLoading = ref(false)
const searchInputRef = ref<HTMLInputElement | null>(null)

const { get, post } = useKatanaApi()

// Carrito persistente entre páginas
const { items: cart, total, totalUnits, itemCount, addItem, updateQuantity, removeItem, clearCart } = useCart()

// Cambio / Vuelto en efectivo
const changeAmount = computed(() => {
  if (paymentMethod.value !== 'CASH' || !receivedAmount.value) return 0
  return Math.max(0, receivedAmount.value - total.value)
})

// Cargar clientes para fiado
const loadCustomers = async () => {
  const res = await get<Customer[]>('customers')
  if (res.ok && res.data) {
    customers.value = res.data
    if (customers.value.length > 0 && !selectedCustomerId.value) {
      selectedCustomerId.value = customers.value[0]?.id ?? ''
    }
  }
}

// Foco en el lector de códigos
const focusScanner = () => {
  nextTick(() => {
    barcodeInputRef.value?.focus()
  })
}

// Agregar producto al carrito
const addToCart = (prod: Product) => {
  const result = addItem(prod)
  feedbackType.value = result.ok ? 'success' : 'warning'
  feedbackMessage.value = result.message || ''
}

// Agregar por escaneo de código de barras
const handleScan = async () => {
  const code = barcodeInput.value.trim()
  barcodeInput.value = ''

  if (!code) return

  feedbackMessage.value = ''

  try {
    const res = await get<Product>('products', { query: { barcode: code } })

    if (!res.ok || !res.data) {
      feedbackType.value = 'error'
      feedbackMessage.value = `Código «${code}» no encontrado. Presione 🔍 para buscar por nombre.`
      return
    }

    addToCart(res.data)
    focusScanner()
  } catch (err: any) {
    feedbackType.value = 'error'
    feedbackMessage.value = err.message || 'Error al buscar producto'
  }
}

// Abrir modal de búsqueda
const openSearchModal = () => {
  showSearchModal.value = true
  searchQuery.value = ''
  searchResults.value = []
  feedbackMessage.value = ''
  loadAllProducts()
  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

// Cargar todos los productos del inventario
const loadAllProducts = async () => {
  searchLoading.value = true
  try {
    const res = await get<Product[]>('products')
    if (res.ok && res.data) {
      searchResults.value = res.data
    }
  } catch {
    searchResults.value = []
  } finally {
    searchLoading.value = false
  }
}

// Buscar productos por nombre, categoría o código
let searchTimeout: ReturnType<typeof setTimeout> | null = null
const searchProducts = async () => {
  const q = searchQuery.value.trim()

  if (searchTimeout) clearTimeout(searchTimeout)

  // Sin texto: mostrar todo el catálogo
  if (q.length < 1) {
    loadAllProducts()
    return
  }

  searchLoading.value = true

  searchTimeout = setTimeout(async () => {
    try {
      const res = await get<Product[]>('products', { query: { q } })
      if (res.ok && res.data) {
        searchResults.value = res.data
      }
    } catch {
      searchResults.value = []
    } finally {
      searchLoading.value = false
    }
  }, 250)
}

// Seleccionar producto del modal de búsqueda
const selectFromSearch = (prod: Product) => {
  addToCart(prod)
  showSearchModal.value = false
  searchQuery.value = ''
  searchResults.value = []
  focusScanner()
}

// Cerrar modal con Escape
const handleSearchKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') {
    showSearchModal.value = false
    focusScanner()
  }
}

const handleRemoveItem = (index: number) => {
  removeItem(index)
  focusScanner()
}

const handleClearCart = () => {
  clearCart()
  feedbackMessage.value = ''
  receivedAmount.value = null
  focusScanner()
}

// Confirmar venta atómica
const confirmSale = async () => {
  if (cart.value.length === 0) {
    feedbackType.value = 'error'
    feedbackMessage.value = 'El carrito está vacío.'
    return
  }

  if (paymentMethod.value === 'CASH') {
    const received = receivedAmount.value ?? total.value
    if (received < total.value) {
      feedbackType.value = 'error'
      feedbackMessage.value = `El monto recibido (${received.toFixed(2)}) es menor al total ($${total.value.toFixed(2)}).`
      return
    }
  }

  if (paymentMethod.value === 'CREDIT_DEBT' && !selectedCustomerId.value) {
    feedbackType.value = 'error'
    feedbackMessage.value = 'Debe seleccionar un cliente para compras a crédito/fiado.'
    return
  }

  isProcessing.value = true
  feedbackMessage.value = ''

  try {
    const payload = {
      items: cart.value.map((i) => ({
        productId: i.productId,
        name: i.name,
        quantity: i.quantity,
        unitPrice: i.unitPrice,
        subtotal: i.subtotal,
      })),
      paymentMethod: paymentMethod.value,
      customerId: paymentMethod.value === 'CREDIT_DEBT' ? selectedCustomerId.value : null,
      receivedAmount: paymentMethod.value === 'CASH' ? (receivedAmount.value ?? total.value) : undefined,
    }

    const res = await post<any>('sales', payload)

    if (res.ok && res.data) {
      lastSale.value = res.data
      showSuccessModal.value = true
      handleClearCart()
      await loadCustomers()
    } else {
      feedbackType.value = 'error'
      feedbackMessage.value = res.error?.message || 'Error al procesar cobro'
    }
  } catch (err: any) {
    feedbackType.value = 'error'
    feedbackMessage.value = err.message || 'Error en transacción'
  } finally {
    isProcessing.value = false
  }
}

// Atajo de teclado: F2 abre búsqueda, F4 vacía carrito
const handleGlobalKeydown = (e: KeyboardEvent) => {
  if (e.key === 'F2') {
    e.preventDefault()
    openSearchModal()
  }
  if (e.key === 'F4') {
    e.preventDefault()
    handleClearCart()
  }
}

onMounted(() => {
  loadCustomers()
  focusScanner()
  document.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<template>
  <div class="flex-1 flex flex-col p-6 overflow-hidden max-w-7xl mx-auto w-full">
    <!-- Header -->
    <div class="flex items-center justify-between mb-5">
      <div>
        <h2 class="text-xl font-bold text-white tracking-tight flex items-center">
          <span class="mr-2">🛒</span> Terminal de Venta (POS)
          <span
            v-if="itemCount > 0"
            class="ml-3 px-2 py-0.5 bg-sky-500/15 border border-sky-500/30 rounded-full text-[11px] font-bold text-sky-400"
          >
            {{ itemCount }} ítems · {{ totalUnits }} uds
          </span>
        </h2>
        <p class="text-xs text-slate-400">
          Escanee código de barras o presione
          <kbd class="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-[10px] font-mono text-slate-300">F2</kbd>
          para buscar por nombre
        </p>
      </div>

      <div class="flex items-center space-x-2">
        <button
          v-if="cart.length > 0"
          @click="handleClearCart"
          class="px-3 py-1.5 rounded-lg border border-rose-500/30 text-rose-300 hover:bg-rose-500/10 text-xs font-semibold transition-all"
        >
          Vaciar Carrito
        </button>
      </div>
    </div>

    <!-- Layout Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 overflow-hidden">
      <!-- Left Panel: Scanner & Cart Table (8 Cols) -->
      <div class="lg:col-span-8 flex flex-col bg-slate-900 border border-slate-800 rounded-2xl p-5 overflow-hidden shadow-xl">
        <!-- Barcode Scanner Input + Search Button -->
        <div class="mb-4">
          <div class="flex gap-2">
            <div class="relative flex-1">
              <input
                ref="barcodeInputRef"
                v-model="barcodeInput"
                @keydown.enter.prevent="handleScan"
                type="text"
                placeholder="Escanee código de barras o teclee el número y presione Enter..."
                class="w-full pl-11 pr-4 py-3.5 bg-slate-950 border border-slate-700/80 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 text-white placeholder-slate-400 rounded-xl outline-none font-mono text-sm transition-all"
              />
              <div class="absolute left-3.5 top-3.5 text-slate-400 text-lg">🔍</div>
            </div>
            <button
              @click="handleScan"
              class="px-4 py-3.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold transition-colors shrink-0"
            >
              Agregar
            </button>
            <button
              @click="openSearchModal"
              class="px-4 py-3.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-xl text-xs font-bold transition-colors shrink-0 flex items-center gap-1.5"
              title="Buscar por nombre, categoría o código (F2)"
            >
              <span>📋</span> Buscar
            </button>
          </div>
        </div>

        <!-- Feedback Alert -->
        <div
          v-if="feedbackMessage"
          :class="{
            'bg-rose-500/10 border-rose-500/30 text-rose-300': feedbackType === 'error',
            'bg-amber-500/10 border-amber-500/30 text-amber-300': feedbackType === 'warning',
            'bg-emerald-500/10 border-emerald-500/30 text-emerald-300': feedbackType === 'success',
          }"
          class="mb-3 px-3 py-2 border rounded-xl text-xs flex items-center justify-between"
        >
          <span>{{ feedbackMessage }}</span>
          <button @click="feedbackMessage = ''" class="text-xs opacity-70 hover:opacity-100">✕</button>
        </div>

        <!-- Cart Table -->
        <div class="flex-1 overflow-y-auto border border-slate-800/80 rounded-xl bg-slate-950/60">
          <table class="w-full text-left text-sm">
            <thead class="sticky top-0 bg-slate-800/90 backdrop-blur text-xs uppercase text-slate-400 border-b border-slate-800">
              <tr>
                <th class="py-3 px-4 font-semibold">Producto</th>
                <th class="py-3 px-3 font-semibold text-center">Cant.</th>
                <th class="py-3 px-3 font-semibold text-right">Unitario</th>
                <th class="py-3 px-4 font-semibold text-right">Subtotal</th>
                <th class="py-3 px-3 font-semibold text-center"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60">
              <tr v-if="cart.length === 0">
                <td colspan="5" class="py-16 text-center text-slate-400 text-sm">
                  <div class="text-3xl mb-2">🏷️</div>
                  El carrito está vacío. Escanee un producto o presione
                  <kbd class="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-[10px] font-mono">F2</kbd>
                  para buscar.
                </td>
              </tr>
              <tr
                v-for="(item, index) in cart"
                :key="item.productId"
                class="hover:bg-slate-800/30 transition-colors group"
              >
                <td class="py-3 px-4">
                  <div class="font-medium text-slate-200">{{ item.name }}</div>
                  <div class="text-[11px] font-mono text-slate-400">{{ item.barcode }}</div>
                </td>
                <td class="py-3 px-3">
                  <div class="flex items-center justify-center space-x-1">
                    <button
                      @click="updateQuantity(index, -1)"
                      class="w-6 h-6 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center font-bold text-xs"
                    >
                      -
                    </button>
                    <span class="w-8 text-center font-mono font-bold text-sky-400">{{ item.quantity }}</span>
                    <button
                      @click="updateQuantity(index, 1)"
                      class="w-6 h-6 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center font-bold text-xs"
                    >
                      +
                    </button>
                  </div>
                </td>
                <td class="py-3 px-3 text-right font-mono text-slate-300">
                  ${{ item.unitPrice.toFixed(2) }}
                </td>
                <td class="py-3 px-4 text-right font-mono font-bold text-white">
                  ${{ item.subtotal.toFixed(2) }}
                </td>
                <td class="py-3 px-3 text-center">
                  <button
                    @click="handleRemoveItem(index)"
                    class="text-rose-400/60 hover:text-rose-400 p-1 rounded transition-colors"
                    title="Eliminar ítem"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Right Panel: Summary & Checkout (4 Cols) -->
      <div class="lg:col-span-4 flex flex-col justify-between bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
        <div>
          <h3 class="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-2">Total a Cobrar</h3>
          <div class="p-4 bg-slate-950 border border-slate-800 rounded-2xl text-center">
            <span class="text-4xl font-black text-emerald-400 tracking-tight font-mono">
              ${{ total.toFixed(2) }}
            </span>
            <div class="text-xs text-slate-400 mt-1">
              {{ totalUnits }} unidades en {{ itemCount }} ítems
            </div>
          </div>

          <!-- Payment Method Selector -->
          <div class="mt-6">
            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Forma de Pago</label>
            <div class="grid grid-cols-3 gap-2">
              <button
                type="button"
                @click="paymentMethod = 'CASH'"
                :class="paymentMethod === 'CASH' ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300 font-bold' : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'"
                class="py-2.5 px-2 rounded-xl border text-xs flex flex-col items-center justify-center space-y-1 transition-all"
              >
                <span class="text-base">💵</span>
                <span>Efectivo</span>
              </button>
              <button
                type="button"
                @click="paymentMethod = 'CARD'"
                :class="paymentMethod === 'CARD' ? 'bg-sky-500/20 border-sky-500/50 text-sky-300 font-bold' : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'"
                class="py-2.5 px-2 rounded-xl border text-xs flex flex-col items-center justify-center space-y-1 transition-all"
              >
                <span class="text-base">💳</span>
                <span>Tarjeta</span>
              </button>
              <button
                type="button"
                @click="paymentMethod = 'CREDIT_DEBT'"
                :class="paymentMethod === 'CREDIT_DEBT' ? 'bg-amber-500/20 border-amber-500/50 text-amber-300 font-bold' : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'"
                class="py-2.5 px-2 rounded-xl border text-xs flex flex-col items-center justify-center space-y-1 transition-all"
              >
                <span class="text-base">📝</span>
                <span>Fiado</span>
              </button>
            </div>
          </div>

          <!-- Cash Payment Details -->
          <div v-if="paymentMethod === 'CASH'" class="mt-4 p-3.5 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-3">
            <div>
              <label class="block text-xs text-slate-400 mb-1">Monto Recibido</label>
              <input
                v-model.number="receivedAmount"
                type="number"
                step="0.01"
                :placeholder="total.toFixed(2)"
                class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white font-mono text-sm outline-none focus:border-emerald-500"
              />
            </div>
            <div class="flex justify-between items-center text-xs pt-1 border-t border-slate-800">
              <span class="text-slate-400">Vuelto / Cambio:</span>
              <span class="font-mono font-bold text-sm text-emerald-400">${{ changeAmount.toFixed(2) }}</span>
            </div>
          </div>

          <!-- Customer Selection for Credit / Fiado -->
          <div v-if="paymentMethod === 'CREDIT_DEBT'" class="mt-4 p-3.5 bg-amber-500/5 border border-amber-500/20 rounded-xl space-y-2">
            <label class="block text-xs font-semibold text-amber-300">Cliente a Cargar Cuenta</label>
            <select
              v-model="selectedCustomerId"
              class="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs outline-none focus:border-amber-500"
            >
              <option v-for="c in customers" :key="c.id" :value="c.id">
                {{ c.name }} (Deuda: ${{ c.currentDebt.toFixed(2) }})
              </option>
            </select>
          </div>
        </div>

        <!-- Checkout Action Button -->
        <button
          type="button"
          @click="confirmSale"
          :disabled="isProcessing || cart.length === 0"
          class="w-full py-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-500/20 transition-all text-base flex items-center justify-center space-x-2 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <span v-if="isProcessing">Procesando Venta...</span>
          <span v-else>✅ Confirmar y Cobrar</span>
        </button>
      </div>
    </div>

    <!-- ==================== SEARCH MODAL ==================== -->
    <Teleport to="body">
      <div
        v-if="showSearchModal"
        class="fixed inset-0 z-[100] flex items-start justify-center bg-slate-950/80 backdrop-blur-sm p-4 pt-[10vh]"
        @click.self="showSearchModal = false; focusScanner()"
      >
        <div class="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden" @keydown.esc="handleSearchKeydown">
          <!-- Modal Header -->
          <div class="px-5 py-4 border-b border-slate-800 flex items-center justify-between">
            <h3 class="text-base font-bold text-white flex items-center gap-2">
              <span>📋</span> Buscar Productos
            </h3>
            <button
              @click="showSearchModal = false; focusScanner()"
              class="w-7 h-7 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 flex items-center justify-center text-xs"
            >
              ✕
            </button>
          </div>

          <!-- Search Input -->
          <div class="px-5 py-4 border-b border-slate-800/60">
            <div class="relative">
              <input
                ref="searchInputRef"
                v-model="searchQuery"
                @input="searchProducts"
                type="text"
                placeholder="Escriba nombre, categoría o código de barras..."
                class="w-full pl-10 pr-4 py-3 bg-slate-950 border border-slate-700 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 text-white placeholder-slate-400 rounded-xl outline-none text-sm transition-all"
              />
              <div class="absolute left-3.5 top-3.5 text-slate-400">🔍</div>
              <div v-if="searchLoading" class="absolute right-3.5 top-3.5">
                <span class="inline-block w-4 h-4 border-2 border-slate-600 border-t-sky-500 rounded-full animate-spin"></span>
              </div>
            </div>
            <p class="mt-2 text-[11px] text-slate-500">
              <span v-if="searchQuery.length === 0">
                Catálogo completo: <strong class="text-slate-300">{{ searchResults.length }}</strong> productos en inventario
              </span>
              <span v-else>
                <strong class="text-slate-300">{{ searchResults.length }}</strong> resultados para «{{ searchQuery }}»
              </span>
            </p>
          </div>

          <!-- Search Results -->
          <div class="max-h-[50vh] overflow-y-auto">
            <!-- Loading State -->
            <div v-if="searchLoading" class="py-12 text-center text-slate-400">
              <span class="inline-block w-6 h-6 border-2 border-slate-600 border-t-sky-500 rounded-full animate-spin mb-3"></span>
              <p class="text-sm">Cargando productos...</p>
            </div>

            <!-- No Results -->
            <div v-else-if="searchResults.length === 0 && searchQuery.length > 0" class="py-12 text-center text-slate-400">
              <div class="text-3xl mb-2">🔍</div>
              <p class="text-sm">No se encontraron productos con «{{ searchQuery }}»</p>
            </div>

            <!-- Empty Inventory -->
            <div v-else-if="searchResults.length === 0" class="py-12 text-center text-slate-400">
              <div class="text-3xl mb-2">📦</div>
              <p class="text-sm">No hay productos registrados en el inventario</p>
              <p class="text-[11px] text-slate-500 mt-2">Agregue productos desde la sección Inventario</p>
            </div>

            <!-- Results List -->
            <button
              v-for="prod in searchResults"
              :key="prod.id"
              @click="selectFromSearch(prod)"
              :disabled="prod.stock <= 0"
              class="w-full text-left px-5 py-3.5 hover:bg-slate-800/60 border-b border-slate-800/40 transition-colors flex items-center justify-between gap-4 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div class="flex-1 min-w-0">
                <div class="font-semibold text-sm text-slate-200 group-hover:text-white truncate">{{ prod.name }}</div>
                <div class="flex items-center gap-2 mt-0.5">
                  <span class="text-[11px] font-mono text-slate-400">{{ prod.barcode }}</span>
                  <span v-if="prod.category" class="text-[11px] text-slate-500">· {{ prod.category }}</span>
                </div>
              </div>
              <div class="flex items-center gap-4 shrink-0">
                <div class="text-right">
                  <div class="font-mono font-bold text-emerald-400 text-sm">${{ prod.salePrice.toFixed(2) }}</div>
                  <div class="text-[11px]" :class="prod.stock > 5 ? 'text-slate-400' : prod.stock > 0 ? 'text-amber-400' : 'text-rose-400'">
                    Stock: {{ prod.stock }} {{ prod.unit }}
                  </div>
                </div>
                <div class="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/30 text-sky-400 flex items-center justify-center text-sm opacity-0 group-hover:opacity-100 transition-opacity">
                  +
                </div>
              </div>
            </button>
          </div>

          <!-- Modal Footer -->
          <div class="px-5 py-3 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-500">
            <span>Presione <kbd class="px-1 py-0.5 bg-slate-800 border border-slate-700 rounded font-mono text-slate-300">Esc</kbd> para cerrar</span>
            <span>{{ searchResults.length }} resultados</span>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Success Modal -->
    <Teleport to="body">
      <div
        v-if="showSuccessModal"
        class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4"
      >
        <div class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl text-center space-y-4">
          <div class="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-3xl flex items-center justify-center mx-auto">
            ✓
          </div>
          <h3 class="text-xl font-bold text-white">¡Venta Registrada con Éxito!</h3>
          <p class="text-xs text-slate-400 font-mono">Ticket #{{ lastSale?.id }}</p>

          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800/80 text-left space-y-2 text-xs">
            <div class="flex justify-between">
              <span class="text-slate-400">Total cobrado:</span>
              <span class="font-bold text-white font-mono">${{ lastSale?.total?.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Método de pago:</span>
              <span class="font-semibold uppercase text-sky-400">{{ lastSale?.paymentMethod }}</span>
            </div>
            <div v-if="lastSale?.changeAmount > 0" class="flex justify-between text-emerald-400">
              <span>Cambio entregado:</span>
              <span class="font-bold font-mono">${{ lastSale?.changeAmount?.toFixed(2) }}</span>
            </div>
          </div>

          <button
            @click="showSuccessModal = false; focusScanner()"
            class="w-full py-3 bg-sky-600 hover:bg-sky-500 text-white font-bold rounded-xl text-sm transition-colors"
          >
            Nueva Venta
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>
