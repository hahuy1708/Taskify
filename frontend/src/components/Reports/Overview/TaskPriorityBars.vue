<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])

const props = defineProps({
  priority: {
    type: Object,
    default: () => ({ high: 0, medium: 0, low: 0 })
  }
})

const categories = ['High', 'Medium', 'Low']
const values = computed(() => [
  Math.max(0, props.priority.high || 0),
  Math.max(0, props.priority.medium || 0),
  Math.max(0, props.priority.low || 0)
])

const option = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 20, right: 20, top: 20, bottom: 30, containLabel: true },
  xAxis: { type: 'category', data: categories, axisTick: { show: false } },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    {
      type: 'bar',
      data: values.value.map((v, i) => ({
        value: v,
        itemStyle: { color: i === 0 ? '#ef4444' : i === 1 ? '#f59e0b' : '#9ca3af', borderRadius: [6, 6, 0, 0] }
      })),
      barWidth: '40%'
    }
  ]
}))
</script>

<template>
  <div class="bg-white rounded-xl border p-5">
    <h3 class="text-base font-semibold mb-3">Task Priority Distribution</h3>
    <h4>(Open Tasks Only)</h4>
    <v-chart :option="option" autoresize style="height: 260px;" />
  </div>
  </template>

<style scoped>
</style>
