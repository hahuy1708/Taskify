<script setup>
import { ref, watch, computed } from 'vue'
import { getProjectDetails } from '@/api/projectAPi'
import { useAuthStore } from '@/store/auth'
import CreateTaskModal from '@/components/Tasks/Modals/CreateTaskModal.vue'
import { PlusIcon } from 'lucide-vue-next'

const props = defineProps({
	projectId: { type: [String, Number, null], default: null },
})

const auth = useAuthStore()
const project = ref(null)
const lists = ref([])
const loading = ref(false)
const error = ref('')

const isEnterprise = computed(() => !project.value?.is_personal)
const isLeader = computed(() => {
	const u = auth.user
	if (!u || !project.value) return false
	return project.value?.leader?.id === u.id
})
const isPersonalOwner = computed(() => {
  const u = auth.user
  if (!u || !project.value) return false
  return !!project.value?.is_personal && project.value?.owner?.id === u.id
})

const fetchKanban = async () => {
	if (!props.projectId) { project.value = null; lists.value = []; return }
	try {
		loading.value = true
		error.value = ''
		const data = await getProjectDetails(props.projectId)
		project.value = data
		lists.value = Array.isArray(data?.lists) ? data.lists : []
	} catch (e) {
		error.value = 'Failed to load board.'
	} finally {
		loading.value = false
	}
}

watch(() => props.projectId, fetchKanban, { immediate: true })

// Create modal state
const openCreate = ref(false)
const defaultListId = ref('')
const onCreated = async () => {
	openCreate.value = false
	await fetchKanban()
}

const fmtDate = (d) => {
	if (!d) return '-'
	try { const dt = new Date(d); return isNaN(dt.getTime()) ? '-' : dt.toLocaleDateString() } catch { return '-' }
}
</script>

<template>
	<div>
		<div v-if="!props.projectId" class="text-gray-500">Select a project to view its board.</div>
		<div v-else-if="loading" class="py-10 text-center text-gray-500">Loading board...</div>
		<div v-else-if="error" class="py-10 text-center text-red-600">{{ error }}</div>
		<div v-else>
			<!-- Board header -->
			<div class="flex items-center justify-between mb-4">
				<div>
					<h2 class="text-lg font-semibold text-gray-900">{{ project?.name }}</h2>
					<p class="text-sm text-gray-500">{{ project?.is_personal ? 'Personal Project' : 'Company Project' }}</p>
				</div>
				<div>
					<button
						v-if="(isEnterprise && isLeader) || isPersonalOwner"
						class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-2 rounded-lg text-sm"
						@click="openCreate = true; defaultListId = lists?.[0]?.id || ''"
					>
						<PlusIcon class="w-4 h-4 inline-block mr-1" />
						Create Task
					</button>
				</div>
			</div>

			<!-- Columns -->
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
				<div
					v-for="col in lists"
					:key="col.id"
					class="bg-white rounded-xl shadow-sm border border-gray-200 p-3"
				>
					
					<div class="space-y-2 min-h-[40px]">
						<div
							v-for="t in col.tasks || []"
							:key="t.id"
							class="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-sm"
						>
							<div class="text-sm font-medium text-gray-900">{{ t.name }}</div>
							<div class="mt-1 flex items-center justify-between">
								<div class="flex items-center gap-2">
									<span
										class="text-[10px] px-2 py-0.5 rounded-full"
										:class="{
											'bg-gray-100 text-gray-700': !t.priority || t.priority === 'low',
											'bg-yellow-100 text-yellow-700': t.priority === 'medium',
											'bg-red-100 text-red-700': t.priority === 'high',
										}"
									>{{ (t.priority || 'low').toUpperCase() }}</span>
									<span class="text-xs text-gray-500">{{ fmtDate(t.deadline) }}</span>
								</div>
								<div class="text-xs text-gray-700">
									{{ t.assignee?.full_name || t.assignee?.username || '—' }}
								</div>
							</div>
						</div>
						<div v-if="!(col.tasks && col.tasks.length)" class="text-xs text-gray-400">No tasks</div>
					</div>
				</div>
			</div>

			<CreateTaskModal
				:open="openCreate"
				:default-project-id="project?.id || ''"
				:default-list-id="defaultListId || ''"
				:lock-project="true"
				@close="openCreate=false"
				@created="onCreated"
			/>
		</div>
	</div>
</template>

<style scoped></style>
