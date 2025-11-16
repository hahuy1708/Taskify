<script setup>
import { ref, onMounted, computed } from 'vue'
import { getTaskSummary, getTaskTimeseries, getDashboardStats } from '@/api/statsApi'

// === DATA ===
const dashboard = ref(null)
const summary = ref(null)
const series = ref([])
const loading = ref(false)
const startDate = ref('')
const endDate = ref('')
const interval = ref('day')

// === HELPERS ===
function defaultRange(days = 30) {
  const now = new Date()
  const start = new Date(now)
  start.setDate(now.getDate() - days)
  return {
    start: start.toISOString().slice(0, 10),
    end: now.toISOString().slice(0, 10)
  }
}

// === LOAD DATA ===
async function load(range) {
  loading.value = true
  try {
    const [dash, sum] = await Promise.all([
      getDashboardStats(),
      getTaskSummary()
    ])
    dashboard.value = dash
    summary.value = sum

    const r = range || { start: startDate.value, end: endDate.value, interval: interval.value }
    const final = (r.start && r.end) ? r : defaultRange(30)

    startDate.value = final.start
    endDate.value = final.end
    interval.value = r.interval || 'day'

    series.value = await getTaskTimeseries(final)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const r = defaultRange(30)
  startDate.value = r.start
  endDate.value = r.end
  load(r)
})

function refresh() {
  load({ start: startDate.value, end: endDate.value, interval: interval.value })
}

// === SVG CHART DATA ===
const chartWidth = 600
const chartHeight = 220
const pad = { t: 20, r: 30, b: 40, l: 50 }
const w = chartWidth - pad.l - pad.r
const h = chartHeight - pad.t - pad.b

const linePoints = computed(() => {
  if (!series.value.length) return ''
  const max = Math.max(...series.value.map(d => d.count), 1)
  return series.value.map((d, i) => {
    const x = (i / (series.value.length - 1)) * w + pad.l
    const y = h - (d.count / max) * h + pad.t
    return `${x},${y}`
  }).join(' ')
})

const areaPoints = computed(() => {
  if (!linePoints.value) return ''
  return `${pad.l},${chartHeight - pad.b} ${linePoints.value} ${chartWidth - pad.r},${chartHeight - pad.b}`
})

const xLabels = computed(() => {
  const step = Math.max(1, Math.ceil(series.value.length / 6))
  return series.value.filter((_, i) => i % step === 0)
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 md:p-6">
    <div class="max-w-7xl mx-auto space-y-6">

      <!-- HEADER -->
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-gray-100">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Báo cáo Quản trị</h1>
            <p class="text-sm text-gray-500 mt-1">Theo dõi hiệu suất & xu hướng nhiệm vụ</p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <input type="date" v-model="startDate" class="input" />
            <input type="date" v-model="endDate" class="input" />
            <select v-model="interval" class="input">
              <option value="day">Ngày</option>
              <option value="week">Tuần</option>
            </select>
            <button @click="refresh" class="btn-refresh">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- LOADING -->
      <div v-if="loading" class="flex justify-center py-16">
        <div class="animate-spin rounded-full h-12 w-12 border-b-3 border-indigo-600"></div>
      </div>

      <!-- STATS CARDS -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
        <div class="stat-card group">
          <p class="text-sm font-medium text-gray-500">Tổng dự án</p>
          <p class="text-3xl font-bold text-indigo-600 mt-1">{{ dashboard?.total_projects ?? summary?.total ?? 0 }}</p>
          <div class="mt-3 h-1 bg-indigo-100 rounded-full overflow-hidden">
            <div class="h-full bg-indigo-600 transition-all duration-1000 group-hover:w-full" :style="{ width: '70%' }"></div>
          </div>
        </div>

        <div class="stat-card group">
          <p class="text-sm font-medium text-gray-500">Người dùng hoạt động</p>
          <p class="text-3xl font-bold text-emerald-600 mt-1">{{ dashboard?.active_users ?? 0 }}</p>
          <div class="mt-3 h-1 bg-emerald-100 rounded-full overflow-hidden">
            <div class="h-full bg-emerald-600 transition-all duration-1000" :style="{ width: `${(dashboard?.active_users ?? 0) * 2}%` }"></div>
          </div>
        </div>

        <div class="stat-card group">
          <p class="text-sm font-medium text-gray-500">Nhiệm vụ hoàn thành</p>
          <p class="text-3xl font-bold text-blue-600 mt-1">{{ dashboard?.tasks_completed ?? 0 }}</p>
          <div class="mt-3 h-1 bg-blue-100 rounded-full overflow-hidden">
            <div class="h-full bg-blue-600 transition-all duration-1000" :style="{ width: '85%' }"></div>
          </div>
        </div>

        <div class="stat-card group">
          <p class="text-sm font-medium text-gray-500">Hiệu suất</p>
          <p class="text-3xl font-bold text-purple-600 mt-1">{{ dashboard?.productivity ?? 0 }}%</p>
          <div class="mt-3 h-2 bg-purple-100 rounded-full overflow-hidden">
            <div class="h-full bg-purple-600 transition-all duration-1000" :style="{ width: `${dashboard?.productivity ?? 0}%` }"></div>
          </div>
        </div>
      </div>

      <!-- CHARTS SECTION -->
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 border border-gray-100">
        <h2 class="text-lg font-semibold text-gray-800 mb-5">Xu hướng nhiệm vụ hoàn thành</h2>

        <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <!-- SVG LINE CHART (inline) -->
          <div class="xl:col-span-2">
            <div class="bg-gray-50/50 rounded-xl p-4 border border-gray-200">
              <svg :viewBox="`0 0 ${chartWidth} ${chartHeight}`" class="w-full h-64">
                <!-- Grid -->
                <path v-for="i in 5" :key="i"
                  :d="`M ${pad.l} ${pad.t + (i * h / 5)} H ${chartWidth - pad.r}`"
                  stroke="#e5e7eb" stroke-width="1" />

                <!-- Area Fill -->
                <polygon :points="areaPoints" fill="url(#grad)" />

                <!-- Line -->
                <polyline :points="linePoints" fill="none" stroke="#6366f1" stroke-width="3"
                  stroke-linecap="round" class="transition-all duration-700" />

                <!-- Dots -->
                <circle v-for="(p, i) in linePoints.split(' ')" :key="i"
                  :cx="p.split(',')[0]" :cy="p.split(',')[1]" r="4" fill="#6366f1"
                  class="hover:r-6 transition-all cursor-pointer" />

                <!-- Gradient -->
                <defs>
                  <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#6366f1" stop-opacity="0.3" />
                    <stop offset="100%" stop-color="#6366f1" stop-opacity="0" />
                  </linearGradient>
                </defs>
              </svg>

              <!-- X-axis labels -->
              <div class="flex justify-between text-xs text-gray-500 mt-3 px-12">
                <span v-for="d in xLabels" :key="d.period">
                  {{ new Date(d.period).toLocaleDateString('vi-VN', { day: 'numeric', month: 'short' }) }}
                </span>
              </div>
            </div>
          </div>

          <!-- RIGHT SIDEBAR -->
          <div class="space-y-5">
            <div class="bg-gradient-to-br from-indigo-50 to-purple-50 p-5 rounded-xl border">
              <h3 class="text-sm font-semibold text-gray-700 mb-3">Trạng thái nhiệm vụ</h3>
              <StatusPie :data="summary?.by_status || {}" />
            </div>

            <div class="bg-gradient-to-br from-blue-50 to-cyan-50 p-5 rounded-xl border">
              <h3 class="text-sm font-semibold text-gray-700 mb-3">Top dự án</h3>
              <TopProjectsTable :projects="summary?.by_project || []" />
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.input {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.15s ease;
}
.input:focus {
  box-shadow: 0 0 0 4px rgba(99,102,241,0.12);
  border-color: #6366f1;
}
.btn-refresh {
  padding: 0.625rem;
  color: #ffffff;
  border-radius: 0.5rem;
  background-image: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
  box-shadow: 0 6px 12px rgba(79,70,229,0.12);
  transition: all 0.15s ease;
}
.btn-refresh:hover {
  filter: brightness(0.95);
}
.stat-card {
  background-color: rgba(255,255,255,0.9);
  backdrop-filter: blur(6px);
  padding: 1.5rem;
  border-radius: 1rem;
  border: 1px solid #f3f4f6;
  box-shadow: 0 6px 18px rgba(15,23,42,0.06);
  transition: box-shadow 0.25s ease, transform 0.15s ease;
}
.stat-card:hover {
  box-shadow: 0 12px 28px rgba(15,23,42,0.08);
  transform: translateY(-4px);
}
</style>