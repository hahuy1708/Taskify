<script setup>

import { useAuthStore } from '@/store/auth';
import { getDashboardStats } from '@/api/statsApi';
import { getProjects } from '@/api/projectAPi';
import { computed, onMounted, ref } from 'vue';
import ProjectCard from '@/components/Projects/ProjectCard.vue';


const store = useAuthStore();

const projects = ref([]);
const stats = ref({
  assigned_projects: 0,
  assigned_tasks: 0,
  completed_tasks: 0,
  productivity: 0,
});
const upcomingDeadlines = ref([])

onMounted(async () => {
  try {
    const [projectsData, statsData] = await Promise.all([
      getProjects(),
      getDashboardStats()
    ]);
    projects.value = projectsData;
    stats.value = statsData;
    upcomingDeadlines.value = statsData.upcoming_deadlines || []
  } catch (error) {
    console.error('Error loading dashboard data:', error);
  }
});


const statCards = computed(() => [
  { label: 'Assigned Projects', value: stats.value.assigned_projects },
  { label: 'Assigned Tasks', value: stats.value.assigned_tasks },
  { label: 'Tasks Completed', value: stats.value.completed_tasks },
  { label: 'Productivity', value: `${stats.value.productivity}%` }
]);

function formatDate(d) {
  if (!d) return 'N/A'
  try {
    const dt = new Date(d)
    return dt.toLocaleDateString()
  } catch(e) {
    return d
  }
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
        <h1 class="text-3xl font-bold">Your Dashboard</h1>
        <p class="text-gray-500">Overview of all your works and activities</p>
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
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div class="xl:col-span-2 space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold">Joined Projects</h2>
          <router-link to="/dashboard/projects" class="text-sm px-3 py-2 rounded-lg border">View All</router-link>
        </div>

        <div class="grid grid-cols-1 gap-4">
          <ProjectCard v-for="p in projects" :key="p.id" :project="p" />
        </div>
      </div>
     
      <div class="space-y-4">
        <h2 class="text-xl font-semibold">Upcoming Deadlines</h2>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <div class="space-y-3">
            <template v-if="upcomingDeadlines.length === 0">
              <p class="text-sm text-gray-500">No upcoming deadlines.</p>
            </template>
            <template v-else>
              <div v-for="item in upcomingDeadlines" :key="item.id || item.name" class="flex items-start gap-3">
                <div class="h-8 w-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-semibold">{{ (item.assignee && item.assignee.username) ? item.assignee.username[0] : (item.project && item.project.name ? item.project.name[0] : 'T') }}</div>
                <div class="flex-1">
                  <p class="text-sm">
                    <span class="font-medium">{{ item.name }}</span>
                    <span class="text-gray-500"> · {{ item.project?.name || 'No project' }}</span>
                  </p>
                  <p class="text-xs text-gray-500">
                    Due: <span class="font-medium">{{ formatDate(item.deadline) }}</span>
                    <span v-if="item.deadline"> • {{ dueInDays(item.deadline) }}</span>
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