<!-- src/components/Users/Modals/UserEditModal.vue -->

<script setup>
import { ref } from 'vue'
import { updateProfile } from '@/api/authApi'

const props = defineProps({
  user: {
    type: Object,
    required: true
  },
})

const emit = defineEmits(['close', 'success'])

const formData = ref({
  email: props.user.email || '',
  full_name: props.user.full_name || '',
  phone_number: props.user.phone_number || '',
  address: props.user.address || '',
  birth_date: props.user.birth_date
    ? props.user.birth_date.split('T')[0]
    : '', // format yyyy-mm-dd
})

const handleSubmit = async () => {
  try {
    const payload = { ...formData.value }
    const updated = await updateProfile(payload)
    emit('success', updated)
  } catch (error) {
    console.error('Failed to update user profile:', error)
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg p-6 max-w-md w-full">
      <h2 class="text-xl font-bold mb-4">Edit Your Profile</h2>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Email -->
        <div>
          <label class="block text-sm font-medium mb-1">Email</label>
          <input
            v-model="formData.email"
            type="email"
            class="w-full border rounded px-3 py-2"
            required
          />
        </div>

        <!-- Full name -->
        <div>
          <label class="block text-sm font-medium mb-1">Full Name</label>
          <input
            v-model="formData.full_name"
            type="text"
            class="w-full border rounded px-3 py-2"
          />
        </div>

        <!-- Phone -->
        <div>
          <label class="block text-sm font-medium mb-1">Phone Number</label>
          <input
            v-model="formData.phone_number"
            type="text"
            class="w-full border rounded px-3 py-2"
          />
        </div>

        <!-- Address -->
        <div>
          <label class="block text-sm font-medium mb-1">Address</label>
          <input
            v-model="formData.address"
            type="text"
            class="w-full border rounded px-3 py-2"
          />
        </div>

        <!-- Birth date -->
        <div>
          <label class="block text-sm font-medium mb-1">Birth Date</label>
          <input
            v-model="formData.birth_date"
            type="date"
            class="w-full border rounded px-3 py-2"
          />
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