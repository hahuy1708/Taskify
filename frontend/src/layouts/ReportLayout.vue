<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, required: true },
  tabs: { type: Array, default: () => [] },
  title: { type: String, default: 'Reports' },
  subtitle: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

const active = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

function selectTab(key) {
  active.value = key
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-gray-900">{{ title }}</h2>
        <p v-if="subtitle" class="text-sm text-gray-500 mt-1">{{ subtitle }}</p>
      </div>
      <div>
        <slot name="header-actions" />
      </div>
    </div>

    <div class="flex justify-start">
      <div class="inline-flex gap-2 p-1 rounded-lg border border-gray-200 bg-gray-50">
        <button
          v-for="t in tabs"
          :key="t.key"
          type="button"
          class="flex items-center gap-2 px-4 py-2 rounded-md border transition-all"
          :class="active === t.key
            ? 'bg-indigo-50 border-indigo-300 text-indigo-700 font-medium'
            : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'"
          @click="selectTab(t.key)"
        >
          <component v-if="t.icon" :is="t.icon" class="w-4 h-4" />
          <span>{{ t.label }}</span>
        </button>
      </div>
    </div>

    <div>
      <slot />
    </div>
  </div>
  </template>

<style scoped>
</style>
