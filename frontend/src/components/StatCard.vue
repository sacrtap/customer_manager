<template>
  <div class="stat-card">
    <div class="stat-header">
      <div class="stat-icon" :class="iconClass">
        <component :is="icon" />
      </div>
      <slot name="extra"></slot>
    </div>
    <div class="stat-value">{{ value }}</div>
    <div class="stat-label">{{ label }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed, type Component } from "vue";

interface Props {
  icon: Component;
  label: string;
  value: string | number;
  color?: "blue" | "green" | "orange" | "red";
}

const props = withDefaults(defineProps<Props>(), {
  color: "blue",
});

const iconClass = computed(() => props.color);
</script>

<style scoped lang="scss">
.stat-card {
  background: var(--color-bg-1);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-medium);
  padding: 24px;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--border-radius-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-icon.blue {
  background: var(--color-primary-light-1);
  color: var(--color-primary);
}

.stat-icon.green {
  background: var(--color-success-light-1);
  color: var(--color-success);
}

.stat-icon.orange {
  background: var(--color-warning-light-1);
  color: var(--color-warning);
}

.stat-icon.red {
  background: var(--color-danger-light-1);
  color: var(--color-danger);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-1);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-3);
}
</style>
