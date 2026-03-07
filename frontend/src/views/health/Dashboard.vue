<!-- 健康度仪表盘 -->
<template>
  <div class="health-dashboard">
    <a-spin :loading="loading" tip="加载中...">
      <!-- 欢迎横幅 -->
      <div class="welcome-banner">
        <div class="welcome-content">
          <h2 class="welcome-title">客户健康度监控</h2>
          <p class="welcome-subtitle">实时监控客户健康状态，及时发现流失风险</p>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <StatCard
          :icon="IconUserGroup"
          label="客户总数"
          :value="stats.total_customers"
          color="blue"
        />
        <StatCard
          :icon="IconCheckCircle"
          label="健康客户"
          :value="stats.healthy_customers"
          color="green"
        />
        <StatCard
          :icon="IconExclamationCircle"
          label="风险客户"
          :value="stats.at_risk_customers"
          color="orange"
        />
        <StatCard
          :icon="IconCloseCircle"
          label="僵尸客户"
          :value="stats.zombie_customers"
          color="red"
        />
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
        <Table
          :columns="riskColumns"
          :data="riskData"
          :pagination="false"
          size="small"
        />
      </div>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useRouter } from "vue-router";
import { Message } from "@arco-design/web-vue";
import * as echarts from "echarts";
import type { HealthDashboard, RiskCustomer } from "@/api/health";
import { healthApi } from "@/api/health";
import StatCard from "@/components/StatCard.vue";
import {
  IconUserGroup,
  IconCheckCircle,
  IconExclamationCircle,
  IconCloseCircle,
} from "@arco-design/web-vue/es/icon";

const router = useRouter();

const loading = ref(false);
const trendPeriod = ref<"week" | "month" | "quarter">("month");
const trendChart = ref<HTMLElement | null>(null);
const distributionChart = ref<HTMLElement | null>(null);
let trendChartInstance: echarts.ECharts | null = null;
let distributionChartInstance: echarts.ECharts | null = null;

const stats = ref<HealthDashboard>({
  total_customers: 0,
  healthy_customers: 0,
  at_risk_customers: 0,
  zombie_customers: 0,
  health_trend: [],
  value_distribution: [],
});

interface RiskColumn {
  title: string;
  dataIndex: string;
  width: number;
  ellipsis?: boolean;
  align?: "left" | "center" | "right";
  slotName?: string;
}

const riskColumns: RiskColumn[] = [
  { title: "客户名称", dataIndex: "name", width: 200, ellipsis: true },
  { title: "等级", dataIndex: "tier_level", width: 80 },
  {
    title: "未使用天数",
    dataIndex: "days_inactive",
    width: 100,
    align: "center",
  },
  { title: "健康评分", dataIndex: "health_score", width: 100, align: "center" },
  { title: "风险等级", dataIndex: "risk_level", width: 100, align: "center" },
];

const riskData = ref<RiskCustomer[]>([]);

const loadDashboardData = async () => {
  loading.value = true;
  try {
    const data = await healthApi.getDashboard();
    stats.value = {
      total_customers: data.total_customers,
      healthy_customers: data.healthy_customers,
      at_risk_customers: data.at_risk_customers,
      zombie_customers: data.zombie_customers,
      health_trend: data.health_trend,
      value_distribution: data.value_distribution,
    };

    riskData.value = data.risk_customers?.slice(0, 5) || [];

    initTrendChart(data.health_trend);
    initDistributionChart(data.value_distribution);
  } catch (error) {
    console.error("加载健康度数据失败:", error);
    Message.error("加载健康度数据失败，请稍后重试");
  } finally {
    loading.value = false;
  }
};

const initTrendChart = (trendData: any[]) => {
  if (!trendChart.value) return;

  trendChartInstance = echarts.init(trendChart.value);
  const option = {
    tooltip: { trigger: "axis" },
    legend: { data: ["健康度评分"], bottom: 0 },
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
      data: trendData?.map((item: any) => item.date?.slice(5, 10) || "") || [],
    },
    yAxis: { type: "value", min: 0, max: 100 },
    series: [
      {
        name: "健康度评分",
        type: "line",
        smooth: true,
        data: trendData?.map((item: any) => item.score) || [],
        areaStyle: { opacity: 0.1 },
        itemStyle: { color: "#00B42A" },
      },
    ],
  };
  trendChartInstance.setOption(option);
};

const initDistributionChart = (distribution: any[]) => {
  if (!distributionChart.value) return;

  distributionChartInstance = echarts.init(distributionChart.value);
  const option = {
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    legend: { orient: "vertical", right: "5%", top: "center" },
    series: [
      {
        name: "健康度分布",
        type: "pie",
        radius: ["45%", "75%"],
        center: ["35%", "50%"],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 8, borderColor: "#fff", borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 16, fontWeight: "bold" } },
        data:
          distribution?.map((item: any) => ({
            value: item.count,
            name: item.label,
            itemStyle: {
              color:
                item.status === "healthy"
                  ? "#00B42A"
                  : item.status === "risk"
                    ? "#FF7D00"
                    : "#F53F3F",
            },
          })) || [],
      },
    ],
  };
  distributionChartInstance.setOption(option);
};

const handleResize = () => {
  trendChartInstance?.resize();
  distributionChartInstance?.resize();
};

watch(trendPeriod, () => {
  loadDashboardData();
});

onMounted(() => {
  loadDashboardData();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
  trendChartInstance?.dispose();
  distributionChartInstance?.dispose();
});
</script>

<style scoped lang="scss">
.health-dashboard {
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

.welcome-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.welcome-subtitle {
  font-size: 14px;
  opacity: 0.8;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

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

.chart-container {
  height: 300px;
}

.chart-container-small {
  height: 300px;
}

.alert-list-card {
  background: var(--color-bg-1);
  border-radius: var(--border-radius-medium);
  padding: 24px;
  border: 1px solid var(--color-border);
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
  color: var(--color-text-1);
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
