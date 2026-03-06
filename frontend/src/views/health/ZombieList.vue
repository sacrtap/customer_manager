<!-- 僵尸客户列表 -->
<template>
  <div class="zombie-list">
    <Card>
      <template #title>
        <Space>
          <span>僵尸客户列表</span>
          <Tag color="red">
            <icon-close-circle />
            {{ total }} 条僵尸
          </Tag>
        </Space>
      </template>

      <Space style="margin-bottom: 16px" :size="12">
        <Input v-model="keyword" placeholder="搜索客户名称" allow-clear style="width: 240px" @press-enter="loadData" />
        <Select v-model="tierLevel" placeholder="价值等级" allow-clear style="width: 120px" @change="loadData">
          <Option value="S">S 级</Option>
          <Option value="A">A 级</Option>
          <Option value="B">B 级</Option>
          <Option value="C">C 级</Option>
          <Option value="D">D 级</Option>
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

        <template #days_inactive="{ record }">
          <Tag :color="getDaysColor(record.days_inactive)">
            {{ record.days_inactive }} 天
          </Tag>
        </template>

        <template #action="{ record }">
          <Space>
            <Button type="text" size="small" @click="router.push(`/customers/${record.id}`)">查看</Button>
            <Button type="text" size="small" @click="handleWakeUp(record)">唤醒</Button>
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
import type { ZombieCustomer } from '@/api/health'
import { healthApi } from '@/api/health'

const router = useRouter()

const loading = ref(false)
const data = ref<ZombieCustomer[]>([])
const total = ref(0)

const keyword = ref('')
const tierLevel = ref('')

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
  { title: '未使用天数', dataIndex: 'days_inactive', slotName: 'days_inactive', width: 120, align: 'center' },
  { title: '最后活跃时间', dataIndex: 'last_active_at', width: 180 },
  { title: '操作', slotName: 'action', width: 150, fixed: 'right' }
]

const getTierLevelColor = (tier: string): string => {
  const colors: Record<string, string> = { S: 'red', A: 'orange', B: 'gold', C: 'cyan', D: 'gray' }
  return colors[tier] || 'gray'
}

const getDaysColor = (days: number): string => {
  if (days >= 90) return 'red'
  if (days >= 60) return 'orange'
  return 'yellow'
}

const loadData = async () => {
  loading.value = true
  try {
    const response = await healthApi.getZombies({
      page: pagination.current,
      size: pagination.pageSize,
      keyword: keyword.value || undefined,
      tier_level: tierLevel.value || undefined
    })
    data.value = response.items || []
    pagination.total = response.total || 0
    total.value = pagination.total
  } catch (error) {
    Message.error('加载僵尸客户列表失败')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  keyword.value = ''
  tierLevel.value = ''
  pagination.current = 1
  loadData()
}

const onPageChange = (page: number) => {
  pagination.current = page
  loadData()
}

const handleWakeUp = (record: any) => {
  Message.info(`发起唤醒流程：${record.name}`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.zombie-list {
  padding: 24px;
}
</style>
