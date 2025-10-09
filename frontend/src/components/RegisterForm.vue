<!-- src/components/RegisterForm.vue -->
<script setup>
import { ref } from 'vue';
import { register } from '@/api/authApi';

const emit = defineEmits(['register-success', 'register-failed']);
const userData = ref({
  username: '',
  email: '',
  password: '',
  re_password: '',
  full_name: '',
  phone_number: '',
  birth_date: '',
  address: ''
});
const isLoading = ref(false);
const message = ref('');

async function handleRegister() {
  isLoading.value = true;
  message.value = '';
  
  // Basic validation
  if (userData.value.password !== userData.value.re_password) {
    message.value = 'Mật khẩu xác nhận không khớp';
    isLoading.value = false;
    return;
  }
  
  if (!userData.value.username || !userData.value.email || !userData.value.password) {
    message.value = 'Vui lòng điền đầy đủ thông tin bắt buộc';
    isLoading.value = false;
    return;
  }
  
  try {
    await register(userData.value);
    emit('register-success');
  } catch (err) {
    message.value = 'Đăng ký thất bại';
    emit('register-failed', err);
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <form @submit.prevent="handleRegister">
    <div class="mb-4">
      <input
        v-model="userData.username"
        id="username"
        name="username"
        type="text"
        placeholder="Username *"
        required
        class="w-full p-2 text-indigo-700 border-b-2 border-indigo-500 outline-none focus:bg-gray-200"
      />
    </div>

    <div class="mb-4">
      <input
        v-model="userData.email"
        id="email"
        name="email"
        type="email"
        placeholder="Email *"
        required
        class="w-full p-2 text-indigo-700 border-b-2 border-indigo-500 outline-none focus:bg-gray-200"
      />
    </div>

    <div class="mb-4">
      <input
        v-model="userData.password"
        id="password"
        name="password"
        type="password"
        placeholder="Password *"
        required
        class="w-full p-2 text-indigo-700 border-b-2 border-indigo-500 outline-none focus:bg-gray-200"
      />
    </div>

    <div class="mb-4">
      <input
        v-model="userData.re_password"
        id="re_password"
        name="re_password"
        type="password"
        placeholder="Confirm Password *"
        required
        class="w-full p-2 text-indigo-700 border-b-2 border-indigo-500 outline-none focus:bg-gray-200"
      />
    </div>

    <div class="mb-4">
      <input
        v-model="userData.full_name"
        id="full_name"
        name="full_name"
        type="text"
        placeholder="Full Name"
        class="w-full p-2 text-indigo-700 border-b-2 border-indigo-500 outline-none focus:bg-gray-200"
      />
    </div>

    <div class="mb-4">
      <input
        v-model="userData.phone_number"
        id="phone_number"
        name="phone_number"
        type="tel"
        placeholder="Phone Number"
        class="w-full p-2 text-indigo-700 border-b-2 border-indigo-500 outline-none focus:bg-gray-200"
      />
    </div>

    <div class="mb-4">
      <input
        v-model="userData.birth_date"
        id="birth_date"
        name="birth_date"
        type="date"
        placeholder="Birth Date"
        class="w-full p-2 text-indigo-700 border-b-2 border-indigo-500 outline-none focus:bg-gray-200"
      />
    </div>

    <div class="mb-6">
      <textarea
        v-model="userData.address"
        id="address"
        name="address"
        placeholder="Address"
        rows="3"
        class="w-full p-2 text-indigo-700 border-b-2 border-indigo-500 outline-none focus:bg-gray-200 resize-none"
      ></textarea>
    </div>

    <button
      type="submit"
      :disabled="isLoading"
      class="w-full bg-indigo-700 hover:bg-pink-700 text-white font-bold py-2 px-4 rounded transition-all duration-200"
    >
      {{ isLoading ? 'Đang đăng ký...' : 'Register' }}
    </button>

    <p v-if="message" class="text-red-500 text-center mt-4">{{ message }}</p>
  </form>
</template>
