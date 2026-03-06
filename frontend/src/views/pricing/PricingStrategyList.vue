<!-- 定价策略列表 -->
<template>
  <div class="pricing-strategy-list">
    <Card>
      <template #title>
        <Space>
          <span>定价策略管理</span>
          <Button type="primary" @click="handleCreate">新增策略</Button>
        </Space>
      </template>

      <Table :columns="columns" :data="data" :loading="loading" :pagination="pagination">
        <template #status="{ record }">
          <Tag :color="record.status ? 'green' : 'gray'">{{ record.status ? '启用' : '禁用' }}</Tag>
        </template>
        <template #action="{ record }">
          <Space>
            <Button type="text" size="small" @click="handleEdit(record)">编辑</Button>
            <Button type="text" size="small" status="danger" @click="handleDelete(record)">删除</Button>
          </Space>
        </template>
      </Table>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { pricingStrategyApi } from '@/api/pricing-strategy'

const loading = ref(false)
const data = ref<any[]>([])

const pagination = reactive({ total: 0, current: 1, pageSize: 20 })

const columns = [
  { title: '策略名称', dataIndex: 'name', width: 200 },
  { title: '策略编码', dataIndex: 'code', width: 150 },
  { title: '适用客户', dataIndex: 'applicable_customers', width: 200 },
  { title: '折扣率', dataIndex: 'discount_rate', width: 100 },
  { title: '状态', dataIndex: 'status', slotName: 'status', width: 80 },
  { title: '操作', slotName: 'action', width: 150, fixed: 'right' }
]

const loadData = async () => {
  loading.value = true
  try {
    const response = await pricingStrategyApi.list({ page: pagination.current, size: pagination.pageSize })
    data.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    Message.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = () => Message.info('新增策略功能')
const handleEdit = (record: any) => Message.info(`编辑：${record.name}`)
const handleDelete = (record: any) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定删除"${record.name}"吗？`,
    onOk: async () => {
      await pricingStrategyApi.delete(record.id)
      Message.success('删除成功')
      loadData()
    }
  })
}

onMounted(() => loadData())
</script>

<style scoped lang="scss">
.pricing-strategy-list { padding: 24px; }
</style>
