<!-- src/components/Projects/Modals/CreateProjectModal.vue -->
<script setup>
import { ref, onMounted, computed } from 'vue'
import { createProject } from '@/api/projectAPi'
import { getUsers } from '@/api/userApi'
import { useAuthStore } from '@/store/auth'

const emit = defineEmits(['close', 'success'])
const authStore = useAuthStore()
const isAdmin = computed(() => authStore.user?.role === 'admin')
const allowPersonal = computed(() => !!authStore.user?.allow_personal)

const formData = ref({
  name: '',
  description: '',
  deadline: '',
  is_personal: false,
  leader: null
})
const leaders = ref([])

// Non-admins can only create personal projects 
onMounted(() => {
  if (!isAdmin.value) {
    formData.value.is_personal = true
  }
})

// // If switching to personal, clear any selected leader and skip asking for it
// watch(() => formData.value.is_personal, (isPersonal) => {
//   if (isPersonal) {
//     formData.value.leader = null
//   }
// })

const handleSearch = async (search) => {
  try{
    leaders.value = await getUsers(search)
  }
  catch(error){
    console.error('Failed to search leaders:', error)
  }
}

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

        <div class="flex items-center gap-2" v-if="allowPersonal">
          <template v-if="isAdmin">
            <!-- Admin: can create enterprise only, hide personal toggle -->
          </template>
          <template v-else>
            <!-- Non-admin: personal-only creation -->
            <input 
              v-model="formData.is_personal"
              type="checkbox"
              id="is_personal"
              disabled
            />
            <label for="is_personal" class="text-gray-500">Personal Project (required)</label>
          </template>
        </div>

        <div v-if="!formData.is_personal">
          <label class="block text-sm font-medium mb-1">Leader</label>
          <input 
            type="text"
            placeholder="Search leaders..."
            @input="handleSearch($event.target.value)"
            class="w-full border rounded p-2 mb-2"
          />
          <select 
            v-model="formData.leader"
            class="w-full border rounded p-2"
          >
            <option 
              v-for="leader in leaders" 
              :key="leader.id" 
              :value="leader.id"
            >
              {{ leader.username }} ({{ leader.email }})
            </option>
          </select>
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