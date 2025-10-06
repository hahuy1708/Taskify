<template>
  <div class="flex min-h-screen">
    <!-- Sidebar -->
    <aside class="w-64 bg-gray-900 text-white p-4">
      <h2 class="text-xl font-bold mb-4">Taskify</h2>
      <nav>
        <router-link to="/dashboard" class="block py-2">Dashboard</router-link>
        <router-link to="/projects" class="block py-2">Projects</router-link>
      </nav>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col">
      <header class="bg-white shadow p-4">Welcome, {{ user.username }}</header>
      <main class="p-6 bg-gray-100 flex-1">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
const user = { name: "Admin" }
</script>
