<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import { getTaskDetail } from '@/api/taskApi'
import { getComments, createComment, getChecklistItems, createChecklistItem, updateChecklistItem, deleteChecklistItem } from '@/api/comment_checklistApi'
import { Edit3, Delete, Check, X } from 'lucide-vue-next'


const props = defineProps({
  taskId: { type: [String, Number], required: true },
})

const auth = useAuthStore()
const task = ref(null)
const loading = ref(false)
const error = ref('')

const comments = ref([])
const posting = ref(false)
const commentText = ref('')
const checklist = ref([])
const newItem = ref('')

const editingItemID = ref(null)
const editingName = ref('')
const confirmDeleteId = ref(null)
const actionLoadingId = ref(null)

const canComment = computed(() => {
  const u = auth.user
  const t = task.value
  if (!u || !t) return false
  const isLeader = t.project?.leader?.id === u.id
  const isAssignee = t.assignee?.id === u.id
  const isCreator = t.creator?.id === u.id
  return (isLeader || isAssignee || isCreator) && !t.is_deleted
})

const fmtDate = (d) => {
  if (!d) return '-'
  try {
    const dt = new Date(d)
    return isNaN(dt.getTime()) ? '-' : dt.toLocaleDateString()
  } catch {
    return '-'
  }
}

const fetchAll = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await getTaskDetail(props.taskId)
    task.value = data
    try {
      comments.value = await getComments(props.taskId)
    } catch (_) {
      comments.value = data.comments || []
    }
    try {
      const u = auth.user
      if (u && data.assignee && u.id === data.assignee.id) {
        checklist.value = await getChecklistItems(props.taskId)
      } else if (u && data.project?.leader && u.id === data.project.leader.id) {
        checklist.value = (data.checklist_items || []).filter(i => !i.is_deleted)
      } else {
        checklist.value = []
      }
    } catch (_) {
      const u = auth.user
      if (u && data.project?.leader && u.id === data.project.leader.id) {
        checklist.value = (data.checklist_items || []).filter(i => !i.is_deleted)
      }
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Failed to load task.'
  } finally {
    loading.value = false
  }
}

const submitComment = async () => {
  if (!canComment.value) return
  const text = (commentText.value || '').trim()
  if (!text) return
  posting.value = true
  try {
    await createComment(props.taskId, { text })
    commentText.value = ''
    comments.value = await getComments(props.taskId)
  } catch (e) {
    error.value = e?.response?.data?.error || e?.response?.data?.detail || 'Failed to post comment.'
  } finally {
    posting.value = false
  }
}

onMounted(fetchAll)
watch(() => props.taskId, fetchAll)

// Checklist CRUD (assignee only)
const isAssignee = computed(() => {
  const u = auth.user
  const t = task.value
  return !!(u && t && t.assignee && u.id === t.assignee.id && !t.is_deleted)
})

// Leader (project leader) read-only flag
const isLeader = computed(() => {
  const u = auth.user
  const t = task.value
  return !!(u && t && t.project && t.project.leader && u.id === t.project.leader.id && !t.is_deleted)
})

const completedCount = computed(() => (checklist.value || []).filter(i => i.is_checked).length)
const totalCount = computed(() => (checklist.value || []).length)

const addItem = async () => {
  const name = (newItem.value || '').trim()
  if (!isAssignee.value || !name) return
  try {
    await createChecklistItem(props.taskId, { name })
    newItem.value = ''
    checklist.value = await getChecklistItems(props.taskId)
  } catch (e) {
    error.value = e?.response?.data?.error || e?.response?.data?.detail || 'Failed to add item.'
  }
}

const toggleItem = async (item) => {
  if (!isAssignee.value) return
  try {
    await updateChecklistItem(item.id, { is_checked: !item.is_checked })
    item.is_checked = !item.is_checked
  } catch (e) {
    error.value = e?.response?.data?.error || e?.response?.data?.detail || 'Failed to update item.'
  }
}



// Inline edit UX
const startEdit = (item) => {
  if (!isAssignee.value) return
  editingItemID.value = item.id
  editingName.value = item.name
  confirmDeleteId.value = null
}

const cancelEdit = () => {
  editingItemID.value = null
  editingName.value = ''
}

const saveEdit = async (item) => {
  if (!isAssignee.value) return
  const name = (editingName.value || '').trim()
  if (!name || name === item.name) { cancelEdit(); return }
  try {
    actionLoadingId.value = item.id
    await updateChecklistItem(item.id, { name })
    item.name = name
    cancelEdit()
  } catch (e) {
    error.value = e?.response?.data?.error || e?.response?.data?.detail || 'Failed to rename item.'
  } finally {
    actionLoadingId.value = null
  }
}

// Delete with inline confirm
const askDelete = (item) => {
  if (!isAssignee.value) return
  confirmDeleteId.value = item.id
  editingItemID.value = null
}

const cancelDelete = () => {
  confirmDeleteId.value = null
}

const confirmDelete = async (item) => {
  if (!isAssignee.value) return
  try {
    actionLoadingId.value = item.id
    await deleteChecklistItem(item.id)
    checklist.value = checklist.value.filter(i => i.id !== item.id)
    confirmDeleteId.value = null
  } catch (e) {
    error.value = e?.response?.data?.error || e?.response?.data?.detail || 'Failed to delete item.'
  } finally {
    actionLoadingId.value = null
  }
}
</script>

<template>
  <div>
    <div v-if="loading" class="text-center text-gray-500 py-8">Loading…</div>
    <div v-else-if="error" class="text-center text-red-600 py-8">{{ error }}</div>
    <div v-else-if="!task" class="text-center text-gray-500 py-8">Task not found.</div>
    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-4">
        <div class="bg-white rounded-xl border border-gray-200 p-4">
          <div class="flex items-start justify-between">
            <h1 class="text-xl font-semibold text-gray-900">{{ task.name }}</h1>
            <span v-if="task.project?.is_personal" class="text-[10px] px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">Personal</span>
          </div>
          <p class="mt-2 text-sm text-gray-700 whitespace-pre-line">{{ task.description || '—' }}</p>
          <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
            <div><span class="text-gray-500">Project:</span> <span class="text-gray-900">{{ task.project?.name || '—' }}</span></div>
            <div><span class="text-gray-500">Deadline:</span> <span class="text-gray-900">{{ fmtDate(task.deadline) }}</span></div>
            <div><span class="text-gray-500">Assignee:</span> <span class="text-gray-900">{{ task.assignee?.full_name || task.assignee?.username || '—' }}</span></div>
            <div><span class="text-gray-500">Creator:</span> <span class="text-gray-900">{{ task.creator?.full_name || task.creator?.username || '—' }}</span></div>
            <div><span class="text-gray-500">Priority:</span> <span class="text-gray-900">{{ (task.priority || 'low').toUpperCase() }}</span></div>
            <div><span class="text-gray-500">Status:</span> <span class="text-gray-900">{{ task.status }}</span></div>
          </div>
          <div v-if="task.is_deleted" class="mt-3 p-2 rounded bg-red-50 border border-red-200 text-xs text-red-700">Task này đang ở trạng thái Deleted.</div>
        </div>

        <div class="bg-white rounded-xl border border-gray-200 p-4">
          <h2 class="text-base font-semibold text-gray-900 mb-3">Comments</h2>
          <div v-if="comments.length === 0" class="text-sm text-gray-500">Chưa có bình luận nào.</div>
          <div v-else class="space-y-3">
            <div v-for="c in comments" :key="c.id" class="border border-gray-100 rounded-lg p-3">
              <div class="text-sm text-gray-900 font-medium">{{ c.user?.full_name || c.user?.username || 'User' }}</div>
              <div class="text-xs text-gray-500">{{ new Date(c.created_at).toLocaleString() }}</div>
              <div class="mt-1 text-sm text-gray-800 whitespace-pre-line">{{ c.text }}</div>
            </div>
          </div>

          <div v-if="canComment" class="mt-4">
            <label class="block text-xs font-medium mb-1">Thêm bình luận</label>
            <textarea v-model="commentText" rows="3" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Viết bình luận…" />
            <div class="mt-2 flex justify-end">
              <button :disabled="posting || !commentText.trim()" @click="submitComment" class="px-3 py-1.5 text-sm rounded-lg bg-blue-600 text-white disabled:opacity-50">
                {{ posting ? 'Đang gửi…' : 'Gửi' }}
              </button>
            </div>
          </div>
          <div v-else class="mt-4 text-xs text-gray-500">Bạn không thể bình luận ở trạng thái hiện tại.</div>
        </div>
      </div>

      <div class="space-y-4">
        <div class="bg-white rounded-xl border border-gray-200 p-4">
          <template v-if="isAssignee || isLeader">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <h3 class="text-sm font-semibold text-gray-900">Checklist</h3>
                <span v-if="totalCount" class="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">{{ completedCount }}/{{ totalCount }}</span>
              </div>
              <span v-if="isLeader && !isAssignee" class="text-[10px] text-gray-500">Read-only</span>
            </div>
            <div v-if="isAssignee" class="mt-2 flex gap-2">
              <input v-model="newItem" type="text" class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Thêm checklist item…" @keyup.enter="addItem" />
              <button @click="addItem" class="px-3 py-2 text-sm rounded-lg bg-blue-600 text-white disabled:opacity-50" :disabled="!newItem.trim()">Add</button>
            </div>
            <ul class="mt-3 space-y-1">
              <li v-for="item in checklist" :key="item.id" class="group text-sm text-gray-700 flex items-start justify-between gap-3 py-1.5 px-2 rounded hover:bg-gray-50 border border-transparent hover:border-gray-200">
                <div class="flex items-start gap-2 flex-1">
                  <input type="checkbox" :checked="item.is_checked" :disabled="!isAssignee" class="mt-0.5" @change="isAssignee && toggleItem(item)" />
                  <div class="flex-1 min-w-0">
                    <template v-if="editingItemID === item.id">
                      <input v-model="editingName" class="w-full border border-gray-300 rounded px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-blue-500" @keyup.enter="saveEdit(item)" @keyup.esc="cancelEdit" />
                      <div class="mt-1 flex gap-1">
                        <button @click="saveEdit(item)" class="px-2 py-0.5 text-xs rounded bg-green-600 text-white flex items-center gap-1"><Check class="w-3 h-3" />Save</button>
                        <button @click="cancelEdit" class="px-2 py-0.5 text-xs rounded bg-gray-300 text-gray-700 flex items-center gap-1"><X class="w-3 h-3" />Cancel</button>
                      </div>
                    </template>
                    <template v-else>
                      <span :class="{ 'line-through text-gray-400': item.is_checked }" class="block truncate">{{ item.name }}</span>
                      <div v-if="confirmDeleteId === item.id" class="mt-1 flex gap-1">
                        <span class="text-[10px] text-red-600">Confirm delete?</span>
                        <button @click="confirmDelete(item)" :disabled="actionLoadingId === item.id" class="px-2 py-0.5 text-[10px] rounded bg-red-600 text-white">Yes</button>
                        <button @click="cancelDelete" :disabled="actionLoadingId === item.id" class="px-2 py-0.5 text-[10px] rounded bg-gray-200 text-gray-700">No</button>
                      </div>
                    </template>
                  </div>
                </div>
                <div v-if="isAssignee && editingItemID !== item.id && confirmDeleteId !== item.id" class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button @click="startEdit(item)" class="p-1 rounded hover:bg-gray-200" title="Edit"><Edit3 class="w-4 h-4" /></button>
                  <button @click="askDelete(item)" class="p-1 rounded hover:bg-red-100 text-red-600" title="Delete"><Delete class="w-4 h-4" /></button>
                </div>
              </li>
              <li v-if="!(checklist && checklist.length)" class="text-xs text-gray-400">No items</li>
            </ul>
          </template>
          <template v-else>
            <h3 class="text-sm font-semibold text-gray-900">Checklist</h3>
            <p class="mt-2 text-xs text-gray-400">Bạn không có quyền xem checklist.</p>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>