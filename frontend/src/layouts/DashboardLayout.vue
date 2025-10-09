<!-- src/layouts/DashboardLayout.vue (Cập nhật để gọi components) -->
<script setup>
import Sidebar from '@/components/Sidebar.vue'  // Import Sidebar
import Header from '@/components/Header.vue'  // Import Header
</script>

<template>
  <div class="flex min-h-screen bg-gray-100">
    <!-- Sidebar component -->
    <Sidebar />

    <!-- Main content -->
    <div class="flex-1 flex flex-col">
      <!-- Header component -->
      <Header />
      
      <main class="p-6 flex-1 overflow-y-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>