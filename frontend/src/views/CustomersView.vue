<template>
  <div class="customers-container">
    <div class="header">
      <h1>客户管理</h1>
      <a-button type="primary">新增客户</a-button>
    </div>
    <a-table :columns="columns" :data="data" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const columns = ref([
  { title: 'ID', dataIndex: 'id' },
  { title: '客户名称', dataIndex: 'name' },
  { title: '联系人', dataIndex: 'contact' },
  { title: '电话', dataIndex: 'phone' }
])

const data = ref([])
</script>

<style scoped>
.customers-container {
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
</style>
