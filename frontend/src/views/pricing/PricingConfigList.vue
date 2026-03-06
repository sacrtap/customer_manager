<!-- 价格配置列表 -->
<template>
  <div class="pricing-config-list">
    <Card>
      <template #title><span>价格配置管理</span></template>
      <Table :columns="columns" :data="data" :loading="loading" :pagination="pagination">
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

const loading = ref(false)
const data = ref<any[]>([])
const pagination = reactive({ total: 0, current: 1, pageSize: 20 })

const columns = [
  { title: '配置名称', dataIndex: 'name', width: 200 },
  { title: '价格区间', dataIndex: 'price_band_name', width: 150 },
  { title: '定价策略', dataIndex: 'pricing_strategy_name', width: 150 },
  { title: '基础价格', dataIndex: 'base_price', width: 120 },
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

const handleEdit = (record: any) => Message.info(`编辑：${record.name}`)
const handleDelete = (record: any) => Message.info(`删除：${record.name}`)

onMounted(() => loadData())
</script>

<style scoped lang="scss">
.pricing-config-list { padding: 24px; }
</style>
