<!-- pages/Dashboard/DashboardHome.vue -->
<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/store/auth';
import AdminDashboard from '@/pages/Dashboard/AdminDashboard.vue';
import UserDashboard from '@/pages/Dashboard/UserDashboard.vue';

const store = useAuthStore();
const role = computed(() => store.user?.role || store.getRole());
</script>

<template>
  <div>
    <AdminDashboard v-if="role === 'admin'" />
    <UserDashboard v-else />
  </div>
  
</template>
