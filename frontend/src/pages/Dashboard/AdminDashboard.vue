<script setup>
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';
import { logout } from '@/api/authApi';

const store = useAuthStore();
const router = useRouter();

async function handleLogout() {
  await logout();  // Optional nếu có endpoint
  store.logout();
  router.push('/auth/login');
}

</script>

<template>
    <div v-if="store.user">
  <h1>Welcome, {{ store.user?.username }} ({{ store.user?.role }})</h1>
  <button @click="handleLogout">Logout</button>
  <!-- Nội dung admin: Quản lý users, projects -->
  <p>Admin panel: Manage enterprise projects, teams, etc.</p>
  </div>
  <p v-else>Loading or logged out...</p>
</template>