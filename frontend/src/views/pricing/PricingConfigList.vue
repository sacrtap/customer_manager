<!-- 价格配置列表 -->
<template>
  <div class="pricing-config-list">
    <Card>
      <template #title>
        <Space>
          <span>价格配置管理</span>
          <Button type="primary" @click="handleCreate">新增配置</Button>
        </Space>
      </template>

      <Table
        :columns="columns"
        :data="data"
        :loading="loading"
        :pagination="pagination"
      >
        <template #status="{ record }">
          <Tag :color="record.status === 'active' ? 'green' : 'red'">{{
            record.status === "active" ? "启用" : "禁用"
          }}</Tag>
        </template>
        <template #base_price="{ record }">
          <span>¥{{ record.base_price.toFixed(2) }}</span>
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
      width="560px"
      :confirm-loading="submitting"
      @ok="handleSubmit"
      @cancel="handleCancel"
    >
      <Form ref="formRef" :model="form" :rules="rules" layout="vertical">
        <FormItem label="配置代码" field="code" required>
          <Input
            v-model="form.code"
            placeholder="请输入配置代码（如：STD_PRICING）"
            :disabled="!!editingId"
          />
        </FormItem>
        <FormItem label="配置名称" field="name" required>
          <Input v-model="form.name" placeholder="请输入配置名称" />
        </FormItem>
        <FormItem label="描述" field="description">
          <Textarea
            v-model="form.description"
            placeholder="请输入配置描述"
            :auto-size="{ minRows: 2, maxRows: 4 }"
          />
        </FormItem>
        <FormItem label="基准价格" field="base_price" required>
          <InputNumber
            v-model="form.base_price"
            placeholder="请输入基准价格"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </FormItem>
        <FormItem label="状态" field="status">
          <RadioGroup v-model="form.status" type="button">
            <Radio value="active">启用</Radio>
            <Radio value="disabled">禁用</Radio>
          </RadioGroup>
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { Message, Modal } from "@arco-design/web-vue";
import type {
  PriceConfig,
  PriceConfigCreate,
  PriceConfigUpdate,
} from "@/api/price-config";
import { priceConfigApi } from "@/api/price-config";
import type { FormInstance } from "@arco-design/web-vue/es/form/interface";

const loading = ref(false);
const submitting = ref(false);
const data = ref<PriceConfig[]>([]);

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
  { title: "配置代码", dataIndex: "code", width: 150 },
  { title: "配置名称", dataIndex: "name", width: 200 },
  { title: "描述", dataIndex: "description", width: 250, ellipsis: true },
  {
    title: "基准价格",
    dataIndex: "base_price",
    slotName: "base_price",
    width: 120,
  },
  { title: "状态", dataIndex: "status", slotName: "status", width: 80 },
  { title: "操作", slotName: "action", width: 150, fixed: "right" },
];

const modalVisible = ref(false);
const editingId = ref<number | null>(null);
const formRef = ref<FormInstance>();

const defaultForm = {
  code: "",
  name: "",
  description: "",
  base_price: 0,
  status: "active" as "active" | "disabled",
};

const form = reactive<PriceConfigCreate>({ ...defaultForm });

const modalTitle = computed(() =>
  editingId.value ? "编辑价格配置" : "新增价格配置",
);

const rules = {
  code: [{ required: true, message: "请输入配置代码" }],
  name: [{ required: true, message: "请输入配置名称" }],
  base_price: [{ required: true, message: "请输入基准价格" }],
};

const loadData = async () => {
  loading.value = true;
  try {
    const response = await priceConfigApi.list({
      page: pagination.current,
      size: pagination.pageSize,
    });
    data.value = response.data || [];
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

const handleEdit = (record: PriceConfig) => {
  editingId.value = record.id;
  form.code = record.code;
  form.name = record.name;
  form.description = record.description || "";
  form.base_price = record.base_price;
  form.status = record.status;
  modalVisible.value = true;
};

const handleDelete = (record: PriceConfig) => {
  Modal.confirm({
    title: "确认删除",
    content: `确定删除"${record.name}"吗？此操作不可恢复。`,
    onOk: async () => {
      try {
        await priceConfigApi.delete(record.id);
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
    if (editingId.value) {
      const updateData: PriceConfigUpdate = {
        name: form.name,
        description: form.description || undefined,
        base_price: form.base_price,
        status: form.status,
      };
      await priceConfigApi.update(editingId.value, updateData);
      Message.success("更新成功");
    } else {
      await priceConfigApi.create(form);
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
.pricing-config-list {
  padding: 24px;
}
</style>
