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
@import "@/styles/variables.scss";

.stat-card {
  @include stat-card;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-sm;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: $border-radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-size-lg;
}

.stat-icon.blue {
  background: $blue-gradient;
  color: $primary-color;
}

.stat-icon.green {
  background: $success-gradient;
  color: $success-color;
}

.stat-icon.orange {
  background: $warning-gradient;
  color: $warning-color;
}

.stat-icon.red {
  background: $danger-gradient;
  color: $danger-color;
}

.stat-value {
  font-size: $font-size-3xl;
  font-weight: 700;
  color: #1d2129;
  margin-bottom: 4px;
}

.stat-label {
  font-size: $font-size-md;
  color: #86909c;
}
</style>
