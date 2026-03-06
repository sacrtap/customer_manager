<template>
  <div class="dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-content">
        <h2 class="welcome-title">👋 欢迎回来，{{ userInfo.real_name }}</h2>
        <p class="welcome-subtitle">
          今天是 {{ currentDate }}，以下是您的运营概览
        </p>
        <div class="welcome-stats">
          <div class="welcome-stat">
            <span class="welcome-stat-value">48</span>
            <span class="welcome-stat-label">待处理预警</span>
          </div>
          <div class="welcome-stat">
            <span class="welcome-stat-value">12</span>
            <span class="welcome-stat-label">本月已唤醒</span>
          </div>
          <div class="welcome-stat">
            <span class="welcome-stat-value">¥2.4M</span>
            <span class="welcome-stat-label">本月结算金额</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-icon blue">
            <icon-user-group />
          </div>
          <div class="stat-trend up">
            <icon-arrow-up />
            <span>+2.5%</span>
          </div>
        </div>
        <div class="stat-value">
          {{ stats.total_customers.toLocaleString() }}
        </div>
        <div class="stat-label">客户总数</div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-icon green">
            <icon-check-circle />
          </div>
          <div class="stat-trend up">
            <icon-arrow-up />
            <span>+5.2%</span>
          </div>
        </div>
        <div class="stat-value">
          {{ stats.healthy_customers.toLocaleString() }}
        </div>
        <div class="stat-label">活跃客户</div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-icon orange">
            <icon-exclamation-circle />
          </div>
          <div class="stat-trend down">
            <icon-arrow-down />
            <span>-1.2%</span>
          </div>
        </div>
        <div class="stat-value">
          {{ stats.at_risk_customers.toLocaleString() }}
        </div>
        <div class="stat-label">风险客户</div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-icon red">
            <icon-close-circle />
          </div>
          <div class="stat-trend down">
            <icon-arrow-down />
            <span>-3.8%</span>
          </div>
        </div>
        <div class="stat-value">
          {{ stats.zombie_customers.toLocaleString() }}
        </div>
        <div class="stat-label">僵尸客户</div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">客户健康度趋势</span>
          <div class="chart-actions">
            <a-radio-group type="button" size="small" v-model="trendPeriod">
              <a-radio value="week">本周</a-radio>
              <a-radio value="month">本月</a-radio>
              <a-radio value="quarter">本季</a-radio>
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
          <span class="table-title">⚠️ 风险客户预警</span>
          <span class="view-all" @click="goToRiskList">查看全部</span>
        </div>
        <a-table
          :columns="riskColumns"
          :data="riskData"
          :pagination="false"
          size="small"
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
          <template #action>
            <a-button type="text" size="mini">查看</a-button>
          </template>
        </a-table>
      </div>

      <div class="table-card">
        <div class="table-header">
          <span class="table-title">📋 最近结算记录</span>
          <span class="view-all" @click="goToBillingList">查看全部</span>
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
            <a-button type="text" size="mini">详情</a-button>
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
    },
    series: [
      {
        name: "健康度评分",
        type: "line",
        smooth: true,
        data: dashboardData.value.health_trend.map(
          (item: { date: string; score: number }) => item.score,
        ),
        areaStyle: { opacity: 0.1 },
        itemStyle: { color: "#00b42a" },
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
          borderRadius: 8,
          borderColor: "#fff",
          borderWidth: 2,
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
        },
        data: dashboardData.value.value_distribution.map((item: any) => ({
          value: item.count,
          name: item.tier + "级",
          itemStyle: {
            color:
              item.tier === "A"
                ? "#165dff"
                : item.tier === "B"
                  ? "#00b42a"
                  : item.tier === "C"
                    ? "#86909c"
                    : "#c9cdd4",
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
@import "@/styles/variables.scss";

.dashboard {
  padding: $spacing-md;
}

/* 欢迎横幅 */
.welcome-banner {
  @include chart-card;
  background: $primary-gradient;
  border-radius: $border-radius-md;
  padding: $spacing-lg;
  color: white;
  margin-bottom: $spacing-md;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-banner::before {
  content: "";
  position: absolute;
  top: -50%;
  right: -20%;
  width: 60%;
  height: 200%;
  background: radial-gradient(
    circle,
    rgba(255, 255, 255, 0.1) 0%,
    transparent 70%
  );
  transform: rotate(-15deg);
}

.welcome-content {
  position: relative;
  z-index: 1;
}

.welcome-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.welcome-subtitle {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 20px;
}

.welcome-stats {
  display: flex;
  gap: 40px;
}

.welcome-stat {
  display: flex;
  flex-direction: column;
}

.welcome-stat-value {
  font-size: 28px;
  font-weight: 700;
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
  margin-bottom: $spacing-md;
}

.stat-card {
  @include stat-card;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-sm;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: $border-radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-size-lg;
}

.stat-icon.blue {
  background: $blue-gradient;
  color: $primary-color;
}

.stat-icon.green {
  background: $success-gradient;
  color: $success-color;
}

.stat-icon.orange {
  background: $warning-gradient;
  color: $warning-color;
}

.stat-icon.red {
  background: $danger-gradient;
  color: $danger-color;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
}

.stat-trend.up {
  color: #00b42a;
}

.stat-trend.down {
  color: #f53f3f;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1d2129;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #86909c;
}

/* 图表区域 */
.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: $spacing-md;
}

.chart-card {
  @include chart-card;
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
  color: #1d2129;
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
  @include chart-card;
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
  color: #1d2129;
}

.view-all {
  font-size: 14px;
  color: #165dff;
  cursor: pointer;

  &:hover {
    color: #4080ff;
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
  background: rgba(245, 63, 63, 0.1);
  color: #f53f3f;
}

.risk-badge.medium {
  background: rgba(255, 125, 0, 0.1);
  color: #ff7d00;
}

.risk-badge.low {
  background: rgba(255, 202, 43, 0.1);
  color: #f7ba1e;
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
  background: linear-gradient(135deg, #ff7d00 0%, #ff9a2e 100%);
  color: white;
}

.tier-badge.A {
  background: linear-gradient(135deg, #165dff 0%, #4080ff 100%);
  color: white;
}

.tier-badge.B {
  background: linear-gradient(135deg, #00b42a 0%, #23c343 100%);
  color: white;
}

.tier-badge.C {
  background: linear-gradient(135deg, #86909c 0%, #a5abb3 100%);
  color: white;
}

.tier-badge.D {
  background: linear-gradient(135deg, #c9cdd4 0%, #e5e6eb 100%);
  color: #4e5969;
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
