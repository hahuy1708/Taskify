<!-- src/components/Tasks/TaskTableRow.vue -->
<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import { EditIcon } from 'lucide-vue-next'

const emit = defineEmits(['edit'])
const props = defineProps({
  task: { type: Object, required: true },
})

const auth = useAuthStore()
const user = computed(() => auth.user)

const canEdit = computed(() => {
  const u = user.value
  const t = props.task
  if (!u || !t) return false
  const project = t.project || {}
  const ownerId = project.owner
  const isCreator = t.creator?.id === u.id
  const isPersonalProject = !!project.is_personal
  const isPersonalOwner = isPersonalProject && ((ownerId && ownerId === u.id))
  return isPersonalOwner || isCreator
})

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

const onEdit = () => emit('edit', props.task)
</script>

<template>
  <tr class="border-b hover:bg-gray-50">
    <td class="px-6 py-4">
      <span class="text-gray-900 font-medium">{{ task.name }}</span>
    </td>
    <td class="px-6 py-4">
      <div class="flex items-center gap-2">
        <span class="text-gray-700">{{ task.project?.name || '—' }}</span>
        <span v-if="task.project?.is_personal" class="text-[10px] px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">Personal</span>
      </div>
    </td>
    <td class="px-6 py-4 text-gray-700">{{ task.status || 'todo' }}</td>
    <td class="px-6 py-4">
      <span
        class="text-[10px] px-2 py-0.5 rounded-full"
        :class="{
          'bg-gray-100 text-gray-700': !task.priority || task.priority === 'low',
          'bg-yellow-100 text-yellow-700': task.priority === 'medium',
          'bg-red-100 text-red-700': task.priority === 'high',
        }"
      >{{ (task.priority || 'low').toUpperCase() }}</span>
    </td>
    <td class="px-6 py-4 text-gray-700">{{ task.assignee?.full_name || task.assignee?.username || '—' }}</td>
    <td class="px-6 py-4 text-gray-700">{{ fmtDate(task.deadline) }}</td>
    <td class="px-6 py-4 text-right">
      <button
        v-if="canEdit"
        @click="onEdit"
        class="px-3 py-1.5 text-xs rounded-lg border border-gray-300 hover:bg-gray-100"
        title="Edit task"
      >
        <EditIcon class="w-4 h-4" />
      </button>
      <span v-else class="text-xs text-gray-400">—</span>
    </td>
  </tr>
</template>

<style scoped></style>
