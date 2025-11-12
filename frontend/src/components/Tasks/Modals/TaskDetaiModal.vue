<!-- src/components/Tasks/Modals/TaskDetailModal.vue -->
<script setup>
import TaskDetail from '@/components/Tasks/TaskDetail.vue'

const props = defineProps({
	open: { type: Boolean, default: false },
	taskId: { type: [String, Number], required: true },
})
const emit = defineEmits(['close'])

const close = () => emit('close')
</script>

<template>
	<teleport to="body">
		<div v-if="open" class="fixed inset-0 z-50 flex items-start md:items-center justify-center p-4">
			<div class="absolute inset-0 bg-black/50" @click="close" />
			<div class="relative bg-white rounded-xl shadow-lg w-full max-w-6xl p-6 border border-gray-200 max-h-[90vh] overflow-auto">
				<div class="flex items-center justify-between mb-4">
					<h2 class="text-lg font-semibold">Task Detail</h2>
					<button @click="close" class="text-gray-400 hover:text-gray-600">✕</button>
				</div>
				<TaskDetail :task-id="props.taskId" />
			</div>
		</div>
	</teleport>
</template>

<style scoped></style>