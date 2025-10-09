<template>
  <div class="flex h-screen bg-indigo-700">
    <div class="w-full max-w-xs m-auto bg-indigo-100 rounded p-5">
      <header>
        <img
          class="w-20 mx-auto mb-5"
          src="@/assets/images/logo.png"
          alt="Logo"
        />
      </header>

      <!-- Nơi render nội dung form -->
      <router-view />

      <footer class="mt-4 text-center">
        <router-link
          to="/forgot-password"
          class="text-indigo-700 hover:text-pink-700 text-sm"
        >
          Forgot Password?
        </router-link>
      </footer>

    </div>
  </div>
</template>
