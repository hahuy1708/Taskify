<script setup>
import { useAuthStore } from '@/store/auth';

const store = useAuthStore();
</script>

<template>
  <h1>Welcome, {{ store.user.username }} ({{ store.user.role }})</h1>
  <!-- Nội dung user: List tasks, projects -->
  <p>User dashboard: View your tasks, teams, etc.</p>
</template>