<!-- frontend/src/views/customer/CustomerList.vue -->
<template>
  <div class="customer-list">
    <Card>
      <template #title>
        <Space>
          <span>客户列表</span>
          <Button type="primary" @click="handleCreate">
            新增客户
          </Button>
          <Button @click="handleImport">
            批量导入
          </Button>
          <Button @click="handleExport">
            批量导出
          </Button>
        </Space>
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
        @row-click="handleRowClick"
      >
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message, Modal } from '@arco-design/web-vue'
import { customerApi } from '@/api/customer'

const router = useRouter()

const loading = ref(false)
const customers = ref<any[]>([])

// 搜索表单
const search = reactive({
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

const pagination = reactive({
  total: 0,
  current: 1,
  pageSize: 20
})

// 搜索字段定义
const searchFields = [
  { label: '关键词', field: 'keyword', type: 'input' },
  { label: '所属销售', field: 'sales_rep_ids', type: 'select' },
  { label: '行业', field: 'industries', type: 'select' },
  { label: '客户状态', field: 'status', type: 'select' },
  { label: '价值等级', field: 'tier_levels', type: 'select' },
  { label: '年消费金额', field: 'annual_consumption', type: 'range' }
]

// 表格列定义
const columns = [
  { title: '客户名称', dataIndex: 'name', width: 200 },
  { title: '客户编码', dataIndex: 'code', width: 150 },
  { title: '行业', dataIndex: 'industry', width: 120 },
  { title: '价值等级', dataIndex: 'tier_level', width: 100 },
  { title: '年消费', dataIndex: 'annual_consumption', width: 120 },
  { title: '状态', dataIndex: 'status', width: 100 },
  { title: '联系人', dataIndex: 'contact_person', width: 120 },
  { title: '联系电话', dataIndex: 'contact_phone', width: 150 },
  {
    title: '操作',
    slotName: 'action',
    width: 180,
    fixed: 'right'
  }
]

// 加载客户列表
const loadCustomers = async () => {
  loading.value = true
  try {
    const response = await customerApi.list(search)
    customers.value = response.data.items
    pagination.total = response.data.total
    pagination.current = response.data.page
  } catch (error) {
    Message.error('加载客户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  search.page = 1
  loadCustomers()
}

// 重置
const handleReset = () => {
  Object.assign(search, {
    page: 1,
    size: 20,
    keyword: '',
    sales_rep_ids: [],
    industries: [],
    status: [],
    tier_levels: []
  })
  loadCustomers()
}

// 查看
const handleView = (record: any) => {
  router.push(`/customers/${record.id}`)
}

// 编辑
const handleEdit = (record: any) => {
  router.push(`/customers/${record.id}?mode=edit`)
}

// 删除
const handleDelete = (record: any) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除客户"${record.name}"吗?`,
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

// 新增
const handleCreate = () => {
  router.push('/customers/create')
}

// 导入
const handleImport = () => {
  router.push('/customers/import')
}

// 导出
const handleExport = async () => {
  try {
    // TODO: 实现导出功能
    Message.info('导出功能开发中')
  } catch (error) {
    Message.error('导出失败')
  }
}

// 分页变化
const handlePageChange = (page: number) => {
  search.page = page
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
</style>
