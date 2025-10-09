<!-- src/pages/Auth/Register.vue -->
<script setup>
import RegisterForm from '@/components/RegisterForm.vue';
import { useRouter } from 'vue-router';

const router = useRouter();

function handleRegisterSuccess() {
  // Redirect to login page after successful registration
  router.push('/auth/login');
}

function handleRegisterFailed(error) {
  console.error('Registration failed:', error);
}
</script>

<template>
  <div class="register-page">
    <h1>Đăng ký tài khoản mới</h1>
    <RegisterForm @register-success="handleRegisterSuccess" @register-failed="handleRegisterFailed" />
    <p class="text-center mt-4">
      Đã có tài khoản? 
      <router-link to="/auth/login" class="text-indigo-600 hover:text-indigo-800 underline">
        Đăng nhập ngay
      </router-link>
    </p>
  </div>
</template>
