<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import { kickMemberFromTeam } from '@/api/teamApi'

const props = defineProps({
  team: { type: Object, required: true },
  members: { type: Array, required: true }
})
const emit = defineEmits(['close', 'memberKicked'])

const authStore = useAuthStore()
const currentUser = computed(() => authStore.user || {})
const isLeader = computed(() => {
  const u = currentUser.value
  return !!u && (u.id === props.team.leader?.id || u.role === 'admin' || u.id === props.team.project?.leader?.id)
})

const kickingMemberId = ref(null)
const isKicking = ref(false)
const reassignRequired = ref(false)
const reassignToId = ref('')
const error = ref('')

const memberUsers = computed(() => props.members)
const reassignableMembers = computed(() => memberUsers.value.filter(m => m.id !== props.team.leader?.id && m.id !== kickingMemberId.value))

const startKick = (memberId) => {
  kickingMemberId.value = memberId
  reassignRequired.value = false
  reassignToId.value = ''
  error.value = ''
}

const cancelKick = () => {
  kickingMemberId.value = null
  reassignRequired.value = false
  reassignToId.value = ''
  error.value = ''
}

const confirmKick = async () => {
  if (reassignRequired.value && !reassignToId.value) {
    error.value = 'Thành viên có tasks chưa hoàn thành. Chọn người nhận.'
    return
  }
  try {
    isKicking.value = true
    error.value = ''
    const reassignId = reassignToId.value ? parseInt(reassignToId.value) : undefined
    await kickMemberFromTeam(props.team.id, kickingMemberId.value, reassignId)
    emit('memberKicked')
    cancelKick()
  } catch (e) {
    const detail = e?.response?.data?.detail || ''
    if (typeof detail === 'string' && detail.includes('Cần chọn reassign_to_id')) {
      reassignRequired.value = true
      error.value = 'Thành viên có tasks chưa hoàn thành. Chọn người nhận.'
    } else {
      error.value = detail || 'Không thể kick member.'
    }
  } finally {
    isKicking.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 w-96 max-h-[70vh] overflow-auto">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Team Members — {{ team.name }}</h3>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-800">✕</button>
      </div>

      <div v-if="members.length === 0" class="text-gray-500">No members yet.</div>

      <ul class="space-y-3">
        <li v-for="m in members" :key="m.id" class="border-b pb-3">
          <div class="flex items-center gap-3">
            <div class="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-sm font-semibold text-indigo-700">{{ m.username ? m.username.charAt(0).toUpperCase() : 'U' }}</div>
            <div class="flex-1">
              <div class="font-medium">
                {{ m.username }}
                <span v-if="m.id === team.leader?.id" class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded ml-2">Leader</span>
              </div>
              <div class="text-xs text-gray-500">Role: {{ m.project_role || '—' }}</div>
            </div>
            <button v-if="isLeader && m.id !== team.leader?.id && kickingMemberId !== m.id" @click="startKick(m.id)" class="text-xs px-2 py-1 text-red-600 hover:bg-red-50 rounded">Kick</button>
          </div>

          <div v-if="kickingMemberId === m.id" class="mt-3 p-3 bg-gray-50 rounded space-y-2">
            <p class="text-sm font-medium">Kick {{ m.username }}?</p>
            <div v-if="reassignRequired">
              <p class="text-xs text-gray-600 mb-1">Thành viên có tasks chưa hoàn thành. Chọn người nhận:</p>
              <select v-model="reassignToId" class="w-full text-sm border border-gray-300 rounded px-2 py-1">
                <option value="">-- Chọn member --</option>
                <option v-for="rm in reassignableMembers" :key="rm.id" :value="rm.id">{{ rm.username }} ({{ rm.project_role || 'Member' }})</option>
              </select>
            </div>
            <p v-else class="text-xs text-gray-600">Nếu thành viên có tasks chưa hoàn thành, bạn sẽ cần chọn người nhận.</p>
            <div v-if="error" class="text-xs text-red-600">{{ error }}</div>
            <div class="flex gap-2 justify-end mt-2">
              <button @click="cancelKick" class="text-xs px-3 py-1 border border-gray-300 rounded hover:bg-gray-100" :disabled="isKicking">Cancel</button>
              <button @click="confirmKick" class="text-xs px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50" :disabled="isKicking || (reassignRequired && !reassignToId)">{{ isKicking ? 'Kicking...' : 'Confirm Kick' }}</button>
            </div>
          </div>
        </li>
      </ul>

      <div class="mt-4 text-right">
        <button @click="$emit('close')" class="px-4 py-2 bg-gray-200 rounded">Close</button>
      </div>
    </div>
  </div>
</template>
