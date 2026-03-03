<!-- frontend/src/views/Dashboard.vue -->
<template>
  <div class="dashboard">
    <Row :gutter="16">
      <!-- 欢迎卡片 -->
      <Col :span="24">
        <Card class="welcome-card">
          <Space align="center">
            <Avatar :size="64" :style="{ backgroundColor: '#1890ff' }">
              {{ userInfo.real_name?.charAt(0) }}
            </Avatar>
            <div>
              <div class="welcome-title">
                欢迎回来,{{ userInfo.real_name }}!
              </div>
              <div class="welcome-subtitle">
                {{ roleText }} | {{ userInfo.email }}
              </div>
            </div>
          </Space>
        </Card>
      </Col>

      <!-- 快捷入口 -->
      <Col :span="6">
        <Card class="quick-link-card" hoverable @click="goToCustomerList">
          <template #extra>
            <Icon type="icon-user-group" :size="32" />
          </template>
          <div class="card-title">客户管理</div>
          <div class="card-desc">管理客户数据</div>
        </Card>
      </Col>

      <Col :span="6" v-if="hasPermission('customer.import')">
        <Card class="quick-link-card" hoverable @click="goToCustomerImport">
          <template #extra>
            <Icon type="icon-import" :size="32" />
          </template>
          <div class="card-title">批量导入</div>
          <div class="card-desc">Excel 数据导入</div>
        </Card>
      </Col>

      <Col :span="6" v-if="hasPermission('system.log.view')">
        <Card class="quick-link-card" hoverable @click="goToSystemLogs">
          <template #extra>
            <Icon type="icon-history" :size="32" />
          </template>
          <div class="card-title">操作日志</div>
          <div class="card-desc">查看操作记录</div>
        </Card>
      </Col>

      <Col :span="6" v-if="hasPermission('user.view')">
        <Card class="quick-link-card" hoverable @click="goToSystemUsers">
          <template #extra>
            <Icon type="icon-user" :size="32" />
          </template>
          <div class="card-title">用户管理</div>
          <div class="card-desc">管理系统用户</div>
        </Card>
      </Col>
    </Row>

    <!-- 最近操作记录 -->
    <Row :gutter="16" style="margin-top: 16px;">
      <Col :span="24">
        <Card title="最近操作" class="recent-operations">
          <Table
            :columns="logColumns"
            :data="recentOperations"
            :loading="loading"
            :pagination="false"
          />
        </Card>
      </Col>
    </Row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { useUserStore } from '@/stores/user'
import type { OperationLog } from '@/types/log'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const recentOperations = ref<OperationLog[]>([])

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 角色文本
const roleText = computed(() => {
  if (!userInfo.value) return ''
  const roleMap: Record<string, string> = {
    'admin': '系统管理员',
    'manager': '运营经理',
    'specialist': '运营专员',
    'sales': '销售人员'
  }
  return roleMap[userInfo.value.role] || ''
})

// 权限检查
const hasPermission = (permission: string) => {
  return userStore.hasPermission(permission)
}

// 导航方法
const goToCustomerList = () => router.push('/customers')
const goToCustomerImport = () => router.push('/customers/import')
const goToSystemLogs = () => router.push('/system/logs')
const goToSystemUsers = () => router.push('/system/users')

// 表格列定义
const logColumns = [
  { title: '操作类型', dataIndex: 'operation_type', width: 150 },
  { title: '目标', dataIndex: 'target_type', width: 120 },
  { title: '操作时间', dataIndex: 'created_at', width: 180 },
  { title: 'IP 地址', dataIndex: 'ip_address', width: 140 }
]

// 加载最近操作
const loadRecentOperations = async () => {
  loading.value = true
  try {
    // TODO: 实现获取最近操作的 API 调用
    // const response = await logApi.list({ page: 1, size: 5 })
    // recentOperations.value = response.data.items
    recentOperations.value = []
  } catch (error) {
    Message.error('加载最近操作失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRecentOperations()
})
</script>

<style scoped lang="scss">
.dashboard {
  padding: 24px;

  .welcome-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

    :deep(.arco-card-body) {
      padding: 32px;
    }

    .welcome-title {
      font-size: 24px;
      font-weight: 600;
      color: #ffffff;
      margin-bottom: 8px;
    }

    .welcome-subtitle {
      font-size: 16px;
      color: #e0e0e0;
    }
  }

  .quick-link-card {
    cursor: pointer;
    transition: all 0.3s;
    text-align: center;
    padding: 24px 16px;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }

    .card-title {
      font-size: 18px;
      font-weight: 600;
      margin-top: 12px;
      margin-bottom: 4px;
    }

    .card-desc {
      font-size: 14px;
      color: #86909c;
    }
  }

  .recent-operations {
    margin-top: 24px;
  }
}
</style>
