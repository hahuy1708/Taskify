<script setup>
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';
import { logout } from '@/api/authApi';
import { getProjects } from '@/api/coreAPi';
import { onMounted, ref } from 'vue';

const store = useAuthStore();
const router = useRouter();

const projects = ref([]);

onMounted(async () => {
  projects.value = await getProjects();
});

async function handleLogout() {
  await logout();
  store.logout();
  router.push('/auth/login');
}

// UI-only demo data below. Does not affect auth logic above.
const stats = [
  { label: 'Total Projects', value: 24, delta: '+12%' },
  { label: 'Active Users', value: 156, delta: '+8%' },
  { label: 'Tasks Completed', value: 892, delta: '+23%' },
  { label: 'Productivity', value: '94%', delta: '+5%' }
]

// const projects = [
//   { title: 'E-commerce Platform', desc: 'Building a modern e-commerce solution with React and Django', progress: 75, date: '2025-11-30', members: 8, status: 'Active', leader: 'Nguyễn Văn A' },
//   { title: 'Mobile App Redesign', desc: 'Complete UI/UX overhaul of the mobile application', progress: 40, date: '2025-12-18', members: 5, status: 'In Review', leader: 'Lê Văn C' }
// ]

const activities = [
  { user: 'Nguyễn Văn A', text: "completed task 'Database Schema Design'", time: '5 minutes ago' },
  { user: 'Trần Thị B', text: "created new project 'Marketing Campaign'", time: '1 hour ago' },
  { user: 'Lê Văn C', text: 'assigned task to team member', time: '2 hours ago' }
]
</script>

<template>
  <div v-if="store.user" class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold">Admin Dashboard</h1>
        <p class="text-gray-500">Overview of all projects and activities</p>
      </div>
      <button @click="handleLogout" class="text-sm px-3 py-2 rounded-lg border">Logout</button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <div v-for="s in stats" :key="s.label" class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <p class="text-sm text-gray-500">{{ s.label }}</p>
        <div class="mt-2 flex items-end justify-between">
          <p class="text-3xl font-bold">{{ s.value }}</p>
          <span class="text-xs text-emerald-600 bg-emerald-50 px-2 py-1 rounded">{{ s.delta }}</span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div class="xl:col-span-2 space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold">Recent Projects</h2>
          <button class="text-sm px-3 py-2 rounded-lg border">View All</button>
        </div>

        <div v-for="p in projects" :key="p.title" class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h3 class="font-semibold">{{ p.name }}</h3>
          <p class="text-sm text-gray-500">{{ p.description }}</p>
          <div class="mt-4">
            <div class="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
              <div class="h-full bg-indigo-600" :style="{ width: p.progress + '%' }"></div>
            </div>
            <div class="mt-2 flex items-center justify-between text-sm text-gray-600">
              <span>Progress</span>
              <span>{{ p.progress }}%</span>
            </div>
          </div>
          <div class="mt-4 flex items-center gap-4 text-sm text-gray-600">
            <span>Deadline 📅 {{ p.deadline }}</span>
            <span>Members 👥 {{ p.member_count }}</span>
            <span class="ml-auto px-2 py-0.5 rounded-full text-xs" :class="p.status === 'Active' ? 'bg-emerald-100 text-emerald-700' : 'bg-yellow-100 text-yellow-700'">{{ p.status }}</span>
          </div>
          <div class="mt-2 text-sm text-gray-500">Leader: 
            <span v-if="p.leader" class="text-gray-700 font-medium">
              {{ p.leader.name }} (#{{ p.leader.id }})
            </span>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <h2 class="text-xl font-semibold">Recent Activities</h2>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <div class="space-y-5">
            <div v-for="a in activities" :key="a.text" class="flex items-start gap-3">
              <div class="h-8 w-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-semibold">{{ a.user[0] }}</div>
              <div>
                <p class="text-sm"><span class="font-medium">{{ a.user }}</span> {{ a.text }}</p>
                <p class="text-xs text-gray-500">{{ a.time }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <p v-else>Loading or logged out...</p>
</template>