<!-- src/components/Tasks/TaskTableRow.vue -->
<script setup>
import { computed, ref } from "vue";
import { useAuthStore } from "@/store/auth";
import { EditIcon, EyeIcon } from "lucide-vue-next";
import TaskDetaiModal from "@/components/Tasks/Modals/TaskDetaiModal.vue";
import { formatDate } from "@/utils/date";

const emit = defineEmits(["edit"]);
const props = defineProps({
  task: { type: Object, required: true },
});

const auth = useAuthStore();
const user = computed(() => auth.user);

const canEdit = computed(() => {
  const u = user.value;
  const t = props.task;
  if (!u || !t) return false;
  const project = t.project || {};
  const ownerId = project.owner?.id || project.owner; // support both nested object or id
  const isCreator = t.creator?.id === u.id;
  const isPersonalProject = !!project.is_personal;
  const isPersonalOwner = isPersonalProject && ownerId === u.id;
  return isPersonalOwner || isCreator || project.leader?.id === u.id;
});

const onEdit = () => emit("edit", props.task);
const openDetail = ref(false);
const toggleDetail = () => {
  openDetail.value = !openDetail.value;
};
</script>

<template>
  <tr class="border-b hover:bg-gray-50">
    <td class="px-6 py-4">
      <button
        class="text-left text-gray-900 font-medium hover:underline"
        @click="toggleDetail"
      >
        {{ props.task.name }}
      </button>
    </td>
    <td class="px-6 py-4">
      <div class="flex items-center gap-2">
        <span class="text-gray-700">{{ props.task.project?.name || "—" }}</span>
        <span
          v-if="props.task.project?.is_personal"
          class="text-[10px] px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700"
          >Personal</span
        >
      </div>
    </td>
    <td class="px-6 py-4 text-gray-700">{{ props.task.status || "todo" }}</td>
    <td class="px-6 py-4">
      <span
        class="text-[10px] px-2 py-0.5 rounded-full"
        :class="{
          'bg-gray-100 text-gray-700':
            !props.task.priority || props.task.priority === 'low',
          'bg-yellow-100 text-yellow-700': props.task.priority === 'medium',
          'bg-red-100 text-red-700': props.task.priority === 'high',
        }"
        >{{ (props.task.priority || "low").toUpperCase() }}</span
      >
    </td>
    <td class="px-6 py-4 text-gray-700">
      {{
        props.task.assignee?.full_name || props.task.assignee?.username || "—"
      }}
    </td>
    <td class="px-6 py-4 text-gray-700">
      {{ formatDate(props.task.deadline) }}
    </td>
    <td class="px-6 py-4 text-right whitespace-nowrap">
      <span class="inline-flex items-center gap-2">
        <button
          @click="toggleDetail"
          class="px-3 py-1.5 text-xs rounded-lg border border-gray-300 hover:bg-gray-100"
          title="View detail"
        >
          <EyeIcon class="w-4 h-4" />
        </button>
        <button
          v-if="canEdit"
          @click="onEdit"
          class="px-3 py-1.5 text-xs rounded-lg border border-gray-300 hover:bg-gray-100"
          title="Edit task"
        >
          <EditIcon class="w-4 h-4" />
        </button>
      </span>
      <TaskDetaiModal
        :open="openDetail"
        :task-id="props.task.id"
        @close="openDetail = false"
      />
    </td>
  </tr>
</template>

<style scoped></style>
