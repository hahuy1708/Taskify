<!-- src/pages/Auth/ResetPasswordConfirm.vue -->
<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { resetPasswordConfirm } from '@/api/authApi';

const route = useRoute();
const router = useRouter();
const uid = route.params.uid;
const token = route.params.token;

const newPassword = ref('');
const reNewPassword = ref('');
const isLoading = ref(false);
const message = ref('');
const success = ref(false);

async function handleResetConfirm() {
  isLoading.value = true;
  message.value = '';
  success.value = false;
  
  if (newPassword.value !== reNewPassword.value) {
    message.value = 'Passwords do not match';
    isLoading.value = false;
    return;
  }
  
  if (!newPassword.value) {
    message.value = 'Please enter a new password';
    isLoading.value = false;
    return;
  }
  
  try {
    await resetPasswordConfirm({ uid, token, new_password: newPassword.value, re_new_password: reNewPassword.value });
    success.value = true;
    message.value = 'Password has been reset successfully. You will be redirected to the login page.';
    setTimeout(() => router.push('/auth/login'), 2000);  // Redirect after 2s
  } catch (error) {
    message.value = error.message || 'An error occurred. The link may have expired.';
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="reset-confirm-page max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-6 text-center">Reset Password</h2>
    
    <form @submit.prevent="handleResetConfirm">
      <div class="mb-4">
        <label for="new_password" class="block text-sm font-medium text-gray-700">New Password *</label>
        <input
          v-model="newPassword"
          id="new_password"
          type="password"
          required
          class="mt-1 w-full p-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Enter new password"
        />
      </div>

      <div class="mb-4">
        <label for="re_new_password" class="block text-sm font-medium text-gray-700">Confirm New Password *</label>
        <input
          v-model="reNewPassword"
          id="re_new_password"
          type="password"
          required
          class="mt-1 w-full p-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Confirm new password"
        />
      </div>

      <button
        type="submit"
        :disabled="isLoading"
        class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 disabled:bg-indigo-400"
      >
        {{ isLoading ? 'Confirming...' : 'Confirm Reset' }}
      </button>
    </form>

    <p v-if="message" class="mt-4 text-center" :class="{ 'text-green-600': success, 'text-red-600': !success }">
      {{ message }}
    </p>

    <p v-if="success" class="mt-4 text-center text-sm">
      <router-link to="/auth/login" class="text-indigo-600 hover:underline">Back to Login</router-link>
    </p>
  </div>
</template>