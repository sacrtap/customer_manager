<template>
  <div class="transfer-history">
    <Card>
      <template #title>
        <Space>
          <span>客户转移记录</span>
          <Button type="primary" @click="router.push('/transfers/create')">
            发起转移
          </Button>
        </Space>
      </template>

      <!-- 搜索栏 -->
      <Form layout="inline" :model="searchForm" style="margin-bottom: 16px;">
        <FormItem label="状态">
          <Select
            v-model="searchForm.status"
            placeholder="全部状态"
            allow-clear
            style="width: 150px"
          >
            <Option value="pending">待审批</Option>
            <Option value="approved">已批准</Option>
            <Option value="rejected">已拒绝</Option>
            <Option value="completed">已完成</Option>
          </Select>
        </FormItem>
        <FormItem>
          <Space>
            <Button type="primary" @click="handleSearch">
              查询
            </Button>
            <Button @click="handleReset">
              重置
            </Button>
          </Space>
        </FormItem>
      </Form>

      <!-- 转移记录表格 -->
      <Table
        :columns="columns"
        :data="transfers"
        :loading="loading"
        :pagination="pagination"
        :row-key="(record: any) => record.id"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
      >
        <template #status="{ record }">
          <Tag :color="getStatusColor(record.status)">
            {{ getStatusText(record.status) }}
          </Tag>
        </template>

        <template #action="{ record }">
          <Space>
            <Button
              v-if="record.status === 'pending' && canApprove"
              type="text"
              size="small"
              status="success"
              @click="handleApprove(record)"
            >
              批准
            </Button>
            <Button
              v-if="record.status === 'pending' && canApprove"
              type="text"
              size="small"
              status="danger"
              @click="handleReject(record)"
            >
              拒绝
            </Button>
            <Button
              v-if="record.status === 'approved' && canComplete(record)"
              type="text"
              size="small"
              @click="handleComplete(record)"
            >
              完成
            </Button>
            <Button
              type="text"
              size="small"
              @click="handleView(record)"
            >
              查看
            </Button>
          </Space>
        </template>
      </Table>
    </Card>

    <!-- 查看详情弹窗 -->
    <Modal
      v-model:visible="detailVisible"
      title="转移详情"
      @ok="detailVisible = false"
      :footer="false"
      width="600px"
    >
      <Descriptions :data="detailData" :column="1" v-if="currentTransfer">
        <DescriptionsItem label="转移 ID">{{ currentTransfer.id }}</DescriptionsItem>
        <DescriptionsItem label="客户 ID">{{ currentTransfer.customer_id }}</DescriptionsItem>
        <DescriptionsItem label="转出销售 ID">{{ currentTransfer.from_sales_rep_id }}</DescriptionsItem>
        <DescriptionsItem label="转入销售 ID">{{ currentTransfer.to_sales_rep_id }}</DescriptionsItem>
        <DescriptionsItem label="转移原因">{{ currentTransfer.reason }}</DescriptionsItem>
        <DescriptionsItem label="状态">
          <Tag :color="getStatusColor(currentTransfer.status)">
            {{ getStatusText(currentTransfer.status) }}
          </Tag>
        </DescriptionsItem>
        <DescriptionsItem label="审批人 ID">{{ currentTransfer.approved_by || '-' }}</DescriptionsItem>
        <DescriptionsItem label="审批时间">{{ currentTransfer.approved_at || '-' }}</DescriptionsItem>
        <DescriptionsItem label="创建人 ID">{{ currentTransfer.created_by }}</DescriptionsItem>
        <DescriptionsItem label="创建时间">{{ currentTransfer.created_at }}</DescriptionsItem>
        <DescriptionsItem label="更新时间">{{ currentTransfer.updated_at }}</DescriptionsItem>
      </Descriptions>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message, Modal } from '@arco-design/web-vue'
import { transferApi } from '@/api/transfer'
import type { Transfer, TransferQuery } from '@/types/transfer'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const detailVisible = ref(false)
const currentTransfer = ref<Transfer | null>(null)

const transfers = ref<Transfer[]>([])

const searchForm = reactive<TransferQuery>({
  page: 1,
  size: 20,
  status: undefined
})

const pagination = reactive({
  total: 0,
  current: 1,
  pageSize: 20
})

const canApprove = computed(() => {
  // TODO: 检查用户是否有审批权限
  const permissions = userStore.permissions || []
  return permissions.includes('customer.transfer.approve') || permissions.includes('*')
})

const canComplete = (record: Transfer) => {
  // TODO: 检查是否是转入销售
  return true
}

const columns = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '客户 ID', dataIndex: 'customer_id', width: 100 },
  { title: '转出销售 ID', dataIndex: 'from_sales_rep_id', width: 130 },
  { title: '转入销售 ID', dataIndex: 'to_sales_rep_id', width: 130 },
  { title: '转移原因', dataIndex: 'reason', ellipsis: true, tooltip: true },
  {
    title: '状态',
    dataIndex: 'status',
    slotName: 'status',
    width: 120
  },
  { title: '创建时间', dataIndex: 'created_at', width: 180 },
  {
    title: '操作',
    slotName: 'action',
    width: 200,
    fixed: 'right'
  }
]

const detailData = computed(() => currentTransfer.value ? [currentTransfer.value] : [])

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    pending: 'orange',
    approved: 'green',
    rejected: 'red',
    completed: 'blue'
  }
  return colors[status] || 'default'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝',
    completed: '已完成'
  }
  return texts[status] || status
}

const loadTransfers = async () => {
  loading.value = true
  try {
    const response = await transferApi.list(searchForm)
    transfers.value = response.items || []
    pagination.total = response.total || 0
    pagination.current = response.page || 1
    pagination.pageSize = response.size || 20
  } catch (error) {
    Message.error('加载转移记录失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  searchForm.page = 1
  loadTransfers()
}

const handleReset = () => {
  searchForm.page = 1
  searchForm.size = 20
  searchForm.status = undefined
  loadTransfers()
}

const handlePageChange = (page: number) => {
  searchForm.page = page
  loadTransfers()
}

const handlePageSizeChange = (size: number) => {
  searchForm.size = size
  searchForm.page = 1
  loadTransfers()
}

const handleApprove = (record: Transfer) => {
  Modal.confirm({
    title: '确认批准',
    content: '确定要批准这个转移申请吗?',
    onOk: async () => {
      try {
        await transferApi.approve(record.id)
        Message.success('批准成功')
        loadTransfers()
      } catch (error: any) {
        Message.error(error.message || '批准失败')
      }
    }
  })
}

const handleReject = (record: Transfer) => {
  Modal.confirm({
    title: '确认拒绝',
    content: '确定要拒绝这个转移申请吗?',
    onOk: async () => {
      try {
        await transferApi.reject(record.id)
        Message.success('已拒绝')
        loadTransfers()
      } catch (error: any) {
        Message.error(error.message || '拒绝失败')
      }
    }
  })
}

const handleComplete = (record: Transfer) => {
  Modal.confirm({
    title: '确认完成',
    content: '确定要完成这个转移吗? 完成后客户将正式转移给新销售。',
    onOk: async () => {
      try {
        await transferApi.complete(record.id)
        Message.success('转移已完成')
        loadTransfers()
      } catch (error: any) {
        Message.error(error.message || '完成失败')
      }
    }
  })
}

const handleView = (record: Transfer) => {
  currentTransfer.value = record
  detailVisible.value = true
}

onMounted(() => {
  loadTransfers()
})
</script>

<style scoped lang="scss">
.transfer-history {
  padding: 24px;
}
</style>
