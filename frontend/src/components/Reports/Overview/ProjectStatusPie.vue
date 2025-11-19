<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent])

const props = defineProps({
  status: {
    type: Object,
    default: () => ({ active: 0, completed: 0, overdue: 0 })
  }
})

const total = computed(() => (props.status.active || 0) + (props.status.completed || 0) + (props.status.overdue || 0))

const option = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0 },
  series: [
    {
      name: 'Projects',
      type: 'pie',
      radius: ['45%', '70%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      data: [
        { value: Math.max(0, props.status.active || 0), name: 'Active', itemStyle: { color: '#22c55e' } },
        { value: Math.max(0, props.status.completed || 0), name: 'Completed', itemStyle: { color: '#9ca3af' } },
        { value: Math.max(0, props.status.overdue || 0), name: 'Overdue', itemStyle: { color: '#ef4444' } }
      ]
    }
  ]
}))
</script>

<template>
  <div class="bg-white rounded-xl border p-5">
    <h3 class="text-base font-semibold mb-3">Project Status Distribution</h3>
    <div v-if="total === 0" class="text-sm text-gray-500">No projects to display.</div>
    <div v-else class="w-full">
      <v-chart :option="option" autoresize style="height: 260px;" />
    </div>
  </div>
</template>

<style scoped>
</style>
