<!-- src/components/Sidebar.vue -->
<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '@/store/auth'

const store = useAuthStore()
const userRole = computed(() => store.user?.role || 'user')  // Default to 'user' if not set

// Dynamic menu items based on role
const menuItems = computed(() => {
  if (userRole.value === 'admin') {
    return [
      { to: '/dashboard/admin', icon: '🏠', label: 'Dashboard' },
      { to: '/dashboard/projects', icon: '📁', label: 'Projects' },
      { to: '/dashboard/users', icon: '👥', label: 'Users', hasSub: true },
      { to: '/reports', icon: '📊', label: 'Reports' },
      { to: '/settings', icon: '⚙️', label: 'Settings' }
    ]
  } else {
    // For user/leader/member: Focus on personal/project features
    return [
      { to: '/dashboard/user', icon: '🏠', label: 'My Dashboard' },
      { to: '/dashboard/projects', icon: '📁', label: 'My Projects' },
      { to: '/my-tasks', icon: '✅', label: 'My Tasks' },
      { to: '/team', icon: '👥', label: 'My Team' },
      { to: '/settings', icon: '⚙️', label: 'Settings' }
    ]
  }
})
const usersOpen = ref(false)
</script>

<template>
  <aside class="w-64 bg-gray-900 text-white flex flex-col">
    <div class="flex items-center gap-3 px-5 h-16 border-b border-gray-800">
      <div class="h-9 w-9 rounded-xl bg-indigo-500 flex items-center justify-center font-bold">T</div>
      <div>
        <p class="text-base leading-none font-semibold">Taskify</p>
        <p class="text-xs text-gray-400 -mt-0.5">Project Management</p>
      </div>
    </div>

    <div class="px-3 py-4 text-xs uppercase tracking-wider text-gray-400">
      {{ userRole === 'admin' ? 'Admin Panel' : 'User Panel' }}
    </div>
    <nav class="px-2 space-y-1">
      <template v-for="item in menuItems" :key="item.to">
        <div v-if="item.hasSub" class="px-1">
          <button
            @click="usersOpen = !usersOpen"
            class="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition"
          >
            <span class="inline-flex h-5 w-5 items-center justify-center">{{ item.icon }}</span>
            <span class="flex-1 text-left">{{ item.label }}</span>
            <span class="text-xs">{{ usersOpen ? '▾' : '▸' }}</span>
          </button>

          <div v-if="usersOpen" class="pl-8 mt-1 space-y-1">
            <router-link to="/dashboard/users" class="block px-3 py-2 rounded-lg hover:bg-gray-800">All Users</router-link>
            <router-link to="/dashboard/users/leaders" class="block px-3 py-2 rounded-lg hover:bg-gray-800">Leaders</router-link>
          </div>
        </div>
        <router-link v-else :to="item.to" class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition">
          <span class="inline-flex h-5 w-5 items-center justify-center">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </router-link>
      </template>
    </nav>

    <div class="mt-auto p-4 text-sm text-gray-400">© 2025 Taskify</div>
  </aside>
</template>