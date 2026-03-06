<!-- 结算单生成 -->
<template>
  <div class="billing-generate">
    <Card title="生成结算单">
      <Form :model="form" layout="vertical">
        <FormItem label="结算月份" required>
          <DatePicker mode="month" v-model="form.month" style="width: 100%" />
        </FormItem>
        <FormItem label="客户范围">
          <Select v-model="form.customer_scope" multiple placeholder="选择客户（留空表示全部）" style="width: 100%" />
        </FormItem>
        <FormItem>
          <Space>
            <Button type="primary" @click="handleSubmit" :loading="loading">生成结算单</Button>
            <Button @click="router.back()">返回</Button>
          </Space>
        </FormItem>
      </Form>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'

const router = useRouter()
const loading = ref(false)
const form = reactive({ month: null, customer_scope: [] })

const handleSubmit = async () => {
  loading.value = true
  setTimeout(() => {
    Message.success('结算单生成成功')
    router.push('/billing/list')
    loading.value = false
  }, 1000)
}
</script>

<style scoped lang="scss">
.billing-generate { padding: 24px; }
</style>
