<!-- frontend/src/views/customer/CustomerList.vue -->
<template>
  <div class="customer-list">
    <Card class="customer-card">
      <template #title>
        <div class="card-header">
          <span class="card-title">客户列表</span>
          <div class="card-actions">
            <Button type="primary" @click="handleCreate">
              <template #icon><icon-plus /></template>
              新增客户
            </Button>
            <Button @click="handleImport">
              <template #icon><icon-upload /></template>
              批量导入
            </Button>
            <Button @click="handleExport">
              <template #icon><icon-download /></template>
              批量导出
            </Button>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <SearchBar
        v-model="searchForm"
        :fields="searchFields"
        @search="handleSearch"
        @reset="handleReset"
      />

      <!-- 客户表格 -->
      <Table
        :columns="columns"
        :data="customers"
        :loading="loading"
        :pagination="pagination"
        :row-selection="{ type: 'checkbox', showCheckedAll: true }"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
      >
        <template #tier_level="{ record }">
          <Tag :color="getTierLevelColor(record.tier_level)" size="medium">
            {{ record.tier_level }}级
          </Tag>
        </template>

        <template #status="{ record }">
          <Tag :color="getStatusColor(record.status)" size="medium">
            {{ getStatusText(record.status) }}
          </Tag>
        </template>

        <template #annual_consumption="{ record }">
          <span class="amount">¥{{ formatAmount(record.annual_consumption) }}</span>
        </template>

        <template #action="{ record }">
          <Space>
            <Button
              type="text"
              size="small"
              @click="handleView(record)"
            >
              查看
            </Button>
            <Button
              type="text"
              size="small"
              @click="handleEdit(record)"
            >
              编辑
            </Button>
            <Button
              type="text"
              size="small"
              status="danger"
              @click="handleDelete(record)"
            >
              删除
            </Button>
          </Space>
        </template>
      </Table>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Message, Modal } from '@arco-design/web-vue'
import { customerApi, type Customer } from '@/api/customer'
import SearchBar from '@/components/SearchBar.vue'

const router = useRouter()

const loading = ref(false)
const customers = ref<Customer[]>([])

const searchForm = reactive({
  keyword: '',
  sales_rep_ids: [] as number[],
  industries: [] as string[],
  status: [] as string[],
  tier_levels: [] as string[],
  annual_consumption_min: undefined as number | undefined,
  annual_consumption_max: undefined as number | undefined
})

const search = reactive({
  page: 1,
  size: 20,
  keyword: '',
  sales_rep_ids: [] as number[],
  industries: [] as string[],
  status: [] as string[],
  tier_levels: [] as string[],
  annual_consumption_min: undefined as number | undefined,
  annual_consumption_max: undefined as number | undefined
})

const pagination = reactive({
  total: 0,
  current: 1,
  pageSize: 20,
  showTotal: true,
  showJumper: true
})

const searchFields = [
  { label: '关键词', field: 'keyword', type: 'input', placeholder: '客户名称/编码/联系人' },
  { label: '客户状态', field: 'status', type: 'select', options: [
    { label: '活跃', value: 'active' },
    { label: '风险', value: 'risk' },
    { label: '僵尸', value: 'zombie' },
    { label: '停用', value: 'inactive' }
  ]},
  { label: '价值等级', field: 'tier_levels', type: 'select', options: [
    { label: 'S 级', value: 'S' },
    { label: 'A 级', value: 'A' },
    { label: 'B 级', value: 'B' },
    { label: 'C 级', value: 'C' },
    { label: 'D 级', value: 'D' }
  ]},
  { label: '年消费金额', field: 'annual_consumption', type: 'range' }
]

const columns = [
  { title: '客户名称', dataIndex: 'name', width: 200, ellipsis: true, tooltip: true },
  { title: '客户编码', dataIndex: 'code', width: 150, ellipsis: true, tooltip: true },
  { title: '价值等级', dataIndex: 'tier_level', width: 100, slotName: 'tier_level' },
  { title: '年消费金额', dataIndex: 'annual_consumption', width: 130, slotName: 'annual_consumption', sortable: true },
  { title: '状态', dataIndex: 'status', width: 100, slotName: 'status' },
  { title: '联系人', dataIndex: 'contact_person', width: 120, ellipsis: true, tooltip: true },
  { title: '联系电话', dataIndex: 'contact_phone', width: 150, ellipsis: true, tooltip: true },
  {
    title: '操作',
    slotName: 'action',
    width: 180,
    fixed: 'right'
  }
]

const getTierLevelColor = (tierLevel: string): string => {
  const colors: Record<string, string> = {
    S: 'red',
    A: 'orange',
    B: 'gold',
    C: 'cyan',
    D: 'gray'
  }
  return colors[tierLevel] || 'gray'
}

const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    active: 'green',
    risk: 'orange',
    zombie: 'red',
    inactive: 'gray'
  }
  return colors[status] || 'gray'
}

const getStatusText = (status: string): string => {
  const texts: Record<string, string> = {
    active: '活跃',
    risk: '风险',
    zombie: '僵尸',
    inactive: '停用'
  }
  return texts[status] || status
}

const formatAmount = (amount: number): string => {
  return (amount || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const loadCustomers = async () => {
  loading.value = true
  try {
    const response = await customerApi.list(search)
    customers.value = response.items
    pagination.total = response.total
    pagination.current = response.page
  } catch (error) {
    Message.error('加载客户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  search.page = 1
  Object.assign(search, { ...searchForm })
  loadCustomers()
}

const handleReset = () => {
  Object.assign(searchForm, {
    keyword: '',
    sales_rep_ids: [],
    industries: [],
    status: [],
    tier_levels: [],
    annual_consumption_min: undefined,
    annual_consumption_max: undefined
  })
  Object.assign(search, {
    page: 1,
    size: 20,
    keyword: '',
    sales_rep_ids: [],
    industries: [],
    status: [],
    tier_levels: [],
    annual_consumption_min: undefined,
    annual_consumption_max: undefined
  })
  loadCustomers()
}

const handleView = (record: Customer) => {
  router.push(`/customers/${record.id}`)
}

const handleEdit = (record: Customer) => {
  router.push(`/customers/${record.id}?mode=edit`)
}

const handleDelete = (record: Customer) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除客户"${record.name}"吗？此操作不可恢复。`,
    onOk: async () => {
      try {
        await customerApi.delete(record.id)
        Message.success('删除成功')
        loadCustomers()
      } catch (error) {
        Message.error('删除失败')
      }
    }
  })
}

const handleCreate = () => {
  router.push('/customers/create')
}

const handleImport = () => {
  router.push('/customers/import')
}

const handleExport = async () => {
  try {
    const params = new URLSearchParams()
    if (search.keyword) params.append('keyword', search.keyword)
    if (search.status?.length) search.status.forEach(s => params.append('status', s))
    if (search.tier_levels?.length) search.tier_levels.forEach(t => params.append('tier_levels', t))
    
    const link = document.createElement('a')
    link.href = `${import.meta.env.VITE_API_BASE_URL}/customers/export?${params.toString()}`
    link.download = `客户数据_${new Date().toISOString().split('T')[0]}.xlsx`
    link.click()
    Message.success('导出成功')
  } catch (error) {
    Message.error('导出失败')
  }
}

const handlePageChange = (page: number) => {
  search.page = page
  loadCustomers()
}

const handlePageSizeChange = (size: number) => {
  search.size = size
  search.page = 1
  pagination.pageSize = size
  loadCustomers()
}

onMounted(() => {
  loadCustomers()
})
</script>

<style scoped lang="scss">
.customer-list {
  padding: 24px;
}

.customer-card {
  :deep(.arco-card-header) {
    border-bottom: 1px solid var(--color-border-2);
    padding: 16px 20px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text-1);
}

.card-actions {
  display: flex;
  gap: 12px;
}

.amount {
  font-weight: 500;
  color: var(--color-text-1);
}
</style>
