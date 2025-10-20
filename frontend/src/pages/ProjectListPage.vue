<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/store/auth'
import ProjectList from '@/components/Projects/ProjectList.vue'
import UpdateProjectModal from '@/components/Projects/Modals/UpdateProjectModal.vue'
import CreateProjectModal from '@/components/Projects/Modals/CreateProjectModal.vue'

const authStore = useAuthStore()
const showCreateModal = ref(false)
const showUpdateModal = ref(false)
const selectedProject = ref(null)
const projectListRef = ref(null)

const handleEdit = (project) => {
  selectedProject.value = project
  showUpdateModal.value = true
}

const handleUpdateSuccess = async () => {
  showUpdateModal.value = false
  // Optionally update local selectedProject or show a message using updatedProject
  if (projectListRef.value && projectListRef.value.fetchProjects) {
    await projectListRef.value.fetchProjects()
  }
}

const handleCreateSuccess = async () => {
  showCreateModal.value = false
  if (projectListRef.value && projectListRef.value.fetchProjects) {
    await projectListRef.value.fetchProjects()
  }
}

</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Projects</h1>
        <p class="text-sm text-gray-500">Manage all projects</p>
      </div>
      
      <button 
        v-if="authStore.user?.role === 'admin'"
        @click="showCreateModal = true"
        class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2"
      >
        <span>+</span>
        Create Project
      </button>
    </div>

    <!-- Project List -->
    <div class="bg-white rounded-xl shadow-sm">
      <table class="min-w-full divide-y divide-gray-200">
        <thead>
          <tr class="bg-gray-50">
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Name</th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Description</th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Deadline</th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Members</th>
            <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
    <ProjectList ref="projectListRef" @edit="handleEdit" />
        </tbody>
      </table>
    </div>

    <!-- Modals -->
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
    />
  </div>
</template>