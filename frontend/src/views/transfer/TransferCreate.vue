<template>
  <div class="transfer-create">
    <Card>
      <template #title>
        <Space>
          <span>发起客户转移</span>
        </Space>
      </template>

      <Form
        ref="formRef"
        :model="formData"
        :rules="rules"
        layout="vertical"
        @submit="handleSubmit"
      >
        <FormItem label="选择客户" field="customer_id">
          <Select
            v-model="formData.customer_id"
            placeholder="请选择要转移的客户"
            :loading="customersLoading"
            :filterable="true"
            style="width: 100%"
          >
            <Option
              v-for="customer in customers"
              :key="customer.id"
              :value="customer.id"
            >
              {{ customer.name }} ({{ customer.code }})
            </Option>
          </Select>
        </FormItem>

        <FormItem label="转入销售" field="to_sales_rep_id">
          <Select
            v-model="formData.to_sales_rep_id"
            placeholder="请选择转入的销售人员"
            :loading="salesLoading"
            :filterable="true"
            style="width: 100%"
          >
            <Option
              v-for="sales in salesReps"
              :key="sales.id"
              :value="sales.id"
            >
              {{ sales.real_name }} ({{ sales.username }})
            </Option>
          </Select>
        </FormItem>

        <FormItem label="转移原因" field="reason">
          <Textarea
            v-model="formData.reason"
            placeholder="请输入转移原因"
            :max-length="1000"
            :show-word-limit="true"
            :auto-size="{ minRows: 4, maxRows: 8 }"
          />
        </FormItem>

        <FormItem>
          <Space>
            <Button type="primary" html-type="submit" :loading="submitting">
              提交申请
            </Button>
            <Button @click="handleReset">
              重置
            </Button>
            <Button @click="router.back()">
              返回
            </Button>
          </Space>
        </FormItem>
      </Form>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message, FormInstance } from '@arco-design/web-vue'
import { customerApi, type Customer } from '@/api/customer'
import { userApi, type UserInfo } from '@/api/user'
import { transferApi } from '@/api/transfer'
import type { TransferCreateRequest } from '@/types/transfer'

const router = useRouter()
const formRef = ref<FormInstance>()

const submitting = ref(false)
const customersLoading = ref(false)
const salesLoading = ref(false)

const customers = ref<Customer[]>([])
const salesReps = ref<UserInfo[]>([])

const formData = reactive<TransferCreateRequest>({
  customer_id: 0,
  to_sales_rep_id: 0,
  reason: ''
})

const rules = {
  customer_id: [
    { required: true, message: '请选择客户' }
  ],
  to_sales_rep_id: [
    { required: true, message: '请选择转入销售' }
  ],
  reason: [
    { required: true, message: '请输入转移原因' },
    { minLength: 1, maxLength: 1000, message: '转移原因长度需在 1-1000 字符之间' }
  ]
}

const loadCustomers = async () => {
  customersLoading.value = true
  try {
    const response = await customerApi.list({ size: 1000 })
    customers.value = response.items || []
  } catch (error) {
    Message.error('加载客户列表失败')
  } finally {
    customersLoading.value = false
  }
}

const loadSalesReps = async () => {
  salesLoading.value = true
  try {
    // TODO: 后端需要实现获取销售列表的 API
    // salesReps.value = await userApi.listSales()
    Message.info('销售列表功能开发中')
  } catch (error) {
    Message.error('加载销售人员列表失败')
  } finally {
    salesLoading.value = false
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    await transferApi.create(formData)
    Message.success('转移申请提交成功')
    router.push('/transfers/history')
  } catch (error: any) {
    Message.error(error.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

const handleReset = () => {
  formData.customer_id = 0
  formData.to_sales_rep_id = 0
  formData.reason = ''
  formRef.value?.clearValidate()
}

onMounted(() => {
  loadCustomers()
  // TODO: 等后端 API 就绪后取消注释
  // loadSalesReps()
})
</script>

<style scoped lang="scss">
.transfer-create {
  padding: 24px;
}
</style>
