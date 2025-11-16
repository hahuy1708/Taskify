<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Object, default: () => ({}) } })

const entries = computed(() => {
  const d = props.data || {}
  return Object.keys(d).map((k, i) => ({
    label: k,
    value: d[k],
    color: ['#6366f1', '#10b981', '#ef4444', '#f59e0b', '#60a5fa'][i % 5]
  }))
})
</script>

<template>
  <div>
    <h3 class="text-sm text-gray-500 mb-2">By Status</h3>
    <div class="space-y-2">
      <template v-if="entries.length === 0">
        <p class="text-xs text-gray-500">No data</p>
      </template>
      <template v-else>
        <div v-for="e in entries" :key="e.label" class="flex items-center gap-3">
          <span :style="{ background: e.color }" class="w-3 h-3 rounded-md inline-block"></span>
          <span class="text-sm font-medium">{{ e.label }}</span>
          <span class="text-sm text-gray-500 ml-2">{{ e.value }}</span>
        </div>
      </template>
    </div>
  </div>
</template>
