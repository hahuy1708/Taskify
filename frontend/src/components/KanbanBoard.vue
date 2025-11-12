<script setup>
import { ref, watch, computed } from "vue";
import { getProjectDetails } from "@/api/projectAPi";
import { updateTask } from "@/api/taskApi";
import { useAuthStore } from "@/store/auth";
import CreateTaskModal from "@/components/Tasks/Modals/CreateTaskModal.vue";
import TaskDetail from "@/components/Tasks/TaskDetail.vue";
import { PlusIcon } from "lucide-vue-next";

const props = defineProps({
  projectId: { type: [String, Number, null], default: null },
});

const auth = useAuthStore();
const project = ref(null);
const lists = ref([]);
const loading = ref(false);
const error = ref("");

const isEnterprise = computed(() => !project.value?.is_personal);
const isLeader = computed(() => {
  const u = auth.user;
  if (!u || !project.value) return false;
  return project.value?.leader?.id === u.id;
});
const isPersonalOwner = computed(() => {
  const u = auth.user;
  if (!u || !project.value) return false;
  return !!project.value?.is_personal && project.value?.owner?.id === u.id;
});

// View filter: default show only my tasks for non-leader/non-owner
const showOnlyMine = ref(true);
watch(
  () => [project.value?.id, isLeader.value, isPersonalOwner.value],
  () => {
    // Leaders and owners default to seeing all; members default to only mine
    showOnlyMine.value = !(isLeader.value || isPersonalOwner.value);
  },
  { immediate: true }
);

const isMyTask = (t) => {
  const u = auth.user;
  if (!u) return false;
  // Leaders/owners see everything regardless of toggle logic elsewhere
  if (isLeader.value || isPersonalOwner.value) return true;
  return t?.assignee?.id === u.id;
};

const fetchKanban = async () => {
  if (!props.projectId) {
    project.value = null;
    lists.value = [];
    return;
  }
  try {
    loading.value = true;
    error.value = "";
    const data = await getProjectDetails(props.projectId);
    project.value = data;
    lists.value = Array.isArray(data?.lists) ? data.lists : [];
  } catch (e) {
    error.value = "Failed to load board.";
  } finally {
    loading.value = false;
  }
};

watch(() => props.projectId, fetchKanban, { immediate: true });

// Create modal state
const openCreate = ref(false);
const defaultListId = ref("");
const onCreated = async () => {
  openCreate.value = false;
  await fetchKanban();
};

const fmtDate = (d) => {
  if (!d) return "-";
  try {
    const dt = new Date(d);
    return isNaN(dt.getTime()) ? "-" : dt.toLocaleDateString();
  } catch {
    return "-";
  }
};

const detailOpen = ref(false);
const selectedTaskId = ref(null);
const openDetail = (taskId) => {
  selectedTaskId.value = taskId;
  detailOpen.value = true;
};
const closeDetail = () => {
  detailOpen.value = false;
  selectedTaskId.value = null;
};

// View permission on board: deny admins; allow leader, personal owner, or members (assignee of any task in project)
const isAssigneeInProject = computed(() => {
  const u = auth.user;
  if (!u) return false;
  for (const col of lists.value || []) {
    for (const t of col.tasks || []) {
      if (t?.assignee?.id === u.id) return true;
    }
  }
  return false;
});
const canViewBoard = computed(() => {
  const u = auth.user;
  if (!u) return false;
  if (u.role === 'admin') return false; // per requirement
  if (isLeader.value || isPersonalOwner.value) return true;
  return isAssigneeInProject.value;
});

// Drag & Drop state
// Draggable per-task: assignee can drag their tasks; leader can drag only unassigned; personal owner can drag all in personal project
const canDragTask = (t) => {
  const u = auth.user;
  if (!u) return false;
  // Do not allow dragging tasks already done
  if (t?.status === 'done') return false;
  if (isPersonalOwner.value) return true; // personal projects
  // enterprise: leader can move unassigned tasks only
  if (isEnterprise.value && isLeader.value && !t?.assignee) return true;
  // assignee can drag their own task
  if (t?.assignee?.id === u.id) return true;
  return false;
};
const dragging = ref(null); // { taskId, fromListId }
const dragOverListId = ref(null);

const statusForListName = (name) => {
  const key = String(name || "").toLowerCase();
  if (key.includes("progress")) return "in_progress";
  if (key.includes("done")) return "done";
  return "todo";
};

const onDragStart = (evt, task, list) => {
  if (!canDragTask(task)) return;
  dragging.value = { taskId: task.id, fromListId: list.id };
  try {
    evt.dataTransfer?.setData("text/plain", String(task.id));
  } catch { /* void */ }
};

const onDragOver = (evt, list) => {
  if (!dragging.value) return;
  evt.preventDefault();
  dragOverListId.value = list.id;
};

const onDragLeave = (evt, list) => {
  if (dragOverListId.value === list.id) dragOverListId.value = null;
};

const onDrop = async (evt, targetList) => {
  if (!dragging.value) return;
  evt.preventDefault();
  const { taskId, fromListId } = dragging.value;
  dragOverListId.value = null;
  dragging.value = null;
  if (fromListId === targetList.id) return;
  try {
    const from = lists.value.find((l) => l.id === fromListId);
    const to = lists.value.find((l) => l.id === targetList.id);
    if (!from || !to) return;
    const idx = (from.tasks || []).findIndex((t) => t.id === taskId);
    if (idx === -1) return;
    const moving = from.tasks[idx];
    if (!canDragTask(moving)) return; // final guard
    if ((from.position ?? from?.pos ?? 0) >= 3) return;
    if ((to.position ?? to?.pos ?? 0) < (from.position ?? from?.pos ?? 0)) return;
    await updateTask(taskId, { list: targetList.id });
    // Move locally
    const [moved] = from.tasks.splice(idx, 1);
    moved.status = statusForListName(to.name);
    moved.list = targetList.id;
    to.tasks = to.tasks || [];
    to.tasks.push(moved);
  } catch (e) {
    // Fallback refresh
    await fetchKanban();
  }
};
</script>

<template>
  <div>
    <div v-if="!props.projectId" class="text-gray-500">
      Select a project to view its board.
    </div>
    <div v-else-if="loading" class="py-10 text-center text-gray-500">
      Loading board...
    </div>
    <div v-else-if="error" class="py-10 text-center text-red-600">
      {{ error }}
    </div>
    <div v-else>
      <div v-if="!canViewBoard" class="p-6 text-center text-sm text-gray-500 bg-white border border-gray-200 rounded-xl">
        Bạn không có quyền xem Kanban board của project này.
      </div>
      <template v-else>
      <!-- Board header -->
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">
            {{ project?.name }}
          </h2>
          <p class="text-sm text-gray-500">
            {{ project?.is_personal ? "Personal Project" : "Company Project" }}
          </p>
        </div>
        <div>
          <button
            v-if="(isEnterprise && isLeader) || isPersonalOwner"
            class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-2 rounded-lg text-sm"
            @click="
              openCreate = true;
              defaultListId = lists?.[0]?.id || '';
            "
          >
            <PlusIcon class="w-4 h-4 inline-block mr-1" />
            Create Task
          </button>
        </div>
      </div>

      <!-- View Options (members can toggle visibility) -->
      <div class="mb-3 flex items-center gap-4">
        <label v-if="!isLeader && !isPersonalOwner" class="flex items-center gap-2 text-xs text-gray-600 select-none">
          <input type="checkbox" v-model="showOnlyMine" class="rounded border-gray-300" />
          Chỉ hiện task của tôi
        </label>
      </div>

      <!-- Columns -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          v-for="col in lists"
          :key="col.id"
          class="bg-white rounded-xl shadow-sm border border-gray-200 p-3"
          :class="{ 'ring-2 ring-blue-400': dragOverListId === col.id }"
          @dragover="(e) => onDragOver(e, col)"
          @dragleave="(e) => onDragLeave(e, col)"
          @drop="(e) => onDrop(e, col)"
        >
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-base font-semibold text-gray-800">
              {{ col.name }}
            </h3>
            <span class="text-xs text-gray-400">
              {{ col.tasks?.length || 0 }} tasks
            </span>
          </div>

          <div class="space-y-2 min-h-[40px]">
            <div
              v-for="t in (col.tasks || []).filter(t => !showOnlyMine || isMyTask(t))"
              :key="t.id"
              class="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-sm cursor-pointer"
              :draggable="canDragTask(t)"
              @dragstart="(e) => onDragStart(e, t, col)"
              @click="openDetail(t.id)"
            >
              <div class="text-sm font-medium text-gray-900 line-clamp-2">{{ t.name }}</div>
              <div class="mt-1 flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span
                    class="text-[10px] px-2 py-0.5 rounded-full"
                    :class="{
                      'bg-gray-100 text-gray-700':
                        !t.priority || t.priority === 'low',
                      'bg-yellow-100 text-yellow-700': t.priority === 'medium',
                      'bg-red-100 text-red-700': t.priority === 'high',
                    }"
                    >{{ (t.priority || "low").toUpperCase() }}</span
                  >
                  <span class="text-xs text-gray-500">{{
                    fmtDate(t.deadline)
                  }}</span>
                </div>
                <div class="text-xs text-gray-700">
                  {{ t.assignee?.full_name || t.assignee?.username || "—" }}
                </div>
              </div>
            </div>
            <div v-if="!((col.tasks || []).filter(t => !showOnlyMine || isMyTask(t)).length)" class="text-xs text-gray-400">No tasks</div>
          </div>
        </div>
      </div>

      <CreateTaskModal
        :open="openCreate"
        :default-project-id="project?.id || ''"
        :default-list-id="defaultListId || ''"
        :lock-project="true"
        @close="openCreate = false"
        @created="onCreated"
      />

      <!-- Task Detail Modal -->
      <teleport to="body">
        <div v-if="detailOpen" class="fixed inset-0 z-50">
          <div class="absolute inset-0 bg-black/40" @click="closeDetail"></div>
          <div class="absolute inset-0 flex items-center justify-center p-4">
            <div class="bg-white w-full max-w-5xl max-h-[90vh] overflow-auto rounded-xl shadow-lg">
              <div class="flex items-center justify-between p-3 border-b">
                <h3 class="text-base font-semibold">Task Detail</h3>
                <button class="px-2 py-1 text-sm rounded bg-gray-100 hover:bg-gray-200" @click="closeDetail">Close</button>
              </div>
              <div class="p-4">
                <TaskDetail v-if="selectedTaskId" :task-id="selectedTaskId" />
              </div>
            </div>
          </div>
        </div>
      </teleport>
      </template>
    </div>
  </div>
</template>

<style scoped></style>
