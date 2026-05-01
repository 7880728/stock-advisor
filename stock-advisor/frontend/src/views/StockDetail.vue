<template>
  <div>
    <div style="margin-bottom: 16px">
      <el-button @click="$router.push('/')" text>← 返回</el-button>
      <span style="font-size: 20px; font-weight: bold; margin-left: 16px">
        {{ stock?.name }} ({{ stock?.code }})
      </span>
      <el-tag style="margin-left: 12px">{{ stock?.industry }}</el-tag>
    </div>

    <!-- K-line chart placeholder -->
    <el-card style="margin-bottom: 20px">
      <template #header>K线图 + 技术指标</template>
      <div id="kline-chart" style="width: 100%; height: 400px"></div>
    </el-card>

    <!-- Signals -->
    <el-card style="margin-bottom: 20px">
      <template #header>历史信号</template>
      <el-table :data="signals" size="small">
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="direction" label="方向" width="80" />
        <el-table-column prop="score" label="评分" width="80" />
        <el-table-column prop="reason" label="原因" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </el-card>

    <!-- Financials -->
    <el-card>
      <template #header>基本面数据</template>
      <el-table :data="financials" size="small">
        <el-table-column prop="report_date" label="报告期" width="120" />
        <el-table-column prop="pe" label="PE" />
        <el-table-column prop="pb" label="PB" />
        <el-table-column prop="roe" label="ROE(%)" />
        <el-table-column prop="revenue_yoy" label="营收增速(%)" />
        <el-table-column prop="profit_yoy" label="利润增速(%)" />
        <el-table-column prop="total_market_cap" label="总市值" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'

const route = useRoute()
const code = route.params.code as string
const stock = ref<any>({})
const signals = ref<any[]>([])
const financials = ref<any[]>([])

onMounted(async () => {
  try {
    const [detail, sigs, fins, kline] = await Promise.all([
      axios.get(`/api/stock/${code}`),
      axios.get(`/api/stock/${code}/signals`),
      axios.get(`/api/stock/${code}/financials`),
      axios.get(`/api/stock/${code}/kline`),
    ])
    stock.value = detail.data
    signals.value = sigs.data
    financials.value = fins.data
    renderKline(kline.data)
  } catch (e) {
    console.error(e)
  }
})

function renderKline(data: any[]) {
  if (!data.length) return
  const chart = echarts.init(document.getElementById('kline-chart')!)
  const dates = data.map((d: any) => d.date)
  const values = data.map((d: any) => [d.open, d.close, d.low, d.high])
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { data: dates, type: 'category' },
    yAxis: { scale: true },
    series: [{
      type: 'candlestick',
      data: values,
      itemStyle: {
        color: '#ef5350',
        color0: '#26a69a',
        borderColor: '#ef5350',
        borderColor0: '#26a69a',
      },
    }],
  })
}
</script>
