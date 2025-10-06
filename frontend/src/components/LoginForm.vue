<!-- src/components/LoginForm.vue -->
<script setup>
import { ref } from 'vue';
import { login } from '@/api/authApi';

const emit = defineEmits(['login-success', 'login-failed']);
const credentials = ref({ username: '', password: '' });
const isLoading = ref(false);
const message = ref('');

async function handleLogin() {
  isLoading.value = true;
  message.value = '';
  try {
    await login(credentials.value);
    emit('login-success');
  } catch (err) {
    message.value = 'Đăng nhập thất bại';
    emit('login-failed', err);
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <form @submit.prevent="handleLogin">
    <input v-model="credentials.username" placeholder="Username" />
    <input v-model="credentials.password" type="password" />
    <button type="submit" :disabled="isLoading">
      {{ isLoading ? 'Đang đăng nhập...' : 'Login' }}
    </button>
    <p v-if="message" style="color:red;">{{ message }}</p>
  </form>
</template>
