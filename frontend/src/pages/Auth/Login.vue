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
  router.push(role === 'admin' ? '/dashboard/admin' : '/dashboard/user');
}
</script>

<template>
  <div class="login-page">
    <LoginForm @login-success="handleLoginSuccess" />
    <p class="text-center mt-4">
      Don't have an account? 
      <router-link to="/auth/register" class="text-indigo-600 hover:text-indigo-800 underline">
        Register now
      </router-link>
    </p>
  </div>
</template>
