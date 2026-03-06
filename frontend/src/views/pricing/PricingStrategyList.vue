<!-- 定价策略列表 -->
<template>
  <div class="pricing-strategy-list">
    <Card>
      <template #title>
        <Space>
          <span>定价策略管理</span>
          <Button type="primary" @click="handleCreate">新增策略</Button>
        </Space>
      </template>

      <Table
        :columns="columns"
        :data="data"
        :loading="loading"
        :pagination="pagination"
      >
        <template #status="{ record }">
          <Tag :color="record.status === 'active' ? 'green' : 'gray'">{{
            record.status === "active" ? "启用" : "禁用"
          }}</Tag>
        </template>
        <template #discount_rate="{ record }">
          <span>{{
            record.discount_type === "percentage"
              ? `${record.discount_value}%`
              : `¥${record.discount_value}`
          }}</span>
        </template>
        <template #action="{ record }">
          <Space>
            <Button type="text" size="small" @click="handleEdit(record)"
              >编辑</Button
            >
            <Button
              type="text"
              size="small"
              status="danger"
              @click="handleDelete(record)"
              >删除</Button
            >
          </Space>
        </template>
      </Table>
    </Card>

    <Modal
      v-model:visible="modalVisible"
      :title="modalTitle"
      width="640px"
      :confirm-loading="submitting"
      @ok="handleSubmit"
      @cancel="handleCancel"
    >
      <Form ref="formRef" :model="form" :rules="rules" layout="vertical">
        <FormItem label="策略名称" field="name" required>
          <Input v-model="form.name" placeholder="请输入策略名称" />
        </FormItem>
        <FormItem label="策略编码" field="code" required>
          <Input
            v-model="form.code"
            placeholder="请输入策略编码（如：VIP_DISCOUNT）"
            :disabled="!!editingId"
          />
        </FormItem>
        <FormItem label="描述" field="description">
          <Textarea
            v-model="form.description"
            placeholder="请输入策略描述"
            :auto-size="{ minRows: 2, maxRows: 4 }"
          />
        </FormItem>
        <FormItem label="适用客户类型" field="applicable_customer_type">
          <Input
            v-model="form.applicable_customer_type"
            placeholder="如：企业客户、个人客户"
          />
        </FormItem>
        <FormItem label="适用等级" field="applicable_tier_levels">
          <Select
            v-model="form.applicable_tier_levels"
            multiple
            placeholder="选择适用等级"
            allow-create
          >
            <Option value="tier1">tier1</Option>
            <Option value="tier2">tier2</Option>
            <Option value="tier3">tier3</Option>
          </Select>
        </FormItem>
        <FormItem label="折扣类型" field="discount_type" required>
          <RadioGroup v-model="form.discount_type" type="button">
            <Radio value="percentage">百分比</Radio>
            <Radio value="fixed">固定金额</Radio>
          </RadioGroup>
        </FormItem>
        <FormItem label="折扣值" field="discount_value" required>
          <InputNumber
            v-model="form.discount_value"
            :placeholder="
              form.discount_type === 'percentage'
                ? '请输入百分比值（如：15 表示 15%）'
                : '请输入固定金额'
            "
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </FormItem>
        <FormItem label="优先级" field="priority" required>
          <InputNumber
            v-model="form.priority"
            placeholder="数字越大优先级越高"
            :min="0"
            style="width: 100%"
          />
        </FormItem>
        <FormItem label="状态" field="status">
          <RadioGroup v-model="form.status" type="button">
            <Radio value="active">启用</Radio>
            <Radio value="inactive">禁用</Radio>
          </RadioGroup>
        </FormItem>
        <FormItem label="有效期" field="valid_period">
          <RangePicker
            v-model="form.valid_period"
            :allow-clear="true"
            style="width: 100%"
          />
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { Message, Modal } from "@arco-design/web-vue";
import type {
  PricingStrategy,
  PricingStrategyCreate,
  PricingStrategyUpdate,
} from "@/api/pricing-strategy";
import { pricingStrategyApi } from "@/api/pricing-strategy";
import type { FormInstance } from "@arco-design/web-vue/es/form/interface";

const loading = ref(false);
const submitting = ref(false);
const data = ref<PricingStrategy[]>([]);

const pagination = reactive({
  total: 0,
  current: 1,
  pageSize: 20,
  showTotal: true,
  showPageSize: true,
});

interface Column {
  title: string;
  dataIndex: string;
  width: number;
  slotName?: string;
  fixed?: "left" | "right";
}

const columns: Column[] = [
  { title: "策略名称", dataIndex: "name", width: 200 },
  { title: "策略编码", dataIndex: "code", width: 150 },
  { title: "适用客户", dataIndex: "applicable_customer_type", width: 150 },
  {
    title: "折扣率",
    dataIndex: "discount_value",
    slotName: "discount_rate",
    width: 120,
  },
  { title: "优先级", dataIndex: "priority", width: 80 },
  { title: "状态", dataIndex: "status", slotName: "status", width: 80 },
  { title: "操作", slotName: "action", width: 150, fixed: "right" },
];

const modalVisible = ref(false);
const editingId = ref<number | null>(null);
const formRef = ref<FormInstance>();

const defaultForm = {
  name: "",
  code: "",
  description: "",
  applicable_customer_type: "",
  applicable_tier_levels: [] as string[],
  discount_type: "percentage" as "percentage" | "fixed",
  discount_value: 0,
  priority: 0,
  status: "active" as "active" | "inactive",
  valid_period: [] as (string | number | Date)[] | null,
};

const form = reactive<
  PricingStrategyCreate & { valid_period: (string | number | Date)[] | null }
>({ ...defaultForm });

const modalTitle = computed(() =>
  editingId.value ? "编辑定价策略" : "新增定价策略",
);

const rules = {
  name: [{ required: true, message: "请输入策略名称" }],
  code: [{ required: true, message: "请输入策略编码" }],
  discount_type: [{ required: true, message: "请选择折扣类型" }],
  discount_value: [{ required: true, message: "请输入折扣值" }],
  priority: [{ required: true, message: "请输入优先级" }],
};

const loadData = async () => {
  loading.value = true;
  try {
    const response = await pricingStrategyApi.list({
      page: pagination.current,
      size: pagination.pageSize,
    });
    data.value = response.items || [];
    pagination.total = response.total || 0;
  } catch (error) {
    Message.error("加载失败");
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  Object.assign(form, defaultForm);
  formRef.value?.resetFields();
};

const handleCreate = () => {
  resetForm();
  editingId.value = null;
  modalVisible.value = true;
};

const handleEdit = (record: PricingStrategy) => {
  editingId.value = record.id;
  form.name = record.name;
  form.code = record.code;
  form.description = record.description || "";
  form.applicable_customer_type = record.applicable_customer_type || "";
  form.applicable_tier_levels = [...record.applicable_tier_levels];
  form.discount_type = record.discount_type;
  form.discount_value = record.discount_value;
  form.priority = record.priority;
  form.status = record.status;
  form.valid_period =
    record.valid_from && record.valid_to
      ? [record.valid_from, record.valid_to]
      : null;
  modalVisible.value = true;
};

const handleDelete = (record: PricingStrategy) => {
  Modal.confirm({
    title: "确认删除",
    content: `确定删除"${record.name}"吗？此操作不可恢复。`,
    onOk: async () => {
      try {
        await pricingStrategyApi.delete(record.id);
        Message.success("删除成功");
        loadData();
      } catch (error) {
        Message.error("删除失败");
      }
    },
  });
};

const handleCancel = () => {
  resetForm();
  modalVisible.value = false;
};

const handleSubmit = async () => {
  try {
    await formRef.value?.validate();
  } catch {
    return;
  }

  submitting.value = true;
  try {
    const submitData: PricingStrategyCreate = {
      name: form.name,
      code: form.code,
      description: form.description || undefined,
      applicable_customer_type: form.applicable_customer_type || undefined,
      applicable_tier_levels: form.applicable_tier_levels,
      discount_type: form.discount_type,
      discount_value: form.discount_value,
      priority: form.priority,
      status: form.status,
      ...(form.valid_period && form.valid_period.length === 2
        ? {
            valid_from: String(form.valid_period[0]),
            valid_to: String(form.valid_period[1]),
          }
        : {}),
    };

    if (editingId.value) {
      const updateData: PricingStrategyUpdate = {};
      if (submitData.name) updateData.name = submitData.name;
      if (submitData.description !== undefined)
        updateData.description = submitData.description;
      if (submitData.applicable_customer_type !== undefined)
        updateData.applicable_customer_type =
          submitData.applicable_customer_type;
      if (submitData.applicable_tier_levels)
        updateData.applicable_tier_levels = submitData.applicable_tier_levels;
      if (submitData.discount_type)
        updateData.discount_type = submitData.discount_type;
      if (submitData.discount_value !== undefined)
        updateData.discount_value = submitData.discount_value;
      if (submitData.priority !== undefined)
        updateData.priority = submitData.priority;
      if (submitData.status) updateData.status = submitData.status;
      if (submitData.valid_from) updateData.valid_from = submitData.valid_from;
      if (submitData.valid_to) updateData.valid_to = submitData.valid_to;

      await pricingStrategyApi.update(editingId.value, updateData);
      Message.success("更新成功");
    } else {
      await pricingStrategyApi.create(submitData);
      Message.success("创建成功");
    }

    modalVisible.value = false;
    resetForm();
    loadData();
  } catch (error) {
    Message.error(editingId.value ? "更新失败" : "创建失败");
  } finally {
    submitting.value = false;
  }
};

onMounted(() => loadData());
</script>

<style scoped lang="scss">
.pricing-strategy-list {
  padding: 24px;
}
</style>
