<!-- 结算单列表 -->
<template>
  <div class="billing-list">
    <Card title="结算单列表">
      <Table :columns="columns" :data="data" :loading="loading" :pagination="pagination">
        <template #status="{ record }">
          <Tag :color="record.status === 'sent' ? 'green' : 'orange'">{{ record.status === 'sent' ? '已发送' : '待发送' }}</Tag>
        </template>
        <template #action="{ record }">
          <Space>
            <Button type="text" size="small" @click="router.push(`/billing/${record.id}`)">详情</Button>
            <Button type="text" size="small">下载</Button>
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

const router = useRouter()
const loading = ref(false)
const data = ref<any[]>([])
const pagination = reactive({ total: 0, current: 1, pageSize: 20 })

const columns = [
  { title: '结算单号', dataIndex: 'code', width: 150 },
  { title: '月份', dataIndex: 'month', width: 100 },
  { title: '客户数', dataIndex: 'customer_count', width: 80 },
  { title: '总金额', dataIndex: 'total_amount', width: 150 },
  { title: '状态', dataIndex: 'status', slotName: 'status', width: 80 },
  { title: '创建时间', dataIndex: 'created_at', width: 180 },
  { title: '操作', slotName: 'action', width: 150, fixed: 'right' }
]

const loadData = async () => {
  loading.value = true
  try {
    data.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => loadData())
</script>

<style scoped lang="scss">
.billing-list { padding: 24px; }
</style>
