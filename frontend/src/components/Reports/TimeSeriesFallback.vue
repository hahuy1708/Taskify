<script setup>
const props = defineProps({ points: { type: Array, default: () => [] } })
</script>

<template>
  <div>
    <h3 class="text-sm text-gray-500 mb-2">Series (table fallback)</h3>
    <div class="overflow-auto">
      <table class="min-w-full text-sm">
        <thead>
          <tr class="text-left text-xs text-gray-500">
            <th class="px-2 py-1">Date</th>
            <th class="px-2 py-1">Count</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in props.points" :key="p.period">
            <td class="px-2 py-2">{{ p.period }}</td>
            <td class="px-2 py-2">{{ p.count }}</td>
          </tr>
          <tr v-if="props.points.length === 0">
            <td class="px-2 py-2" colspan="2">No data</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
