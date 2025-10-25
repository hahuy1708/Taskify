<!-- src/components/Projects/ProjectTableRow.vue -->
<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'

const props = defineProps({
  project: {
    type: Object,
    required: true
  }
})

// eslint-disable-next-line no-unused-vars
const emit = defineEmits(['edit', 'delete'])
const authStore = useAuthStore()

const canEdit = computed(() => {
  const user = authStore.user
  if (!user) return false
  if (user.role === 'admin') return true
  if (props.project.leader?.id === user.id) {
    return true
    
  }
  return false
})

const canDelete = computed(() => {
  const user = authStore.user
  if (!user) return false
  return user.role === 'admin' && !props.project.is_completed
})
</script>


<template>
  <tr v-if="authStore.user" class="border-b hover:bg-gray-50">
    <td class="px-6 py-4">{{ project.name }}</td>
    <td class="px-6 py-4">{{ project.description }}</td>
    <td class="px-6 py-4">{{ new Date(project.deadline).toLocaleDateString() }}</td>
    <td class="px-6 py-4">{{ project.member_count }}</td>
    <td class="px-6 py-4">
      <div class="flex items-center gap-2">
        <button
          v-if="canEdit"
          @click="$emit('edit', project)"
          class="text-blue-600 hover:text-blue-800"
        >
          Edit
        </button>
        <button
          v-if="canDelete"
          @click="$emit('delete', project)"
          class="text-red-600 hover:text-red-800"
        >
          Delete
        </button>
      </div>
    </td>
  </tr>
</template>