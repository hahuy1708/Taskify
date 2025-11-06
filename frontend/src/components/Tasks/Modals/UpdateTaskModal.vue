<script setup>
import { ref, watchEffect, computed } from 'vue'
import { updateTask } from '@/api/taskApi'
import { getListTeams, getTeamMembers } from '@/api/teamApi'
import { useAuthStore } from '@/store/auth'

// Props
const props = defineProps({
  task: { type: Object, required: true },
  open: { type: Boolean, default: false }
})
const emit = defineEmits(['close', 'success'])

const authStore = useAuthStore()
const currentUser = computed(() => authStore.user)

// Leader logic: enterprise leader OR personal owner
const isLeader = computed(() => {
  const u = currentUser.value
  const p = props.task?.project
  if (!u || !p) return false
  return (p.leader?.id === u.id) || (p.is_personal && p.owner?.id === u.id) || (props.task?.creator?.id === u.id)
})

const isPersonal = computed(() => !!props.task?.project?.is_personal)

// Assignee check (for future drag/drop logic)
// const isAssignee = computed(() => props.task?.assignee?.id === currentUser.value?.id)

const formData = ref({
  name: '',
  description: '',
  deadline: '',
  priority: 'low',
  is_deleted: false,
  assignee: null,
})

const loadingMembers = ref(false)
const members = ref([])
const memberSearch = ref('')
const filteredMembers = computed(() => {
  const q = memberSearch.value.trim().toLowerCase()
  if (!q) return members.value
  return members.value.filter(m => (m.full_name || m.username || '').toLowerCase().includes(q) || (m.email || '').toLowerCase().includes(q))
})

const loadMembers = async () => {
  members.value = []
  const project = props.task?.project
  if (!project || project.is_personal || !isLeader.value) return
  loadingMembers.value = true
  try {
    const allTeams = await getListTeams()
    const projectTeams = (allTeams || []).filter(t => t.project_id === project.id)
    const userMap = {}
    for (const team of projectTeams) {
      try {
        const teamMembers = await getTeamMembers(team.id)
        for (const m of teamMembers || []) {
          userMap[m.id] = m
        }
      } catch (_) {/* ignore individual team errors */}
    }
    members.value = Object.values(userMap)
  } finally {
    loadingMembers.value = false
  }
}

// Lock fields when the task is already soft-deleted (only allow toggling is_deleted)
const isSoftDeleted = computed(() => props.task?.is_deleted === true)

const setFormFromTask = () => {
  const t = props.task || {}
  formData.value = {
    name: t.name || '',
    description: t.description || '',
    deadline: t.deadline ? String(t.deadline).split('T')[0] : '',
    priority: t.priority || 'low',
    is_deleted: t.is_deleted || false,
    assignee: t.assignee?.id ?? null,
  }
}

watchEffect(() => {
  if (props.open && props.task) {
    setFormFromTask()
    loadMembers()
  }
})

const submitting = ref(false) 
const errorMsg = ref('')

const handleSubmit = async () => {
  if (!isLeader.value) { // currently only leaders can use modal
    emit('close');
    return
  }
  submitting.value = true
  errorMsg.value = ''
  try {
    // If task is currently soft-deleted, only send is_deleted flag to restore
    let payload
    if (isSoftDeleted.value) {
      payload = { is_deleted: formData.value.is_deleted }
    } else {
      payload = {
        name: formData.value.name?.trim?.() || '',
        description: formData.value.description || '',
        deadline: formData.value.deadline || null,
        priority: formData.value.priority,
        is_deleted: formData.value.is_deleted,
      }
      if (isLeader.value && !isPersonal.value) {
        if (formData.value.assignee !== null && formData.value.assignee !== '') {
          payload.assignee = formData.value.assignee
        }
      }
    }
    const updated = await updateTask(props.task.id, payload)
    emit('success', updated)
  } catch (e) {
    errorMsg.value = e?.response?.data?.detail || e?.response?.data?.error || 'Failed to update task.'
  } finally {
    submitting.value = false
  }
}

const close = () => {
  emit('close')
}
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" @click="close" />
    <div class="relative bg-white rounded-xl shadow-lg w-full max-w-lg p-6 border border-gray-200">
      <h2 class="text-lg font-semibold mb-4 flex justify-between items-center">
        <span>Update Task</span>
        <button @click="close" class="text-gray-400 hover:text-gray-600">✕</button>
      </h2>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Deleted banner -->
        <div v-if="isSoftDeleted" class="p-3 rounded bg-red-50 border border-red-200 text-xs text-red-700">
          Task này đang ở trạng thái Deleted. Chỉ có thể bỏ chọn 'Mark as Deleted' để khôi phục.
        </div>

        <div v-if="isLeader" class="space-y-4">
          <div>
            <label class="block text-xs font-medium mb-1">Name</label>
            <input v-model="formData.name" :disabled="isSoftDeleted" type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm disabled:opacity-60" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1">Deadline</label>
            <input v-model="formData.deadline" :disabled="isSoftDeleted" type="date" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm disabled:opacity-60" />
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium mb-1">Description</label>
          <textarea v-model="formData.description" :disabled="isSoftDeleted" rows="3" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm disabled:opacity-60" />
        </div>
        <div>
          <label class="block text-xs font-medium mb-1">Priority</label>
          <select v-model="formData.priority" :disabled="isSoftDeleted" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm disabled:opacity-60">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        <div>
          <label class="flex items-center gap-2 text-xs font-medium">
            <input type="checkbox" v-model="formData.is_deleted" />
            Mark as Deleted
          </label>
        </div>
        <div v-if="isLeader && !props.task?.project?.is_personal">
          <label class="flex text-xs font-medium mb-1 items-center justify-between">Assignee
            <input v-model="memberSearch" :disabled="isSoftDeleted" type="text" placeholder="Search" class="ml-2 border px-2 py-1 rounded text-xs w-32 disabled:opacity-60" />
          </label>
          <select v-model="formData.assignee" :disabled="isSoftDeleted" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm disabled:opacity-60">
            <option :value="null">Unassigned</option>
            <option v-for="m in filteredMembers" :key="m.id" :value="m.id">
              {{ m.full_name || m.username }} ({{ m.email }})
            </option>
          </select>
          <p v-if="loadingMembers && !isSoftDeleted" class="text-xs text-gray-500 mt-1">Loading members...</p>
        </div>

        <div v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</div>

        <div class="flex justify-end gap-2 pt-2">
          <button type="button" @click="close" class="px-3 py-2 text-sm rounded-lg border border-gray-300 hover:bg-gray-100">Cancel</button>
          <button type="submit" :disabled="submitting" class="px-3 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-50">
            {{ submitting ? 'Saving...' : (isSoftDeleted ? 'Restore' : 'Save Changes') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>