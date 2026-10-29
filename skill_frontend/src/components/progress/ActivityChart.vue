<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  points: { type: Array, required: true }, // [{ date, label, hours }]
})

const W = 320
const H = 160
const PAD = { top: 18, right: 10, bottom: 26, left: 30 }

const active = ref(null)

const total = computed(() => props.points.reduce((sum, p) => sum + (p.hours || 0), 0))

const ceiling = computed(() => {
  const max = Math.max(...props.points.map((p) => p.hours || 0), 0)
  return Math.max(3, Math.ceil(max / 3) * 3)
})

const ticks = computed(() => [0, 1, 2, 3].map((step) => (ceiling.value / 3) * step))

const coords = computed(() => {
  const innerW = W - PAD.left - PAD.right
  const innerH = H - PAD.top - PAD.bottom
  const count = props.points.length
  const step = count > 1 ? innerW / (count - 1) : 0
  return props.points.map((point, index) => ({
    ...point,
    x: PAD.left + step * index,
    y: PAD.top + innerH * (1 - (point.hours || 0) / ceiling.value),
  }))
})

const linePath = computed(() => {
  const rows = coords.value
  if (!rows.length) return ''
  let d = `M${rows[0].x},${rows[0].y}`
  for (let i = 1; i < rows.length; i += 1) {
    const prev = rows[i - 1]
    const mid = (prev.x + rows[i].x) / 2
    d += ` C${mid},${prev.y} ${mid},${rows[i].y} ${rows[i].x},${rows[i].y}`
  }
  return d
})

const areaPath = computed(() => {
  const rows = coords.value
  if (!rows.length) return ''
  const baseline = H - PAD.bottom
  return `${linePath.value} L${rows[rows.length - 1].x},${baseline} L${rows[0].x},${baseline} Z`
})

function labelFor(point) {
  const hours = point.hours || 0
  if (!hours) return `${point.label}: no sessions`
  return `${point.label}: ${Math.round(hours * 10) / 10} hrs swapped`
}
</script>

<template>
  <div class="relative">
    <svg :viewBox="`0 0 ${W} ${H}`" class="h-auto w-full" role="img" aria-label="Swap hours over the last seven days">
      <defs>
        <linearGradient id="activity-line" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="var(--chart-3)" />
          <stop offset="55%" stop-color="var(--accent-primary)" />
          <stop offset="100%" stop-color="var(--chart-4)" />
        </linearGradient>
        <linearGradient id="activity-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="var(--accent-primary)" stop-opacity="0.32" />
          <stop offset="100%" stop-color="var(--chart-4)" stop-opacity="0.04" />
        </linearGradient>
      </defs>

      <g>
        <line
          v-for="tick in ticks"
          :key="tick"
          :x1="PAD.left"
          :x2="W - PAD.right"
          :y1="H - PAD.bottom - (H - PAD.top - PAD.bottom) * (tick / ceiling)"
          :y2="H - PAD.bottom - (H - PAD.top - PAD.bottom) * (tick / ceiling)"
          stroke="var(--border-color)"
          stroke-width="1"
          stroke-dasharray="2 5"
        />
        <text
          v-for="tick in ticks"
          :key="`label-${tick}`"
          :x="PAD.left - 6"
          :y="H - PAD.bottom - (H - PAD.top - PAD.bottom) * (tick / ceiling) + 3"
          text-anchor="end"
          font-size="8"
          fill="var(--text-secondary)"
        >{{ Math.round(tick) }}h</text>
      </g>

      <path :d="areaPath" fill="url(#activity-fill)" />
      <path :d="linePath" fill="none" stroke="url(#activity-line)" stroke-width="2.5" stroke-linecap="round" />

      <g>
        <circle
          v-for="(point, index) in coords"
          :key="point.date"
          :cx="point.x"
          :cy="point.y"
          :r="active === index ? 4.5 : 3"
          fill="var(--bg-surface)"
          stroke="var(--accent-primary)"
          stroke-width="2"
          class="transition-all duration-150"
        />
        <text
          v-for="point in coords"
          :key="`x-${point.date}`"
          :x="point.x"
          :y="H - 8"
          text-anchor="middle"
          font-size="8"
          fill="var(--text-secondary)"
        >{{ point.label }}</text>
      </g>

      <rect
        v-for="(point, index) in coords"
        :key="`hit-${point.date}`"
        :x="point.x - 14"
        :y="0"
        width="28"
        :height="H"
        fill="transparent"
        @mouseenter="active = index"
        @mouseleave="active = null"
        @focus="active = index"
        @blur="active = null"
      />
    </svg>

    <div
      v-if="active !== null"
      class="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-[130%] whitespace-nowrap rounded-md bg-[var(--text-primary)] px-2 py-1 text-[11px] font-semibold text-[var(--bg-surface)] shadow-lg"
      :style="{ left: `${(coords[active].x / W) * 100}%`, top: `${(coords[active].y / H) * 100}%` }"
    >{{ labelFor(coords[active]) }}</div>

    <p v-if="!total" class="absolute inset-x-0 top-1/2 -translate-y-1/2 text-center text-xs font-semibold text-[var(--text-secondary)]">
      No swap hours logged in the last 7 days
    </p>
  </div>
</template>
