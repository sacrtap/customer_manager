<!-- 健康度仪表盘 -->
<template>
  <div class="health-dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-content">
        <h2 class="welcome-title">客户健康度监控</h2>
        <p class="welcome-subtitle">
          实时监控客户健康状态，及时发现流失风险
        </p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-icon blue">
            <icon-user-group />
          </div>
        </div>
        <div class="stat-value">{{ stats.total_customers }}</div>
        <div class="stat-label">客户总数</div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-icon green">
            <icon-check-circle />
          </div>
        </div>
        <div class="stat-value">{{ stats.healthy_customers }}</div>
        <div class="stat-label">健康客户</div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-icon orange">
            <icon-exclamation-circle />
          </div>
        </div>
        <div class="stat-value">{{ stats.at_risk_customers }}</div>
        <div class="stat-label">风险客户</div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-icon red">
            <icon-close-circle />
          </div>
        </div>
        <div class="stat-value">{{ stats.zombie_customers }}</div>
        <div class="stat-label">僵尸客户</div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">健康度趋势</span>
          <a-radio-group v-model="trendPeriod" type="button" size="small">
            <a-radio value="week">本周</a-radio>
            <a-radio value="month">本月</a-radio>
            <a-radio value="quarter">本季</a-radio>
          </a-radio-group>
        </div>
        <div ref="trendChart" class="chart-container"></div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">健康度分布</span>
        </div>
        <div ref="distributionChart" class="chart-container-small"></div>
      </div>
    </div>

    <!-- 风险预警列表 -->
    <div class="alert-list-card">
      <div class="card-header">
        <span class="card-title">⚠️ 风险客户预警</span>
        <Button type="text" @click="router.push('/health/risks')">
          查看全部 <icon-arrow-right />
        </Button>
      </div>
      <Table :columns="riskColumns" :data="riskData" :pagination="false" size="small" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { healthApi } from '@/api/health'

const router = useRouter()

const trendPeriod = ref('month')
const trendChart = ref<HTMLElement | null>(null)
const distributionChart = ref<HTMLElement | null>(null)
let trendChartInstance: echarts.ECharts | null = null
let distributionChartInstance: echarts.ECharts | null = null

const stats = ref({
  total_customers: 0,
  healthy_customers: 0,
  at_risk_customers: 0,
  zombie_customers: 0
})

const riskColumns = [
  { title: '客户名称', dataIndex: 'name', width: 200, ellipsis: true },
  { title: '等级', dataIndex: 'tier_level', width: 80 },
  { title: '未使用天数', dataIndex: 'days_inactive', width: 100, align: 'center' },
  { title: '健康评分', dataIndex: 'health_score', width: 100, align: 'center' },
  { title: '风险等级', dataIndex: 'risk_level', width: 100, align: 'center' }
]

const riskData = ref<any[]>([])

const loadDashboardData = async () => {
  try {
    const data = await healthApi.getDashboard()
    stats.value = {
      total_customers: data.total_customers,
      healthy_customers: data.healthy_customers,
      at_risk_customers: data.at_risk_customers,
      zombie_customers: data.zombie_customers
    }
    
    riskData.value = data.risk_customers?.slice(0, 5) || []
    
    initTrendChart(data.health_trend)
    initDistributionChart(data.value_distribution)
  } catch (error) {
    console.error('加载健康度数据失败:', error)
  }
}

const initTrendChart = (trendData: any[]) => {
  if (!trendChart.value) return

  trendChartInstance = echarts.init(trendChart.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['健康度评分'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trendData?.map((item: any) => item.date?.slice(5, 10) || '') || []
    },
    yAxis: { type: 'value', min: 0, max: 100 },
    series: [{
      name: '健康度评分',
      type: 'line',
      smooth: true,
      data: trendData?.map((item: any) => item.score) || [],
      areaStyle: { opacity: 0.1 },
      itemStyle: { color: '#00B42A' }
    }]
  }
  trendChartInstance.setOption(option)
}

const initDistributionChart = (distribution: any[]) => {
  if (!distributionChart.value) return

  distributionChartInstance = echarts.init(distributionChart.value)
  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', right: '5%', top: 'center' },
    series: [{
      name: '健康度分布',
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
      data: distribution?.map((item: any) => ({
        value: item.count,
        name: item.label,
        itemStyle: {
          color: item.status === 'healthy' ? '#00B42A' : item.status === 'risk' ? '#FF7D00' : '#F53F3F'
        }
      })) || []
    }]
  }
  distributionChartInstance.setOption(option)
}

const handleResize = () => {
  trendChartInstance?.resize()
  distributionChartInstance?.resize()
}

watch(trendPeriod, () => {
  loadDashboardData()
})

onMounted(() => {
  loadDashboardData()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
.health-dashboard {
  padding: 24px;
}

.welcome-banner {
  background: linear-gradient(135deg, #165DFF 0%, #0E42D2 100%);
  border-radius: 12px;
  padding: 32px;
  color: white;
  margin-bottom: 24px;
}

.welcome-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.welcome-subtitle {
  font-size: 14px;
  opacity: 0.9;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #E5E6EB;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue {
  background: linear-gradient(135deg, rgba(22,93,255,0.1) 0%, rgba(22,93,255,0.05) 100%);
  color: #165DFF;
}

.stat-icon.green {
  background: linear-gradient(135deg, rgba(0,180,42,0.1) 0%, rgba(0,180,42,0.05) 100%);
  color: #00B42A;
}

.stat-icon.orange {
  background: linear-gradient(135deg, rgba(255,125,0,0.1) 0%, rgba(255,125,0,0.05) 100%);
  color: #FF7D00;
}

.stat-icon.red {
  background: linear-gradient(135deg, rgba(245,63,63,0.1) 0%, rgba(245,63,63,0.05) 100%);
  color: #F53F3F;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1D2129;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #86909C;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #E5E6EB;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #1D2129;
}

.chart-container {
  height: 300px;
}

.chart-container-small {
  height: 300px;
}

.alert-list-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #E5E6EB;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1D2129;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
