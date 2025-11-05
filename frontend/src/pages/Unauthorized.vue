<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const auth = useAuthStore()
const role = computed(() => auth.user?.role || 'user')

const goBack = () => {
  if (role.value === 'admin') router.push('/dashboard/admin')
  else router.push('/dashboard/user')
}
</script>

<template>
  <div class="min-h-[60vh] flex items-center justify-center">
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 max-w-lg w-full text-center">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">403 — Unauthorized</h1>
      <p class="text-gray-600 mb-6">Bạn không có quyền truy cập chức năng này. Nếu bạn nghĩ đây là nhầm lẫn, vui lòng liên hệ quản trị viên.</p>
      <button
        @click="goBack"
        class="inline-flex items-center justify-center px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-500"
      >
        Quay lại Dashboard
      </button>
    </div>
  </div>
</template>

<style scoped></style>
