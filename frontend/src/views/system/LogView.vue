<template>
  <div class="log-view">
    <Card>
      <template #title>
        <Space>
          <span>操作日志</span>
        </Space>
      </template>

      <Space class="filter-bar" direction="vertical" :size="12">
        <Space :size="16">
          <Input
            v-model="filters.user_id"
            placeholder="用户 ID"
            allow-clear
            style="width: 120px"
            @press-enter="handleSearch"
          />
          <Input
            v-model="filters.operation_type"
            placeholder="操作类型"
            allow-clear
            style="width: 150px"
            @press-enter="handleSearch"
          />
          <Input
            v-model="filters.target_type"
            placeholder="目标类型"
            allow-clear
            style="width: 120px"
            @press-enter="handleSearch"
          />
          <DatePicker
            v-model="filters.dateRange"
            :mode="'date'"
            range
            placeholder="操作时间"
            style="width: 240px"
            @change="handleSearch"
          />
          <Button type="primary" @click="handleSearch">
            <IconSearch />
            搜索
          </Button>
          <Button @click="handleReset">
            <IconRefresh />
            重置
          </Button>
        </Space>
      </Space>

      <Table
        :columns="columns"
        :data="logs"
        :loading="loading"
        :pagination="pagination"
        @page-change="onPageChange"
      >
        <template #operation_type="{ record }">
          <Tag :color="getOperationTypeColor(record.operation_type)">
            {{ getOperationTypeLabel(record.operation_type) }}
          </Tag>
        </template>
        <template #target="{ record }">
          <span v-if="record.target_type && record.target_id">
            {{ getTargetTypeLabel(record.target_type) }} #{{ record.target_id }}
          </span>
          <span v-else>-</span>
        </template>
        <template #ip_address="{ record }">
          <a-typography-text v-if="record.ip_address" :ellipsis="true">
            {{ record.ip_address }}
          </a-typography-text>
          <span v-else>-</span>
        </template>
        <template #created_at="{ record }">
          {{ formatDateTime(record.created_at) }}
        </template>
        <template #action="{ record }">
          <Space>
            <Button
              type="text"
              size="small"
              @click="handleViewDetail(record)"
            >
              详情
            </Button>
          </Space>
        </template>
      </Table>
    </Card>

    <Modal
      v-model:visible="detailVisible"
      title="操作日志详情"
      width="720px"
      :footer="false"
    >
      <a-descriptions
        v-if="currentLog"
        :column="1"
        bordered
      >
        <a-descriptions-item label="日志 ID">
          {{ currentLog.id }}
        </a-descriptions-item>
        <a-descriptions-item label="用户 ID">
          {{ currentLog.user_id }}
        </a-descriptions-item>
        <a-descriptions-item label="操作类型">
          <Tag :color="getOperationTypeColor(currentLog.operation_type)">
            {{ getOperationTypeLabel(currentLog.operation_type) }}
          </Tag>
        </a-descriptions-item>
        <a-descriptions-item label="目标类型">
          {{ currentLog.target_type || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="目标 ID">
          {{ currentLog.target_id || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="IP 地址">
          {{ currentLog.ip_address || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="操作时间">
          {{ formatDateTime(currentLog.created_at) }}
        </a-descriptions-item>
        <a-descriptions-item label="旧值">
          <pre class="json-view">{{ JSON.stringify(currentLog.old_value, null, 2) || '-' }}</pre>
        </a-descriptions-item>
        <a-descriptions-item label="新值">
          <pre class="json-view">{{ JSON.stringify(currentLog.new_value, null, 2) || '-' }}</pre>
        </a-descriptions-item>
      </a-descriptions>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  IconSearch,
  IconRefresh,
  IconUser,
  IconSettings,
  IconDelete,
  IconEdit,
  IconPlus,
  IconCheckCircle,
  IconCloseCircle
} from '@arco-design/web-vue/es/icon'
import { Message } from '@arco-design/web-vue'
import { logApi, type OperationLog } from '@/api/log'

const loading = ref(false)
const logs = ref<OperationLog[]>([])
const detailVisible = ref(false)
const currentLog = ref<OperationLog | null>(null)

const filters = reactive({
  user_id: '',
  operation_type: '',
  target_type: '',
  dateRange: []
})

const pagination = reactive({
  total: 0,
  current: 1,
  pageSize: 20
})

const columns = [
  { title: '日志 ID', dataIndex: 'id', width: 80 },
  { title: '用户 ID', dataIndex: 'user_id', width: 100 },
  {
    title: '操作类型',
    slotName: 'operation_type',
    width: 120
  },
  {
    title: '目标',
    slotName: 'target',
    width: 150
  },
  {
    title: 'IP 地址',
    slotName: 'ip_address',
    width: 140
  },
  {
    title: '操作时间',
    slotName: 'created_at',
    width: 180,
    sortable: 'desc'
  },
  {
    title: '操作',
    slotName: 'action',
    width: 80,
    fixed: 'right'
  }
]

const operationTypeLabels: Record<string, string> = {
  CREATE: '创建',
  UPDATE: '更新',
  DELETE: '删除',
  VIEW: '查看',
  EXPORT: '导出',
  IMPORT: '导入',
  LOGIN: '登录',
  LOGOUT: '登出',
  ASSIGN_ROLE: '分配角色',
  RESET_PASSWORD: '重置密码'
}

const operationTypeColors: Record<string, string> = {
  CREATE: 'green',
  UPDATE: 'blue',
  DELETE: 'red',
  VIEW: 'gray',
  EXPORT: 'cyan',
  IMPORT: 'purple',
  LOGIN: 'orange',
  LOGOUT: 'gray',
  ASSIGN_ROLE: 'pink',
  RESET_PASSWORD: 'orange'
}

const targetTypeLabels: Record<string, string> = {
  user: '用户',
  customer: '客户',
  role: '角色',
  permission: '权限',
  price_config: '价格配置',
  price_band: '价格区间',
  pricing_strategy: '定价策略',
  billing: '结算单',
  transfer: '转移'
}

const getOperationTypeLabel = (type: string) => {
  return operationTypeLabels[type] || type
}

const getOperationTypeColor = (type: string) => {
  return operationTypeColors[type] || 'gray'
}

const getTargetTypeLabel = (type: string) => {
  return targetTypeLabels[type] || type
}

const formatDateTime = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const loadLogs = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.current,
      size: pagination.pageSize
    }

    if (filters.user_id) {
      params.user_id = filters.user_id
    }
    if (filters.operation_type) {
      params.operation_type = filters.operation_type
    }
    if (filters.target_type) {
      params.target_type = filters.target_type
    }
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_time = filters.dateRange[0]
      params.end_time = filters.dateRange[1]
    }

    const response = await logApi.list(params)
    logs.value = response.data?.items || response.items || []
    pagination.total = response.data?.total || response.total || 0
  } catch (error) {
    Message.error('加载日志列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadLogs()
}

const handleReset = () => {
  filters.user_id = ''
  filters.operation_type = ''
  filters.target_type = ''
  filters.dateRange = []
  pagination.current = 1
  loadLogs()
}

const onPageChange = (page: number) => {
  pagination.current = page
  loadLogs()
}

const handleViewDetail = (record: OperationLog) => {
  currentLog.value = record
  detailVisible.value = true
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped lang="scss">
.log-view {
  padding: 24px;

  .filter-bar {
    margin-bottom: 16px;
  }
}

.json-view {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
