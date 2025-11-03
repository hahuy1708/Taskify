<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import TeamList from '@/components/Teams/TeamList.vue'
import { getProjects } from '@/api/projectAPi'
import { createTeam } from '@/api/teamApi'
import { PlusCircle } from 'lucide-vue-next'

const authStore = useAuthStore()
const teamListRef = ref(null)

// Create team modal state
const projects = ref([])
const showCreateModal = ref(false)
const selectedProjectId = ref(null)
const newTeamName = ref('')

const canCreateTeams = computed(() => {
  if (!authStore.user) return false
  return projects.value.some(p => p.leader?.id === authStore.user.id)
})

onMounted(async () => {
  try {
    projects.value = await getProjects()
  } catch (err) {
    console.error('Failed to fetch projects for team creation:', err)
  }
})

const filteredProjects = computed(() =>{
  if (!authStore.user) return []
  if (authStore.user.role === 'admin') return projects.value
  return projects.value.filter(p => p.leader?.id === authStore.user.id)
})

const handleCreateTeam = async () => {
  if (!selectedProjectId.value || !newTeamName.value) return
  try {
    await createTeam(selectedProjectId.value, newTeamName.value)
    showCreateModal.value = false
    newTeamName.value = ''
    selectedProjectId.value = null
    if (teamListRef.value && teamListRef.value.fetchTeams) await teamListRef.value.fetchTeams()
  } catch (err) {
    console.error('Failed to create team:', err)
    alert(err.response?.data?.detail || err.message || 'Create failed')
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Your Teams</h1>
      </div>
      <!-- Create team button -->
      <div class="mt-4">
        <button v-if="canCreateTeams" @click="showCreateModal = true" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg">
          <PlusCircle class="w-4 h-4 inline-block mr-1" />
          Create Team
        </button>
      </div>
    </div>

    <!-- Team List -->
    <div class="bg-white rounded-xl shadow-sm">
      <table class="min-w-full divide-y divide-gray-200">
        <thead>
          <tr class="bg-gray-50">
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Name</th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Project</th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Leader</th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Members</th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <TeamList ref="teamListRef" />
        </tbody>
      </table>
    </div>


    <!-- Create Team Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-semibold mb-3">Create Team</h3>
        <label class="block text-sm">Select Project</label>
        <select v-model="selectedProjectId" class="w-full border p-2 rounded mt-1">
          <option v-for="p in filteredProjects" :key="p.id" :value="p.id">
             {{ p.name }}
          </option>
        </select>
        <label class="block text-sm mt-3">Team Name</label>
        <input v-model="newTeamName" class="w-full border p-2 rounded mt-1" />
        <div class="mt-4 flex justify-end gap-2">
          <button @click="showCreateModal = false" class="px-4 py-2 bg-gray-200 rounded">Cancel</button>
          <button @click="handleCreateTeam" class="px-4 py-2 bg-blue-600 text-white rounded">Create</button>
        </div>
      </div>
    </div>

  </div>
</template>