<script setup>
import { ref, onMounted } from 'vue'
import { getListTeams, getTeamMembers } from '@/api/teamApi'
import TeamTableRow from './TeamTableRow.vue'
import TeamMembersModal from './Modals/TeamMembersModal.vue'
import AddMembersModal from './Modals/AddMembersModal.vue'

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

// Modal & interaction state
const showMembersModal = ref(false)
const modalMembers = ref([])
const selectedTeamForView = ref(null)

const showAddModal = ref(false)
const selectedTeamForAdd = ref(null)

const handleViewMembers = async (team) => {
  try {
    modalMembers.value = []
    selectedTeamForView.value = team
    showMembersModal.value = true
    const data = await getTeamMembers(team.id)
    modalMembers.value = data
  } catch (error) {
    console.error('Failed to fetch team members:', error)
    showMembersModal.value = false
  }
}

const handleAddMembers = (team) => {
  selectedTeamForAdd.value = team
  showAddModal.value = true
}

const onMembersAdded = async () => {
  showAddModal.value = false
  // refresh list
  await fetchTeams()
  // if currently viewing members for the same team, refresh that list
  if (selectedTeamForView.value && selectedTeamForView.value.id === selectedTeamForAdd.value.id) {
    try {
      modalMembers.value = await getTeamMembers(selectedTeamForView.value.id)
    } catch (e) { console.error('Failed to refresh members after add', e) }
  }
}

onMounted(fetchTeams)

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
      @view-members="handleViewMembers"
      @add-members="handleAddMembers"
    />
  </template>
  <!-- Members modal component -->
  <TeamMembersModal v-if="showMembersModal" :team="selectedTeamForView" :members="modalMembers" @close="showMembersModal=false" />

  <!-- Add members modal component -->
  <AddMembersModal v-if="showAddModal" :team="selectedTeamForAdd" @close="() => (showAddModal=false)" @success="onMembersAdded" />
</template>