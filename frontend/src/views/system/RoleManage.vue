<template>
  <div class="role-manage">
    <Card>
      <template #title>
        <Space>
          <span>角色管理</span>
          <Button type="primary" @click="handleCreate">
            新增角色
          </Button>
        </Space>
      </template>

      <Table
        :columns="columns"
        :data="roles"
        :loading="loading"
        :pagination="pagination"
      >
        <template #permissions="{ record }">
          <Space>
            <Tag
              v-for="(perm, index) in getPermissionsList(record.permissions)"
              :key="index"
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
      @ok="handleModalOk"
      @cancel="handleModalCancel"
    >
      <Form :model="form" :rules="rules" layout="vertical">
        <FormItem field="name" label="角色名称">
          <Input v-model="form.name" placeholder="请输入角色名称" />
        </FormItem>
        <FormItem field="code" label="角色编码">
          <Input
            v-model="form.code"
            placeholder="请输入角色编码"
            :disabled="!!form.id"
          />
        </FormItem>
        <FormItem field="description" label="描述">
          <Input.TextArea
            v-model="form.description"
            placeholder="请输入描述"
            :auto-size="{ minRows: 3, maxRows: 5 }"
          />
        </FormItem>
        <FormItem field="permissions" label="权限配置">
          <Checkbox.Group v-model="form.permissions">
            <Space direction="vertical">
              <Checkbox
                v-for="perm in allPermissions"
                :key="perm"
                :value="perm"
              >
                {{ perm }}
              </Checkbox>
            </Space>
          </Checkbox.Group>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { roleApi, type Role, type RoleCreate, type RoleUpdate } from '@/api/role'

const loading = ref(false)
const roles = ref<Role[]>([])

const modalVisible = ref(false)
const modalTitle = ref('新增角色')
const modalMode = ref<'create' | 'edit'>('create')

const form = reactive<Partial<RoleCreate & { id?: number }>>({
  name: '',
  code: '',
  description: '',
  permissions: []
})

const allPermissions = [
  'customer.view',
  'customer.create',
  'customer.update',
  'customer.delete',
  'customer.import',
  'customer.export',
  'user.view',
  'user.create',
  'user.update',
  'user.delete',
  'rbac.role',
  'system.log.view',
  'system.*',
  '*'
]

const rules = {
  name: [{ required: true, message: '请输入角色名称' }],
  code: [{ required: true, message: '请输入角色编码' }],
  permissions: [{ required: true, message: '请选择权限' }]
}

const pagination = reactive({
  total: 0,
  current: 1,
  pageSize: 20
})

const columns = [
  { title: '角色名称', dataIndex: 'name', width: 150 },
  { title: '角色编码', dataIndex: 'code', width: 150 },
  { title: '描述', dataIndex: 'description', width: 200 },
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
      size: pagination.pageSize
    })
    roles.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    Message.error('加载角色列表失败')
  } finally {
    loading.value = false
  }
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
    if (modalMode.value === 'create') {
      await roleApi.create(form as RoleCreate)
      Message.success('创建成功')
    } else {
      await roleApi.update(form.id!, form as RoleUpdate)
      Message.success('更新成功')
    }
    modalVisible.value = false
    loadRoles()
  } catch (error) {
    Message.error('操作失败')
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
</style>
