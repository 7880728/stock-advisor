<template>
  <div>
    <h2>策略配置</h2>
    <el-button type="primary" @click="showCreate = true" style="margin-bottom: 16px">+ 新建策略</el-button>

    <el-table :data="strategies" style="width: 100%">
      <el-table-column prop="name" label="名称" />
      <el-table-column label="规则数" width="100">
        <template #default="{ row }">{{ row.config?.rules?.length || 0 }}</template>
      </el-table-column>
      <el-table-column label="买入阈值" width="100">
        <template #default="{ row }">{{ row.config?.buy_threshold }}</template>
      </el-table-column>
      <el-table-column label="卖出阈值" width="100">
        <template #default="{ row }">{{ row.config?.sell_threshold }}</template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="activate(row.id)" v-if="!row.is_active">启用</el-button>
          <el-button size="small" @click="runBacktest(row.id)">回测</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create dialog -->
    <el-dialog v-model="showCreate" title="新建策略" width="600px">
      <el-form label-width="100px">
        <el-form-item label="策略名">
          <el-input v-model="newStrategy.name" />
        </el-form-item>
        <el-form-item label="买入阈值">
          <el-slider v-model="newStrategy.buy_threshold" :min="50" :max="90" show-input />
        </el-form-item>
        <el-form-item label="卖出阈值">
          <el-slider v-model="newStrategy.sell_threshold" :min="10" :max="50" show-input />
        </el-form-item>
        <el-divider>规则列表</el-divider>
        <div v-for="(rule, i) in newStrategy.rules" :key="i" style="margin-bottom: 8px">
          <el-row :gutter="8">
            <el-col :span="8"><el-select v-model="rule.indicator" placeholder="指标"><el-option v-for="ind in indicators" :key="ind" :label="ind" :value="ind" /></el-select></el-col>
            <el-col :span="6"><el-select v-model="rule.op"><el-option label=">" value=">" /><el-option label="<" value="<" /><el-option label=">=" value=">=" /><el-option label="<=" value="<=" /><el-option label="上穿" value="cross_above" /><el-option label="下穿" value="cross_below" /></el-select></el-col>
            <el-col :span="5"><el-input-number v-model="rule.value" :step="0.1" /></el-col>
            <el-col :span="3"><el-input-number v-model="rule.weight" :min="0.1" :max="5" :step="0.5" size="small" /></el-col>
            <el-col :span="2"><el-button @click="newStrategy.rules.splice(i, 1)" type="danger" size="small" circle>X</el-button></el-col>
          </el-row>
        </div>
        <el-button @click="newStrategy.rules.push({ indicator: 'ma5', op: '>', value: 0, weight: 1 })" size="small">+ 添加规则</el-button>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="createStrategy">创建</el-button>
      </template>
    </el-dialog>

    <!-- Backtest result -->
    <el-dialog v-model="showBacktest" title="回测结果" width="500px">
      <el-descriptions :column="2" border v-if="backtestResult">
        <el-descriptions-item label="总收益">{{ backtestResult.total_return }}%</el-descriptions-item>
        <el-descriptions-item label="年化收益">{{ backtestResult.annual_return }}%</el-descriptions-item>
        <el-descriptions-item label="最大回撤">{{ backtestResult.max_drawdown }}%</el-descriptions-item>
        <el-descriptions-item label="夏普比率">{{ backtestResult.sharpe_ratio }}</el-descriptions-item>
        <el-descriptions-item label="胜率">{{ backtestResult.win_rate }}%</el-descriptions-item>
        <el-descriptions-item label="交易次数">{{ backtestResult.total_trades }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'

const strategies = ref<any[]>([])
const showCreate = ref(false)
const showBacktest = ref(false)
const backtestResult = ref<any>(null)

const indicators = ['ma5', 'ma10', 'ma20', 'ma60', 'macd_dif', 'macd_dea', 'macd_bar',
  'k', 'd', 'j', 'rsi6', 'rsi14', 'boll_upper', 'boll_mid', 'boll_lower',
  'obv', 'atr14', 'wr14', 'cci14', 'bias6', 'bias12', 'bias24']

const newStrategy = reactive({
  name: '',
  buy_threshold: 70,
  sell_threshold: 30,
  rules: [{ indicator: 'ma5', op: 'cross_above', value: 20, weight: 1 }] as any[],
})

async function loadStrategies() {
  const { data } = await axios.get('/api/strategy/')
  strategies.value = data
}

async function createStrategy() {
  await axios.post('/api/strategy/', {
    name: newStrategy.name,
    rules: newStrategy.rules,
    buy_threshold: newStrategy.buy_threshold,
    sell_threshold: newStrategy.sell_threshold,
  })
  showCreate.value = false
  loadStrategies()
}

async function activate(id: number) {
  await axios.put(`/api/strategy/${id}`, { is_active: true })
  loadStrategies()
}

async function runBacktest(id: number) {
  try {
    const { data } = await axios.post(`/api/strategy/${id}/backtest`)
    backtestResult.value = data
    showBacktest.value = true
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadStrategies)
</script>
