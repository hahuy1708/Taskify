<script setup>
import { useAuthStore } from '@/store/auth';
import { logout } from '@/api/authApi';
import { useRouter } from 'vue-router';

const router = useRouter();
const store = useAuthStore();

async function handleLogout() {
  await logout();  
  store.logout();
  router.push('/auth/login');
}

</script>

<template>
 <div v-if="store.user">
  <h1>Welcome, {{ store.user?.username }} ({{ store.user?.role }})</h1>
  <button @click="handleLogout">Logout</button>
  <!-- Nội dung user: List tasks, projects -->
  <p>User dashboard: View your tasks, teams, etc.</p>
 </div>
 <p v-else>Loading or logged out...</p>
</template>