<!-- 风险客户列表 -->
<template>
  <div class="risk-list">
    <Card>
      <template #title>
        <Space>
          <span>风险客户列表</span>
          <Tag color="orange">
            <icon-exclamation-circle />
            {{ total }} 条风险
          </Tag>
        </Space>
      </template>

      <Space style="margin-bottom: 16px" :size="12">
        <Input v-model="keyword" placeholder="搜索客户名称" allow-clear style="width: 240px" @press-enter="loadData" />
        <Select v-model="riskLevel" placeholder="风险等级" allow-clear style="width: 120px" @change="loadData">
          <Option value="high">高风险</Option>
          <Option value="medium">中风险</Option>
          <Option value="low">低风险</Option>
        </Select>
        <Button type="primary" @click="loadData">
          <icon-search />
          搜索
        </Button>
        <Button @click="handleReset">
          <icon-refresh />
          重置
        </Button>
      </Space>

      <Table :columns="columns" :data="data" :loading="loading" :pagination="pagination" @page-change="onPageChange">
        <template #tier_level="{ record }">
          <Tag :color="getTierLevelColor(record.tier_level)" size="medium">
            {{ record.tier_level }}级
          </Tag>
        </template>

        <template #risk_level="{ record }">
          <Tag :color="getRiskLevelColor(record.risk_level)">
            {{ getRiskLevelText(record.risk_level) }}
          </Tag>
        </template>

        <template #health_score="{ record }">
          <Progress :percent="record.health_score" :status="getHealthStatus(record.health_score)" show-text style="width: 150px" />
        </template>

        <template #action="{ record }">
          <Space>
            <Button type="text" size="small" @click="router.push(`/customers/${record.id}`)">查看</Button>
            <Button type="text" size="small" @click="handleContact(record)">联系</Button>
          </Space>
        </template>
      </Table>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { healthApi } from '@/api/health'

const router = useRouter()

const loading = ref(false)
const data = ref<any[]>([])
const total = ref(0)

const keyword = ref('')
const riskLevel = ref('')

const pagination = reactive({
  total: 0,
  current: 1,
  pageSize: 20
})

const columns = [
  { title: '客户名称', dataIndex: 'name', width: 200, ellipsis: true },
  { title: '客户编码', dataIndex: 'code', width: 120 },
  { title: '等级', dataIndex: 'tier_level', slotName: 'tier_level', width: 80 },
  { title: '销售人员', dataIndex: 'sales_rep_name', width: 120 },
  { title: '未使用天数', dataIndex: 'days_inactive', width: 100, align: 'center' },
  { title: '健康评分', dataIndex: 'health_score', slotName: 'health_score', width: 180 },
  { title: '风险等级', dataIndex: 'risk_level', slotName: 'risk_level', width: 100 },
  { title: '操作', slotName: 'action', width: 150, fixed: 'right' }
]

const getTierLevelColor = (tier: string): string => {
  const colors: Record<string, string> = { S: 'red', A: 'orange', B: 'gold', C: 'cyan', D: 'gray' }
  return colors[tier] || 'gray'
}

const getRiskLevelColor = (level: string): string => {
  const colors: Record<string, string> = { high: 'red', medium: 'orange', low: 'yellow' }
  return colors[level] || 'gray'
}

const getRiskLevelText = (level: string): string => {
  const texts: Record<string, string> = { high: '高风险', medium: '中风险', low: '低风险' }
  return texts[level] || level
}

const getHealthStatus = (score: number): 'success' | 'warning' | 'error' | 'normal' => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'normal'
  if (score >= 40) return 'warning'
  return 'error'
}

const loadData = async () => {
  loading.value = true
  try {
    const response = await healthApi.getRisks({
      page: pagination.current,
      size: pagination.pageSize,
      keyword: keyword.value || undefined,
      risk_level: riskLevel.value || undefined
    })
    data.value = response.items || []
    pagination.total = response.total || 0
    total.value = pagination.total
  } catch (error) {
    Message.error('加载风险客户列表失败')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  keyword.value = ''
  riskLevel.value = ''
  pagination.current = 1
  loadData()
}

const onPageChange = (page: number) => {
  pagination.current = page
  loadData()
}

const handleContact = (record: any) => {
  Message.info(`联系客户：${record.name}`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.risk-list {
  padding: 24px;
}
</style>
