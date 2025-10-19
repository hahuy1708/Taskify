<script setup>
import { ref } from 'vue'
import { updateProject } from '@/api/projectAPi'

const props = defineProps({
  project: {
    type: Object,
    required: true
  },
  userRole: {
    type: String,
    required: false,
    default: 'user'
  }
})

const emit = defineEmits(['close', 'success'])

const formData = ref({
  name: props.project.name,
  description: props.project.description,
  deadline: props.project.deadline?.split('T')[0], // Format date for input
  is_completed: props.project.is_completed,
})

const handleSubmit = async () => {
  try {
    // Build payload; include only allowed fields the backend expects
    const payload = {
      ...formData.value,
    }
    const updated = await updateProject(props.project.id, payload, props.userRole)
    // Emit the updated project back to parent
    emit('success', updated)
  } catch (error) {
    console.error('Failed to update project:', error)
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg p-6 max-w-md w-full">
      <h2 class="text-xl font-bold mb-4">Update Project</h2>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Admin only fields -->
        <template v-if="userRole === 'admin'">
          <div>
            <label class="block text-sm font-medium mb-1">Name</label>
            <input 
              v-model="formData.name"
              type="text"
              class="w-full border rounded p-2"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Deadline</label>
            <input 
              v-model="formData.deadline"
              type="date"
              class="w-full border rounded p-2"
            />
          </div>
        </template>

        <div>
          <label class="block text-sm font-medium mb-1">Description</label>
          <textarea 
            v-model="formData.description"
            class="w-full border rounded p-2"
            rows="3"
          />
        </div>

        <div class="flex items-center gap-2">
          <input 
            v-model="formData.is_completed"
            type="checkbox"
            id="is_completed"
          />
          <label for="is_completed">Mark as completed</label>
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
            Save Changes
          </button>
        </div>
      </form>
    </div>
  </div>
</template>