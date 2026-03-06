<!-- 异常数据处理 -->
<template>
  <div class="exception-list">
    <Card title="异常数据处理">
      <Table
        :columns="columns"
        :data="data"
        :loading="loading"
        :pagination="pagination"
      >
        <template #exception_type="{ record }">
          <Tag color="red">{{ record.exception_type }}</Tag>
        </template>
        <template #action="{ record }">
          <Space>
            <Button type="text" size="small" @click="handleFix(record)"
              >修复</Button
            >
            <Button type="text" size="small" @click="handleIgnore(record)"
              >忽略</Button
            >
          </Space>
        </template>
      </Table>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { Message } from "@arco-design/web-vue";

const loading = ref(false);
const data = ref<any[]>([]);
const pagination = reactive({ total: 0, current: 1, pageSize: 20 });

const columns = [
  { title: "异常 ID", dataIndex: "id", width: 80 },
  {
    title: "类型",
    dataIndex: "exception_type",
    slotName: "exception_type",
    width: 150,
  },
  { title: "描述", dataIndex: "description", width: 400 },
  { title: "发生时间", dataIndex: "created_at", width: 180 },
  { title: "操作", slotName: "action", width: 150, fixed: "right" },
];

const handleFix = (record: any) => Message.info(`修复：${record.description}`);
const handleIgnore = (record: any) =>
  Message.info(`忽略：${record.description}`);

const loadData = async () => {
  loading.value = true;
  try {
    data.value = [];
  } finally {
    loading.value = false;
  }
};

onMounted(() => loadData());
</script>

<style scoped lang="scss">
.exception-list {
  padding: 24px;
}
</style>
