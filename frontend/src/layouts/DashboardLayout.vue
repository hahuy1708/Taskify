<!-- src/layouts/DashboardLayout.vue -->
<script setup>
import Sidebar from '@/components/Sidebar.vue'  
import Header from '@/components/Header.vue' 
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