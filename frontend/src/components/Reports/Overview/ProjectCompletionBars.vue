<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, LegendComponent])

const props = defineProps({
  projects: {
    type: Array,
    default: () => [] // [{id, name, done, total, remaining}]
  }
})

const categories = computed(() => props.projects.map(p => p.name))
const doneSeries = computed(() => props.projects.map(p => Math.max(0, p.done || 0)))
const remainingSeries = computed(() => props.projects.map(p => Math.max(0, p.remaining || 0)))

const option = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { bottom: 0 },
  grid: { left: 20, right: 20, top: 10, bottom: 40, containLabel: true },
  xAxis: { type: 'value', minInterval: 1 },
  yAxis: { type: 'category', data: categories.value, axisTick: { show: false } },
  series: [
    { name: 'Done', type: 'bar', stack: 'total', data: doneSeries.value, itemStyle: { color: '#22c55e' } },
    { name: 'Remaining', type: 'bar', stack: 'total', data: remainingSeries.value, itemStyle: { color: '#e5e7eb' } }
  ]
}))
</script>

<template>
  <div class="bg-white rounded-xl border p-5">
    <h3 class="text-base font-semibold mb-3">Project Completion Rate</h3>
    <div v-if="!projects || projects.length === 0" class="text-sm text-gray-500">No active projects with tasks.</div>
    <div v-else>
      <v-chart :option="option" autoresize style="height: 360px;" />
    </div>
  </div>
</template>

<style scoped>
</style>
