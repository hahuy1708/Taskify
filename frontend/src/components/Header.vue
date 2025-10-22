<!-- src/components/Header.vue -->
<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'  
import { logout } from '@/api/authApi';
import { useRouter } from 'vue-router';
import { User, Menu } from 'lucide-vue-next'
// import { Bell, Search  } from 'lucide-vue-next'


const router = useRouter()
const store = useAuthStore()

const displayName = computed(() => store.user?.username || 'Guest')
const displayRole = computed(() => store.user?.role || '')
const avatarInitial = computed(() => (displayName.value?.[0] || 'U').toUpperCase())

async function handleLogout() {
  await logout();
  store.logout();
  router.push('/auth/login');
}
</script>

<template>
  <header class="bg-white border-b border-gray-200 h-16 px-6 flex items-center justify-between">
    <!-- Left section -->
    <div class="flex items-center gap-3 flex-1">
      <!-- Menu icon -->
      <button class="md:hidden h-9 w-9 rounded-lg bg-gray-100 flex items-center justify-center">
        <Menu class="w-5 h-5 text-gray-600" />
      </button>

      <!-- Search box -->
      <!-- <div class="hidden md:flex items-center gap-3 flex-1 max-w-xl bg-gray-100 rounded-lg px-3 py-2">
        <Search class="w-4 h-4 text-gray-500" />
        <input 
          class="bg-transparent outline-none flex-1 text-sm" 
          placeholder="Search projects, tasks, or teams..." 
        />
      </div> -->
    </div>

    <!-- Right section -->
    <div class="flex items-center gap-3">
      <!-- Notification -->
      <!-- <button class="relative h-9 w-9 rounded-lg bg-gray-100 flex items-center justify-center">
        <Bell class="w-5 h-5 text-gray-600" />
        <span class="absolute -top-1 -right-1 h-5 min-w-[20px] px-1 rounded-full bg-red-500 text-white text-[10px] leading-5 text-center">
          3
        </span>
      </button> -->

      <!-- Profile button -->
    <router-link to="/dashboard/profile" class="hidden sm:block">
    <button
        class="h-9 px-3 rounded-lg bg-indigo-600 text-white text-sm font-medium flex items-center justify-center gap-2"
      >
        <User class="w-4 h-4" />
        <span>Profile</span>
      </button>
    </router-link>

      <!-- Logout -->
      <button @click="handleLogout" class="text-sm px-3 py-2 rounded-lg border hover:bg-gray-50">
        Logout
      </button>

      <!-- Avatar -->
      <div class="flex items-center gap-2 pl-3 border-l">
        <div class="h-9 w-9 rounded-full bg-indigo-200 flex items-center justify-center text-indigo-700 font-semibold">
          {{ avatarInitial }}
        </div>
        <div class="hidden sm:block leading-tight">
          <p class="text-sm font-medium">{{ displayName }}</p>
          <p class="text-xs text-gray-500">{{ displayRole }}</p>
        </div>
      </div>
    </div>
  </header>
</template>
