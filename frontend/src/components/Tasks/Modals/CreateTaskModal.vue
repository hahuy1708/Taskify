<script setup>
import { ref, computed, watch } from 'vue'
import { X } from 'lucide-vue-next'
import { createTask } from '@/api/taskApi'
import { getProjects, getProjectDetails } from '@/api/projectAPi'
import { getListTeams, getTeamMembers } from '@/api/teamApi'

const props = defineProps({
  open: { type: Boolean, default: false },
  defaultProjectId: { type: [String, Number], default: '' },
  defaultListId: { type: [String, Number], default: '' },
  lockProject: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'created'])

const isSubmitting = ref(false)
const error = ref('')

const name = ref('')
const description = ref('')
const deadline = ref('') // yyyy-mm-dd
const priority = ref('low')
const selectedProjectId = ref('')
const lists = ref([])
const selectedListId = ref('')
const assigneeId = ref('')
const teams = ref([])
const selectedTeamId = ref('')

const projects = ref([])
const loadProjects = async () => {
  try {
    projects.value = await getProjects()
  } catch (_) {
    projects.value = []
  }
}

// When project changes, load its default lists via kanban endpoint
const loadListsForProject = async (projectId) => {
  lists.value = []
  selectedListId.value = ''
  if (!projectId) return
  try {
    const data = await getProjectDetails(projectId)
    const ls = data?.lists || data?.project?.lists || []
    lists.value = Array.isArray(ls) ? ls : []
    // Try find a list named "To Do" else first
    const todo = lists.value.find((l) => l.name?.toLowerCase() === 'to do')
    selectedListId.value = todo?.id || lists.value[0]?.id || ''
  } catch (e) {
    lists.value = []
  }
}
// Teams & members (enterprise only)
const memberSearch = ref('')
const members = ref([])
const isLoadingMembers = ref(false)
const teamMembersCache = ref({}) // { [teamId]: Array<Member> }
const loadTeamsForProject = async () => {
  teams.value = []
  selectedTeamId.value = ''
  members.value = []
  teamMembersCache.value = {}
  if (!selectedProjectId.value) return
  const allTeams = await getListTeams()
  const pid = selectedProjectId.value
  teams.value = (allTeams || []).filter(t => t.project_id === pid)
  if (teams.value.length && !selectedTeamId.value) {
    selectedTeamId.value = teams.value[0].id
  }
}


watch(
  () => selectedProjectId.value,
  async (pid) => {
    await loadListsForProject(pid) // default to To Do silently
    // load teams for this project
    await loadTeamsForProject()
  }
)

const filterMembers = () => {
  const src = teamMembersCache.value[selectedTeamId.value] || []
  const q = (memberSearch.value || '').toLowerCase()
  members.value = q
    ? src.filter(m => (m.full_name || m.username || '').toLowerCase().includes(q) || (m.email || '').toLowerCase().includes(q))
    : src
}

const loadMembers = async () => {
  members.value = []
  if (!selectedTeamId.value) return
  const cached = teamMembersCache.value[selectedTeamId.value]
  if (cached) { filterMembers(); return }
  try {
    isLoadingMembers.value = true
    const teamMembers = await getTeamMembers(selectedTeamId.value)
    teamMembersCache.value[selectedTeamId.value] = teamMembers || []
    filterMembers()
  } finally {
    isLoadingMembers.value = false
  }
}
watch(() => selectedTeamId.value, loadMembers)
watch(() => memberSearch.value, filterMembers)

const selectedProject = computed(() =>
  projects.value.find((p) => p.id === selectedProjectId.value)
)
const isPersonal = computed(() => !!selectedProject.value?.is_personal)

const resetForm = () => {
  name.value = ''
  description.value = ''
  deadline.value = ''
  priority.value = 'low'
  selectedProjectId.value = ''
  lists.value = []
  selectedListId.value = ''
  assigneeId.value = ''
  error.value = ''
}

const submit = async () => {
  if (!selectedProjectId.value || !selectedListId.value || !name.value.trim()) {
    error.value = 'Please fill required fields.'
    return
  }
  try {
    isSubmitting.value = true
    error.value = ''
    const payload = {
      name: name.value.trim(),
      description: description.value?.trim?.() || '',
      deadline: deadline.value || null,
      priority: priority.value,
      project: selectedProjectId.value,
      list: selectedListId.value,
    }
    if (!isPersonal.value) {
      if (selectedTeamId.value) payload.team = selectedTeamId.value
      if (assigneeId.value) payload.assignee = assigneeId.value
    }
    await createTask(payload)
    emit('created')
    resetForm()
  } catch (e) {
    error.value =
      e?.response?.data?.detail ||
      e?.response?.data?.error ||
      'Failed to create task. Check permissions and input.'
  } finally {
    isSubmitting.value = false
  }
}

const close = () => {
  resetForm()
  emit('close')
}

// Load projects when modal opens, rely on selectedProjectId watcher to cascade lists/teams
watch(
  () => props.open,
  (open) => {
    if (open) {
      loadProjects().then(() => {
        if (props.defaultProjectId) {
          selectedProjectId.value = props.defaultProjectId
        }
      })
    }
  }
)
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/60" @click="close" />
    <div class="relative bg-white border border-gray-200 rounded-xl w-full max-w-xl mx-4 p-5 text-gray-900 shadow-xl">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-lg font-semibold">Create Task</h3>
        <button @click="close" class="p-1 rounded hover:bg-gray-100">
          <X class="w-5 h-5 text-gray-500" />
        </button>
      </div>

      <div class="space-y-3">
        <div class="grid grid-cols-1 gap-3">
          <label class="text-sm">Project</label>
          <select v-model="selectedProjectId" :disabled="lockProject" class="bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm disabled:opacity-60">
            <option value="" disabled>Select a project</option>
            <option v-for="p in projects" :key="p.id" :value="p.id">
              {{ p.name }} {{ p.is_personal ? '[Personal]' : '[Company]' }}
            </option>
          </select>
        </div>

        <div class="grid grid-cols-1 gap-2">
          <label class="text-sm">Task name</label>
          <input v-model="name" type="text" class="bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g., Setup CI" />
        </div>

        <div class="grid grid-cols-1 gap-2">
          <label class="text-sm">Description</label>
          <textarea v-model="description" rows="3" class="bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="Optional details..." />
        </div>

        <div class="grid grid-cols-3 gap-3">
          <div>
            <label class="text-sm">Priority</label>
            <select v-model="priority" class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          <div>
            <label class="text-sm">Deadline</label>
            <input v-model="deadline" type="date" class="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
        </div>

        <div v-if="!isPersonal" class="grid grid-cols-1 gap-2">
          <label class="text-sm">Team</label>
          <select v-model="selectedTeamId" class="bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="">Select a team</option>
            <option v-for="t in teams" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
          <p v-if="selectedProjectId && teams.length === 0" class="text-xs text-gray-500">
            No teams found for this project. You can still create an unassigned task, or create a team first in My Team.
          </p>
          <div v-if="selectedTeamId" class="grid grid-cols-1 gap-2">
            <div class="flex items-center justify-between">
              <label class="text-sm">Assignee</label>
              <input
                v-model="memberSearch"
                @input="loadMembers"
                placeholder="Search members..."
                class="bg-white border border-gray-300 rounded px-2 py-1 text-xs w-44"
              />
            </div>
            <select v-model="assigneeId" class="bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">Unassigned</option>
              <option v-for="m in members" :key="m.id" :value="m.id">
                {{ m.full_name || m.username }} ({{ m.email }})
              </option>
            </select>
            <p class="text-xs text-gray-500">Only leaders/admin can assign. Members are filtered by selected team.</p>
          </div>
        </div>
        <div v-else class="text-xs text-gray-600">Personal projects can’t assign to others. Assignee will be the creator implicitly.</div>

        <div v-if="error" class="text-sm text-red-600">{{ error }}</div>
      </div>

      <div class="mt-4 flex justify-end gap-2">
        <button class="px-3 py-2 text-sm rounded-lg border border-gray-300 hover:bg-gray-100" @click="close">Cancel</button>
        <button
          class="px-3 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-50"
          :disabled="isSubmitting"
          @click="submit"
        >
          {{ isSubmitting ? 'Creating...' : 'Create' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
