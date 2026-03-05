<!-- frontend/src/components/SearchBar.vue -->
<template>
  <div class="search-bar">
    <Form :model="modelValue" layout="inline" @submit="handleSearch">
      <template v-for="field in fields" :key="field.field">
        <!-- 输入框 -->
        <FormItem v-if="field.type === 'input'" :label="field.label" :field="field.field">
          <Input
            v-model="modelValue[field.field]"
            :placeholder="field.placeholder || `请输入${field.label}`"
            allow-clear
            style="width: 200px"
          />
        </FormItem>

        <!-- 选择器 -->
        <FormItem v-else-if="field.type === 'select'" :label="field.label" :field="field.field">
          <Select
            v-model="modelValue[field.field]"
            :placeholder="field.placeholder || `请选择${field.label}`"
            allow-clear
            multiple
            style="width: 200px"
          >
            <Option
              v-for="option in field.options"
              :key="option.value"
              :value="option.value"
              :label="option.label"
            />
          </Select>
        </FormItem>

        <!-- 范围选择 -->
        <FormItem v-else-if="field.type === 'range'" :label="field.label">
          <InputNumber
            v-model="modelValue[`${field.field}_min`]"
            :placeholder="`最小${field.label}`"
            style="width: 120px"
          />
          <span style="margin: 0 8px">-</span>
          <InputNumber
            v-model="modelValue[`${field.field}_max`]"
            :placeholder="`最大${field.label}`"
            style="width: 120px"
          />
        </FormItem>

        <!-- 日期选择 -->
        <FormItem v-else-if="field.type === 'date'" :label="field.label">
          <RangePicker v-model="modelValue[field.field]" style="width: 240px" />
        </FormItem>
      </template>

      <FormItem>
        <Space>
          <Button type="primary" html-type="submit">
            <template #icon><icon-search /></template>
            搜索
          </Button>
          <Button @click="handleReset">
            <template #icon><icon-refresh /></template>
            重置
          </Button>
        </Space>
      </FormItem>
    </Form>
  </div>
</template>

<script setup lang="ts">
import {
  Form,
  FormItem,
  Input,
  Select,
  Option,
  Button,
  Space,
  InputNumber,
  RangePicker
} from '@arco-design/web-vue'

interface SearchField {
  label: string
  field: string
  type: 'input' | 'select' | 'range' | 'date'
  placeholder?: string
  options?: Array<{ value: string | number; label: string }>
}

defineProps<{
  modelValue: Record<string, any>
  fields: SearchField[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: Record<string, any>): void
  (e: 'search'): void
  (e: 'reset'): void
}>()

const handleSearch = () => {
  emit('search')
}

const handleReset = () => {
  emit('reset')
}
</script>

<style scoped lang="scss">
.search-bar {
  padding: 16px 0;
  margin-bottom: 16px;
  background: var(--color-bg-2);
  border-radius: 4px;
}
</style>
