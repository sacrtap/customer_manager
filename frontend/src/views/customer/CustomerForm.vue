<!-- frontend/src/views/customer/CustomerForm.vue -->
<template>
  <div class="customer-form">
    <Card class="form-card">
      <template #title>
        <div class="card-header">
          <span class="card-title">{{ isEdit ? '编辑客户' : '新增客户' }}</span>
          <Button @click="handleBack">返回列表</Button>
        </div>
      </template>

      <a-form
        ref="formRef"
        :model="form"
        :rules="rules"
        layout="vertical"
        @submit="handleSubmit"
      >
        <div class="form-section">
          <div class="section-title">基本信息</div>
          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="客户名称" field="name">
                <a-input
                  v-model="form.name"
                  placeholder="请输入客户名称"
                  allow-clear
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="客户编码" field="code">
                <a-input
                  v-model="form.code"
                  placeholder="请输入客户编码"
                  allow-clear
                />
              </a-form-item>
            </a-col>
          </a-row>

          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="行业" field="industry">
                <a-select
                  v-model="form.industry"
                  placeholder="请选择行业"
                  allow-clear
                >
                  <a-option value="technology">科技</a-option>
                  <a-option value="manufacturing">制造业</a-option>
                  <a-option value="finance">金融</a-option>
                  <a-option value="retail">零售</a-option>
                  <a-option value="healthcare">医疗</a-option>
                  <a-option value="education">教育</a-option>
                  <a-option value="energy">能源</a-option>
                  <a-option value="telecom">电信</a-option>
                  <a-option value="other">其他</a-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="价值等级" field="tier_level">
                <a-select
                  v-model="form.tier_level"
                  placeholder="请选择价值等级"
                >
                  <a-option value="S">S 级（战略客户）</a-option>
                  <a-option value="A">A 级（重要客户）</a-option>
                  <a-option value="B">B 级（普通客户）</a-option>
                  <a-option value="C">C 级（一般客户）</a-option>
                  <a-option value="D">D 级（潜力客户）</a-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>

          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="年消费金额" field="annual_consumption">
                <a-input-number
                  v-model="form.annual_consumption"
                  placeholder="请输入年消费金额"
                  :min="0"
                  :precision="2"
                  style="width: 100%"
                >
                  <template #prefix>¥</template>
                </a-input-number>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="客户状态" field="status">
                <a-select
                  v-model="form.status"
                  placeholder="请选择客户状态"
                >
                  <a-option value="active">活跃</a-option>
                  <a-option value="risk">风险</a-option>
                  <a-option value="zombie">僵尸</a-option>
                  <a-option value="inactive">停用</a-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
        </div>

        <div class="form-section">
          <div class="section-title">联系人信息</div>
          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="联系人" field="contact_person">
                <a-input
                  v-model="form.contact_person"
                  placeholder="请输入联系人姓名"
                  allow-clear
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="联系电话" field="contact_phone">
                <a-input
                  v-model="form.contact_phone"
                  placeholder="请输入 11 位手机号码"
                  allow-clear
                  maxlength="11"
                />
              </a-form-item>
            </a-col>
          </a-row>

          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="联系邮箱" field="contact_email">
                <a-input
                  v-model="form.contact_email"
                  placeholder="请输入联系邮箱"
                  allow-clear
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="地址" field="address">
                <a-input
                  v-model="form.address"
                  placeholder="请输入地址"
                  allow-clear
                />
              </a-form-item>
            </a-col>
          </a-row>
        </div>

        <div class="form-section">
          <div class="section-title">其他信息</div>
          <a-form-item label="备注" field="remark">
            <a-textarea
              v-model="form.remark"
              placeholder="请输入备注信息"
              :max-length="1000"
              show-word-limit
              :auto-size="{ minRows: 3, maxRows: 6 }"
            />
          </a-form-item>
        </div>

        <div class="form-actions">
          <a-space>
            <a-button type="primary" html-type="submit" :loading="submitting">
              {{ isEdit ? '保存修改' : '创建客户' }}
            </a-button>
            <a-button @click="handleBack">取消</a-button>
          </a-space>
        </div>
      </a-form>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Message, FormInstance } from '@arco-design/web-vue'
import { customerApi, type Customer } from '@/api/customer'

const router = useRouter()
const route = useRoute()
const formRef = ref<FormInstance>()
const submitting = ref(false)

const customerId = computed(() => {
  const id = route.params.id as string
  return id ? parseInt(id) : null
})

const isEdit = computed(() => !!customerId.value)

const form = reactive<Partial<Customer>>({
  name: '',
  code: '',
  industry: '',
  sales_rep_id: 1, // TODO: 从当前用户获取
  tier_level: 'D',
  annual_consumption: 0,
  status: 'active',
  contact_person: '',
  contact_phone: '',
  contact_email: '',
  address: '',
  remark: ''
})

const rules = {
  name: [
    { required: true, message: '请输入客户名称', trigger: 'blur' },
    { min: 1, max: 200, message: '客户名称长度应在 1-200 个字符之间', trigger: 'blur' }
  ],
  code: [
    { max: 50, message: '客户编码长度不能超过 50 个字符', trigger: 'blur' }
  ],
  industry: [
    { max: 100, message: '行业长度不能超过 100 个字符', trigger: 'blur' }
  ],
  contact_person: [
    { max: 100, message: '联系人长度不能超过 100 个字符', trigger: 'blur' }
  ],
  contact_phone: [
    { pattern: /^\\d{11}$/, message: '请输入正确的 11 位手机号码', trigger: 'blur' }
  ],
  contact_email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  address: [
    { max: 500, message: '地址长度不能超过 500 个字符', trigger: 'blur' }
  ],
  remark: [
    { max: 1000, message: '备注长度不能超过 1000 个字符', trigger: 'blur' }
  ]
}

const loadCustomer = async () => {
  if (!customerId.value) return
  
  try {
    const customer = await customerApi.get(customerId.value)
    Object.assign(form, customer)
  } catch (error) {
    Message.error('加载客户信息失败')
  }
}

const handleSubmit = async () => {
  const error = await formRef.value?.validate()
  if (error) return
  
  submitting.value = true
  try {
    const data = { ...form }
    
    if (isEdit.value) {
      await customerApi.update(customerId.value, data)
      Message.success('客户信息已更新')
    } else {
      await customerApi.create(data)
      Message.success('客户创建成功')
    }
    
    router.push('/customers')
  } catch (error) {
    Message.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadCustomer()
})
</script>

<style scoped lang="scss">
.customer-form {
  padding: 24px;
}

.form-card {
  :deep(.arco-card-header) {
    border-bottom: 1px solid var(--color-border-2);
    padding: 16px 20px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text-1);
}

.form-section {
  margin-bottom: 32px;
  padding: 20px;
  background: var(--color-bg-2);
  border-radius: 4px;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-1);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border-2);
}

.form-actions {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--color-border-2);
}
</style>
