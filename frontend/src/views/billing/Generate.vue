<!-- 结算单生成 -->
<template>
  <div class="billing-generate">
    <Card title="生成结算单">
      <Form ref="formRef" :model="form" :rules="rules" layout="vertical">
        <FormItem label="结算月份" field="month" required>
          <DatePicker
            v-model="form.month"
            mode="month"
            style="width: 100%"
            placeholder="选择结算月份"
          />
        </FormItem>
        <FormItem label="客户范围" field="customer_scope">
          <Select
            v-model="form.customer_scope"
            multiple
            placeholder="选择客户（留空表示全部）"
            style="width: 100%"
            :loading="customersLoading"
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
        <FormItem>
          <Space>
            <Button type="primary" @click="handleSubmit" :loading="loading"
              >生成结算单</Button
            >
            <Button @click="router.back()">返回</Button>
          </Space>
        </FormItem>
      </Form>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { Message } from "@arco-design/web-vue";
import { customerApi, type Customer } from "@/api/customer";
import { billingApi, type BillingCreate } from "@/api/billing";
import type { FormInstance } from "@arco-design/web-vue/es/form/interface";

const router = useRouter();
const formRef = ref<FormInstance>();
const loading = ref(false);
const customersLoading = ref(false);
const customers = ref<Customer[]>([]);

const form = reactive({
  month: null as Date | null,
  customer_scope: [] as number[],
});

const rules = {
  month: [{ required: true, message: "请选择结算月份" }],
};

const loadCustomers = async () => {
  customersLoading.value = true;
  try {
    const response = await customerApi.list({ page: 1, size: 1000 });
    customers.value = response.items || [];
  } catch (error) {
    Message.error("加载客户列表失败");
  } finally {
    customersLoading.value = false;
  }
};

const handleSubmit = async () => {
  try {
    await formRef.value?.validate();
  } catch {
    return;
  }

  if (!form.month) {
    Message.error("请选择结算月份");
    return;
  }

  loading.value = true;
  try {
    const billingDate = form.month.toISOString().split("T")[0] + "-01";

    const targetCustomers =
      form.customer_scope.length > 0
        ? customers.value.filter((c) => form.customer_scope.includes(c.id))
        : customers.value;

    if (targetCustomers.length === 0) {
      Message.warning("没有可生成结算单的客户");
      loading.value = false;
      return;
    }

    let successCount = 0;
    let failCount = 0;

    for (const customer of targetCustomers) {
      try {
        const billingData: BillingCreate = {
          customer_id: customer.id,
          customer_name: customer.name,
          customer_code: customer.code,
          amount: 0,
          billing_date: billingDate,
          remark: `自动生成 - ${billingDate.slice(0, 7)}`,
        };
        await billingApi.create(billingData);
        successCount++;
      } catch (error) {
        failCount++;
        console.error(`为客户 ${customer.name} 生成结算单失败:`, error);
      }
    }

    let message = `生成完成：成功 ${successCount} 个`;
    if (failCount > 0) {
      message += `，失败 ${failCount} 个`;
    }
    Message.success(message);
    router.push("/billing/list");
  } catch (error) {
    Message.error("批量生成失败");
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadCustomers();
});
</script>

<style scoped lang="scss">
.billing-generate {
  padding: 24px;
}
</style>
