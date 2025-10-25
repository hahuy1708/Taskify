<script setup>
import { ref, onMounted } from 'vue'
import { getUsers } from '@/api/userApi'
import { addMembersToTeam } from '@/api/teamApi'

const props = defineProps({
  team: { type: Object, required: true }
})

const emit = defineEmits(['close','success'])

const rows = ref([{ user_id: null, role: '' }])
const users = ref([])
const loadingUsers = ref(false)
const submitting = ref(false)
const error = ref(null)

onMounted(async () => {
  loadingUsers.value = true
  try {
    const all = await getUsers()
    console.log('all user: ', all)
    // only enterprise users
    users.value = (all || []).filter(u => u.is_enterprise)
    console.log('filtered user: ', users.value)
  } catch (e) {
    console.error('Failed to load users for add members', e)
  } finally {
    loadingUsers.value = false
  }
})

function addRow() { rows.value.push({ user_id: null, role: '' }) }
function removeRow(i) { rows.value.splice(i,1) }

async function submit() {
  error.value = null
  const payload = []
  for (const r of rows.value) {
    if (!r.user_id) continue
    payload.push({ user_id: Number(r.user_id), role: r.role || '' })
  }
  if (payload.length === 0) { error.value = 'Please add at least one member.'; return }
  submitting.value = true
  try {
    await addMembersToTeam(props.team.id, payload)
    emit('success')
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || 'Failed to add members'
  } finally { submitting.value = false }
}
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 w-[580px] max-w-[90vw] max-h-[80vh] overflow-y-auto">
      
      <!-- Header -->
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Add Members to {{ team.name }}</h3>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-800">✕</button>
      </div>

      <!-- Loading -->
      <div v-if="loadingUsers" class="py-4 text-center text-gray-500">Loading users...</div>

      <!-- Content -->
      <div v-else>
        <div class="space-y-3">
          <div v-for="(r, i) in rows" :key="i" class="flex flex-wrap gap-2 items-center">
            <select v-model="r.user_id" class="flex-1 border p-2 rounded">
              <option :value="null">Select user</option>
              <option v-for="u in users" :key="u.id" :value="u.id">
                {{ u.username }} — {{ u.email }}
              </option>
            </select>
            <input v-model="r.role" placeholder="role (optional)" class="w-36 border p-2 rounded" />
            <button @click.prevent="removeRow(i)" class="text-red-600">Remove</button>
          </div>
        </div>

        <div class="mt-3">
          <button @click.prevent="addRow" class="px-3 py-1 bg-gray-200 rounded">Add another</button>
        </div>

        <div v-if="error" class="mt-3 text-red-600">{{ error }}</div>

        <div class="mt-4 flex justify-end gap-2">
          <button @click="$emit('close')" class="px-4 py-2 bg-gray-200 rounded">Cancel</button>
          <button @click="submit" :disabled="submitting" class="px-4 py-2 bg-green-600 text-white rounded">
            Add
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
