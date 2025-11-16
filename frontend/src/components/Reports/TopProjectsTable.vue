<script setup>
const props = defineProps({ projects: { type: Array, default: () => [] } })
</script>

<template>
  <div>
    <h3 class="text-lg font-medium mb-2">Top Projects</h3>
    <div class="overflow-auto">
      <table class="min-w-full text-sm">
        <thead>
          <tr class="text-left text-xs text-gray-500">
            <th class="px-2 py-1">#</th>
            <th class="px-2 py-1">Project</th>
            <th class="px-2 py-1">Tasks</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(p, idx) in props.projects" :key="p.id" class="border-b">
            <td class="px-2 py-2">{{ idx + 1 }}</td>
            <td class="px-2 py-2">{{ p.name }}</td>
            <td class="px-2 py-2">{{ p.count }}</td>
          </tr>
          <tr v-if="props.projects.length === 0">
            <td class="px-2 py-2" colspan="3">No projects</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
