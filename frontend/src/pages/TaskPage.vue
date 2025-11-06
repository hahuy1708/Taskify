<script setup>
import { ref, watch } from 'vue'
import { getProjects } from '@/api/projectAPi'
import TaskList from '@/components/Tasks/TaskList.vue'
import KanbanBoard from '@/components/KanbanBoard.vue'
import UpdateTaskModal from '@/components/Tasks/Modals/UpdateTaskModal.vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// Project filter
const projects = ref([])
const selectedProjectId = ref('')
const activeTab = ref('list') // 'list' | 'board'

const isLoadingProjects = ref(false)
const loadProjects = async () => {
  try {
    isLoadingProjects.value = true
    projects.value = await getProjects()
  } finally {
    isLoadingProjects.value = false
  }
}
loadProjects()

// Initialize from URL query
watch(
  () => route.query,
  (q) => {
    if (q?.project) selectedProjectId.value = q.project
    if (q?.tab === 'board' || q?.tab === 'list') activeTab.value = q.tab
  },
  { immediate: true }
)


// Keep URL query in sync when user changes project from the dropdown
watch(
  () => selectedProjectId.value,
  (pid) => {
    const newQuery = { ...route.query }
    if (pid) newQuery.project = pid
    else delete newQuery.project
    // preserve current tab
    if (!newQuery.tab) newQuery.tab = activeTab.value
    router.replace({ query: newQuery })
  }
)


const listRef = ref(null)
const editOpen = ref(false)
const editingTask = ref(null)

const onEditTask = (task) => {
  editingTask.value = task
  editOpen.value = true
}

const onEditSuccess = () => {
  editOpen.value = false
  if (listRef.value?.refresh) listRef.value.refresh()
}

 </script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Tasks</h1>
        <p class="text-sm text-gray-500">Create and manage tasks across projects</p>
      </div>

      <!-- Create button moved to Board tab via KanbanBoard -->
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-3 items-center">
      <div>
        <select
          v-model="selectedProjectId"
          class="border border-gray-300 text-gray-700 text-sm px-3 py-2 rounded-lg min-w-60 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Select a project</option>
          <option v-for="p in projects" :key="p.id" :value="p.id">
            {{ p.name }} {{ p.is_personal ? '[Personal]' : '[Company]' }}
          </option>
        </select>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex gap-4" aria-label="Tabs">
        <button
          class="px-3 py-2 text-sm border-b-2"
          :class="activeTab==='list' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
          @click="activeTab='list'; router.replace({ query: { ...route.query, tab: 'list', project: selectedProjectId || '' } })"
        >
          List
        </button>
        <button
          class="px-3 py-2 text-sm border-b-2"
          :class="activeTab==='board' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
          @click="activeTab='board'; router.replace({ query: { ...route.query, tab: 'board', project: selectedProjectId || '' } })"
        >
          Board
        </button>
      </nav>
    </div>

    <div v-if="activeTab==='list'" class="bg-white rounded-xl shadow-sm">
      <TaskList ref="listRef" :project-id="selectedProjectId || null" @edit="onEditTask" />
    </div>

    <div v-else>
      <KanbanBoard :project-id="selectedProjectId || null" />
    </div>

    <UpdateTaskModal
      v-if="editingTask"
      :task="editingTask"
      :open="editOpen"
      @close="editOpen=false"
      @success="onEditSuccess"
    />
  </div>
</template>

<style scoped></style>
