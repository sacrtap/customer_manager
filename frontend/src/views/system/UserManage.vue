<template>
  <div class="user-manage">
    <Card>
      <template #title>
        <Space>
          <span>用户管理</span>
          <Button type="primary" @click="handleCreate">
            <IconPlus />
            新增用户
          </Button>
        </Space>
      </template>

      <Space style="margin-bottom: 16px">
        <Input
          v-model="searchKeyword"
          placeholder="搜索用户名/姓名/邮箱"
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
        :data="users"
        :loading="loading"
        :pagination="pagination"
        @page-change="onPageChange"
      >
        <template #status="{ record }">
          <Tag v-if="record.status === 'active'" color="green">
            <IconCheckCircle />
            启用
          </Tag>
          <Tag v-else color="red">
            <IconCloseCircle />
            禁用
          </Tag>
        </template>
        <template #roles="{ record }">
          <Space>
            <Tag
              v-for="role in record.roles"
              :key="role"
            >
              {{ role }}
            </Tag>
          </Space>
        </template>
        <template #action="{ record }">
          <Space>
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
              @click="handleResetPassword(record)"
            >
              重置密码
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

    <Modal
      v-model:visible="modalVisible"
      :title="modalTitle"
      width="640px"
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
          field="username"
          label="用户名"
          v-if="modalMode === 'create'"
        >
          <Input
            v-model="form.username"
            placeholder="请输入用户名"
            :disabled="modalMode === 'edit'"
          />
        </FormItem>
        <FormItem
          field="password"
          label="密码"
          v-if="modalMode === 'create'"
        >
          <InputPassword
            v-model="form.password"
            placeholder="请输入密码"
          />
        </FormItem>
        <FormItem
          field="real_name"
          label="真实姓名"
        >
          <Input
            v-model="form.real_name"
            placeholder="请输入真实姓名"
          />
        </FormItem>
        <FormItem
          field="email"
          label="邮箱"
        >
          <Input
            v-model="form.email"
            placeholder="请输入邮箱"
          />
        </FormItem>
        <FormItem
          field="phone"
          label="手机号"
        >
          <Input
            v-model="form.phone"
            placeholder="请输入手机号"
            :max-length="11"
          />
        </FormItem>
        <FormItem
          field="status"
          label="状态"
        >
          <RadioGroup v-model="form.status">
            <Radio value="active">启用</Radio>
            <Radio value="inactive">禁用</Radio>
          </RadioGroup>
        </FormItem>
        <FormItem
          field="role_ids"
          label="角色"
        >
          <Select
            v-model="form.role_ids"
            multiple
            placeholder="请选择角色"
            allow-clear
          >
            <Option
              v-for="role in roles"
              :key="role.id"
              :value="role.id"
            >
              {{ role.name }}
            </Option>
          </Select>
        </FormItem>
      </Form>
    </Modal>

    <Modal
      v-model:visible="passwordModalVisible"
      title="重置密码"
      width="480px"
      @ok="handlePasswordOk"
      @cancel="passwordModalVisible = false"
      :confirm-loading="submitting"
    >
      <Form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        layout="vertical"
      >
        <FormItem
          field="new_password"
          label="新密码"
        >
          <InputPassword
            v-model="passwordForm.new_password"
            placeholder="请输入新密码"
          />
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import {
  IconPlus,
  IconSearch,
  IconRefresh,
  IconCheckCircle,
  IconCloseCircle,
  IconEdit,
  IconDelete
} from '@arco-design/web-vue/es/icon'
import { userApi, type User, type UserCreate, type UserUpdate } from '@/api/user'
import { roleApi } from '@/api/role'

const loading = ref(false)
const submitting = ref(false)
const users = ref<User[]>([])
const roles = ref<any[]>([])

const searchKeyword = ref('')

const modalVisible = ref(false)
const modalTitle = ref('新增用户')
const modalMode = ref<'create' | 'edit'>('create')

const formRef = ref()
const form = reactive<Partial<UserCreate & { id?: number }>>({
  username: '',
  password: '',
  real_name: '',
  email: '',
  phone: '',
  status: 'active',
  role_ids: []
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度应在 3-50 个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ]
}

const pagination = reactive({
  total: 0,
  current: 1,
  pageSize: 20
})

const columns = [
  { title: '用户名', dataIndex: 'username', width: 150 },
  { title: '真实姓名', dataIndex: 'real_name', width: 120 },
  { title: '邮箱', dataIndex: 'email', width: 200, ellipsis: true },
  { title: '手机号', dataIndex: 'phone', width: 120 },
  {
    title: '状态',
    slotName: 'status',
    width: 100
  },
  {
    title: '角色',
    slotName: 'roles',
    width: 200,
    ellipsis: true
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    width: 180
  },
  {
    title: '操作',
    slotName: 'action',
    width: 200,
    fixed: 'right'
  }
]

const passwordModalVisible = ref(false)
const passwordFormRef = ref()
const passwordForm = reactive({
  new_password: ''
})
const passwordRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ]
}
const currentUserId = ref<number | null>(null)

const loadRoles = async () => {
  try {
    const response = await roleApi.list({ page: 1, size: 100 })
    roles.value = response.data?.items || response.items || []
  } catch (error) {
    console.error('加载角色失败:', error)
  }
}

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await userApi.list({
      page: pagination.current,
      size: pagination.pageSize,
      keyword: searchKeyword.value || undefined
    })
    users.value = response.data?.items || response.items || []
    pagination.total = response.data?.total || response.total || 0
  } catch (error) {
    Message.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadUsers()
}

const handleReset = () => {
  searchKeyword.value = ''
  pagination.current = 1
  loadUsers()
}

const onPageChange = (page: number) => {
  pagination.current = page
  loadUsers()
}

const handleCreate = () => {
  modalMode.value = 'create'
  modalTitle.value = '新增用户'
  Object.assign(form, {
    username: '',
    password: '',
    real_name: '',
    email: '',
    phone: '',
    status: 'active',
    role_ids: []
  })
  modalVisible.value = true
}

const handleEdit = (record: User) => {
  modalMode.value = 'edit'
  modalTitle.value = '编辑用户'
  Object.assign(form, {
    id: record.id,
    username: record.username,
    real_name: record.real_name,
    email: record.email,
    phone: record.phone,
    status: record.status,
    role_ids: record.role_ids || []
  })
  modalVisible.value = true
}

const handleModalOk = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true

    if (modalMode.value === 'create') {
      await userApi.create(form as UserCreate)
      Message.success('创建成功')
    } else {
      const { username, password, ...updateData } = form
      await userApi.update(form.id!, updateData as UserUpdate)
      Message.success('更新成功')
    }

    modalVisible.value = false
    loadUsers()
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

const handleResetPassword = (record: User) => {
  currentUserId.value = record.id
  passwordForm.new_password = ''
  passwordModalVisible.value = true
}

const handlePasswordOk = async () => {
  try {
    await passwordFormRef.value?.validate()
    submitting.value = true

    if (currentUserId.value) {
      await userApi.updatePassword(currentUserId.value, passwordForm.new_password)
      Message.success('密码重置成功')
    }

    passwordModalVisible.value = false
  } catch (error: any) {
    if (error?.message !== 'validate error') {
      Message.error('重置密码失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleDelete = (record: User) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除用户"${record.username}"吗？`,
    onOk: async () => {
      try {
        await userApi.delete(record.id)
        Message.success('删除成功')
        loadUsers()
      } catch (error) {
        Message.error('删除失败')
      }
    }
  })
}

onMounted(() => {
  loadRoles()
  loadUsers()
})
</script>

<style scoped lang="scss">
.user-manage {
  padding: 24px;
}
</style>
