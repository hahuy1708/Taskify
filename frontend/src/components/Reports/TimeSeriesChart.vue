<script setup>
import { computed, onMounted, ref } from 'vue'

const props = defineProps({ points: { type: Array, default: () => [] } })

const ChartComponent = ref(null)
const chartAvailable = ref(false)
const ready = ref(false)

const labels = computed(() => props.points.map(p => p.period))
const dataValues = computed(() => props.points.map(p => p.count))

const chartData = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      label: 'Tasks Completed',
      backgroundColor: '#4f46e5',
      data: dataValues.value,
    }
  ]
}))

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
}

onMounted(async () => {
  // Try to dynamically load chart libraries. If not installed, fall back to table.
  try {
    const vueChart = await import('vue-chartjs')
    const chartjs = await import('chart.js')
    const { Bar } = vueChart
    // register necessary elements
    const { Chart, BarElement, CategoryScale, LinearScale, Tooltip, Legend } = chartjs
    if (Chart && Chart.register) {
      Chart.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)
    }
    ChartComponent.value = Bar
    chartAvailable.value = true
  } catch (e) {
    chartAvailable.value = false
  } finally {
    ready.value = true
  }
})
</script>

<template>
  <div style="height:320px">
    <template v-if="ready && chartAvailable && ChartComponent">
      <component :is="ChartComponent" :chart-data="chartData" :options="options" />
    </template>
    <template v-else>
      <div class="overflow-auto h-full">
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
    </template>
  </div>
</template>
