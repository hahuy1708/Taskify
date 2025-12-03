<!-- src/pages/Auth/ForgotPassword.vue -->
<script setup>
import { ref } from 'vue';
import { forgotPassword } from '@/api/authApi';

const email = ref('');
const isLoading = ref(false);
const message = ref('');
const success = ref(false);

async function handleForgotPassword() {
  isLoading.value = true;
  message.value = '';
  success.value = false;
  
  if (!email.value) {
    message.value = 'Please enter your email address';
    isLoading.value = false;
    return;
  }
  
  try {
    await forgotPassword({ email: email.value });
    success.value = true;
    message.value = 'A password reset link has been sent to your email. Please check your inbox.';
  } catch (error) {
    message.value = error.message || 'An error occurred. Please try again.';
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="forgot-password-page max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-6 text-center">Forgot Password</h2>
    
    <form @submit.prevent="handleForgotPassword">
      <div class="mb-4">
        <label for="email" class="block text-sm font-medium text-gray-700">Email *</label>
        <input
          v-model="email"
          id="email"
          type="email"
          required
          class="mt-1 w-full p-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Enter your email"
        />
      </div>

      <button
        type="submit"
        :disabled="isLoading"
        class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:bg-indigo-400"
      >
        {{ isLoading ? 'Sending...' : 'Send Reset Link' }}
      </button>
    </form>

    <p v-if="message" class="mt-4 text-center" :class="{ 'text-green-600': success, 'text-red-600': !success }">
      {{ message }}
    </p>

    <p class="mt-4 text-center text-sm">
      <router-link to="/auth/login" class="text-indigo-600 hover:underline">Back to Login</router-link>
    </p>
  </div>
</template>

