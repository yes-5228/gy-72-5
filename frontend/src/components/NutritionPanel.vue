<template>
  <section class="panel">
    <div class="panel-title">
      <h2>营养成分分析</h2>
      <button class="ghost-button small" type="button" :disabled="items.length === 0 || loading" @click="runAnalysis">
        {{ loading ? '分析中...' : '重新分析' }}
      </button>
    </div>

    <div v-if="!analysis && !loading" class="empty-state">餐盘中有菜品后可查看总热量、蛋白质、脂肪、碳水和钠含量。</div>
    <template v-else>
      <div class="macro-grid-wrapper">
        <div v-if="loading" class="recalculating-overlay">
          <span>正在重新计算...</span>
        </div>
        <div class="macro-grid">
          <div v-for="item in macroItems" :key="item.label">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </div>
      <ul v-if="analysis" class="advice-list">
        <li v-for="advice in analysis.advice" :key="advice">{{ advice }}</li>
      </ul>
    </template>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { analyzeNutrition } from '../api/canteen'

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
})

const analysis = ref(null)
const loading = ref(false)
let pendingRequest = 0

const macroItems = computed(() => {
  if (!analysis.value) {
    return [
      { label: '热量', value: '— kcal' },
      { label: '蛋白质', value: '— g' },
      { label: '脂肪', value: '— g' },
      { label: '碳水', value: '— g' },
      { label: '钠', value: '— mg' },
    ]
  }
  const t = analysis.value.totals
  return [
    { label: '热量', value: `${Math.round(t.calories)} kcal` },
    { label: '蛋白质', value: `${Number(t.protein).toFixed(1)} g` },
    { label: '脂肪', value: `${Number(t.fat).toFixed(1)} g` },
    { label: '碳水', value: `${Number(t.carbohydrate).toFixed(1)} g` },
    { label: '钠', value: `${Math.round(t.sodium)} mg` },
  ]
})

async function runAnalysis() {
  if (props.items.length === 0) {
    analysis.value = null
    return
  }
  const requestId = ++pendingRequest
  loading.value = true
  try {
    const result = await analyzeNutrition(props.items)
    if (requestId === pendingRequest) {
      analysis.value = result
    }
  } finally {
    if (requestId === pendingRequest) {
      loading.value = false
    }
  }
}

watch(
  () => props.items.map((item) => `${item.dish?.id ?? item.dish_id}:${item.quantity}`).join(','),
  runAnalysis,
  { immediate: true },
)
</script>

<style scoped>
.macro-grid-wrapper {
  position: relative;
}

.recalculating-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgb(255 255 255 / 0.7);
  border-radius: 8px;
  z-index: 1;
  color: #66746b;
  font-size: 13px;
}
</style>
