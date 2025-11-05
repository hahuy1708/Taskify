<!-- src/components/Projects/ProjectTableRow.vue -->
<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import { EditIcon, Trash2, EyeIcon } from 'lucide-vue-next'

const props = defineProps({
  project: {
    type: Object,
    required: true
  }
})

// eslint-disable-next-line no-unused-vars
const emit = defineEmits(['edit', 'delete'])
const authStore = useAuthStore()

const isPersonal = computed(() => !!props.project?.is_personal)

const leaderName = computed(() => {
  if (isPersonal.value) return '—'
  const leader = props.project?.leader
  return leader?.full_name || leader?.username || leader?.name || '—'
})

const safeDate = (val) => {
  if (!val) return '—'
  const d = new Date(val)
  return isNaN(d.getTime()) ? '—' : d.toLocaleDateString()
}

const canEdit = computed(() => {
  const user = authStore.user
  if (!user) return false
  if (isPersonal.value) {
    const ownerId = props.project?.owner?.id ?? props.project?.owner
    return ownerId === user.id
  } else {
    return user.role === 'admin' || props.project?.leader?.id === user.id
  }
})

const canDelete = computed(() => {
  const user = authStore.user
  if (!user || props.project?.is_completed) return false
  if (isPersonal.value) {
    const ownerId = props.project?.owner?.id ?? props.project?.owner
    return ownerId === user.id
  }
  return user.role === 'admin'
})
</script>


<template>
  <tr v-if="authStore.user" class="border-b hover:bg-gray-50">
    <td class="px-6 py-4">
      <div class="flex items-center gap-2">
        <span class="font-medium">{{ project.name }}</span>
        <span v-if="isPersonal" class="text-[10px] px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">Personal</span>
      </div>
    </td>
    <td class="px-6 py-4">{{ project.description }}</td>
    <td class="px-6 py-4">{{ safeDate(project.deadline) }}</td>
    <td class="px-6 py-4">{{ leaderName }}</td>
    <td class="px-6 py-4">{{ project.member_count }}</td>
    <td class="px-6 py-4">
      <div class="flex items-center gap-2">
        <router-link
          :to="{ path: '/dashboard/tasks', query: { project: project.id, tab: 'board' } }"
          class="text-blue-600 hover:text-blue-800 text-sm"
        >
          <EyeIcon class="w-4 h-4 mr-1" />
        </router-link>
        <button
          v-if="canEdit"
          @click="$emit('edit', project)"
          class="text-blue-600 hover:text-blue-800"
        >
          <EditIcon class="w-4 h-4 mr-1" />
        </button>
        <button
          v-if="canDelete"
          @click="$emit('delete', project)"
          class="text-red-600 hover:text-red-800"
        >
          <Trash2 class="w-4 h-4 mr-1" />
        </button>
      </div>
    </td>
  </tr>
</template>