<template>
  <div class="main-layout">
    <a-layout>
      <!-- 侧边栏菜单 -->
      <a-layout-sider
        :width="240"
        :collapsed-width="64"
        collapsible
        breakpoint="xl"
        class="layout-sider"
      >
        <div class="sidebar-header">
          <div class="sidebar-logo">
            <span style="font-size: 18px; font-weight: bold;">CM</span>
          </div>
          <span v-if="!collapsed" class="sidebar-title">客户管理系统</span>
        </div>

        <a-menu
          :selected-keys="selectedMenuKeys"
          :default-selected-keys="['dashboard']"
          @menu-item-click="handleMenuSelect"
          class="sidebar-menu"
        >
          <a-menu-item-group title="工作台">
            <a-menu-item key="dashboard">
              <template #icon>
                <icon-home />
              </template>
              仪表盘
            </a-menu-item>
          </a-menu-item-group>

          <a-menu-item-group title="客户管理">
            <a-sub-menu key="customer">
              <template #icon>
                <icon-user-group />
              </template>
              <template #title>客户管理</template>
              <a-menu-item key="customer-list"> 客户列表 </a-menu-item>
              <a-menu-item
                v-if="hasPermission('customer.import')"
                key="customer-import"
              >
                批量导入
              </a-menu-item>
            </a-sub-menu>
          </a-menu-item-group>

          <a-menu-item-group title="健康监控">
            <a-sub-menu
              v-if="
                hasAnyPermission([
                  'health.view',
                  'health.risk',
                  'health.zombie',
                ])
              "
              key="health"
            >
              <template #icon>
                <icon-bar-chart />
              </template>
              <template #title>健康度监控</template>
              <a-menu-item
                v-if="hasPermission('health.view')"
                key="health-dashboard"
              >
                健康仪表盘
              </a-menu-item>
              <a-menu-item
                v-if="hasPermission('health.risk')"
                key="health-risks"
              >
                风险客户
              </a-menu-item>
              <a-menu-item
                v-if="hasPermission('health.zombie')"
                key="health-zombies"
              >
                僵尸客户
              </a-menu-item>
            </a-sub-menu>
          </a-menu-item-group>

          <a-menu-item-group title="定价管理">
            <a-sub-menu
              v-if="hasAnyPermission(['pricing.view', 'pricing.edit'])"
              key="pricing"
            >
              <template #icon>
                <icon-coins />
              </template>
              <template #title>定价管理</template>
              <a-menu-item
                v-if="hasPermission('pricing.view')"
                key="pricing-configs"
              >
                价格配置
              </a-menu-item>
              <a-menu-item
                v-if="hasPermission('pricing.view')"
                key="pricing-bands"
              >
                价格区间
              </a-menu-item>
              <a-menu-item
                v-if="hasPermission('pricing.view')"
                key="pricing-strategies"
              >
                定价策略
              </a-menu-item>
            </a-sub-menu>
          </a-menu-item-group>

          <a-menu-item-group title="结算管理">
            <a-sub-menu
              v-if="
                hasAnyPermission([
                  'billing.view',
                  'billing.create',
                  'billing.edit',
                ])
              "
              key="billing"
            >
              <template #icon>
                <icon-file />
              </template>
              <template #title>结算管理</template>
              <a-menu-item
                v-if="hasPermission('billing.create')"
                key="billing-generate"
              >
                结算单生成
              </a-menu-item>
              <a-menu-item
                v-if="hasPermission('billing.view')"
                key="billing-list"
              >
                结算单列表
              </a-menu-item>
              <a-menu-item
                v-if="hasPermission('billing.edit')"
                key="billing-exceptions"
              >
                异常处理
              </a-menu-item>
            </a-sub-menu>
          </a-menu-item-group>

          <a-menu-item-group title="客户转移">
            <a-sub-menu
              v-if="hasAnyPermission(['transfer.view', 'transfer.create'])"
              key="transfer"
            >
              <template #icon>
                <icon-swap />
              </template>
              <template #title>客户转移</template>
              <a-menu-item
                v-if="hasPermission('transfer.create')"
                key="transfer-create"
              >
                新建转移
              </a-menu-item>
              <a-menu-item
                v-if="hasPermission('transfer.view')"
                key="transfer-history"
              >
                转移历史
              </a-menu-item>
            </a-sub-menu>
          </a-menu-item-group>

          <a-menu-item-group title="系统管理">
            <a-menu-item
              v-if="hasPermission('system.log.view')"
              key="system-logs"
            >
              <template #icon>
                <icon-history />
              </template>
              操作日志
            </a-menu-item>

            <a-sub-menu
              v-if="hasAnyPermission(['user.view', 'rbac.role'])"
              key="system"
            >
              <template #icon>
                <icon-settings />
              </template>
              <template #title>系统管理</template>
              <a-menu-item v-if="hasPermission('user.view')" key="system-users">
                用户管理
              </a-menu-item>
              <a-menu-item v-if="hasPermission('rbac.role')" key="system-roles">
                角色管理
              </a-menu-item>
              <a-menu-item
                v-if="hasPermission('system.permission')"
                key="system-permissions"
              >
                权限配置
              </a-menu-item>
            </a-sub-menu>
          </a-menu-item-group>
        </a-menu>

        <!-- 侧边栏底部用户信息 -->
        <div class="sidebar-footer">
          <div class="user-info-sidebar">
            <div class="user-avatar-sidebar">
              {{ userInfo.real_name?.charAt(0) }}
            </div>
            <div class="user-details-sidebar">
              <div class="user-name-sidebar">{{ userInfo.real_name }}</div>
              <div class="user-role-sidebar">{{ userInfo.role }}</div>
            </div>
          </div>
        </div>
      </a-layout-sider>

      <a-layout>
        <!-- 顶部导航栏 -->
        <a-layout-header class="layout-header">
          <div class="header-left">
            <a-space>
              <a-breadcrumb>
                <a-breadcrumb-item>首页</a-breadcrumb-item>
                <a-breadcrumb-item>{{ currentPageTitle }}</a-breadcrumb-item>
              </a-breadcrumb>
            </a-space>
          </div>

          <div class="header-right">
            <a-space>
              <!-- 通知图标 -->
              <a-badge :count="notificationCount" :max-count="99">
                <a-button
                  shape="circle"
                  type="text"
                  @click="showNotifications"
                  class="header-icon-btn"
                >
                  <icon-notification />
                </a-button>
              </a-badge>

              <!-- 帮助图标 -->
              <a-button shape="circle" type="text" class="header-icon-btn">
                <icon-question-circle />
              </a-button>

              <!-- 用户信息下拉菜单 -->
              <a-dropdown @select="handleMenuSelect">
                <div class="user-info">
                  <a-avatar
                    :size="32"
                    :style="{
                      background: 'var(--color-primary-light-1)',
                      color: 'var(--color-primary)',
                    }"
                  >
                    {{ userInfo.real_name?.charAt(0) }}
                  </a-avatar>
                  <span class="user-name">{{ userInfo.real_name }}</span>
                  <icon-down />
                </div>

                <template #content>
                  <a-dropdown-menu>
                    <a-dropdown-menu-item key="profile">
                      <icon-user />
                      个人信息
                    </a-dropdown-menu-item>
                    <a-dropdown-menu-item key="change-password">
                      <icon-lock />
                      修改密码
                    </a-dropdown-menu-item>
                    <a-dropdown-menu-item key="divider" />
                    <a-dropdown-menu-item key="logout">
                      <icon-logout />
                      退出登录
                    </a-dropdown-menu-item>
                  </a-dropdown-menu>
                </template>
              </a-dropdown>
            </a-space>
          </div>
        </a-layout-header>

        <!-- 内容区域 -->
        <a-layout-content class="layout-content">
          <router-view />
        </a-layout-content>
      </a-layout>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { Modal, Message } from "@arco-design/web-vue";
import { useUserStore } from "@/stores/user";

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const notificationCount = ref(0);
const collapsed = ref(false);

// 用户信息
const userInfo = computed(() => userStore.userInfo || { real_name: "用户" });

// 当前页面标题
const currentPageTitle = computed(() => {
  const path = route.path;
  if (path === "/dashboard") return "工作台";
  if (path.startsWith("/customers")) {
    if (path === "/customers") return "客户列表";
    if (path === "/customers/import") return "批量导入";
    return "客户管理";
  }
  if (path.startsWith("/health")) {
    if (path === "/health/dashboard") return "健康度仪表盘";
    if (path === "/health/risks") return "风险客户";
    if (path === "/health/zombies") return "僵尸客户";
    return "健康度监控";
  }
  if (path.startsWith("/tiers")) {
    if (path === "/tiers/config") return "等级配置";
    if (path === "/tiers/history") return "定级历史";
    return "价值评估";
  }
  if (path.startsWith("/pricing")) {
    if (path === "/pricing/configs") return "价格配置";
    if (path === "/pricing/bands") return "价格区间";
    if (path === "/pricing/strategies") return "定价策略";
    return "定价管理";
  }
  if (path.startsWith("/billing")) {
    if (path === "/billing/generate") return "结算单生成";
    if (path === "/billing/list") return "结算单列表";
    if (path === "/billing/exceptions") return "异常处理";
    return "结算管理";
  }
  if (path.startsWith("/transfers")) {
    if (path === "/transfers/new") return "客户转移";
    if (path === "/transfers/history") return "转移历史";
    return "客户转移";
  }
  if (path.startsWith("/system")) {
    if (path === "/system/users") return "用户管理";
    if (path === "/system/roles") return "角色管理";
    if (path === "/system/logs") return "操作日志";
    if (path === "/system/permissions") return "权限配置";
    return "系统管理";
  }
  return "首页";
});

// 选中的菜单
const selectedMenuKeys = computed(() => {
  const path = route.path;
  if (path === "/dashboard") return ["dashboard"];
  if (path.startsWith("/customers")) {
    if (path === "/customers") return ["customer", "customer-list"];
    if (path === "/customers/import") return ["customer", "customer-import"];
  }
  if (path.startsWith("/health")) {
    if (path === "/health/dashboard") return ["health", "health-dashboard"];
    if (path === "/health/risks") return ["health", "health-risks"];
    if (path === "/health/zombies") return ["health", "health-zombies"];
  }
  if (path.startsWith("/tiers")) {
    if (path === "/tiers/config") return ["tier", "tier-config"];
    if (path === "/tiers/history") return ["tier", "tier-history"];
  }
  if (path.startsWith("/pricing")) {
    if (path === "/pricing/configs") return ["pricing", "pricing-configs"];
    if (path === "/pricing/bands") return ["pricing", "pricing-bands"];
    if (path === "/pricing/strategies")
      return ["pricing", "pricing-strategies"];
  }
  if (path.startsWith("/billing")) {
    if (path === "/billing/generate") return ["billing", "billing-generate"];
    if (path === "/billing/list") return ["billing", "billing-list"];
    if (path === "/billing/exceptions")
      return ["billing", "billing-exceptions"];
  }
  if (path.startsWith("/transfers")) {
    if (path === "/transfers/new") return ["transfer", "transfer-create"];
    if (path === "/transfers/history") return ["transfer", "transfer-history"];
  }
  if (path.startsWith("/system")) {
    if (path === "/system/users") return ["system", "system-users"];
    if (path === "/system/roles") return ["system", "system-roles"];
    if (path === "/system/logs") return ["system-logs"];
    if (path === "/system/permissions") return ["system", "system-permissions"];
  }
  return [];
});

// 权限检查
const hasPermission = (permission: string) => {
  return userStore.hasPermission(permission);
};

const hasAnyPermission = (permissions: string[]) => {
  return userStore.hasAnyPermission(permissions);
};

// 菜单选择处理
const handleMenuSelect = (key: string) => {
  switch (key) {
    case "dashboard":
      router.push("/dashboard");
      break;
    case "customer-list":
      router.push("/customers");
      break;
    case "customer-import":
      router.push("/customers/import");
      break;
    case "health-dashboard":
      router.push("/health/dashboard");
      break;
    case "health-risks":
      router.push("/health/risks");
      break;
    case "health-zombies":
      router.push("/health/zombies");
      break;
    case "tier-config":
      router.push("/tiers/config");
      break;
    case "tier-history":
      router.push("/tiers/history");
      break;
    case "pricing-configs":
      router.push("/pricing/configs");
      break;
    case "pricing-bands":
      router.push("/pricing/bands");
      break;
    case "pricing-strategies":
      router.push("/pricing/strategies");
      break;
    case "billing-generate":
      router.push("/billing/generate");
      break;
    case "billing-list":
      router.push("/billing/list");
      break;
    case "billing-exceptions":
      router.push("/billing/exceptions");
      break;
    case "transfer-create":
      router.push("/transfers/new");
      break;
    case "transfer-history":
      router.push("/transfers/history");
      break;
    case "system-users":
      router.push("/system/users");
      break;
    case "system-roles":
      router.push("/system/roles");
      break;
    case "system-logs":
      router.push("/system/logs");
      break;
    case "system-permissions":
      router.push("/system/permissions");
      break;
    case "profile":
      router.push("/profile");
      break;
    case "change-password":
      router.push("/change-password");
      break;
    case "logout":
      handleLogout();
      break;
  }
};

// 退出登录
const handleLogout = () => {
  Modal.confirm({
    title: "确认退出",
    content: "确定要退出登录吗?",
    onOk: async () => {
      try {
        await userStore.logout();
        Message.success("退出成功");
        router.push("/login");
      } catch (error) {
        Message.error("退出失败");
      }
    },
  });
};

// 显示通知
const showNotifications = () => {
  Message.info("暂无新通知");
};
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  overflow: hidden;

  .layout-sider {
    background: var(--color-bg-1);
    height: 100vh;
    overflow: hidden;
    border-right: 1px solid var(--color-border);

    .sidebar-header {
      height: 64px;
      display: flex;
      align-items: center;
      padding: 0 20px;
      border-bottom: 1px solid var(--color-border);
    }

    .sidebar-logo {
      width: 40px;
      height: 40px;
      background: var(--color-primary-light-1);
      border-radius: var(--border-radius-medium);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--color-primary);
      font-size: 18px;
      font-weight: bold;
      margin-right: 12px;
      flex-shrink: 0;
    }

    .sidebar-title {
      color: var(--color-text-1);
      font-size: 18px;
      font-weight: 600;
    }

    .sidebar-footer {
      padding: 16px 12px;
      border-top: 1px solid var(--color-border);
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;

      .user-info-sidebar {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 8px;
        border-radius: var(--border-radius-medium);
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          background: var(--color-fill-2);
        }

        .user-avatar-sidebar {
          width: 40px;
          height: 40px;
          background: var(--color-primary-light-1);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--color-primary);
          font-size: 16px;
          font-weight: 600;
          flex-shrink: 0;
        }

        .user-details-sidebar {
          flex: 1;
          overflow: hidden;

          .user-name-sidebar {
            font-size: 14px;
            color: var(--color-text-1);
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }

          .user-role-sidebar {
            font-size: 12px;
            color: var(--color-text-3);
            margin-top: 2px;
          }
        }
      }
    }
  }

  .layout-header {
    height: 64px;
    background: var(--color-bg-1);
    border-bottom: 1px solid var(--color-border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px;

    .header-left {
      display: flex;
      align-items: center;
    }

    .header-right {
      display: flex;
      align-items: center;

      .header-icon-btn {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--color-text-2);
        transition: all 0.2s;

        &:hover {
          background: var(--color-fill-2);
        }
      }

      .user-info {
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
        padding: 6px 12px;
        border-radius: var(--border-radius-medium);
        transition: all 0.2s;

        &:hover {
          background: var(--color-fill-2);
        }

        .user-name {
          font-size: 14px;
          color: var(--color-text-1);
          font-weight: 500;
        }
      }
    }
  }

  .layout-content {
    background: var(--color-fill-2);
    height: calc(100vh - 64px);
    overflow: auto;
  }
}
</style>
