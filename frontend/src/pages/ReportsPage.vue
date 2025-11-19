<script setup>
import { onMounted, ref } from 'vue'
import { LayoutDashboard, BarChartHorizontal } from 'lucide-vue-next'
import { getReportsOverview, getReportsMembersWorkload } from '@/api/statsApi'
import ReportLayout from '@/layouts/ReportLayout.vue'
import ProjectStatusPie from '@/components/Reports/Overview/ProjectStatusPie.vue'
import TaskPriorityBars from '@/components/Reports/Overview/TaskPriorityBars.vue'
import ProjectCompletionBars from '@/components/Reports/Overview/ProjectCompletionBars.vue'
import TopContributorsBar from '@/components/Reports/Members-Workload/TopContributorsBar.vue'
import TeamWorkloadBar from '@/components/Reports/Members-Workload/TeamWorkloadBar.vue'
import ProjectsByLeaderBar from '@/components/Reports/Members-Workload/ProjectsByLeaderBar.vue'

const loading = ref(false)
const error = ref('')
const overview = ref({
  project_status: { active: 0, completed: 0, overdue: 0 },
  task_priority: { high: 0, medium: 0, low: 0 },
  completion_bars: []
})
const membersWorkload = ref({
  top_contributors: [],
  team_workload: [],
  projects_by_leader: []
})

const activeTab = ref('overview')
const tabs = [
  { key: 'overview', label: 'Overview', icon: LayoutDashboard },
  { key: 'members-workload', label: 'Members-Workload', icon: BarChartHorizontal },
]

async function load() {
  loading.value = true
  error.value = ''
  try {
    overview.value = await getReportsOverview()
    membersWorkload.value = await getReportsMembersWorkload()
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Failed to load reports overview'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <ReportLayout v-model="activeTab" :tabs="tabs" title="Reports" subtitle="Insightful metrics for your workspace">
    <div class="space-y-6">
      <div v-if="loading" class="text-center text-gray-500 py-8">Loading…</div>
      <div v-else-if="error" class="text-center text-red-600 py-8">{{ error }}</div>
      <template v-else>
        <template v-if="activeTab === 'overview'">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ProjectStatusPie :status="overview.project_status" />
            <TaskPriorityBars :priority="overview.task_priority" />
          </div>
          <ProjectCompletionBars :projects="overview.completion_bars" />
        </template>
        <template v-else-if="activeTab === 'members-workload'">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TopContributorsBar :contributors="membersWorkload.top_contributors" />
            <TeamWorkloadBar :teams="membersWorkload.team_workload" />
          </div>
          <ProjectsByLeaderBar :leaders="membersWorkload.projects_by_leader" />
        </template>
      </template>
    </div>
  </ReportLayout>
</template>

<style scoped>
</style>
