<template>
  <div>
    <h2>仪表盘</h2>
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card shadow="hover">
          <div style="color: #999; font-size: 13px">{{ stat.label }}</div>
          <div style="font-size: 28px; font-weight: bold; margin-top: 8px">{{ stat.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>最近信号</template>
      <el-table :data="signals" style="width: 100%" size="small">
        <el-table-column prop="code" label="代码" width="100" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="tagType(row.type)" size="small">{{ typeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="direction" label="方向" width="80" />
        <el-table-column prop="score" label="评分" width="80" />
        <el-table-column prop="reason" label="原因" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref([
  { label: '覆盖股票', value: '--' },
  { label: '今日信号', value: '--' },
  { label: '虚拟盘盈亏', value: '--' },
  { label: '持仓数', value: '--' },
])
const signals = ref<any[]>([])

function tagType(type: string) {
  return type === 'entry_exit' ? 'danger' : type === 'anomaly' ? 'warning' : 'success'
}
function typeLabel(type: string) {
  return type === 'ranking' ? '排名' : type === 'entry_exit' ? '买卖点' : '异动'
}

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/dashboard/summary')
    stats.value = [
      { label: '覆盖股票', value: data.total_stocks },
      { label: '今日信号', value: data.recent_signals?.length || 0 },
      { label: '虚拟盘盈亏', value: `${data.paper_account?.pnl_pct?.toFixed(2)}%` },
      { label: '持仓数', value: data.paper_account?.positions },
    ]
    signals.value = data.recent_signals || []
  } catch (e) {
    console.error(e)
  }
})
</script>
