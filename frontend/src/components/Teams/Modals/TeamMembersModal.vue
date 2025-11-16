<script setup>

// eslint-disable-next-line no-unused-vars
const props = defineProps({
  team: { type: Object, required: true },
  members: { type: Array, required: true }
})
// eslint-disable-next-line no-unused-vars
const emit = defineEmits(['close'])
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 w-96 max-h-[70vh] overflow-auto">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Team Members — {{ team.name }}</h3>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-800">✕</button>
      </div>

      <div v-if="members.length === 0" class="text-gray-500">No members yet.</div>

      <ul class="space-y-3">
        <li v-for="m in members" :key="m.id" class="flex items-center gap-3">
          <div class="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-sm font-semibold text-indigo-700">{{ m.username ? m.username.charAt(0).toUpperCase() : 'U' }}</div>
          <div class="flex-1">
            <div class="font-medium">{{ m.username }}</div>
              <div class="text-xs text-gray-500">Role: {{ m.project_role || '—' }}</div>
          </div>
        </li>
      </ul>

      <div class="mt-4 text-right">
        <button @click="$emit('close')" class="px-4 py-2 bg-gray-200 rounded">Close</button>
      </div>
    </div>
  </div>
</template>
