<!-- src/views/Auth/Login.vue -->
<script setup>
import LoginForm from '@/components/LoginForm.vue';
import { getProfile } from '@/api/authApi';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';

const store = useAuthStore();
const router = useRouter();

async function handleLoginSuccess() {
  const profile = await getProfile();
  store.setUser(profile);
  const role = profile.role;
  // router.push('/dashboard');
  router.push(role === 'admin' ? '/dashboard/admin' : '/dashboard/user');
}
</script>

<template>
  <div class="login-page">
    <h1>Đăng nhập vào hệ thống</h1>
    <LoginForm @login-success="handleLoginSuccess" />
  </div>
</template>
