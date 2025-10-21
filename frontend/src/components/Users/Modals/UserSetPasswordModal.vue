<!-- src/components/Users/Modals/UserSetPasswordModal.vue -->

<script setup>
import { ref } from 'vue'
import { setPassword } from '@/api/authApi'


const emit = defineEmits(['close', 'success'])

const formData = ref({
  new_password: '',
  re_new_password: '',
  current_password: '',
})

const handleSubmit = async () => {
  try {
    if (formData.value.new_password !== formData.value.re_new_password) {
      alert("New passwords do not match!")
      return
    }
    const payload = { ...formData.value }
    const result = await setPassword(payload)
    emit('success', result)
  } catch (error) {
    console.error('Failed to set password - Full Error:', {
      message: error.message,
      response: error.response?.data || 'No response data',
      status: error.response?.status,
      request: error.request,
    })
    const errorMessage = error.response?.data?.detail || error.response?.data?.non_field_errors?.[0] || 'Failed to change password. Please check your input.'
    alert(errorMessage)
  }
}
</script>   

<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg p-6 max-w-md w-full shadow-lg">
      <h2 class="text-xl font-bold mb-4 text-gray-800">Change Password</h2>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Current Password -->
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700">Current Password</label>
          <input
            v-model="formData.current_password"
            type="password"
            placeholder="Enter your current password"
            class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <!-- New Password -->
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700">New Password</label>
          <input
            v-model="formData.new_password"
            type="password"
            placeholder="Enter a new password"
            class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <!-- Confirm New Password -->
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700">Confirm New Password</label>
          <input
            v-model="formData.re_new_password"
            type="password"
            placeholder="Re-enter the new password"
            class="w-full border rounded px-3 py-2 focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-2 pt-4">
          <button 
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 border rounded text-gray-700 hover:bg-gray-100 transition"
          >
            Cancel
          </button>
          <button 
            type="submit"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            Save Changes
          </button>
        </div>
      </form>
    </div>
  </div>
</template>