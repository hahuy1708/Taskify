<script setup>
import { ref, computed } from 'vue'
import { manageEmployee } from '@/api/authApi'

const emit = defineEmits(['close', 'success'])

const step = ref('input') // 'input' | 'create' | 'upgrade'
const email = ref('')
const username = ref('')
const fullName = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const canCheckEmail = computed(() => {
  const emailValue = email.value.trim()
  return emailValue && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailValue)
})

const canCreate = computed(() => {
  return username.value.trim() && fullName.value.trim() && password.value.trim().length >= 8
})

const checkEmail = async () => {
  if (!canCheckEmail.value) {
    error.value = 'Vui lòng nhập email hợp lệ.'
    return
  }
  try {
    loading.value = true
    error.value = ''
    const response = await manageEmployee(email.value.trim(), 'check')
    
    if (response.status === 'not_found') {
      step.value = 'create'
      // Auto-generate username from email
      const localPart = email.value.split('@')[0].replace(/[^a-z0-9]/gi, '_').toLowerCase()
      username.value = localPart
    } else if (response.status === 'personal') {
      step.value = 'upgrade'
    } else if (response.status === 'enterprise') {
      error.value = 'Nhân viên này đã có trong hệ thống.'
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Không thể kiểm tra email.'
  } finally {
    loading.value = false
  }
}

const createEmployee = async () => {
  if (!canCreate.value) {
    error.value = 'Vui lòng nhập đầy đủ thông tin. Password phải có ít nhất 8 ký tự.'
    return
  }
  try {
    loading.value = true
    error.value = ''
    await manageEmployee(
      email.value.trim(),
      'create',
      username.value.trim(),
      fullName.value.trim(),
      password.value
    )
    emit('success')
    emit('close')
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.response?.data?.username?.[0] || 'Không thể tạo nhân viên.'
  } finally {
    loading.value = false
  }
}

const upgradeEmployee = async () => {
  try {
    loading.value = true
    error.value = ''
    await manageEmployee(email.value.trim(), 'upgrade')
    emit('success')
    emit('close')
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Không thể nâng cấp user.'
  } finally {
    loading.value = false
  }
}

const reset = () => {
  step.value = 'input'
  email.value = ''
  username.value = ''
  fullName.value = ''
  password.value = ''
  error.value = ''
}
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 w-96 max-w-full">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Add Employee</h3>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-800 text-xl">&times;</button>
      </div>

      <!-- Step 1: Input Email -->
      <div v-if="step === 'input'" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input 
            v-model="email" 
            type="email" 
            placeholder="employee@company.com"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            @keyup.enter="checkEmail"
            autofocus
          />
        </div>
        <div v-if="error" class="text-sm text-red-600 bg-red-50 p-2 rounded">{{ error }}</div>
        <div class="flex gap-2 justify-end">
          <button @click="$emit('close')" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50" :disabled="loading">
            Cancel
          </button>
          <button @click="checkEmail" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50" :disabled="!canCheckEmail || loading">
            {{ loading ? 'Checking...' : 'Check Email' }}
          </button>
        </div>
      </div>

      <!-- Step 2: Create New Employee -->
      <div v-else-if="step === 'create'" class="space-y-4">
        <div class="text-sm text-gray-700 bg-blue-50 border border-blue-200 p-3 rounded">
          Email <strong>{{ email }}</strong> chưa có. Tạo nhân viên mới.
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="username"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
          <input 
            v-model="fullName" 
            type="text" 
            placeholder="Nguyễn Văn A"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="Minimum 8 characters"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <p class="text-xs text-gray-500 mt-1">Password phải có ít nhất 8 ký tự</p>
        </div>
        <div v-if="error" class="text-sm text-red-600 bg-red-50 p-2 rounded">{{ error }}</div>
        <div class="flex gap-2 justify-end">
          <button @click="reset" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50" :disabled="loading">
            Back
          </button>
          <button @click="createEmployee" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50" :disabled="!canCreate || loading">
            {{ loading ? 'Creating...' : 'Create Employee' }}
          </button>
        </div>
      </div>

      <!-- Step 3: Upgrade Personal User -->
      <div v-else-if="step === 'upgrade'" class="space-y-4">
        <div class="text-sm text-gray-700 bg-yellow-50 border border-yellow-200 p-3 rounded">
          <p class="font-medium mb-2">User với email <strong>{{ email }}</strong> đang dùng tài khoản cá nhân.</p>
          <p>Bạn có muốn nâng cấp họ thành nhân viên của công ty không?</p>
        </div>
        <div v-if="error" class="text-sm text-red-600 bg-red-50 p-2 rounded">{{ error }}</div>
        <div class="flex gap-2 justify-end">
          <button @click="reset" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50" :disabled="loading">
            Cancel
          </button>
          <button @click="upgradeEmployee" class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50" :disabled="loading">
            {{ loading ? 'Upgrading...' : 'Confirm Upgrade' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
