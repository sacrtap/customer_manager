<template>
  <div class="dashboard">
    <!-- 欢迎横幅 -->
      <div class="welcome-banner">
        <div class="welcome-text">
          <h2><icon-morning/> 早上好，{{ userInfo.real_name }}</h2>
          <p>今天是 {{ currentDate }}，祝您工作愉快！</p>
        </div>
        <div class="welcome-stats">
          <div class="welcome-stat">
            <div class="welcome-stat-value">{{ stats.total_customers.toLocaleString() }}</div>
            <div class="welcome-stat-label">客户总数</div>
          </div>
          <div class="welcome-stat">
            <div class="welcome-stat-value">
              {{ stats.total_customers > 0
                ? Math.round((stats.healthy_customers / stats.total_customers) * 100)
                : 0 }}%
            </div>
            <div class="welcome-stat-label">活跃率</div>
          </div>
        </div>
      </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-card-header">
          <div>
            <div class="stat-card-title">总客户数</div>
          </div>
          <div class="stat-card-icon blue">
            <icon-user-group />
          </div>
        </div>
        <div class="stat-card-value">{{ stats.total_customers.toLocaleString() }}</div>
        <div class="stat-card-footer">
          <span class="stat-card-trend up"><icon-arrow-rise/> 12 本月新增</span>
          <span class="stat-card-sub">较上月 +0.9%</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card-header">
          <div>
            <div class="stat-card-title">活跃客户</div>
          </div>
          <div class="stat-card-icon green">
            <icon-check-circle />
          </div>
        </div>
        <div class="stat-card-value">{{ stats.healthy_customers.toLocaleString() }}</div>
        <div class="stat-card-footer">
          <span class="stat-card-trend up"><icon-arrow-rise/> 82.5%</span>
          <span class="stat-card-sub">活跃率</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card-header">
          <div>
            <div class="stat-card-title">风险客户</div>
          </div>
          <div class="stat-card-icon orange">
            <icon-exclamation-circle />
          </div>
        </div>
        <div class="stat-card-value">{{ stats.at_risk_customers.toLocaleString() }}</div>
        <div class="stat-card-footer">
          <span class="stat-card-trend down"><icon-arrow-fall/> 5 较上周</span>
          <span class="stat-card-sub">3.6% 占比</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card-header">
          <div>
            <div class="stat-card-title">僵尸客户</div>
          </div>
          <div class="stat-card-icon red">
            <icon-user-delete />
          </div>
        </div>
        <div class="stat-card-value">{{ stats.zombie_customers.toLocaleString() }}</div>
        <div class="stat-card-footer">
          <span class="stat-card-trend up"><icon-arrow-rise/> 3 本月新增</span>
          <span class="stat-card-sub">13.9% 占比</span>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">客户健康度趋势</span>
          <div class="chart-actions">
            <a-radio-group type="button" size="small" v-model="trendPeriod">
              <a-radio value="week">7天</a-radio>
              <a-radio value="month">30天</a-radio>
              <a-radio value="quarter">90天</a-radio>
            </a-radio-group>
          </div>
        </div>
        <div ref="trendChart" class="chart-container"></div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">客户价值分布</span>
        </div>
        <div ref="tierChart" class="chart-container-small"></div>
      </div>
    </div>

    <!-- 底部区域 -->
    <div class="bottom-grid">
      <div class="table-card">
        <div class="table-header">
          <span class="table-title"><icon-exclamation-circle style="margin-right: 6px; vertical-align: middle;"/>风险客户预警</span>
          <span class="view-all" @click="goToRiskList">查看全部<icon-right style="margin-left: 4px;"/></span>
        </div>
        <a-table
          :columns="riskColumns"
          :data="riskData"
          :pagination="false"
          size="small"
          :loading="loading"
        >
          <template #tier="{ record }">
            <span :class="['tier-badge', record.tier]">{{ record.tier }}</span>
          </template>
          <template #riskLevel="{ record }">
            <span :class="['risk-badge', record.riskLevel]">
              <icon-exclamation-circle v-if="record.riskLevel === 'high'" />
              <icon-minus-circle v-else-if="record.riskLevel === 'medium'" />
              <icon-info-circle v-else />
              {{
                record.riskLevel === "high"
                  ? "高风险"
                  : record.riskLevel === "medium"
                    ? "中风险"
                    : "低风险"
              }}
            </span>
          </template>
          <template #action="{ record }">
            <a-button type="primary" size="mini">
              <template #icon><icon-eye /></template>
              查看
            </a-button>
          </template>
        </a-table>
      </div>

      <div class="table-card">
        <div class="table-header">
          <span class="table-title"><icon-file-text style="margin-right: 6px; vertical-align: middle;"/>最近结算记录</span>
          <span class="view-all" @click="goToBillingList">查看全部<icon-right style="margin-left: 4px;"/></span>
        </div>
        <a-table
          :columns="billingColumns"
          :data="billingData"
          :pagination="false"
          size="small"
        >
          <template #status="{ record }">
            <a-tag
              :color="
                record.status === '已发送'
                  ? 'green'
                  : record.status === '待发送'
                    ? 'orange'
                    : 'red'
              "
            >
              {{ record.status }}
            </a-tag>
          </template>
          <template #action>
            <a-button type="primary" size="mini">
              <template #icon><icon-file /></template>
              详情
            </a-button>
          </template>
        </a-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import * as echarts from "echarts";
import dayjs from "dayjs";
import { healthApi } from "@/api/health";
import { billingApi } from "@/api/billing";

const router = useRouter();
const userStore = useUserStore();

const trendPeriod = ref("month");
const trendChart = ref<HTMLElement | null>(null);
const tierChart = ref<HTMLElement | null>(null);
let trendChartInstance: echarts.ECharts | null = null;
let tierChartInstance: echarts.ECharts | null = null;

// 用户信息
const userInfo = computed(() => userStore.userInfo || { real_name: "用户" });

// 当前日期
const currentDate = computed(() => {
  return dayjs().format("YYYY 年 M 月 D 日");
});

// Dashboard 数据
const dashboardData = ref<any>(null);
const loading = ref(false);

// 统计卡片数据
const stats = ref({
  total_customers: 0,
  healthy_customers: 0,
  at_risk_customers: 0,
  zombie_customers: 0,
});

// 加载 Dashboard 数据
const loadDashboardData = async () => {
  loading.value = true;
  try {
    dashboardData.value = await healthApi.getDashboard();
    stats.value = {
      total_customers: dashboardData.value.total_customers,
      healthy_customers: dashboardData.value.healthy_customers,
      at_risk_customers: dashboardData.value.at_risk_customers,
      zombie_customers: dashboardData.value.zombie_customers,
    };
    initTrendChart();
    initTierChart();
  } catch (error) {
    console.error("加载仪表盘数据失败:", error);
  } finally {
    loading.value = false;
  }
};

// 风险客户数据
const riskColumns = [
  { title: "客户名称", dataIndex: "name", width: 150 },
  {
    title: "等级",
    dataIndex: "tier",
    slotName: "tier",
    width: 60,
    align: "center",
  },
  { title: "未使用天数", dataIndex: "days", width: 100, align: "center" },
  {
    title: "风险等级",
    dataIndex: "riskLevel",
    slotName: "riskLevel",
    width: 100,
  },
  { title: "操作", slotName: "action", width: 60, align: "center" },
];

const riskData = [
  { name: "XX 科技有限公司", tier: "S", days: 14, riskLevel: "high" },
  { name: "YY 贸易集团", tier: "A", days: 10, riskLevel: "high" },
  { name: "ZZ 建设公司", tier: "B", days: 8, riskLevel: "medium" },
  { name: "AA 装饰公司", tier: "A", days: 7, riskLevel: "medium" },
  { name: "BB 房产中介", tier: "C", days: 12, riskLevel: "low" },
];

// 结算记录数据
const billingColumns = [
  { title: "月份", dataIndex: "month", width: 80 },
  { title: "客户数", dataIndex: "count", width: 80, align: "center" },
  { title: "金额", dataIndex: "amount", width: 120 },
  { title: "状态", dataIndex: "status", slotName: "status", width: 80 },
  { title: "操作", slotName: "action", width: 60, align: "center" },
];

const billingData = [
  { month: "2026-02", count: 1280, amount: "¥2,456,800", status: "已发送" },
  { month: "2026-01", count: 1275, amount: "¥2,234,600", status: "已发送" },
  { month: "2025-12", count: 1268, amount: "¥2,567,900", status: "已发送" },
  { month: "2025-11", count: 1255, amount: "¥2,123,400", status: "异常" },
  { month: "2025-10", count: 1250, amount: "¥2,345,200", status: "已发送" },
];

// 导航方法
const goToRiskList = () => router.push("/health/risks");
const goToBillingList = () => router.push("/billing/list");

// 初始化趋势图
const initTrendChart = () => {
  if (!trendChart.value || !dashboardData.value) return;

  trendChartInstance = echarts.init(trendChart.value);
  const option = {
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
    },
    legend: {
      data: ["健康度评分"],
      bottom: 0,
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "15%",
      top: "10%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: dashboardData.value.health_trend.map(
        (item: { date: string; score: number }) => {
          return dayjs(item.date).format("MM/DD");
        },
      ),
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 100,
      splitLine: {
        lineStyle: {
          color: 'rgba(0, 0, 0, 0.06)',
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: "健康度评分",
        type: "line",
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        data: dashboardData.value.health_trend.map(
          (item: { date: string; score: number }) => item.score,
        ),
        itemStyle: {
          color: '#165DFF'
        },
        lineStyle: {
          width: 3,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#165DFF' },
            { offset: 1, color: '#4080FF' }
          ])
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(22, 93, 255, 0.2)' },
            { offset: 1, color: 'rgba(22, 93, 255, 0.02)' }
          ])
        }
      },
    ],
  };
  trendChartInstance.setOption(option);
};

// 初始化价值分布图
const initTierChart = () => {
  if (!tierChart.value || !dashboardData.value) return;

  tierChartInstance = echarts.init(tierChart.value);
  const option = {
    tooltip: {
      trigger: "item",
      formatter: "{b}: {c} ({d}%)",
    },
    legend: {
      orient: "vertical",
      right: "5%",
      top: "center",
      data: ["A 级", "B 级", "C 级", "D 级"],
    },
    series: [
      {
        name: "客户价值分布",
        type: "pie",
        radius: ["45%", "75%"],
        center: ["35%", "50%"],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: "#fff",
          borderWidth: 3,
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.1)'
        },
        label: {
          show: false,
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: "bold",
          },
          itemStyle: {
            shadowBlur: 20,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.2)'
          }
        },
        data: dashboardData.value.value_distribution.map((item: any) => ({
          value: item.count,
          name: item.tier + "级",
          itemStyle: {
            color:
              item.tier === "A"
                ? "#165DFF"  // 极致蓝
                : item.tier === "B"
                  ? "#00B42A"  // 成功绿
                  : item.tier === "C"
                    ? "#86909C"  // 中性灰
                    : "#C9CDD4", // 浅灰
          },
        })),
      },
    ],
  };
  tierChartInstance.setOption(option);
};

// 窗口大小调整
const handleResize = () => {
  trendChartInstance?.resize();
  tierChartInstance?.resize();
};

onMounted(() => {
  loadDashboardData();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
  trendChartInstance?.dispose();
  tierChartInstance?.dispose();
});
</script>

<style scoped lang="scss">
.dashboard {
  padding: 24px;
}

/* 欢迎横幅 */
.welcome-banner {
  background: var(--color-primary-light-1);
  border-radius: var(--border-radius-medium);
  padding: 32px;
  color: var(--color-primary);
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-text h2 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.welcome-text p {
  font-size: 14px;
  opacity: 0.8;
}

.welcome-stats {
  display: flex;
  gap: 32px;
}

.welcome-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.welcome-stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 4px;
}

.welcome-stat-label {
  font-size: 13px;
  opacity: 0.8;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--color-bg-1);
  border-radius: var(--border-radius-medium);
  padding: 24px;
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(22, 93, 255, 0.12);
    border-color: var(--color-primary-light-2);

    .stat-card-icon {
      transform: scale(1.1);
    }
  }
}

.stat-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.stat-card-title {
  font-size: 14px;
  color: var(--color-text-3);
}

.stat-card-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--border-radius-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition: transform 0.2s ease;
}

.stat-card-icon.blue {
  background: var(--color-primary-light-1);
  color: var(--color-primary);
}

.stat-card-icon.green {
  background: var(--color-success-light-1);
  color: var(--color-success);
}

.stat-card-icon.orange {
  background: var(--color-warning-light-1);
  color: var(--color-warning);
}

.stat-card-icon.red {
  background: var(--color-danger-light-1);
  color: var(--color-danger);
}

.stat-card-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-1);
  margin-bottom: 8px;
}

.stat-card-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.stat-card-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.stat-card-trend.up {
  background: var(--color-success-light-1);
  color: var(--color-success);
}

.stat-card-trend.down {
  background: var(--color-danger-light-1);
  color: var(--color-danger);
}

.stat-card-sub {
  color: var(--color-text-3);
}

/* 图表区域 */
.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: var(--color-bg-1);
  border-radius: var(--border-radius-medium);
  padding: 24px;
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    border-color: var(--color-primary-light-2);
  }
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
  color: var(--color-text-1);
}

.chart-actions {
  display: flex;
  gap: 8px;
}

.chart-container {
  height: 300px;
}

.chart-container-small {
  height: 300px;
}

/* 底部区域 */
.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.table-card {
  background: var(--color-bg-1);
  border-radius: var(--border-radius-medium);
  padding: 24px;
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    border-color: var(--color-primary-light-2);
  }
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-1);
}

.view-all {
  font-size: 14px;
  color: var(--color-primary);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;

  &:hover {
    color: var(--color-primary-hover);
    transform: translateX(4px);
  }
}

/* 风险客户标签 */
.risk-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.risk-badge.high {
  background: var(--color-danger-light-1);
  color: var(--color-danger);
}

.risk-badge.medium {
  background: var(--color-warning-light-1);
  color: var(--color-warning);
}

.risk-badge.low {
  background: var(--color-warning-light-2);
  color: var(--color-warning);
}

/* 价值等级标签 */
.tier-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 700;
}

.tier-badge.S {
  background: var(--color-warning-light-1);
  color: var(--color-warning);
}

.tier-badge.A {
  background: var(--color-primary-light-1);
  color: var(--color-primary);
}

.tier-badge.B {
  background: var(--color-success-light-1);
  color: var(--color-success);
}

.tier-badge.C {
  background: var(--color-text-3);
  color: var(--color-text-1);
}

.tier-badge.D {
  background: var(--color-fill-3);
  color: var(--color-text-2);
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .welcome-stats {
    flex-wrap: wrap;
    gap: 20px;
  }
}
</style>
