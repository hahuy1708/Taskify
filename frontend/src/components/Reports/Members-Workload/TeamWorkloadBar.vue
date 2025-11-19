<script setup>
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { computed } from 'vue'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])

const props = defineProps({
  teams: { type: Array, default: () => [] }
})

const categories = computed(() => props.teams.map(t => t.team_name))
const values = computed(() => props.teams.map(t => t.active_tasks))

const option = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 20, right: 20, top: 30, bottom: 30, containLabel: true },
  xAxis: { type: 'category', data: categories.value, axisTick: { show: false } },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    {
      name: 'Active Tasks',
      type: 'bar',
      data: values.value,
      itemStyle: { color: '#3b82f6', borderRadius: [6, 6, 0, 0] },
      barWidth: '40%'
    }
  ]
}))
</script>

<template>
  <div class="bg-white rounded-xl border p-5">
    <h3 class="text-base font-semibold">Team Workload</h3>
    <p class="text-xs text-gray-500 mb-3">Active tasks per team</p>
    <v-chart :option="option" autoresize style="height: 260px;" />
  </div>
</template>

<style scoped>
</style>
