<script setup>
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { computed } from 'vue'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])

const props = defineProps({
  leaders: { type: Array, default: () => [] }
})

const categories = computed(() => props.leaders.map(l => l.leader_name))
const values = computed(() => props.leaders.map(l => l.project_count))

const option = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 80, right: 20, top: 20, bottom: 30, containLabel: true },
  xAxis: { type: 'value', minInterval: 1 },
  yAxis: { type: 'category', data: categories.value, axisTick: { show: false } },
  series: [
    {
      name: 'Projects',
      type: 'bar',
      data: values.value,
      itemStyle: { color: '#3b82f6', borderRadius: [0, 6, 6, 0] },
      barWidth: '40%'
    }
  ]
}))
</script>

<template>
  <div class="bg-white rounded-xl border p-5">
    <h3 class="text-base font-semibold">Projects by Leader</h3>
    <p class="text-xs text-gray-500 mb-3">Top 5 leaders by number of projects</p>
    <v-chart :option="option" autoresize style="height: 320px;" />
  </div>
</template>

<style scoped>
</style>
