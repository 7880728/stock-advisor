<template>
  <div>
    <h2>信号中心</h2>
    <el-radio-group v-model="filter" style="margin-bottom: 16px">
      <el-radio-button value="">全部</el-radio-button>
      <el-radio-button value="ranking">排名</el-radio-button>
      <el-radio-button value="entry_exit">买卖点</el-radio-button>
      <el-radio-button value="anomaly">异动</el-radio-button>
    </el-radio-group>

    <el-table :data="signals" style="width: 100%">
      <el-table-column prop="code" label="代码" width="100" />
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="row.signal_type === 'entry_exit' ? 'danger' : row.signal_type === 'anomaly' ? 'warning' : 'success'" size="small">
            {{ row.signal_type === 'ranking' ? '排名' : row.signal_type === 'entry_exit' ? '买卖点' : '异动' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="direction" label="方向" width="80" />
      <el-table-column prop="score" label="评分" width="80" />
      <el-table-column prop="reason" label="原因" />
      <el-table-column prop="created_at" label="时间" width="180" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'

const filter = ref('')
const signals = ref<any[]>([])

async function load() {
  const params: any = { limit: 200 }
  if (filter.value) params.signal_type = filter.value
  const { data } = await axios.get('/api/signals/', { params })
  signals.value = data
}

watch(filter, load)
onMounted(load)
</script>
