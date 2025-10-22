<!-- pages/Dashboard/AdminDashboard.vue -->
<script setup>
import { useAuthStore } from '@/store/auth';
import { getProjects } from '@/api/projectAPi';
import { getDashboardStats } from '@/api/statsApi';
import { computed, onMounted, ref, onActivated } from 'vue';
import ProjectCard from '@/components/Projects/ProjectCard.vue';

const store = useAuthStore();

const projects = ref([]);
const stats = ref({
  total_projects: 0,
  active_users: 0,
  tasks_completed: 0,
  productivity: 0,
  deltas: {
    projects: '0%',
    users: '0%',
    tasks: '0%',
    productivity: '0%'
  }
});
const urgentIssues = ref([])

async function loadData() {
  try {
    const [projectsData, statsData] = await Promise.all([
      getProjects(),
      getDashboardStats()
    ]);
    projects.value = projectsData;
    stats.value = statsData;
    urgentIssues.value = statsData.urgent_issues || [];
    // debug: log what the API returned so we can inspect in browser console
    console.debug('getDashboardStats response:', statsData);
  } catch (error) {
    console.error('Error loading dashboard data:', error);
  }
}

onMounted(() => {
  loadData();
});

// if this component is kept-alive by router, also refresh when activated
onActivated(() => {
  loadData();
});



const statCards = computed(() => [
  { label: 'Total Projects', value: stats.value.total_projects, delta: stats.value.deltas.projects },
  { label: 'Active Users', value: stats.value.active_users, delta: stats.value.deltas.users },
  { label: 'Tasks Completed', value: stats.value.tasks_completed, delta: stats.value.deltas.tasks },
  { label: 'Productivity', value: `${stats.value.productivity}%`, delta: stats.value.deltas.productivity }
]);

function formatDate(d) {
  if (!d) return 'N/A'
  try {
    const dt = new Date(d)
    return dt.toLocaleDateString()
  } catch(e) { return d }
}

function dueInDays(d) {
  if (!d) return ''
  try {
    const now = new Date()
    const dt = new Date(d)
    const diff = Math.ceil((dt - now) / (1000 * 60 * 60 * 24))
    if (diff < 0) return `${Math.abs(diff)}d overdue`
    return `in ${diff}d`
  } catch(e) { return '' }
}
</script>

<template>
  <div v-if="store.user" class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold">Admin Dashboard</h1>
        <p class="text-gray-500">Overview of all projects and activities</p>
      </div>
    </div>

        <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <div 
        v-for="stat in statCards" 
        :key="stat.label" 
        class="bg-white rounded-xl shadow-sm border border-gray-100 p-5"
      >
        <p class="text-sm text-gray-500">{{ stat.label }}</p>
        <div class="mt-2 flex items-end justify-between">
          <p class="text-3xl font-bold">{{ stat.value }}</p>
          <span 
            :class="[
              'text-xs px-2 py-1 rounded',
              stat.delta.startsWith('+') 
                ? 'text-emerald-600 bg-emerald-50' 
                : 'text-red-600 bg-red-50'
            ]"
          >
            {{ stat.delta }}
          </span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div class="xl:col-span-2 space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold">Recent Projects</h2>
          <router-link to="/dashboard/projects" class="text-sm px-3 py-2 rounded-lg border">View All</router-link>
        </div>

        <div class="grid grid-cols-1 gap-4">
          <ProjectCard v-for="p in projects" :key="p.id" :project="p" />
        </div>
      </div>
     
      <div class="space-y-4">
        <h2 class="text-xl font-semibold">Urgent Issues</h2>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <div class="space-y-3">
            <template v-if="urgentIssues.length === 0">
              <p class="text-sm text-gray-500">No urgent issues.</p>
            </template>
            <template v-else>
              <div v-for="item in urgentIssues" :key="item.project_id" class="flex items-start gap-3">
                <div class="h-8 w-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-semibold">{{ item.project_name ? item.project_name[0] : 'P' }}</div>
                <div class="flex-1">
                  <p class="text-sm"><span class="font-medium">{{ item.project_name }}</span>
                    <span class="text-gray-500"> · Leader: {{ item.leader?.username || 'N/A' }}</span>
                  </p>
                  <p class="text-xs text-gray-500">Due: <span class="font-medium">{{ formatDate(item.deadline) }}</span>
                    <span v-if="item.deadline"> • {{ dueInDays(item.deadline) }}</span>
                    <span class="ml-2">• Progress: <span class="font-medium">{{ item.progress }}%</span></span>
                  </p>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
  <p v-else>Loading or logged out...</p>
</template>