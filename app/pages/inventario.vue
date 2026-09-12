<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Product {
  id: string
  barcode: string
  name: string
  category?: string | null
  salePrice: number
  costPrice: number
  stock: number
  unit: string
  isActive: boolean
}

const products = ref<Product[]>([])
const loading = ref(false)
const searchQuery = ref('')
const feedback = ref<{ message: string; type: 'success' | 'error' } | null>(null)
const showNewProductModal = ref(false)

const newProductForm = ref({
  barcode: '',
  name: '',
  category: '',
  salePrice: 0,
  costPrice: 0,
  stock: 0,
  unit: 'unit',
})

// Categorías predefinidas para autocompletar
const PRESET_CATEGORIES = [
  'Fasteners', 'Tools', 'Security', 'Electrical', 'Plumbing',
  'Paint', 'Safety', 'Sealants', 'General', 'Hardware',
]

const PRESET_UNITS = ['unit', 'kg', 'meter', 'pair', 'box', 'liter', 'roll', 'pack']

// Generar código de barras EAN-13 válido
const generateBarcode = () => {
  // Prefijo ficticio 750 (México) + 9 dígitos aleatorios
  let code = '750'
  for (let i = 0; i < 9; i++) {
    code += Math.floor(Math.random() * 10)
  }
  // Calcular dígito verificador (Luhn simplificado para EAN-13)
  let sum = 0
  for (let i = 0; i < 12; i++) {
    sum += parseInt(code[i]) * (i % 2 === 0 ? 1 : 3)
  }
  const checkDigit = (10 - (sum % 10)) % 10
  newProductForm.value.barcode = code + checkDigit
}

// Generar SKU a partir del nombre del producto
const generateSku = () => {
  const name = newProductForm.value.name.trim()
  if (!name) {
    feedback.value = { message: 'Escriba primero el nombre del producto para generar el SKU.', type: 'error' }
    return
  }

  // Tomar las primeras 3 letras de cada palabra significativa (máx 4 palabras)
  const words = name.split(/\s+/).filter((w) => w.length > 1)
  const initials = words
    .slice(0, 4)
    .map((w) => w.substring(0, 2).toUpperCase())
    .join('')
  const randomSuffix = Math.floor(100 + Math.random() * 900)

  newProductForm.value.barcode = `${initials}-${randomSuffix}`
}

// Calcular margen de ganancia
const profitMargin = ref(0)
const calculateMargin = () => {
  if (newProductForm.value.costPrice > 0 && newProductForm.value.salePrice > 0) {
    profitMargin.value = Math.round(
      ((newProductForm.value.salePrice - newProductForm.value.costPrice) / newProductForm.value.costPrice) * 100
    )
  } else {
    profitMargin.value = 0
  }
}

const { get, post } = useKatanaApi()

const loadProducts = async () => {
  loading.value = true
  try {
    const res = await get<Product[]>('products', {
      query: searchQuery.value ? { q: searchQuery.value } : undefined,
    })
    if (res.ok && res.data) {
      products.value = res.data
    }
  } catch (err: any) {
    feedback.value = { message: err.message, type: 'error' }
  } finally {
    loading.value = false
  }
}

const openNewProductModal = () => {
  newProductForm.value = { barcode: '', name: '', category: '', salePrice: 0, costPrice: 0, stock: 0, unit: 'unit' }
  profitMargin.value = 0
  showNewProductModal.value = true
}

const handleCreateProduct = async () => {
  if (!newProductForm.value.barcode || !newProductForm.value.name || newProductForm.value.salePrice <= 0) return

  try {
    const res = await post<Product>('products', newProductForm.value)
    if (res.ok) {
      feedback.value = { message: 'Producto registrado exitosamente.', type: 'success' }
      showNewProductModal.value = false
      await loadProducts()
    } else {
      feedback.value = { message: res.error?.message || 'Error al guardar producto', type: 'error' }
    }
  } catch (err: any) {
    feedback.value = { message: err.message, type: 'error' }
  }
}

onMounted(() => {
  loadProducts()
})
</script>

<template>
  <div class="flex-1 flex flex-col p-6 overflow-hidden max-w-7xl mx-auto w-full">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-white tracking-tight flex items-center">
          <span class="mr-2">📦</span> Inventario y Catálogo de Productos
        </h2>
        <p class="text-xs text-slate-400">Control de existencias, precios de venta y reposición</p>
      </div>

      <button
        @click="openNewProductModal"
        class="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-sky-600/20"
      >
        + Nuevo Producto
      </button>
    </div>

    <!-- Search Bar -->
    <div class="mb-4">
      <input
        v-model="searchQuery"
        @input="loadProducts"
        type="text"
        placeholder="Buscar por código de barras, nombre o categoría..."
        class="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-xs outline-none focus:border-sky-500"
      />
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

    <!-- Products Table -->
    <div class="flex-1 overflow-y-auto bg-slate-900 border border-slate-800 rounded-2xl shadow-xl">
      <table class="w-full text-left text-sm">
        <thead class="sticky top-0 bg-slate-800/90 backdrop-blur text-xs uppercase text-slate-400 border-b border-slate-800">
          <tr>
            <th class="py-3 px-4 font-semibold">Código</th>
            <th class="py-3 px-4 font-semibold">Producto</th>
            <th class="py-3 px-4 font-semibold">Categoría</th>
            <th class="py-3 px-4 font-semibold text-right">Precio</th>
            <th class="py-3 px-4 font-semibold text-center">Stock</th>
            <th class="py-3 px-4 font-semibold text-center">Unidad</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/60">
          <tr v-if="products.length === 0">
            <td colspan="6" class="py-12 text-center text-slate-400 text-xs">
              No se encontraron productos en el inventario.
            </td>
          </tr>
          <tr v-for="p in products" :key="p.id" class="hover:bg-slate-800/30 transition-colors">
            <td class="py-3 px-4 font-mono text-xs text-sky-400">{{ p.barcode }}</td>
            <td class="py-3 px-4 font-medium text-slate-200">{{ p.name }}</td>
            <td class="py-3 px-4 text-xs text-slate-400">{{ p.category || '-' }}</td>
            <td class="py-3 px-4 text-right font-mono font-bold text-emerald-400">${{ p.salePrice.toFixed(2) }}</td>
            <td class="py-3 px-4 text-center font-mono font-bold">
              <span :class="p.stock > 5 ? 'text-white' : 'text-amber-400'">
                {{ p.stock }}
              </span>
            </td>
            <td class="py-3 px-4 text-center text-xs text-slate-400">{{ p.unit }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal: Nuevo Producto -->
    <Teleport to="body">
      <div
        v-if="showNewProductModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4"
      >
        <div class="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
          <h3 class="text-lg font-bold text-white">Nuevo Producto</h3>

          <form @submit.prevent="handleCreateProduct" class="space-y-4">
            <!-- Código de Barras + Auto-generate -->
            <div>
              <label class="block text-xs text-slate-300 mb-1">Código de Barras / Referencia *</label>
              <div class="flex gap-2">
                <input
                  v-model="newProductForm.barcode"
                  type="text"
                  required
                  placeholder="Ej. 7501234560012 o SKU-001"
                  class="flex-1 px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white font-mono text-sm outline-none focus:border-sky-500"
                />
                <button
                  type="button"
                  @click="generateBarcode"
                  class="px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition-colors whitespace-nowrap"
                  title="Generar código EAN-13 automáticamente"
                >
                  🎲 EAN-13
                </button>
                <button
                  type="button"
                  @click="generateSku"
                  class="px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition-colors whitespace-nowrap"
                  title="Generar SKU desde el nombre del producto"
                >
                  🏷️ SKU
                </button>
              </div>
              <p class="mt-1 text-[11px] text-slate-500">
                Use <strong>EAN-13</strong> para productos con código de barras real, o <strong>SKU</strong> para referencia interna.
              </p>
            </div>

            <!-- Nombre -->
            <div>
              <label class="block text-xs text-slate-300 mb-1">Nombre del Producto *</label>
              <input
                v-model="newProductForm.name"
                type="text"
                required
                placeholder="Ej. Phillips Screw 1/4 x 2&quot;"
                class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-sky-500"
              />
            </div>

            <!-- Categoría (preset) + Unidad -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs text-slate-300 mb-1">Categoría</label>
                <select
                  v-model="newProductForm.category"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-sky-500"
                >
                  <option value="">Seleccionar...</option>
                  <option v-for="cat in PRESET_CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-slate-300 mb-1">Unidad</label>
                <select
                  v-model="newProductForm.unit"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-sky-500"
                >
                  <option v-for="u in PRESET_UNITS" :key="u" :value="u">{{ u }}</option>
                </select>
              </div>
            </div>

            <!-- Precios + Stock + Margen -->
            <div class="grid grid-cols-3 gap-3">
              <div>
                <label class="block text-xs text-slate-300 mb-1">Precio Venta *</label>
                <input
                  v-model.number="newProductForm.salePrice"
                  type="number"
                  step="0.01"
                  required
                  min="0.01"
                  @input="calculateMargin"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white font-mono text-sm outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label class="block text-xs text-slate-300 mb-1">Costo ($)</label>
                <input
                  v-model.number="newProductForm.costPrice"
                  type="number"
                  step="0.01"
                  min="0"
                  @input="calculateMargin"
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white font-mono text-sm outline-none focus:border-sky-500"
                />
              </div>
              <div>
                <label class="block text-xs text-slate-300 mb-1">Stock Inicial</label>
                <input
                  v-model.number="newProductForm.stock"
                  type="number"
                  min="0"
                  required
                  class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white font-mono text-sm outline-none focus:border-sky-500"
                />
              </div>
            </div>

            <!-- Margen de ganancia (auto-calculado) -->
            <div
              v-if="profitMargin > 0"
              class="flex items-center gap-2 p-2.5 bg-emerald-500/5 border border-emerald-500/20 rounded-xl"
            >
              <span class="text-xs text-emerald-400">📈 Margen de ganancia:</span>
              <span class="font-mono font-bold text-sm text-emerald-400">{{ profitMargin }}%</span>
              <span class="text-[11px] text-slate-400 ml-auto">
                Ganancia: ${{ (newProductForm.salePrice - newProductForm.costPrice).toFixed(2) }} / unidad
              </span>
            </div>

            <!-- Actions -->
            <div class="flex space-x-3 pt-2">
              <button
                type="button"
                @click="showNewProductModal = false"
                class="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="flex-1 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold"
              >
                Guardar Producto
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>
