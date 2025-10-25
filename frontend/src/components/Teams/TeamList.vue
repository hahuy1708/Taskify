<script setup>
import { ref, onMounted } from 'vue'
import { getListTeams } from '@/api/teamApi'
import TeamTableRow from './TeamTableRow.vue'

// const emit = defineEmits(['edit'])

const teams = ref([])
const loading = ref(true)

const fetchTeams = async () => {
  loading.value = true
  try {
    teams.value = await getListTeams()
  } catch (error) {
    console.error('Failed to fetch teams:', error)
  } finally {
    loading.value = false
  }
}

// const handleEdit = (team) => {
//   // Emit to parent so the parent can open an edit modal
//   emit('edit', team)
// }

// const handleDelete = async (project) => {
//   if (!confirm('Are you sure?')) return
//   try {
//     await deleteProject(project.id)
//     await fetchProjects()
//   } catch (error) {
//     console.error('Failed to delete:', error)
//   }
// }

onMounted(fetchTeams)

// Expose fetchProjects to parent components so they can trigger a reload
defineExpose({ fetchTeams })
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
    <TeamTableRow
      v-for="team in teams"
      :key="team.id"
      :team="team"
    />
  </template>
</template>