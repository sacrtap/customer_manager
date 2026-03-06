<!-- 结算单详情 -->
<template>
  <div class="billing-detail">
    <Card title="结算单详情">
      <Descriptions :column="2" bordered>
        <DescriptionsItem label="结算单号">BILL-2026-001</DescriptionsItem>
        <DescriptionsItem label="月份">2026-02</DescriptionsItem>
        <DescriptionsItem label="客户数">1280</DescriptionsItem>
        <DescriptionsItem label="总金额">¥2,456,800.00</DescriptionsItem>
        <DescriptionsItem label="状态"><Tag color="green">已发送</Tag></DescriptionsItem>
        <DescriptionsItem label="创建时间">2026-03-01 10:00:00</DescriptionsItem>
      </Descriptions>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped lang="scss">
.billing-detail { padding: 24px; }
</style>
