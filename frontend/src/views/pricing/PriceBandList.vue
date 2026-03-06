<!-- frontend/src/views/pricing/PriceBandList.vue -->
<template>
  <div class="price-band-list">
    <Card>
      <template #title>
        <Space>
          <span>价格区间管理</span>
          <Button type="primary" @click="handleCreate"> 新增区间 </Button>
        </Space>
      </template>

      <!-- 搜索栏 -->
      <a-form layout="inline" :model="searchForm" class="search-form">
        <a-form-item label="区间代码">
          <a-input
            v-model="searchForm.code"
            placeholder="请输入区间代码"
            allow-clear
            style="width: 200px"
          />
        </a-form-item>
        <a-form-item label="区间名称">
          <a-input
            v-model="searchForm.name"
            placeholder="请输入区间名称"
            allow-clear
            style="width: 200px"
          />
        </a-form-item>
        <a-form-item label="状态">
          <a-select
            v-model="searchForm.is_active"
            placeholder="请选择状态"
            allow-clear
            style="width: 150px"
          >
            <a-option :value="true">启用</a-option>
            <a-option :value="false">禁用</a-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <Space>
            <a-button type="primary" @click="handleSearch">查询</a-button>
            <a-button @click="handleReset">重置</a-button>
          </Space>
        </a-form-item>
      </a-form>

      <!-- 价格区间表格 -->
      <a-table
        :columns="columns"
        :data="priceBands"
        :loading="loading"
        :pagination="pagination"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
        row-key="id"
      >
        <template #is_active="{ record }">
          <a-tag :color="record.is_active ? 'green' : 'red'">
            {{ record.is_active ? "启用" : "禁用" }}
          </a-tag>
        </template>
        <template #priority="{ record }">
          <a-tag :color="getPriorityColor(record.priority)">
            {{ record.priority }}
          </a-tag>
        </template>
        <template #action="{ record }">
          <Space>
            <a-button type="text" size="small" @click="handleEdit(record)">
              编辑
            </a-button>
            <a-button
              type="text"
              size="small"
              status="danger"
              @click="handleDelete(record)"
            >
              删除
            </a-button>
          </Space>
        </template>
      </a-table>
    </Card>

    <!-- 新建/编辑对话框 -->
    <a-modal
      v-model:visible="dialog.visible"
      :title="dialog.isEdit ? '编辑价格区间' : '新增价格区间'"
      width="800px"
      @before-ok="handleSubmit"
    >
      <a-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        layout="vertical"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="区间代码" field="code">
              <a-input
                v-model="formData.code"
                placeholder="请输入区间代码"
                :disabled="dialog.isEdit"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="区间名称" field="name">
              <a-input v-model="formData.name" placeholder="请输入区间名称" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="描述" field="description">
          <a-textarea
            v-model="formData.description"
            placeholder="请输入描述"
            :max-length="500"
            show-word-limit
          />
        </a-form-item>

        <a-divider orientation="left">区间条件</a-divider>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="最小数量" field="min_quantity">
              <a-input-number
                v-model="formData.min_quantity"
                placeholder="请输入最小数量"
                :min="0"
                :step="1"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="最大数量" field="max_quantity">
              <a-input-number
                v-model="formData.max_quantity"
                placeholder="请输入最大数量"
                :min="0"
                :step="1"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="最小金额" field="min_amount">
              <a-input-number
                v-model="formData.min_amount"
                placeholder="请输入最小金额"
                :min="0"
                :precision="2"
                :step="0.01"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="最大金额" field="max_amount">
              <a-input-number
                v-model="formData.max_amount"
                placeholder="请输入最大金额"
                :min="0"
                :precision="2"
                :step="0.01"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-divider orientation="left">价格定义</a-divider>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="单价" field="unit_price">
              <a-input-number
                v-model="formData.unit_price"
                placeholder="请输入单价"
                :min="0"
                :precision="2"
                :step="0.01"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="折扣率 (%)" field="discount_rate">
              <a-input-number
                v-model="formData.discount_rate"
                placeholder="请输入折扣率"
                :min="0"
                :max="100"
                :precision="2"
                :step="0.01"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="最终价格" field="final_price">
              <a-input-number
                v-model="formData.final_price"
                placeholder="请输入最终价格"
                :min="0"
                :precision="2"
                :step="0.01"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="优先级" field="priority">
              <a-input-number
                v-model="formData.priority"
                placeholder="请输入优先级"
                :min="0"
                :step="1"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="状态" field="is_active">
              <a-switch
                v-model="formData.is_active"
                checked-value
                unchecked-value="false"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label=" " field="placeholder">
              <span style="color: #86909c; font-size: 13px">
                开启表示启用该价格区间
              </span>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="生效日期" field="valid_from">
              <a-date-picker
                v-model="formData.valid_from"
                placeholder="请选择生效日期"
                style="width: 100%"
                format="YYYY-MM-DD"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="失效日期" field="valid_until">
              <a-date-picker
                v-model="formData.valid_until"
                placeholder="请选择失效日期"
                style="width: 100%"
                format="YYYY-MM-DD"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { Message, Modal } from "@arco-design/web-vue";
import { priceBandApi } from "@/api/price-band";
import type {
  PriceBand,
  PriceBandFilters,
  PriceBandCreateRequest,
  PriceBandUpdateRequest,
} from "@/types/price-band";

const loading = ref(false);
const priceBands = ref<PriceBand[]>([]);
const formRef = ref();

// 搜索表单
const searchForm = reactive<PriceBandFilters>({
  code: undefined,
  name: undefined,
  is_active: undefined,
  sort_by: "priority",
  sort_order: "desc",
});

// 分页
const pagination = reactive({
  total: 0,
  current: 1,
  pageSize: 20,
  showTotal: true,
  showPageSize: true,
});

// 表格列定义
const columns = [
  { title: "ID", dataIndex: "id", width: 80 },
  { title: "区间代码", dataIndex: "code", width: 150 },
  { title: "区间名称", dataIndex: "name", width: 200 },
  { title: "描述", dataIndex: "description", width: 200, ellipsis: true },
  { title: "最小数量", dataIndex: "min_quantity", width: 100 },
  { title: "最大数量", dataIndex: "max_quantity", width: 100 },
  { title: "最小金额", dataIndex: "min_amount", width: 100 },
  { title: "最大金额", dataIndex: "max_amount", width: 100 },
  { title: "单价", dataIndex: "unit_price", width: 100 },
  { title: "折扣率 (%)", dataIndex: "discount_rate", width: 100 },
  { title: "最终价格", dataIndex: "final_price", width: 100 },
  { title: "优先级", slotName: "priority", width: 80 },
  { title: "状态", slotName: "is_active", width: 80 },
  {
    title: "操作",
    slotName: "action",
    width: 150,
    fixed: "right",
  },
];

// 对话框状态
const dialog = reactive({
  visible: false,
  isEdit: false,
  currentId: null as number | null,
});

// 表单数据
const formData = ref<PriceBandCreateRequest>({
  name: "",
  code: "",
  description: "",
  price_config_id: undefined,
  min_quantity: undefined,
  max_quantity: undefined,
  min_amount: undefined,
  max_amount: undefined,
  unit_price: undefined,
  discount_rate: undefined,
  final_price: undefined,
  priority: 0,
  is_active: true,
  valid_from: undefined,
  valid_until: undefined,
});

// 表单验证规则
const formRules = {
  code: [
    { required: true, message: "请输入区间代码" },
    { maxLength: 50, message: "区间代码不能超过 50 个字符" },
  ],
  name: [
    { required: true, message: "请输入区间名称" },
    { maxLength: 100, message: "区间名称不能超过 100 个字符" },
  ],
};

// 加载价格区间列表
const loadPriceBands = async () => {
  loading.value = true;
  try {
    const response = await priceBandApi.list({
      ...searchForm,
      page: pagination.current,
      page_size: pagination.pageSize,
    });
    priceBands.value = response.items;
    pagination.total = response.total;
  } catch (error) {
    Message.error("加载价格区间列表失败");
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  pagination.current = 1;
  loadPriceBands();
};

// 重置
const handleReset = () => {
  searchForm.code = undefined;
  searchForm.name = undefined;
  searchForm.is_active = undefined;
  handleSearch();
};

// 分页变化
const handlePageChange = (page: number) => {
  pagination.current = page;
  loadPriceBands();
};

const handlePageSizeChange = (size: number) => {
  pagination.pageSize = size;
  pagination.current = 1;
  loadPriceBands();
};

// 打开新建对话框
const handleCreate = () => {
  dialog.visible = true;
  dialog.isEdit = false;
  dialog.currentId = null;
  formData.value = {
    name: "",
    code: "",
    description: "",
    price_config_id: undefined,
    min_quantity: undefined,
    max_quantity: undefined,
    min_amount: undefined,
    max_amount: undefined,
    unit_price: undefined,
    discount_rate: undefined,
    final_price: undefined,
    priority: 0,
    is_active: true,
    valid_from: undefined,
    valid_until: undefined,
  };
  formRef.value?.clearValidate();
};

// 打开编辑对话框
const handleEdit = (record: PriceBand) => {
  dialog.visible = true;
  dialog.isEdit = true;
  dialog.currentId = record.id;
  formData.value = {
    name: record.name,
    code: record.code,
    description: record.description,
    price_config_id: record.price_config_id,
    min_quantity: record.min_quantity,
    max_quantity: record.max_quantity,
    min_amount: record.min_amount,
    max_amount: record.max_amount,
    unit_price: record.unit_price,
    discount_rate: record.discount_rate,
    final_price: record.final_price,
    priority: record.priority,
    is_active: record.is_active,
    valid_from: record.valid_from,
    valid_until: record.valid_until,
  };
};

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate();

    if (dialog.isEdit && dialog.currentId) {
      await priceBandApi.update(
        dialog.currentId,
        formData.value as PriceBandUpdateRequest,
      );
      Message.success("更新成功");
    } else {
      await priceBandApi.create(formData.value as PriceBandCreateRequest);
      Message.success("创建成功");
    }

    dialog.visible = false;
    loadPriceBands();
    return true;
  } catch (error) {
    Message.error("操作失败");
    return false;
  }
};

// 删除
const handleDelete = (record: PriceBand) => {
  Modal.warning({
    title: "确认删除",
    content: `确定要删除价格区间"${record.name}"吗？`,
    okText: "确认删除",
    okButtonProps: { status: "danger" },
    onOk: async () => {
      try {
        await priceBandApi.delete(record.id);
        Message.success("删除成功");
        loadPriceBands();
      } catch (error) {
        Message.error("删除失败");
      }
    },
  });
};

// 获取优先级颜色
const getPriorityColor = (priority: number) => {
  if (priority >= 10) return "red";
  if (priority >= 5) return "orange";
  if (priority > 0) return "blue";
  return "gray";
};

onMounted(() => {
  loadPriceBands();
});
</script>

<style scoped lang="scss">
.price-band-list {
  padding: 20px;
}

.search-form {
  margin-bottom: 16px;
}
</style>
