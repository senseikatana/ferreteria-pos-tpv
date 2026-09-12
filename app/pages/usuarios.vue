<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface UserItem {
  id: string
  fullName: string
  username: string
  role: 'ADMIN' | 'CASHIER'
  isActive: boolean
  createdAt: string
}

const users = ref<UserItem[]>([])
const loading = ref(false)
const feedback = ref<{ message: string; type: 'success' | 'error' } | null>(null)

// Modales
const showNewUserModal = ref(false)
const showResetPasswordModal = ref(false)
const selectedUser = ref<UserItem | null>(null)

// Formularios
const newUserForm = ref({
  fullName: '',
  username: '',
  password: '',
  role: 'CASHIER' as 'ADMIN' | 'CASHIER',
})

const resetPasswordForm = ref({
  newPassword: '',
})

const { get, post } = useKatanaApi()

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await get<UserItem[]>('users')
    if (res.ok && res.data) {
      users.value = res.data
    }
  } catch (err: any) {
    feedback.value = { message: err.message, type: 'error' }
  } finally {
    loading.value = false
  }
}

const handleCreateUser = async () => {
  if (!newUserForm.value.fullName || !newUserForm.value.username || !newUserForm.value.password) return

  try {
    const res = await post<UserItem>('users', newUserForm.value)
    if (res.ok) {
      feedback.value = { message: 'Usuario creado exitosamente.', type: 'success' }
      showNewUserModal.value = false
      newUserForm.value = { fullName: '', username: '', password: '', role: 'CASHIER' }
      await loadUsers()
    } else {
      feedback.value = { message: res.error?.message || 'Error al crear usuario', type: 'error' }
    }
  } catch (err: any) {
    feedback.value = { message: err.message, type: 'error' }
  }
}

const handleToggleStatus = async (user: UserItem) => {
  try {
    const res = await post('users/toggle', {
      userId: user.id,
      isActive: !user.isActive,
    })
    if (res.ok) {
      feedback.value = { message: `Usuario ${user.username} actualizado.`, type: 'success' }
      await loadUsers()
    } else {
      feedback.value = { message: res.error?.message || 'Error al cambiar estado', type: 'error' }
    }
  } catch (err: any) {
    feedback.value = { message: err.message, type: 'error' }
  }
}

const openResetModal = (user: UserItem) => {
  selectedUser.value = user
  resetPasswordForm.value.newPassword = ''
  showResetPasswordModal.value = true
}

const handleResetPassword = async () => {
  if (!selectedUser.value || !resetPasswordForm.value.newPassword) return

  try {
    const res = await post('users/password', {
      userId: selectedUser.value.id,
      newPassword: resetPasswordForm.value.newPassword,
    })
    if (res.ok) {
      feedback.value = { message: 'Contraseña actualizada correctamente.', type: 'success' }
      showResetPasswordModal.value = false
    } else {
      feedback.value = { message: res.error?.message || 'Error al restablecer contraseña', type: 'error' }
    }
  } catch (err: any) {
    feedback.value = { message: err.message, type: 'error' }
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<template>
  <div class="flex-1 flex flex-col p-6 overflow-hidden max-w-7xl mx-auto w-full">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-white tracking-tight flex items-center">
          <span class="mr-2">🔑</span> Gestión de Usuarios y Permisos
        </h2>
        <p class="text-xs text-slate-400">Control de operadores, roles administrativos y credenciales</p>
      </div>

      <button
        @click="showNewUserModal = true"
        class="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-sky-600/20"
      >
        + Crear Usuario
      </button>
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

    <!-- Users Table -->
    <div class="flex-1 overflow-y-auto bg-slate-900 border border-slate-800 rounded-2xl shadow-xl">
      <table class="w-full text-left text-sm">
        <thead class="sticky top-0 bg-slate-800/90 backdrop-blur text-xs uppercase text-slate-400 border-b border-slate-800">
          <tr>
            <th class="py-3.5 px-4 font-semibold">Nombre Completo</th>
            <th class="py-3.5 px-4 font-semibold">Usuario</th>
            <th class="py-3.5 px-4 font-semibold text-center">Rol</th>
            <th class="py-3.5 px-4 font-semibold text-center">Estado</th>
            <th class="py-3.5 px-4 font-semibold text-right">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/60">
          <tr v-for="user in users" :key="user.id" class="hover:bg-slate-800/30 transition-colors">
            <td class="py-3.5 px-4 font-semibold text-slate-200">
              {{ user.fullName }}
            </td>
            <td class="py-3.5 px-4 font-mono text-xs text-slate-300">
              @{{ user.username }}
            </td>
            <td class="py-3.5 px-4 text-center">
              <span
                :class="user.role === 'ADMIN' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-sky-500/10 text-sky-400 border-sky-500/20'"
                class="text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full border"
              >
                {{ user.role }}
              </span>
            </td>
            <td class="py-3.5 px-4 text-center">
              <span
                :class="user.isActive ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' : 'text-slate-400 bg-slate-800 border-slate-700'"
                class="text-[11px] font-bold px-2 py-0.5 rounded-full border"
              >
                {{ user.isActive ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="py-3.5 px-4 text-right space-x-2">
              <button
                @click="handleToggleStatus(user)"
                class="px-2.5 py-1 text-xs rounded-lg border border-slate-700 hover:bg-slate-800 text-slate-300"
              >
                {{ user.isActive ? 'Desactivar' : 'Activar' }}
              </button>
              <button
                @click="openResetModal(user)"
                class="px-2.5 py-1 text-xs rounded-lg border border-slate-700 hover:bg-slate-800 text-sky-400"
              >
                Cambiar clave
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal: Nuevo Usuario -->
    <div
      v-if="showNewUserModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4"
    >
      <div class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
        <h3 class="text-lg font-bold text-white">Crear Nuevo Usuario</h3>
        <form @submit.prevent="handleCreateUser" class="space-y-3">
          <div>
            <label class="block text-xs text-slate-300 mb-1">Nombre Completo *</label>
            <input
              v-model="newUserForm.fullName"
              type="text"
              required
              class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-sky-500"
            />
          </div>
          <div>
            <label class="block text-xs text-slate-300 mb-1">Nombre de Usuario *</label>
            <input
              v-model="newUserForm.username"
              type="text"
              required
              class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-sky-500"
            />
          </div>
          <div>
            <label class="block text-xs text-slate-300 mb-1">Contraseña *</label>
            <input
              v-model="newUserForm.password"
              type="password"
              required
              minlength="6"
              class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-sky-500"
            />
          </div>
          <div>
            <label class="block text-xs text-slate-300 mb-1">Rol</label>
            <select
              v-model="newUserForm.role"
              class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-sky-500"
            >
              <option value="CASHIER">Cajero / Vendedor</option>
              <option value="ADMIN">Administrador</option>
            </select>
          </div>

          <div class="flex space-x-3 pt-3">
            <button
              type="button"
              @click="showNewUserModal = false"
              class="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold"
            >
              Cancelar
            </button>
            <button
              type="submit"
              class="flex-1 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold"
            >
              Crear
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal: Restablecer Contraseña -->
    <div
      v-if="showResetPasswordModal && selectedUser"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4"
    >
      <div class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
        <h3 class="text-lg font-bold text-white">Cambiar Contraseña</h3>
        <p class="text-xs text-slate-400">Usuario: <strong class="text-slate-200">@{{ selectedUser.username }}</strong></p>

        <form @submit.prevent="handleResetPassword" class="space-y-3">
          <div>
            <label class="block text-xs text-slate-300 mb-1">Nueva Contraseña *</label>
            <input
              v-model="resetPasswordForm.newPassword"
              type="password"
              required
              minlength="6"
              class="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-sm outline-none focus:border-sky-500"
            />
          </div>

          <div class="flex space-x-3 pt-3">
            <button
              type="button"
              @click="showResetPasswordModal = false"
              class="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold"
            >
              Cancelar
            </button>
            <button
              type="submit"
              class="flex-1 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold"
            >
              Actualizar
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
