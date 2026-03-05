<template>
  <div class="role-manage">
    <Card>
      <template #title>
        <Space>
          <span>角色管理</span>
          <Button type="primary" @click="handleCreate">
            <IconPlus />
            新增角色
          </Button>
        </Space>
      </template>

      <Space style="margin-bottom: 16px">
        <Input
          v-model="searchKeyword"
          placeholder="搜索角色名称/编码"
          allow-clear
          style="width: 240px"
          @press-enter="handleSearch"
        >
          <template #prefix>
            <IconSearch />
          </template>
        </Input>
        <Button type="primary" @click="handleSearch">
          <IconSearch />
          搜索
        </Button>
        <Button @click="handleReset">
          <IconRefresh />
          重置
        </Button>
      </Space>

      <Table
        :columns="columns"
        :data="roles"
        :loading="loading"
        :pagination="pagination"
        @page-change="onPageChange"
      >
        <template #permissions="{ record }">
          <Space>
            <Tag
              v-for="(perm, index) in getPermissionsList(record.permissions)"
              :key="index"
              size="small"
            >
              {{ perm }}
            </Tag>
          </Space>
        </template>
        <template #is_system="{ record }">
          <Tag v-if="record.is_system" color="orangered">
            系统角色
          </Tag>
          <Tag v-else color="blue">
            自定义
          </Tag>
        </template>
        <template #action="{ record }">
          <Space>
            <Button
              type="text"
              size="small"
              @click="handleEdit(record)"
              :disabled="record.is_system"
            >
              编辑
            </Button>
            <Button
              type="text"
              size="small"
              status="danger"
              @click="handleDelete(record)"
              :disabled="record.is_system"
            >
              删除
            </Button>
          </Space>
        </template>
      </Table>
    </Card>

    <Modal
      v-model:visible="modalVisible"
      :title="modalTitle"
      width="720px"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
      :confirm-loading="submitting"
    >
      <Form
        ref="formRef"
        :model="form"
        :rules="rules"
        layout="vertical"
      >
        <FormItem
          field="name"
          label="角色名称"
        >
          <Input
            v-model="form.name"
            placeholder="请输入角色名称"
          />
        </FormItem>
        <FormItem
          field="code"
          label="角色编码"
        >
          <Input
            v-model="form.code"
            placeholder="请输入角色编码"
            :disabled="!!form.id"
          />
        </FormItem>
        <FormItem
          field="description"
          label="描述"
        >
          <Input.TextArea
            v-model="form.description"
            placeholder="请输入描述"
            :auto-size="{ minRows: 3, maxRows: 5 }"
          />
        </FormItem>
        <FormItem
          field="permissions"
          label="权限配置"
        >
          <div class="permission-panel">
            <div class="permission-group" v-for="(group, moduleName) in permissionGroups" :key="moduleName">
              <div class="permission-group-header">
                <Checkbox
                  :model-value="isModuleSelected(moduleName)"
                  @change="toggleModule(moduleName)"
                >
                  <span class="module-name">{{ getModuleLabel(moduleName) }}</span>
                </Checkbox>
              </div>
              <div class="permission-group-content">
                <Checkbox.Group v-model="form.permissions">
                  <Space>
                    <Checkbox
                      v-for="perm in group"
                      :key="perm.value"
                      :value="perm.value"
                    >
                      {{ perm.label }}
                    </Checkbox>
                  </Space>
                </Checkbox.Group>
              </div>
            </div>

            <div class="permission-group">
              <div class="permission-group-header">
                <Checkbox
                  :model-value="isSpecialPermissionSelected()"
                  @change="toggleSpecialPermissions"
                >
                  <span class="module-name">特殊权限</span>
                </Checkbox>
              </div>
              <div class="permission-group-content">
                <Space direction="vertical">
                  <Checkbox
                    v-for="perm in specialPermissions"
                    :key="perm.value"
                    :value="perm.value"
                    @change="checkSpecialPermissionChange"
                  >
                    {{ perm.label }}
                    <span class="perm-desc">{{ perm.description }}</span>
                  </Checkbox>
                </Space>
              </div>
            </div>
          </div>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import {
  IconPlus,
  IconSearch,
  IconRefresh,
  IconSettings,
  IconUser,
  IconSafe,
  IconFile,
  IconCoins,
  IconDashboard
} from '@arco-design/web-vue/es/icon'
import { roleApi, type Role, type RoleCreate, type RoleUpdate } from '@/api/role'

const loading = ref(false)
const submitting = ref(false)
const roles = ref<Role[]>([])

const searchKeyword = ref('')

const modalVisible = ref(false)
const modalTitle = ref('新增角色')
const modalMode = ref<'create' | 'edit'>('create')

const formRef = ref()
const form = reactive<Partial<RoleCreate & { id?: number }>>({
  name: '',
  code: '',
  description: '',
  permissions: []
})

const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' }
  ],
  permissions: [
    { 
      required: true, 
      message: '请选择权限', 
      trigger: 'change',
      validator: (value: any[], callback: any) => {
        if (!value || value.length === 0) {
          callback('请至少选择一个权限')
        } else {
          callback()
        }
      }
    }
  ]
}

const pagination = reactive({
  total: 0,
  current: 1,
  pageSize: 20
})

const columns = [
  { title: '角色名称', dataIndex: 'name', width: 150 },
  { title: '角色编码', dataIndex: 'code', width: 150 },
  { title: '描述', dataIndex: 'description', width: 200, ellipsis: true },
  {
    title: '权限',
    slotName: 'permissions',
    width: 400,
    ellipsis: true
  },
  {
    title: '类型',
    slotName: 'is_system',
    width: 100
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    width: 180
  },
  {
    title: '操作',
    slotName: 'action',
    width: 120,
    fixed: 'right'
  }
]

const permissionGroups: Record<string, Array<{ value: string; label: string }>> = {
  customer: [
    { value: 'customer.view', label: '查看客户' },
    { value: 'customer.create', label: '新增客户' },
    { value: 'customer.update', label: '编辑客户' },
    { value: 'customer.delete', label: '删除客户' },
    { value: 'customer.import', label: '导入客户' },
    { value: 'customer.export', label: '导出客户' }
  ],
  pricing: [
    { value: 'pricing.view', label: '查看定价' },
    { value: 'pricing.create', label: '新增定价' },
    { value: 'pricing.update', label: '编辑定价' },
    { value: 'pricing.delete', label: '删除定价' }
  ],
  billing: [
    { value: 'billing.view', label: '查看结算' },
    { value: 'billing.create', label: '创建结算' },
    { value: 'billing.update', label: '编辑结算' },
    { value: 'billing.delete', label: '删除结算' }
  ],
  system: [
    { value: 'system.user.view', label: '查看用户' },
    { value: 'system.user.create', label: '新增用户' },
    { value: 'system.user.update', label: '编辑用户' },
    { value: 'system.user.delete', label: '删除用户' },
    { value: 'system.log.view', label: '查看日志' },
    { value: 'system.*', label: '系统管理通配符' }
  ]
}

const specialPermissions = [
  { value: 'rbac.role', label: '角色管理', description: '管理角色和权限分配' },
  { value: '*', label: '超级管理员', description: '拥有所有权限' }
]

const moduleLabels: Record<string, string> = {
  customer: '客户管理',
  pricing: '定价管理',
  billing: '结算管理',
  system: '系统管理'
}

const getModuleLabel = (moduleName: string) => {
  return moduleLabels[moduleName] || moduleName
}

const getModulePermissions = (moduleName: string): string[] => {
  return permissionGroups[moduleName].map(p => p.value)
}

const isModuleSelected = (moduleName: string): boolean => {
  const modulePerms = getModulePermissions(moduleName)
  const selectedPerms = form.permissions || []
  return modulePerms.every(perm => selectedPerms.includes(perm))
}

const toggleModule = (moduleName: string) => {
  const modulePerms = getModulePermissions(moduleName)
  const selectedPerms = form.permissions || []
  
  const allSelected = modulePerms.every(perm => selectedPerms.includes(perm))
  
  if (allSelected) {
    form.permissions = selectedPerms.filter(perm => !modulePerms.includes(perm))
  } else {
    const newPerms = [...selectedPerms]
    modulePerms.forEach(perm => {
      if (!newPerms.includes(perm)) {
        newPerms.push(perm)
      }
    })
    form.permissions = newPerms
  }
}

const isSpecialPermissionSelected = (): boolean => {
  const selectedPerms = form.permissions || []
  return specialPermissions.every(perm => selectedPerms.includes(perm.value))
}

const toggleSpecialPermissions = () => {
  const selectedPerms = form.permissions || []
  const allSelected = specialPermissions.every(perm => selectedPerms.includes(perm.value))
  
  if (allSelected) {
    form.permissions = selectedPerms.filter(
      perm => !specialPermissions.map(p => p.value).includes(perm)
    )
  } else {
    const newPerms = [...selectedPerms]
    specialPermissions.forEach(perm => {
      if (!newPerms.includes(perm.value)) {
        newPerms.push(perm.value)
      }
    })
    form.permissions = newPerms
  }
}

const checkSpecialPermissionChange = () => {
  const selectedPerms = form.permissions || []
  if (selectedPerms.includes('*')) {
    Message.warning('选择超级管理员权限将拥有所有权限，请谨慎操作')
  }
}

const getPermissionsList = (permissions: string[] | Record<string, boolean>) => {
  if (Array.isArray(permissions)) {
    return permissions
  }
  return Object.keys(permissions)
}

const loadRoles = async () => {
  loading.value = true
  try {
    const response = await roleApi.list({
      page: pagination.current,
      size: pagination.pageSize,
      keyword: searchKeyword.value || undefined
    })
    roles.value = response.data?.items || response.items || []
    pagination.total = response.data?.total || response.total || 0
  } catch (error) {
    Message.error('加载角色列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadRoles()
}

const handleReset = () => {
  searchKeyword.value = ''
  pagination.current = 1
  loadRoles()
}

const onPageChange = (page: number) => {
  pagination.current = page
  loadRoles()
}

const handleCreate = () => {
  modalMode.value = 'create'
  modalTitle.value = '新增角色'
  Object.assign(form, {
    name: '',
    code: '',
    description: '',
    permissions: []
  })
  modalVisible.value = true
}

const handleEdit = (record: Role) => {
  modalMode.value = 'edit'
  modalTitle.value = '编辑角色'
  Object.assign(form, {
    id: record.id,
    name: record.name,
    code: record.code,
    description: record.description,
    permissions: getPermissionsList(record.permissions)
  })
  modalVisible.value = true
}

const handleModalOk = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true

    if (modalMode.value === 'create') {
      await roleApi.create(form as RoleCreate)
      Message.success('创建成功')
    } else {
      const { id, ...updateData } = form
      await roleApi.update(form.id!, updateData as RoleUpdate)
      Message.success('更新成功')
    }

    modalVisible.value = false
    loadRoles()
  } catch (error: any) {
    if (error?.response?.status === 400) {
      Message.error(error.response.data?.error?.message || '操作失败')
    } else if (error?.message !== 'validate error') {
      Message.error('操作失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleModalCancel = () => {
  modalVisible.value = false
}

const handleDelete = (record: Role) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除角色"${record.name}"吗？`,
    onOk: async () => {
      try {
        await roleApi.delete(record.id)
        Message.success('删除成功')
        loadRoles()
      } catch (error) {
        Message.error('删除失败')
      }
    }
  })
}

onMounted(() => {
  loadRoles()
})
</script>

<style scoped lang="scss">
.role-manage {
  padding: 24px;
}

.permission-panel {
  border: 1px solid #e5e6eb;
  border-radius: 4px;
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.permission-group {
  margin-bottom: 16px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.permission-group-header {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
  
  .module-name {
    font-weight: 500;
    color: #1d2129;
  }
}

.permission-group-content {
  padding-left: 24px;
  
  .perm-desc {
    color: #86909c;
    font-size: 12px;
    margin-left: 8px;
  }
}
</style>
