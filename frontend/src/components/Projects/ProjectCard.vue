<!-- components/ProjectCard -->
<script setup>
defineProps({
  project: {
    type: Object,
    required: true
  }
})
import { Calendar, Users, CheckCircle } from 'lucide-vue-next'
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition">
    <h3 class="font-semibold">{{ project.name }}</h3>
    <p class="text-sm text-gray-500">{{ project.description }}</p>

    <div class="mt-4">
      <div class="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
        <div
          class="h-full bg-indigo-600 transition-all"
          :style="{ width: project.progress + '%' }"
        ></div>
      </div>
      <div class="mt-2 flex items-center justify-between text-sm text-gray-600">
        <span>Progress</span>
        <span>{{ project.progress }}%</span>
      </div>
    </div>

    <div class="mt-4 flex items-center gap-4 text-sm text-gray-600">
      <span class="flex items-center gap-1">
        <Calendar class="w-4 h-4 text-gray-500" />
        {{ new Date(project.deadline).toLocaleString() }}
      </span>
      <span class="flex items-center gap-1">
        <Users class="w-4 h-4 text-gray-500" />
        {{ project.member_count }}
      </span>
      <span
        class="ml-auto px-2 py-0.5 rounded-full text-xs"
        :class="project.status === 'Active'
          ? 'bg-emerald-100 text-emerald-700'
          : 'bg-yellow-100 text-yellow-700'"
      >
        {{ project.status }}
      </span>
    </div>

    <div class="mt-2 text-sm text-gray-500 flex items-center gap-1">
      <CheckCircle class="w-4 h-4 text-indigo-500" />
      <span>
        Leader:
        <span v-if="project.leader" class="text-gray-700 font-medium">
          {{ project.leader.name }} (#{{ project.leader.id }})
        </span>
      </span>
    </div>
  </div>
</template>
