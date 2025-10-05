<script setup>
import { useAuthStore } from '@/store/auth';

const store = useAuthStore();
</script>

<template>
  <h1>Welcome, {{ store.user.username }} ({{ store.user.role }})</h1>
  <!-- Nội dung admin: Quản lý users, projects -->
  <p>Admin panel: Manage enterprise projects, teams, etc.</p>
</template>