<!-- src/pages/TaskDetailPage.vue -->
<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import TaskDetail from '@/components/Tasks/TaskDetail.vue'

const route = useRoute()
const router = useRouter()
const taskId = computed(() => route.params.id)
const goBack = () => router.back()
</script>

<template>
  <div class="p-4 space-y-4">
    <div>
      <button @click="goBack" class="text-sm text-gray-600 hover:text-gray-800">← Back</button>
    </div>
    <TaskDetail v-if="taskId" :task-id="taskId" />
  </div>
</template>

<style scoped></style>
