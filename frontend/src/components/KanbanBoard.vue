<script setup>
import { ref } from 'vue';
import CreateTaskModal from '@/components/Tasks/Modals/CreateTaskModal.vue';
import TaskDetail from '@/components/Tasks/TaskDetail.vue';
import { PlusIcon } from 'lucide-vue-next';
import { formatDate } from '@/utils/date';

import { useKanbanProject } from '@/composables/useKanbanProject';
import { useKanbanPermissions } from '@/composables/useKanbanPermissions';
import { useKanbanDnd } from '@/composables/useKanbanDnd';

const props = defineProps({
  projectId: { type: [String, Number, null], default: null },
});

const projectIdRef = ref(props.projectId);
import { watch } from 'vue';
watch(
  () => props.projectId,
  (v) => {
    projectIdRef.value = v;
  }
);
const { project, lists, loading, error, fetchKanban } = useKanbanProject(projectIdRef);

const { isEnterprise, isLeader, isPersonalOwner, showOnlyMine, isMyTask, canViewBoard } = useKanbanPermissions(project, lists);

// eslint-disable-next-line
const { canDragTask, dragging, dragOverListId, onDragStart, onDragOver, onDragLeave, onDrop } = useKanbanDnd(lists, { isEnterprise, isLeader, isPersonalOwner }, fetchKanban);

const openCreate = ref(false);
const defaultListId = ref('');
const onCreated = async () => {
  openCreate.value = false;
  await fetchKanban();
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
          Only show my tasks
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
                      'bg-gray-100 text-gray-700': !t.priority || t.priority === 'low',
                      'bg-yellow-100 text-yellow-700': t.priority === 'medium',
                      'bg-red-100 text-red-700': t.priority === 'high',
                    }"
                  >{{ (t.priority || 'low').toUpperCase() }}</span>
                  <span class="text-xs text-gray-500">{{ formatDate(t.deadline) }}</span>
                </div>
                <div class="text-xs text-gray-700">
                  {{ t.assignee?.full_name || t.assignee?.username || '—' }}
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
