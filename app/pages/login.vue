<script setup lang="ts">
definePageMeta({
  layout: false,
})

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

const { login } = useAuth()
const router = useRouter()

const handleLogin = async () => {
  if (!username.value.trim() || !password.value.trim()) {
    errorMessage.value = 'Por favor ingrese usuario y contraseña.'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const res = await login(username.value, password.value)
    if (res.success) {
      router.push('/ventas')
    } else {
      errorMessage.value = res.error || 'Credenciales inválidas.'
    }
  } catch (err: any) {
    errorMessage.value = err.message || 'Error de conexión.'
  } finally {
    loading.value = false
  }
}

const fillDemo = (u: string, p: string) => {
  username.value = u
  password.value = p
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 flex flex-col justify-center items-center p-4">
    <!-- Card Container -->
    <div class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-8 backdrop-blur-xl">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 text-white font-black text-2xl shadow-xl shadow-sky-500/20 mb-3">
          ⚡
        </div>
        <h1 class="text-2xl font-bold text-white tracking-tight">Punto de Venta Universal</h1>
        <p class="text-sm text-slate-400 mt-1">Inicie sesión para acceder a la terminal de caja</p>
      </div>

      <!-- Error Message -->
      <div
        v-if="errorMessage"
        class="mb-6 p-3.5 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-sm flex items-center space-x-2"
      >
        <span>⚠️</span>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">Usuario</label>
          <input
            v-model="username"
            type="text"
            placeholder="admin o vendedor"
            autofocus
            class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 text-white placeholder-slate-500 transition-all outline-none text-sm"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">Contraseña</label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            class="w-full px-4 py-3 rounded-xl bg-slate-950 border border-slate-800 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 text-white placeholder-slate-500 transition-all outline-none text-sm"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3.5 px-4 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-sky-500/25 transition-all text-sm flex items-center justify-center space-x-2 disabled:opacity-50 mt-2"
        >
          <span v-if="loading">Accediendo...</span>
          <span v-else>Ingresar al Sistema</span>
        </button>
      </form>

      <!-- Quick Demo Access Pills -->
      <div class="mt-8 pt-6 border-t border-slate-800/80">
        <p class="text-xs text-slate-400 text-center mb-3">Acceso rápido para demostración:</p>
        <div class="grid grid-cols-2 gap-2">
          <button
            type="button"
            @click="fillDemo('admin', 'admin123')"
            class="px-3 py-2 bg-slate-800/60 hover:bg-slate-800 rounded-lg border border-slate-700/60 text-xs text-slate-300 transition-colors"
          >
            👑 Admin (<code class="text-sky-400">admin</code>)
          </button>
          <button
            type="button"
            @click="fillDemo('vendedor', 'vendedor123')"
            class="px-3 py-2 bg-slate-800/60 hover:bg-slate-800 rounded-lg border border-slate-700/60 text-xs text-slate-300 transition-colors"
          >
            🛒 Vendedor (<code class="text-sky-400">vendedor</code>)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
