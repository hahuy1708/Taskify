<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { getTasks } from '@/api/taskApi'
import TaskTableRow from './TaskTableRow.vue'

const props = defineProps({
  projectId: { type: [String, Number, null], default: null },
})

const emit = defineEmits(['edit'])
const tasks = ref([])
const loading = ref(false)

const fetchTasks = async () => {
  loading.value = true
  try {
    const params = {}
    if (props.projectId) params.project = props.projectId
    const data = await getTasks(params)
    tasks.value = Array.isArray(data) ? data : (data?.results || [])
  } catch (e) {
    console.error('Failed to load tasks:', e)
  } finally {
    loading.value = false
  }
}

const handleEdit = (task) => {
  emit('edit', task)
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

defineExpose({ refresh: fetchTasks })

onMounted(() => {
  fetchTasks()
})

</script>

<template>
  <table class="min-w-full divide-y divide-gray-200">
    <thead>
      <tr class="bg-gray-50">
        <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Task</th>
        <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Project</th>
        <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
        <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Priority</th>
        <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Assignee</th>
        <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Deadline</th>
        <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-200">
      <TaskTableRow
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        @edit="handleEdit"
      />
    </tbody>
  </table>
</template>


