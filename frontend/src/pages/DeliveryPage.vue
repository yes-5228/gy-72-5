<template>
  <section class="panel full-panel">
    <div class="panel-title">
      <h2>配送任务</h2>
      <span>{{ deliveries.length }} 条任务</span>
    </div>

    <div v-if="loading" class="loading">配送数据加载中...</div>
    <div v-else class="delivery-list">
      <article v-for="task in deliveries" :key="task.id" class="delivery-card">
        <div class="delivery-main">
          <div>
            <strong>订单 #{{ task.order }}</strong>
            <p>{{ task.order_detail.student_name }} · {{ task.order_detail.delivery_address }}</p>
            <small>预计 {{ formatTime(task.estimated_arrival) }}</small>
          </div>
          <div class="delivery-meta">
            <span>{{ task.courier_name || '待分配' }}</span>
            <select :value="task.status" @change="changeStatus(task, $event.target.value)">
              <option value="waiting">待分配</option>
              <option value="assigned">已分配</option>
              <option value="picked">已取餐</option>
              <option value="delivered">已送达</option>
              <option value="failed">异常</option>
            </select>
            <button type="button" class="ghost-button small" @click="toggleExpand(task.id)">
              {{ expandedId === task.id ? '收起订单' : '查看订单' }}
            </button>
          </div>
        </div>

        <div v-if="expandedId === task.id" class="order-detail">
          <div class="order-summary">
            <span>学号：{{ task.order_detail.student_no }}</span>
            <span>电话：{{ task.order_detail.phone }}</span>
            <span>状态：{{ statusLabel(task.order_detail.status) }}</span>
            <span v-if="task.order_detail.note">备注：{{ task.order_detail.note }}</span>
          </div>

          <h4>订单明细（营养快照）</h4>
          <table class="nutrition-table">
            <thead>
              <tr>
                <th>菜品</th>
                <th>份数</th>
                <th>单价</th>
                <th>小计</th>
                <th>热量(kcal)</th>
                <th>蛋白质(g)</th>
                <th>脂肪(g)</th>
                <th>碳水(g)</th>
                <th>钠(mg)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in task.order_detail.items" :key="item.id">
                <td>{{ item.dish_detail?.name || `菜品#${item.dish}` }}</td>
                <td>{{ item.quantity }}</td>
                <td>￥{{ item.unit_price }}</td>
                <td>￥{{ (item.unit_price * item.quantity).toFixed(2) }}</td>
                <td>{{ Math.round(Number(item.calories)) }}</td>
                <td>{{ formatDecimal(item.protein) }}</td>
                <td>{{ formatDecimal(item.fat) }}</td>
                <td>{{ formatDecimal(item.carbohydrate) }}</td>
                <td>{{ Math.round(Number(item.sodium)) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="3">合计</td>
                <td>￥{{ task.order_detail.total_amount }}</td>
                <td>{{ Math.round(sumField(task.order_detail.items, 'calories')) }}</td>
                <td>{{ formatDecimal(sumField(task.order_detail.items, 'protein')) }}</td>
                <td>{{ formatDecimal(sumField(task.order_detail.items, 'fat')) }}</td>
                <td>{{ formatDecimal(sumField(task.order_detail.items, 'carbohydrate')) }}</td>
                <td>{{ Math.round(sumField(task.order_detail.items, 'sodium')) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { fetchDeliveries, updateDelivery } from '../api/canteen'

const props = defineProps({
  reloadKey: {
    type: Number,
    default: 0,
  },
})

const deliveries = ref([])
const loading = ref(false)
const expandedId = ref(null)

const statusMap = {
  pending: '待确认',
  confirmed: '已确认',
  preparing: '备餐中',
  delivering: '配送中',
  completed: '已完成',
  cancelled: '已取消',
}

async function loadDeliveries() {
  loading.value = true
  try {
    deliveries.value = await fetchDeliveries()
  } finally {
    loading.value = false
  }
}

async function changeStatus(task, status) {
  const payload = { status }
  if (status === 'delivered') {
    payload.delivered_at = new Date().toISOString()
  }
  const updated = await updateDelivery(task.id, payload)
  Object.assign(task, updated)
}

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

function statusLabel(status) {
  return statusMap[status] || status
}

function formatTime(value) {
  if (!value) return '待确认'
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function formatDecimal(value) {
  if (value === null || value === undefined || value === '') return '0.0'
  return Number(value).toFixed(1)
}

function sumField(items, field) {
  return items.reduce((sum, item) => sum + Number(item[field] || 0), 0)
}

onMounted(loadDeliveries)
watch(() => props.reloadKey, loadDeliveries)
</script>

<style scoped>
.delivery-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
}

.order-detail {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #edf1ee;
  width: 100%;
}

.order-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 8px;
  margin-bottom: 12px;
  color: #445248;
  font-size: 13px;
}

.order-detail h4 {
  margin: 12px 0 8px;
  font-size: 14px;
  color: #17201a;
}

.nutrition-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.nutrition-table th,
.nutrition-table td {
  padding: 8px 10px;
  text-align: right;
  border-bottom: 1px solid #edf1ee;
}

.nutrition-table th:first-child,
.nutrition-table td:first-child {
  text-align: left;
}

.nutrition-table thead th {
  background: #f1f5f2;
  color: #445248;
  font-weight: 600;
}

.nutrition-table tfoot td {
  background: #f1f5f2;
  font-weight: 700;
  color: #1e5c3e;
}

@media (max-width: 640px) {
  .delivery-main {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
