<script setup>
import { ref } from 'vue';
import { login, getProfile } from '@/api/authApi';  // Giả định path đúng (@ là alias cho src)
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';

const router = useRouter();
const store = useAuthStore();
const credentials = ref({ username: '', password: '' });
const message = ref('');
const isLoading = ref(false);

async function handleLogin() {
  message.value = '';
  isLoading.value = true;
  try {
    await login(credentials.value);
    const profile = await getProfile();  // Fetch name + role
    store.setUser(profile);  // Lưu vào store
    const role = profile.role;
    router.push(role === 'admin' ? '/admin-dashboard' : '/user-dashboard');  // Redirect dựa trên role
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
  <p v-if="message" style="color: red;">{{ message }}</p>
</template>