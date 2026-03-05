<!-- frontend/src/views/customer/CustomerDetail.vue -->
<template>
  <div class="customer-detail">
    <Card v-if="customer" class="detail-card">
      <template #title>
        <div class="detail-header">
          <div class="customer-info">
            <h2 class="customer-name">{{ customer.name }}</h2>
            <Space>
              <Tag :color="getTierLevelColor(customer.tier_level)" size="large">
                {{ customer.tier_level }}级
              </Tag>
              <Tag :color="getStatusColor(customer.status)" size="large">
                {{ getStatusText(customer.status) }}
              </Tag>
            </Space>
          </div>
          <div class="actions">
            <Button @click="handleEdit">
              <template #icon><icon-edit /></template>
              编辑
            </Button>
            <Button @click="handleBack">
              <template #icon><icon-arrow-left /></template>
              返回
            </Button>
          </div>
        </div>
      </template>

      <template #default>
        <Descriptions :column="3" bordered>
          <DescriptionsItem label="客户编码">{{ customer.code || '-' }}</DescriptionsItem>
          <DescriptionsItem label="价值等级">
            <Tag :color="getTierLevelColor(customer.tier_level)" size="medium">
              {{ customer.tier_level }}级
            </Tag>
          </DescriptionsItem>
          <DescriptionsItem label="年消费金额">
            <span class="amount">¥{{ formatAmount(customer.annual_consumption) }}</span>
          </DescriptionsItem>
          <DescriptionsItem label="健康度评分">
            <Progress
              :percent="customer.health_score"
              :status="getHealthStatus(customer.health_score)"
              show-text
              style="width: 200px"
            />
          </DescriptionsItem>
          <DescriptionsItem label="行业">{{ customer.industry || '-' }}</DescriptionsItem>
          <DescriptionsItem label="客户状态">
            <Tag :color="getStatusColor(customer.status)" size="medium">
              {{ getStatusText(customer.status) }}
            </Tag>
          </DescriptionsItem>
          <DescriptionsItem label="最后活跃时间">
            {{ customer.last_active_at ? formatDate(customer.last_active_at) : '从未活跃' }}
          </DescriptionsItem>
          <DescriptionsItem label="创建时间">{{ formatDate(customer.created_at) }}</DescriptionsItem>
          <DescriptionsItem label="更新时间">{{ formatDate(customer.updated_at) }}</DescriptionsItem>
          <DescriptionsItem label="联系人">{{ customer.contact_person || '-' }}</DescriptionsItem>
          <DescriptionsItem label="联系电话">{{ customer.contact_phone || '-' }}</DescriptionsItem>
          <DescriptionsItem label="联系邮箱">{{ customer.contact_email || '-' }}</DescriptionsItem>
          <DescriptionsItem label="客户地址" :span="3">{{ customer.address || '-' }}</DescriptionsItem>
          <DescriptionsItem label="备注" :span="3">
            <div class="remark">{{ customer.remark || '无备注信息' }}</div>
          </DescriptionsItem>
        </Descriptions>
      </template>
    </Card>

    <Card v-else-if="!loading" class="not-found">
      <a-result status="404" title="客户不存在" subtitle="该客户可能已被删除或不存在">
        <template #extra>
          <Button type="primary" @click="handleBack">返回列表</Button>
        </template>
      </a-result>
    </Card>

    <div v-if="loading" class="loading-container">
      <Spin size="large" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { customerApi, type Customer } from '@/api/customer'
import {
  Descriptions,
  DescriptionsItem,
  Tag,
  Button,
  Space,
  Progress,
  Spin,
  Result
} from '@arco-design/web-vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const customer = ref<Customer | null>(null)

const customerId = computed(() => Number(route.params.id))

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

const getHealthStatus = (score: number): 'success' | 'warning' | 'error' | 'normal' => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'normal'
  if (score >= 40) return 'warning'
  return 'error'
}

const formatAmount = (amount: number): string => {
  return (amount || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (dateString: string): string => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadCustomer = async () => {
  loading.value = true
  try {
    const response = await customerApi.get(customerId.value)
    customer.value = response
  } catch (error) {
    Message.error('加载客户详情失败')
  } finally {
    loading.value = false
  }
}

const handleEdit = () => {
  router.push(`/customers/${customerId.value}/edit`)
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadCustomer()
})
</script>

<style scoped lang="scss">
.customer-detail {
  padding: 24px;
}

.detail-card {
  :deep(.arco-card-header) {
    border-bottom: 1px solid var(--color-border-2);
    padding: 16px 20px;
  }
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.customer-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.customer-name {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-1);
}

.actions {
  display: flex;
  gap: 12px;
}

.amount {
  font-weight: 500;
  font-size: 16px;
  color: var(--color-text-1);
}

.remark {
  line-height: 1.6;
  color: var(--color-text-2);
  white-space: pre-wrap;
}

.not-found {
  margin-top: 48px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
</style>
