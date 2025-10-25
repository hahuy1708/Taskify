<!-- src/components/Projects/ProjectTableRow.vue -->
<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import { Users, UserPlus } from 'lucide-vue-next'

const props = defineProps({
  team: {
    type: Object,
    required: true
  }
})

// eslint-disable-next-line no-unused-vars
const emit = defineEmits(['view-members', 'add-members'])
const authStore = useAuthStore()

const canEdit = computed(() => {
  const user = authStore.user
  if (!user) return false
  if (props.team.leader?.id === user.id) {
    return true
  }
  return false
})

// const canDelete = computed(() => {
//   const user = authStore.user
//   if (!user) return false
//   return props.team.leader?.id === user.id
// })

const isMember = computed(() => {
  const user = authStore.user
  if (!user) return false
  return props.team.memberships?.some(m => m.user?.id === user.id)
})

</script>


<template>
  <tr v-if="authStore.user" class="border-b hover:bg-gray-50">
    <td class="px-6 py-4 align-middle">{{ team.name }}</td>
    <td class="px-6 py-4 align-middle">{{ team.project }}</td>
    <td class="px-6 py-4 align-middle">{{ team.leader?.username }}</td>
    <td class="px-6 py-4 align-middle">{{ team.memberships?.length }}</td>
    <td class="px-6 py-4 align-middle text-center">
      <div class="flex items-center gap-2 justify-center">
        <button
          @click="$emit('view-members', team)"
          class="inline-flex items-center gap-1 text-gray-700 hover:text-gray-900"
          v-if="isMember || canEdit || authStore.user?.role === 'admin'"
        >
          <Users :size="18" />
          <span>View</span>
        </button>

        <button
          v-if="canEdit"
          @click="$emit('add-members', team)"
          class="inline-flex items-center gap-1 text-green-600 hover:text-green-800"
        >
          <UserPlus :size="18" />
          <span>Add</span>
        </button>
<!-- 
        <button
          v-if="canEdit"
          @click="$emit('edit', team)"
          class="text-blue-600 hover:text-blue-800"
        >
          Edit
        </button>
        <button
          v-if="canDelete"
          @click="$emit('delete', team)"
          class="text-red-600 hover:text-red-800"
        >
          Delete
        </button> -->
      </div>
    </td>
  </tr>
</template>