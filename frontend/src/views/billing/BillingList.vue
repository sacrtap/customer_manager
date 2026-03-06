<!-- 结算单列表 -->
<template>
  <div class="billing-list">
    <Card title="结算单列表">
      <template #extra>
        <Space>
          <Input
            v-model="searchForm.customer_name"
            placeholder="客户名称"
            style="width: 200px"
            @press-enter="handleSearch"
          />
          <Select
            v-model="searchForm.status"
            placeholder="状态"
            style="width: 120px"
            @change="handleSearch"
          >
            <Option value="">全部</Option>
            <Option value="pending">待发送</Option>
            <Option value="sent">已发送</Option>
            <Option value="paid">已付款</Option>
            <Option value="exception">异常</Option>
          </Select>
          <Button type="primary" @click="handleSearch">查询</Button>
          <Button @click="handleReset">重置</Button>
        </Space>
      </template>

      <Table
        :columns="columns"
        :data="data"
        :loading="loading"
        :pagination="pagination"
      >
        <template #status="{ record }">
          <Tag :color="getStatusColor(record.status)">
            {{ getStatusText(record.status) }}
          </Tag>
        </template>
        <template #amount="{ record }">
          <span>¥{{ record.amount.toFixed(2) }}</span>
        </template>
        <template #action="{ record }">
          <Space>
            <Button
              type="text"
              size="small"
              @click="router.push(`/billing/${record.id}`)"
              >详情</Button
            >
            <Dropdown
              trigger="click"
              @select="(key) => handleAction(record, key)"
            >
              <Button type="text" size="small">更多▾</Button>
              <template #content>
                <DOption
                  v-if="record.status === 'pending'"
                  key="send"
                  :disabled="!hasPermission('billing.send')"
                  >发送</DOption
                >
                <DOption
                  v-if="record.status === 'sent'"
                  key="mark_paid"
                  :disabled="!hasPermission('billing.update')"
                  >标记付款</DOption
                >
                <DOption
                  v-if="record.status !== 'exception'"
                  key="mark_exception"
                  :disabled="!hasPermission('billing.update')"
                  >标记异常</DOption
                >
                <DOption
                  v-if="record.status === 'exception'"
                  key="resolve_exception"
                  :disabled="!hasPermission('billing.update')"
                  >解决异常</DOption
                >
                <DOption
                  key="delete"
                  status="danger"
                  :disabled="!hasPermission('billing.delete')"
                  >删除</DOption
                >
              </template>
            </Dropdown>
          </Space>
        </template>
      </Table>
    </Card>

    <Modal
      v-model:visible="exceptionModalVisible"
      title="标记异常原因"
      width="480px"
      :confirm-loading="submitting"
      @ok="handleExceptionSubmit"
      @cancel="exceptionModalVisible = false"
    >
      <Form ref="exceptionFormRef" :model="exceptionForm" layout="vertical">
        <FormItem label="异常原因" field="reason" required>
          <Textarea
            v-model="exceptionForm.reason"
            placeholder="请输入异常原因"
            :auto-size="{ minRows: 3, maxRows: 6 }"
          />
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { Message, Modal } from "@arco-design/web-vue";
import type { Billing } from "@/api/billing";
import { billingApi } from "@/api/billing";
import type { FormInstance } from "@arco-design/web-vue/es/form/interface";
import { useUserStore } from "@/store/user";

const router = useRouter();
const userStore = useUserStore();

const loading = ref(false);
const submitting = ref(false);
const data = ref<Billing[]>([]);
const pagination = reactive({
  total: 0,
  current: 1,
  pageSize: 20,
  showTotal: true,
  showPageSize: true,
});

const searchForm = reactive({
  customer_name: "",
  status: "",
});

interface Column {
  title: string;
  dataIndex: string;
  width: number;
  slotName?: string;
  fixed?: "left" | "right";
}

const columns: Column[] = [
  { title: "结算单号", dataIndex: "id", width: 200 },
  { title: "客户名称", dataIndex: "customer_name", width: 200 },
  { title: "客户代码", dataIndex: "customer_code", width: 120 },
  { title: "金额", dataIndex: "amount", slotName: "amount", width: 120 },
  { title: "结算日期", dataIndex: "billing_date", width: 120 },
  { title: "到期日期", dataIndex: "due_date", width: 120 },
  { title: "状态", dataIndex: "status", slotName: "status", width: 100 },
  { title: "操作", slotName: "action", width: 200, fixed: "right" },
];

const exceptionModalVisible = ref(false);
const currentBillingId = ref<string | null>(null);
const exceptionFormRef = ref<FormInstance>();
const exceptionForm = reactive({ reason: "" });

const hasPermission = (permission: string) => {
  const permissions = userStore.permissions;
  return permissions.includes("admin") || permissions.includes(permission);
};

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    pending: "orange",
    sent: "green",
    paid: "blue",
    exception: "red",
  };
  return colors[status] || "gray";
};

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: "待发送",
    sent: "已发送",
    paid: "已付款",
    exception: "异常",
  };
  return texts[status] || status;
};

const loadData = async () => {
  loading.value = true;
  try {
    const query: Record<string, any> = {
      page: pagination.current,
      size: pagination.pageSize,
    };
    if (searchForm.status) {
      query.status = searchForm.status;
    }

    const response = await billingApi.list(query);
    data.value = response.items || [];
    pagination.total = response.total || 0;
  } catch (error) {
    Message.error("加载失败");
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  pagination.current = 1;
  loadData();
};

const handleReset = () => {
  searchForm.customer_name = "";
  searchForm.status = "";
  pagination.current = 1;
  loadData();
};

const handleAction = (record: Billing, key: string) => {
  switch (key) {
    case "send":
      handleSend(record);
      break;
    case "mark_paid":
      handleMarkPaid(record);
      break;
    case "mark_exception":
      handleMarkException(record);
      break;
    case "resolve_exception":
      handleResolveException(record);
      break;
    case "delete":
      handleDelete(record);
      break;
  }
};

const handleSend = async (record: Billing) => {
  Modal.confirm({
    title: "确认发送",
    content: `确定发送结算单 "${record.id}" 给客户吗？`,
    onOk: async () => {
      try {
        await billingApi.markAsSent(record.id);
        Message.success("发送成功");
        loadData();
      } catch (error) {
        Message.error("发送失败");
      }
    },
  });
};

const handleMarkPaid = async (record: Billing) => {
  Modal.confirm({
    title: "确认付款",
    content: `确定标记结算单 "${record.id}" 为已付款吗？`,
    onOk: async () => {
      try {
        await billingApi.markAsPaid(record.id);
        Message.success("已标记为付款");
        loadData();
      } catch (error) {
        Message.error("操作失败");
      }
    },
  });
};

const handleMarkException = (record: Billing) => {
  currentBillingId.value = record.id;
  exceptionForm.reason = "";
  exceptionModalVisible.value = true;
};

const handleExceptionSubmit = async () => {
  try {
    await exceptionFormRef.value?.validate();
  } catch {
    return;
  }

  if (!currentBillingId.value) return;

  submitting.value = true;
  try {
    await billingApi.markException(
      currentBillingId.value,
      exceptionForm.reason,
    );
    Message.success("已标记为异常");
    exceptionModalVisible.value = false;
    loadData();
  } catch (error) {
    Message.error("操作失败");
  } finally {
    submitting.value = false;
  }
};

const handleResolveException = async (record: Billing) => {
  Modal.confirm({
    title: "解决异常",
    content: `确定解决结算单 "${record.id}" 的异常状态吗？`,
    onOk: async () => {
      try {
        await billingApi.markAsSent(record.id);
        Message.success("已解决异常");
        loadData();
      } catch (error) {
        Message.error("操作失败");
      }
    },
  });
};

const handleDelete = (record: Billing) => {
  Modal.confirm({
    title: "确认删除",
    content: `确定删除结算单 "${record.id}" 吗？此操作不可恢复。`,
    onOk: async () => {
      try {
        await billingApi.delete(record.id);
        Message.success("删除成功");
        loadData();
      } catch (error) {
        Message.error("删除失败");
      }
    },
  });
};

onMounted(() => loadData());
</script>

<style scoped lang="scss">
.billing-list {
  padding: 24px;
}
</style>
