<script setup lang="ts">
const { user, isAdmin, logout } = useAuth()
const route = useRoute()
const { itemCount } = useCart()

const navLinks = computed(() => {
  const links = [
    { label: 'Punto de Venta', to: '/ventas', icon: '🛒', badge: itemCount.value > 0 ? itemCount.value : null },
    { label: 'Clientes / Fiado', to: '/clientes', icon: '👥' },
    { label: 'Cierre de Caja', to: '/caja', icon: '🧾' },
    { label: 'Inventario', to: '/inventario', icon: '📦' },
  ]

  if (isAdmin.value) {
    links.push(
      { label: 'Reportes', to: '/reportes', icon: '📊' },
      { label: 'Usuarios', to: '/usuarios', icon: '🔑' }
    )
  }

  return links
})
</script>

<template>
  <div class="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
    <!-- Sidebar -->
    <aside class="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0 select-none">
      <div>
        <!-- Brand Header -->
        <div class="p-5 border-b border-slate-800 flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-sky-500/20 text-xl">
            ⚡
          </div>
          <div>
            <h1 class="text-base font-bold tracking-tight text-white">POS Universal</h1>
            <p class="text-xs text-slate-400">Retail & Hardware Engine</p>
          </div>
        </div>

        <!-- User Information -->
        <div v-if="user" class="px-5 py-4 border-b border-slate-800/60 bg-slate-900/40">
          <div class="text-sm font-semibold text-slate-200 truncate">{{ user.fullName }}</div>
          <div class="flex items-center space-x-2 mt-1">
            <span
              :class="isAdmin ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-sky-500/10 text-sky-400 border-sky-500/20'"
              class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full border"
            >
              {{ user.role }}
            </span>
            <span class="text-xs text-slate-400">@{{ user.username }}</span>
          </div>
        </div>

        <!-- Navigation Menu -->
        <nav class="p-3 space-y-1">
          <NuxtLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="flex items-center px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors"
            :class="route.path.startsWith(link.to) ? 'bg-sky-500/15 text-sky-400 font-semibold' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'"
          >
            <span class="mr-3 text-lg leading-none">{{ link.icon }}</span>
            <span>{{ link.label }}</span>
            <span
              v-if="link.badge"
              class="ml-auto px-1.5 py-0.5 bg-sky-500/20 border border-sky-500/30 rounded-full text-[10px] font-bold text-sky-400"
            >
              {{ link.badge }}
            </span>
          </NuxtLink>
        </nav>
      </div>

      <!-- Footer & Logout -->
      <div class="p-4 border-t border-slate-800 space-y-3">
        <button
          @click="logout"
          class="w-full flex items-center justify-center px-4 py-2.5 rounded-lg text-sm font-medium text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 transition-all"
        >
          <span class="mr-2">🚪</span> Cerrar sesión
        </button>
        <div class="text-[11px] text-center text-slate-400">
          v1.0.0 • KatanaKit + Prisma
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 flex flex-col overflow-y-auto bg-slate-950">
      <slot />
    </main>
  </div>
</template>
