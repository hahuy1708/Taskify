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
    <div class="mb-4">

      <input
        v-model="credentials.username"
        id="username"
        name="username"
        type="text"
        placeholder="Username"
        class="w-full p-2 text-indigo-700 border-b-2 border-indigo-500 outline-none focus:bg-gray-200"
      />
    </div>

    <div class="mb-6">
      
      <input
        v-model="credentials.password"
        id="password"
        name="password"
        type="password"
        placeholder="Password"
        class="w-full p-2 text-indigo-700 border-b-2 border-indigo-500 outline-none focus:bg-gray-200"
      />
    </div>

    <button
      type="submit"
      :disabled="isLoading"
      class="w-full bg-indigo-700 hover:bg-pink-700 text-white font-bold py-2 px-4 rounded transition-all duration-200"
    >
      {{ isLoading ? 'Đang đăng nhập...' : 'Submit' }}
    </button>

    <p v-if="message" class="text-red-500 text-center mt-4">{{ message }}</p>
  </form>
</template>