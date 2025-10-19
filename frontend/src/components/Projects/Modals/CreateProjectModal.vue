<!-- src/components/Projects/Modals/CreateProjectModal.vue -->
<script setup>
import { ref } from 'vue'
import { createProject } from '@/api/projectAPi'

const emit = defineEmits(['close', 'success'])

const formData = ref({
  name: '',
  description: '',
  deadline: '',
  is_personal: false
})

const handleSubmit = () => {
  try {
    createProject(formData.value).then((newProject) => {
      emit('success', newProject)
    })
  } catch (error) {
    console.error('Failed to create project:', error)
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg p-6 max-w-md w-full">
      <h2 class="text-xl font-bold mb-4">Create New Project</h2>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Name</label>
          <input 
            v-model="formData.name"
            type="text"
            required
            class="w-full border rounded p-2"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Description</label>
          <textarea 
            v-model="formData.description"
            class="w-full border rounded p-2"
            rows="3"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Deadline</label>
          <input 
            v-model="formData.deadline"
            type="date"
            required
            class="w-full border rounded p-2"
          />
        </div>

        <div class="flex items-center gap-2">
          <input 
            v-model="formData.is_personal"
            type="checkbox"
            id="is_personal"
          />
          <label for="is_personal">Personal Project</label>
        </div>

        <div class="flex justify-end gap-2">
          <button 
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 border rounded"
          >
            Cancel
          </button>
          <button 
            type="submit"
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Create Project
          </button>
        </div>
      </form>
    </div>
  </div>
</template>