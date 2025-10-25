<script setup>
import { ref } from 'vue'
// import { useAuthStore } from '@/store/auth'
import TeamList from '@/components/Teams/TeamList.vue'

// const authStore = useAuthStore()
// const showCreateModal = ref(false)
// const showUpdateModal = ref(false)
// const selectedProject = ref(null)
const teamListRef = ref(null)

// const handleEdit = (project) => {
//   selectedProject.value = project
//   showUpdateModal.value = true
// }

// const handleUpdateSuccess = async () => {
//   showUpdateModal.value = false
//   // Optionally update local selectedProject or show a message using updatedProject
//   if (projectListRef.value && projectListRef.value.fetchProjects) {
//     await projectListRef.value.fetchProjects()
//   }
// }

// const handleCreateSuccess = async () => {
//   showCreateModal.value = false
//   if (projectListRef.value && projectListRef.value.fetchProjects) {
//     await projectListRef.value.fetchProjects()
//   }
// }

</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Your Teams</h1>
        <p class="text-sm text-gray-500">Manage Your Teams</p>
      </div>
      
      <!-- <button 
        v-if="authStore.user?.team.id === team.id"
        @click="showCreateModal = true"
        class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2"
      >
        <span>+</span>
        Create Team
      </button> -->
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
    <TeamList ref="teamListRef" @edit="handleEdit" />
        </tbody>
      </table>
    </div>

    <!-- Modals
    <UpdateProjectModal
      v-if="showUpdateModal"
      :project="selectedProject"
      :userRole="authStore.user?.role || 'user'"
      @close="showUpdateModal = false"
      @success="handleUpdateSuccess"
    />

    <CreateProjectModal
      v-if="showCreateModal"
      @close="showCreateModal = false"
      @success="handleCreateSuccess"
    /> -->
  </div>
</template>