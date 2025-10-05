<script setup>
import { ref } from 'vue';
import { login } from '@/api/authApi';  // Giả định path đúng (@ là alias cho src)

const credentials = ref({ username: '', password: '' });
const message = ref('');
const isLoading = ref(false);

async function handleLogin() {
  message.value = '';  // Reset message
  isLoading.value = true;
  try {
    await login(credentials.value);
    message.value = 'Đăng nhập thành công!';
  } catch (error) {
    message.value = `Đăng nhập thất bại: ${error.message}`;
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <form @submit.prevent="handleLogin">
    <input v-model="credentials.username" placeholder="Username" required />
    <input v-model="credentials.password" type="password" placeholder="Password" required />
    <button type="submit" :disabled="isLoading">
      {{ isLoading ? 'Đang đăng nhập...' : 'Login' }}
    </button>
  </form>
  <p v-if="message" :style="{ color: message.includes('thành công') ? 'green' : 'red' }">{{ message }}</p>
</template>