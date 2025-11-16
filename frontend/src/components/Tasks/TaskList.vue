<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { getTasks } from '@/api/taskApi'

const props = defineProps({
  projectId: { type: [String, Number, null], default: null },
})

const tasks = ref([])
const loading = ref(false)
const error = ref('')

const fetchTasks = async () => {
  try {
    loading.value = true
    error.value = ''
  const params = {}
    if (props.projectId) params.project = props.projectId
    const data = await getTasks(params)
    tasks.value = Array.isArray(data) ? data : (data?.results || [])
  } catch (e) {
    error.value = 'Failed to load tasks'
  } finally {
    loading.value = false
  }
}

let t = null
watch(
  () => props.projectId,
  () => {
    clearTimeout(t)
    t = setTimeout(fetchTasks, 200)
  }
)
onUnmounted(() => clearTimeout(t))
onMounted(fetchTasks)

defineExpose({ refresh: fetchTasks })

const fmtDate = (d) => {
  if (!d) return '-'
  try {
    const dt = new Date(d)
    if (Number.isNaN(dt.getTime())) return '-'
    return dt.toLocaleDateString()
  } catch (_) {
    return '-'
  }
}
</script>

<template>
  <template v-if="loading">
    <tr>
      <td colspan="6" class="text-center py-8">
        <div class="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
      </td>
    </tr>
  </template>

  <template v-else>
    <tr v-if="error">
      <td colspan="6" class="text-center py-6 text-red-600">{{ error }}</td>
    </tr>
    <tr v-else-if="!tasks.length">
      <td colspan="6" class="text-center py-6 text-gray-500">No tasks found.</td>
    </tr>
    <tr
      v-else
      v-for="t in tasks"
      :key="t.id"
      class="border-b hover:bg-gray-50"
    >
      <td class="px-6 py-4">
        <span class="text-gray-900 font-medium">{{ t.name }}</span>
      </td>
      <td class="px-6 py-4">
        <div class="flex items-center gap-2">
          <span class="text-gray-700">{{ t.project?.name || '—' }}</span>
          <span
            v-if="t.project?.is_personal"
            class="text-[10px] px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700"
          >Personal</span>
        </div>
      </td>
      <td class="px-6 py-4 text-gray-700">{{ t.status || 'todo' }}</td>
      <td class="px-6 py-4">
        <span
          class="text-[10px] px-2 py-0.5 rounded-full"
          :class="{
            'bg-gray-100 text-gray-700': !t.priority || t.priority === 'low',
            'bg-yellow-100 text-yellow-700': t.priority === 'medium',
            'bg-red-100 text-red-700': t.priority === 'high',
          }"
        >{{ (t.priority || 'low').toUpperCase() }}</span>
      </td>
  <td class="px-6 py-4 text-gray-700">{{ t.assignee?.full_name || t.assignee?.username || '—' }}</td>
      <td class="px-6 py-4 text-gray-700">{{ fmtDate(t.deadline) }}</td>
    </tr>
  </template>
</template>

<style scoped>
</style>
